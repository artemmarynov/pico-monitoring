import logging
import signal
import threading
import time

import apprise
import paho.mqtt.client as mqtt
from common.measurements import Measurement

from notifier.alerts import AlertRules, AlertWorker
from notifier.healthcheck import HEARTBEAT
from notifier.settings import Settings
from notifier.watchdog import SensorWatch

log = logging.getLogger(__name__)


def handle_payload(payload, rules, worker):
    try:
        measurement = Measurement.from_payload(payload)
    except ValueError as exc:
        log.warning("Skipped MQTT message: %s", exc)
        return
    body = rules.evaluate(measurement)
    if body:
        worker.submit(body)
    return measurement


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    settings = Settings()
    provider = None
    if settings.apprise_url and settings.apprise_url.get_secret_value():
        provider = apprise.Apprise()
        if not provider.add(settings.apprise_url.get_secret_value()):
            raise ValueError("Invalid notification provider configuration")
    worker = AlertWorker(provider)
    rules = AlertRules()
    watch = SensorWatch(settings.sensor_stale_seconds)
    stopped = threading.Event()
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: stopped.set())
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(settings.user, settings.password.get_secret_value())
    client.will_set(settings.status_topic, "offline", retain=True)

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            client.subscribe(settings.mqtt_topic)
            client.publish(settings.status_topic, "online", retain=True)
        else:
            log.warning("Broker rejected MQTT connection")

    def on_message(client, userdata, message):
        if handle_payload(message.payload, rules, worker) is not None:
            recovery = watch.received()
            if recovery:
                worker.submit(recovery)

    client.on_connect = on_connect
    client.on_message = on_message
    worker.start()
    delay = 1
    try:
        while not stopped.is_set():
            offline = watch.check()
            if offline:
                worker.submit(offline)
            try:
                HEARTBEAT.unlink(missing_ok=True)
                client.connect(settings.broker, settings.port, keepalive=30)
                while not stopped.is_set():
                    offline = watch.check()
                    if offline:
                        worker.submit(offline)
                    result = client.loop(timeout=1)
                    if result != mqtt.MQTT_ERR_SUCCESS:
                        break
                    if client.is_connected():
                        HEARTBEAT.write_text(str(time.monotonic()))
                        delay = 1
            except OSError:
                log.warning("MQTT connection failed")
            finally:
                HEARTBEAT.unlink(missing_ok=True)
                if stopped.is_set() and client.is_connected():
                    client.publish(settings.status_topic, "offline", retain=True).wait_for_publish(timeout=2)
                client.disconnect()
            if not stopped.is_set():
                log.warning("MQTT disconnected; retry in %ss", delay)
                stopped.wait(delay)
                delay = min(delay * 2, 30)
    finally:
        if client.is_connected():
            client.publish(settings.status_topic, "offline", retain=True).wait_for_publish(timeout=2)
        client.disconnect()
        HEARTBEAT.unlink(missing_ok=True)
        worker.close()


if __name__ == "__main__":
    main()

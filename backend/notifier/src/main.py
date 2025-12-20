# src/main.py

import os
import json
import logging
import time
from paho.mqtt import client as mqtt_client
from models import Settings
import apprise 

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

settings = Settings()
apprise_client = None
if settings.apprise_url:
    logging.info("Apprise URL configured, alerts will be sent.")
    apprise_client = apprise.Apprise()
    apprise_client.add(settings.apprise_url)
else:
    logging.info("No Apprise URL configured, alerts will only be logged.")

def connect_mqtt():
    client_id = f"notifier-{os.getpid()}"
    logging.info(f"Connecting to MQTT broker {settings.broker}:{settings.port}")
    client = mqtt_client.Client(client_id)
    if settings.user:
        logging.info(f"Using MQTT username: {settings.user}")
        client.username_pw_set(settings.user, settings.password)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    try:
        client.connect(settings.broker, settings.port)
    except Exception as e:
        logging.error(f"Could not connect to broker: {e}")
        raise
    return client

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT broker successfully")
        logging.info(f"Subscribing to topic: {settings.base_topic}")
        client.subscribe(settings.base_topic)

        status_topic = f"{settings.base_topic}/status"
        logging.info(f"Publishing status 'online' to {status_topic}")
        client.publish(status_topic, "online", retain=True)
    else:
        logging.error(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    logging.info(f"Message arrived | topic: {msg.topic} | payload: {msg.payload}")
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
    except Exception as e:
        logging.error(f"Error parsing payload: {e}")
        return

    co2 = data.get("co2")
    lux = data.get("lux")
    hum = data.get("hum")
    temp = data.get("temp")

    logging.info(f"Parsed data: co2={co2}, lux={lux}, hum={hum}, temp={temp}")

    if co2 is not None and co2 > 1500:
        logging.warning(f"High CO₂ detected: {co2} ppm — sending notification!")
        send_alert(co2, lux, temp, hum, data)

def on_disconnect(client, userdata, rc):
    logging.warning(f"Disconnected with rc={rc}. Reconnecting...")
    try:
        time.sleep(2)
        client.reconnect()
    except Exception as e:
        logging.error(f"Reconnect failed: {e}")

def send_alert(co2_value, lux_value, temp_value, hum_value, data):
    message = (
        f"⚠️ High CO₂ detected: {co2_value} ppm\n"
        f"💡 Lux: {lux_value}\n"
        f"🌡️ Temp: {temp_value} °C\n"
        f"💧 Humidity: {hum_value} %"
    )

    logging.info(f"Alert message: {message}")

    if apprise_client:
        try:
            apprise_client.notify(
                title="Pico Environment Alert",
                body=message,
            )
            logging.info("Alert sent via Apprise.")
        except Exception as e:
            logging.error(f"Failed to send Apprise notification: {e}")
    else:
        logging.info("Apprise is not configured, skipping notification send.")

def main():
    client = connect_mqtt()
    logging.info("Starting MQTT loop")
    client.loop_forever()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Notifier stopped by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise

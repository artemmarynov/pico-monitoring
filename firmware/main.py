import time
from secrets import secrets

import ujson
from bh1750 import read_lux_once
from dht22 import read_dht_once, wait_for_first_valid_read
from mh19 import read_co2_once
from mqtt import connect_mqtt
from rtc1302 import sync_time
from wifi import connect_wifi

SLEEP_SEC = 10


def do_measurement(client):
    temp, hum = read_dht_once()
    values = {"co2": read_co2_once(), "lux": read_lux_once(), "temp": temp, "hum": hum}
    if all(value is None for value in values.values()):
        print("No valid sensor readings")
        return
    client.publish(secrets["TOPIC_SENSOR"], ujson.dumps(values))


def main():
    client = None
    delay = 1
    while True:
        try:
            wlan = connect_wifi(secrets["ssid"], secrets["password"])
            sync_time()
            client = connect_mqtt(secrets["CLIENT_ID"], secrets["MQTT_BROKER"], secrets["MQTT_PORT"])
            wait_for_first_valid_read()
            while wlan.isconnected():
                do_measurement(client)
                delay = 1
                time.sleep(SLEEP_SEC)
            raise OSError("Wi-Fi disconnected")
        except Exception as exc:
            print("Connection/measurement failed:", exc)
        finally:
            if client is not None:
                try:
                    client.disconnect()
                except Exception:
                    pass
                client = None
        time.sleep(delay)
        delay = min(delay * 2, 30)


if __name__ == "__main__":
    main()

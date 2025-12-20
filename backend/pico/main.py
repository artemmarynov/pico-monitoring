import time
import ujson

from secrets import secrets
from wifi import connect_wifi
from mqtt import connect_mqtt
from rtc1302 import sync_time
from bh1750 import read_lux_once
from mh19 import read_co2_once
from dht22 import read_temperature_once, read_humidity_once

SLEEP_SEC = 10
STATE_CONNECTING_WIFI = "connecting_wifi"
STATE_MEASUREMENT = "measurement"
STATE_SLEEP = "sleep"
state = STATE_CONNECTING_WIFI
wlan = None
client = None

# ----------------------------------------------------------------------------- 
#  Measurement + Publish
# ----------------------------------------------------------------------------- 
def do_measurement():
    global client

    co2 = read_co2_once()
    lux = read_lux_once()
    temp = read_temperature_once()
    hum = read_humidity_once()

    payload = ujson.dumps({
        "co2": co2,
        "lux": lux,
        "temp": temp,
        "hum": hum,
    })
    client.publish(secrets["TOPIC_SENSOR"], payload)
    print("Measurements:", payload)

# ----------------------------------------------------------------------------- 
#  STATE MACHINE
# ----------------------------------------------------------------------------- 
while True:
    try:
        if state == STATE_CONNECTING_WIFI:
            wlan = connect_wifi(
                ssid=secrets["ssid"],
                password=secrets["password"],
            )
            sync_time()
            client = connect_mqtt(
                client_id=secrets["CLIENT_ID"],
                broker=secrets["MQTT_BROKER"],
                port=secrets["MQTT_PORT"],
            )
            state = STATE_MEASUREMENT

        elif state == STATE_MEASUREMENT:
            do_measurement()
            state = STATE_SLEEP

        elif state == STATE_SLEEP:
            time.sleep(SLEEP_SEC)
            state = STATE_MEASUREMENT

    except Exception as e:
        print("Error in main loop / state:", e)
        try:
            if wlan is None or not wlan.isconnected():
                print("Wi-Fi lost, reconnecting...")
            state = STATE_CONNECTING_WIFI
        except Exception:
            state = STATE_CONNECTING_WIFI

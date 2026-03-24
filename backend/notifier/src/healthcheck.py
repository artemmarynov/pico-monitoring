# notifier/src/healthcheck.py
import os
import sys
import time
import paho.mqtt.client as mqtt

BROKER = os.getenv("NOTIFIER_BROKER")
BASE_TOPIC = os.getenv("NOTIFIER_BASE_TOPIC")
STATUS_TOPIC = f"{BASE_TOPIC}/status"

received_payload = None

def on_connect(client, userdata, flags, rc):
    if rc != 0:
        sys.exit(1)
    client.subscribe(STATUS_TOPIC)

def on_message(client, userdata, msg):
    global received_payload
    if msg.topic == STATUS_TOPIC:
        try:
            received_payload = msg.payload.decode().strip()
        except Exception:
            received_payload = None

client = mqtt.Client()

try:
    if not BROKER or not BASE_TOPIC:
        sys.exit(1)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER)
    client.loop_start()

    timeout = time.time() + 3
    while received_payload is None and time.time() < timeout:
        time.sleep(0.1)

    client.loop_stop()
    client.disconnect()

    if received_payload is None:
        sys.exit(1)

    if received_payload != "online":
        sys.exit(1)

    sys.exit(0)

except Exception:
    sys.exit(1)

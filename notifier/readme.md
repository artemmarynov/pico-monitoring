📦 Notifier — MQTT Alerting Service

am106ac/notifier is a lightweight Python-based service for receiving MQTT messages and sending alerts based on configurable conditions.
It is designed for IoT monitoring setups (e.g., Raspberry Pi Pico + sensors) and integrates easily with Docker Compose stacks.

🚀 Features

Connects to any MQTT broker

Subscribes to selected MQTT topic

Parses JSON payloads

Applies alerting logic (thresholds, conditions, etc.)

Sends notifications via Apprise:

Telegram

Lightweight (Python 3.13-slim)

Zero configuration required inside the container — everything via env variables

🛠️ Environment Variables
Variable	Required	Description
NOTIFIER_BROKER	✔	Hostname or IP of MQTT broker
NOTIFIER_PORT	✔	MQTT port (default: 1883)
NOTIFIER_BASE_TOPIC	✔	MQTT topic to subscribe to
APPRISE_URL	✔	Where to send alerts (Telegram, Discord etc.)

Example of Apprise Telegram URL:

tgram://TOKEN/CHAT_ID

▶️ Running the container
Minimal example:
docker run --rm -it \
  -e NOTIFIER_BROKER=mosquitto \
  -e NOTIFIER_PORT=1883 \
  -e NOTIFIER_BASE_TOPIC=pico/env \
  am106ac/notifier:latest

▶️ Docker Compose example
services:
  notifier:
    image: am106ac/notifier:latest
    container_name: notifier
    environment:
      NOTIFIER_BROKER: mosquitto
      NOTIFIER_PORT: 1883
      NOTIFIER_BASE_TOPIC: pico/env
      APPRISE_URL: "tgram://TOKEN/CHAT_ID"
    restart: always
    networks:
      - monitoring

networks:
  monitoring:
    external: true

🔧 How to use it in IoT lab (TUKE IoT1)

Build your pico-monitoring stack

Ensure the MQTT broker (mosquitto) is running

Add notifier either manually or via docker-compose

Send sensor data from Pico (CO₂, humidity, light, etc.)

The notifier will watch incoming messages and fire alerts

🔄 Available Tags
Tag	Description
latest	Most recent build

You can pull any version:

docker pull am106ac/notifier:latest

📁 Source Code Structure (inside the image)
/src
  ├─ main.py
  ├─ models.py
  ├─ healthcheck.py
  ├─ requirements.txt

The image includes:

Python 3.13

Paho MQTT client

Pydantic Settings

Loguru

Apprise
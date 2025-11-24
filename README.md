# 📡 pico-monitoring

IoT stack for monitoring environment data from **Raspberry Pi Pico** (CO₂, light, …) using **MQTT**, **Prometheus**, **Grafana**, and the Python-based alerting service **Notifier** (with Telegram support via Apprise).

## 🏗️ Architecture Overview

### 🌱 Raspberry Pi Pico 2 WH
Publishes JSON messages with sensor data (CO₂, Lux) to the MQTT topic `pico/env`:

```json
{"co2": 1234, "lux": 56.7}
```

🔌 **Pico firmware** ([`pico/`](pico/))

MicroPython code for Raspberry Pi Pico lives in the pico/ directory:
[`main.py`](pico/main.py) – state machine: reads sensors and publishes JSON to MQTT.  
[`wifi.py`](pico/wifi.py), [`mqtt.py`](pico/mqtt.py), [`rtc1302.py`](pico/rtc1302.py), [`bh1750.py`](pico/bh1750.py), [`mh19.py`](pico/mh19.py) – hardware + connectivity helpers.  
[`secrets.py.example`](pico/secrets.py.example) – template with Wi-Fi/MQTT credentials.

---

### Services

📬 **Mosquitto** ([`mosquitto/`](mosquitto/))

Local MQTT broker that receives messages from Pico.

📊 **mqtt-exporter** ([`mqtt-exporter/`](mqtt-exporter/))

Subscribes to specific MQTT topics

🧠 **Prometheus** ([`prometheus/`](prometheus/))

Scrapes data from mqtt-exporter
Stores long-term sensor metrics

🚨 **Notifier** ([`notifier/`](notifier/))

Python microservice that: 
Subscribes to pico/env  
Parses JSON MQTT payloads 
Checks CO₂ threshold  
Sends alerts through Apprise → Telegram 
Exposes health status via MQTT (pico/env/status)

📈 **Grafana**

Visualizes Prometheus data in dashboards
Used to show CO₂ trends, light intensity, time-based graphs

---

### 📋 Requirements

Docker  
Docker Compose v2   
MQTT data source (Pico or any other publishing device)  

🖥️ **OS notes**

Docker stack (Mosquitto, mqtt-exporter, Prometheus, Grafana, Notifier) is expected to run on **Linux** or **WSL**.
Where you flash the Pico is not critical – it can be done from any OS.
**mpy-workbench** works only on **Windows**, so if you use it from VS Code you should copy/move the pico/ folder to a Windows filesystem directory (outside WSL) and work with the firmware from there.

---

### 🚀 Quick Start

1️⃣ Clone repository
```bash
git clone https://github.com/artemmarynov/pico-monitoring.git
cd pico-monitoring
```

2️⃣ Create .env
```bash
cp .env.example .env
```

Then edit the file and set:
```ini
NOTIFIER_APPRISE_URL=tgram://YOUR_BOT_TOKEN/YOUR_CHAT_ID
```

3️⃣ Launch the full stack
```bash
docker compose up -d --build
```

---

🌐 **Services Overview**

| Service                   | URL / Address                                                  |
| ------------------------- | -------------------------------------------------------------- |
| **Mosquitto**             | [mqtt://localhost:1883](mqtt://localhost:1883)                 |
| **Prometheus**            | [http://localhost:9091](http://localhost:9091)                 |
| **Grafana**               | [http://localhost:3001](http://localhost:3001)                 |
| **mqtt-exporter metrics** | [http://localhost:9641/metrics](http://localhost:9641/metrics) |

🧪 **Testing MQTT Messaging**

Send a test message manually:
```bash
docker exec -it mosquitto mosquitto_pub \
  -h mosquitto -p 1883 \
  -t pico/env \
  -m '{"co2": 2000, "lux": 100}'
```
If CO₂ exceeds the threshold →
Notifier sends a Telegram alert 🚨.

🧩 **Notifier Service Details**

Source code is located in the notifier/ directory.

| File                 | Purpose                               |
| -------------------- | ------------------------------------- |
| `src/main.py`        | Main MQTT client and alerting logic   |
| `src/models.py`      | Config loader using Pydantic Settings |
| `src/healthcheck.py` | Docker health-check script            |
| `Dockerfile`         | Image build instructions              |
| `requirements.txt`   | Python dependencies                   |

⚙️ **Notifier Environment Variables**

| Variable               | Required | Description                         |
| ---------------------- | -------- | ----------------------------------- |
| `NOTIFIER_BROKER`      | ✔️ yes   | MQTT broker hostname (`mosquitto`)  |
| `NOTIFIER_PORT`        | ✖️ no    | Port (default: `1883`)              |
| `NOTIFIER_USER`        | ✖️ no    | MQTT username                       |
| `NOTIFIER_PASSWORD`    | ✖️ no    | MQTT password                       |
| `NOTIFIER_BASE_TOPIC`  | ✔️ yes   | MQTT base topic (`pico/env`)        |
| `NOTIFIER_APPRISE_URL` | ✖️ no    | Apprise URL (Telegram, Email, etc.) |

❤️ **Healthcheck**

Notifier’s Docker container runs a health check every 30s:

connects to MQTT broker 
subscribes to <BASE_TOPIC>/status   
expects message "online"  
if the message is missing or incorrect → container becomes unhealthy  

Healthcheck is defined in:

Dockerfile  
docker-compose.yml  
src/healthcheck.py  

---

📜 **License**

This project is intended for educational purposes.  
You may use it as a reference for your own monitoring and alerting stacks.
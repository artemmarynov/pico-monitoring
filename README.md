# 📡 pico-monitoring

IoT stack for monitoring environment data from **Raspberry Pi Pico 2 WH** (CO₂, light, temperature, humidity) using **MQTT**, **Prometheus**, **PostgreSQL**, **Grafana**, and the Python-based alerting service **Notifier** (with Telegram support via Apprise).

## 🏗️ Architecture Overview

### 🌱 Raspberry Pi Pico 2 WH
Publishes JSON messages with sensor data (co₂, light, temperature, humidity) to the MQTT topic `pico/env`:

```json
{"co2": 1234, "lux": 56.7, "temp": 24.3, "hum": 58.7}
```

🔌 **Pico firmware** ([`pico/`](pico/))

MicroPython code for Raspberry Pi Pico lives in the pico/ directory:
[`main.py`](pico/main.py) – state machine: reads sensors and publishes JSON to MQTT.  
[`wifi.py`](pico/wifi.py), [`mqtt.py`](pico/mqtt.py), [`rtc1302.py`](pico/rtc1302.py), [`bh1750.py`](pico/bh1750.py), [`mh19.py`](pico/mh19.py), [`dht22`](pico/dht22.py) – hardware + connectivity helpers.  
[`secrets.py.example`](pico/secrets.py.example) – template with Wi-Fi/MQTT credentials.

---
### Services

📬 **Mosquitto** ([`mosquitto/`](mosquitto/))

Local MQTT broker that receives messages from Pico.       

---
📊 **mqtt-exporter** ([`mqtt-exporter/`](mqtt-exporter/))

Subscribes to `pico/env` and exposes the sensor readings as Prometheus metrics:   
- `pico_co2` – CO₂ concentration (ppm)  
- `pico_lux` – light level (lux)   
- `pico_temp` – temperature (°C)  
- `pico_hum` – relative humidity (%)  

---
🧠 **Prometheus** ([`prometheus/`](prometheus/))

Scrapes metrics from mqtt-exporter
Acts as a metrics source for:
Grafana (visualization)
prom-to-postgres (export to PostgreSQL)

---
🗄️ **PostgreSQL + prom-to-postgres** ([`prom-to-postgres/`](prom-to-postgres/))

- PostgreSQL stores long-term time-series data for all four metrics: CO₂, light, temperature, humidity.
- prom-to-postgres is a Python service that:  
  - Periodically queries Prometheus HTTP API for:   
    `pico_temp`     
    `pico_hum`  
    `pico_co2`  
    `pico_lux`  
  - Inserts the current snapshot into the `sensor_metrics` table in the `metrics` database.   
  
Resulting table structure (created automatically on first run):
```sql
CREATE TABLE IF NOT EXISTS sensor_metrics (
    time        TIMESTAMP,
    temperature REAL,
    humidity    REAL,
    co2         REAL,
    lighting    REAL
);
```
---
🚨 **Notifier** ([`notifier/`](notifier/))

Python microservice that:
-  Subscribes to `pico/env`  
-  Parses JSON MQTT payloads 
-  Checks CO₂ threshold  
-  Sends alerts through Apprise → Telegram 
-  Exposes health status via MQTT (`pico/env/status`)
---
📈 **Grafana**

- Visualizes Prometheus data in dashboards
- Can show:
  - CO₂ trends
  - Light intensity
  - Temperature evolution
  - Humidity changes
  - Combined time-based graphs for all four metrics

---
### 📋 Requirements

- Docker  
- Docker Compose v2   
- MQTT data source (**Raspberry Pi Pico 2 WH** or any other publishing device)
---
🖥️ **OS notes**

- Docker stack (Mosquitto, mqtt-exporter, Prometheus, Grafana, Postgres, Notifier, prom-to-postgres) is expected to run on **Linux** or **WSL**.
- Where you flash the Pico is not critical – it can be done from any OS.
- **mpy-workbench** works only on **Windows**, so if you use it from VS Code you should copy/move the `pico/` folder to a Windows filesystem directory (outside WSL) and work with the firmware from there.
---
### 🚀 Quick Start
1️⃣ Clone repository
```bash
git clone https://github.com/artemmarynov/pico-monitoring.git
cd pico-monitoring
```
2️⃣ Create `.env`

Create a file named `.env` manually in the project root and fill it with the required environment variables.

Example `.env` file structure:
```env
NOTIFIER_APPRISE_URL=tgram://YOUR_TELEGRAM_BOT_TOKEN/YOUR_CHAT_ID
PROM_URL=http://prometheus:9090
PG_USER=postgres
PG_PASSWORD=admin
PG_DB=metrics
PG_HOST=postgres
PG_PORT=5432
MQTT_BROKER=mosquitto
EXPORT_INTERVAL=5
JWT_SECRET=YOUR_JWT_SECRET
ACCESS_TOKEN_MINUTES=60
BOOTSTRAP_SECRET=YOUR_BOOTSTRAP_SECRET
```
Access the front-end by that link:
http://localhost:5173

Backend:
http://localhost:8000/docs

# Prometheus → Postgres exporter settings
PROM_URL=http://prometheus:9090
PG_HOST=postgres
PG_DB=metrics
PG_USER=admin
PG_PASSWORD=admin
EXPORT_INTERVAL=10

3️⃣ Launch the full stack
```bash
docker compose up -d --build
```
---
🌐 **Services Overview**

| Service                   | URL / Address                                                  |
| ------------------------- | -------------------------------------------------------------- |
| **Mosquitto**             | `mqtt://localhost:1883`          |
| **Prometheus**            | [http://localhost:9091](http://localhost:9091)                 |
| **Grafana**               | [http://localhost:3001](http://localhost:3001)                 |
| **mqtt-exporter metrics** | [http://localhost:9641/metrics](http://localhost:9641/metrics) |
| **PostgreSQL**            | `localhost:5432` (DB: `metrics`, user: `admin`, password: admin) |
| **Vite server (Front-end)** | [http://localhost:5173](http://localhost:5173) |
| **FastAPI backend** | [http://localhost:8000/docs](http://localhost:8000/docs) |
---
🧪 **Testing MQTT Messaging**

Send a test message manually:
```bash
docker exec -it mosquitto mosquitto_pub \
  -h mosquitto -p 1883 \
  -t pico/env \
  -m '{"co2": 2000, "lux": 100, "temp": 24.5, "hum": 60.0}'
```
Prometheus (via mqtt-exporter) will see updated:
`pico_co2`,
`pico_lux`,
`pico_temp`,
`pico_hum`.   
**Notifier** will react if CO₂ exceeds the threshold → Notifier sends a Telegram alert 🚨.

🧠 **prom-to-postgres Environment Variables**

Defined in `.env` and passed via `env_file` in `docker-compose.yml`:

| Variable          | Required | Description                                            |
| ----------------- | -------- | ------------------------------------------------------ |
| `PROM_URL`        | ✔️ yes   | Prometheus base URL (inside Docker network)            |
| `PG_HOST`         | ✔️ yes   | PostgreSQL hostname (`postgres` in docker-compose)     |
| `PG_DB`           | ✔️ yes   | Database name (default: `metrics`)                     |
| `PG_USER`         | ✔️ yes   | Database user (default: `admin`)                       |
| `PG_PASSWORD`     | ✔️ yes   | Database password                                      |
| `EXPORT_INTERVAL` | ✔️ yes   | Interval (in seconds) between metric exports (e.g. 10) |

🧩 **Notifier Service Details**

Source code is located in the `notifier/` directory.

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
- connects to MQTT broker 
- subscribes to `<BASE_TOPIC>/status`   
- expects message `"online" `
- if the message is missing or incorrect → container becomes unhealthy  

Healthcheck is defined in:  
`Dockerfile`  
`docker-compose.yml`  
`src/healthcheck.py`  

---

📜 **License**

This project is intended for educational purposes.  
You may use it as a reference for your own monitoring, alerting and metrics storage stacks.
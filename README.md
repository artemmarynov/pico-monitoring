# 📡 Návrh aplikácie pre analýzu a monitorovanie dát z interiéru s využitím platformy Grafana

IoT platforma na monitorovanie údajov o vnútornom prostredí pomocou **Raspberry Pi Pico 2 WH** (CO<sub>2</sub>, osvetlenie, teplota, vlhkosť), **MQTT**, **Promethea**, **PostgreSQL**, **Grafany**, **FastAPI backendu** a webového rozhrania v **Reacte**. Súčasťou riešenia je aj Python mikroslužba **Notifier** s podporou upozornení cez Telegram prostredníctvom knižnice Apprise.

## Prehľad architektúry

### Raspberry Pi Pico 2 WH
Publikuje JSON správy so senzorickými údajmi (CO<sub>2</sub>, osvetlenie, teplota, vlhkosť) do MQTT témy `pico/env`:

```json
{"co2": 1234, "lux": 56.7, "temp": 24.3, "hum": 58.7}
```

**Firmvér pre Pico** ([`backend/pico/`](backend/pico/))

MicroPython kód pre Raspberry Pi Pico sa nachádza v adresári `backend/pico/`:
[`main.py`](backend/pico/main.py) – stavový automat: čítanie senzorov a publikovanie JSON správ do MQTT.  
[`wifi.py`](backend/pico/wifi.py), [`mqtt.py`](backend/pico/mqtt.py), [`rtc1302.py`](backend/pico/rtc1302.py), [`bh1750.py`](backend/pico/bh1750.py), [`mh19.py`](backend/pico/mh19.py), [`dht22.py`](backend/pico/dht22.py) – pomocné moduly pre hardvér a konektivitu.  
[`secrets.py.example`](backend/pico/secrets.py.example) – šablóna s Wi-Fi a MQTT prihlasovacími údajmi.

---
### Služby

**Mosquitto** ([`backend/mosquitto/`](backend/mosquitto/))

Lokálny MQTT broker, ktorý prijíma správy zo senzorového uzla a sprístupňuje ich ostatným službám v systéme.

---
**mqtt-exporter** ([`backend/mqtt-exporter/`](backend/mqtt-exporter/))

Odoberá tému `pico/env` a sprístupňuje prijaté hodnoty ako Prometheus metriky:
- `pico_co2` – koncentrácia CO<sub>2</sub> (ppm)  
- `pico_lux` – úroveň osvetlenia (lux)   
- `pico_temp` – teplota (Celsius)
- `pico_hum` – relatívna vlhkosť (%)  

---
**Prometheus** ([`backend/prometheus/`](backend/prometheus/))

Získava metriky z mqtt-exportera pravidelným scrapovaním.  
Slúži ako zdroj metrík pre:
Grafanu (vizualizácia v reálnom čase)
a monitorovanie krátkodobých časových radov.

---
**PostgreSQL + FastAPI backend** ([`backend/postgress-websocket/`](backend/postgress-websocket/))

- PostgreSQL uchováva historické merania všetkých štyroch veličín: CO<sub>2</sub>, osvetlenie, teplota a vlhkosť.
- FastAPI backend je Python služba, ktorá:
  - odoberá správy z MQTT brokeru,
  - dekóduje JSON payload,
  - priamo zapisuje prijaté merania do tabuľky `sensor_metrics`,
  - poskytuje REST API pre historické údaje,
  - poskytuje WebSocket kanál pre zobrazovanie aktuálnych dát v reálnom čase.

Výsledná tabuľka (vytvorená automaticky pri štarte backendu):
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
**Notifier** ([`backend/notifier/`](backend/notifier/))

Python mikroslužba, ktorá:
- odoberá tému `pico/env`  
- spracúva JSON MQTT payload  
- vyhodnocuje prahové hodnoty  
- odosiela upozornenia cez Apprise → Telegram  
- publikuje stav služby cez MQTT (`pico/env/status`)  
---
**Frontend** ([`frontend/`](frontend/))

Webové rozhranie implementované pomocou React a Vite:
- zobrazuje aktuálne merania v reálnom čase,
- zobrazuje historické údaje cez REST API,
- podporuje agregáciu údajov podľa intervalu,
- komunikuje s backendom cez REST a WebSocket.

---
**Grafana**

- Vizualizuje údaje v dashboardoch
- Môže zobrazovať:
  - vývoj koncentrácie CO<sub>2</sub>
  - intenzitu osvetlenia
  - vývoj teploty
  - zmeny vlhkosti
  - kombinované časové grafy viacerých veličín
- Využíva Prometheus pre realtime metriky a PostgreSQL pre historické dáta

---
### Požiadavky

- Docker  
- Docker Compose v2   
- MQTT zdroj dát (**Raspberry Pi Pico 2 WH** alebo iné zariadenie schopné publikovať MQTT správy)
---
**Poznámky k OS**

- Docker stack (Mosquitto, mqtt-exporter, Prometheus, Grafana, PostgreSQL, Notifier, FastAPI backend) je určený najmä pre **Linux** alebo **WSL**.
- Nahratie firmvéru do Pico je možné z ľubovoľného operačného systému.
- **mpy-workbench** funguje iba na **Windows**, preto ak ho používate vo VS Code, je vhodné pracovať s priečinkom `backend/pico/` na súborovom systéme Windows mimo WSL.
---
### Rýchly štart

## 1️⃣ Príprava projektu

Projekt je súčasťou elektronickej prílohy záverečnej práce.  
Po rozbalení archívu prejdite do koreňového adresára projektu, v ktorom sa nachádza súbor `docker-compose.yml`.

## 2️⃣ Vytvorenie `.env`

Skopírujte súbor `.env.example` na `.env` v koreňovom adresári projektu a doplňte požadované premenné prostredia.

Príklad štruktúry súboru `.env`:
```env
NOTIFIER_APPRISE_URL=tgram://YOUR_TELEGRAM_BOT_TOKEN/YOUR_CHAT_ID
PG_USER=postgres
PG_PASSWORD=admin
PG_DB=metrics
PG_HOST=postgres
PG_PORT=5432
MQTT_BROKER=mosquitto
JWT_SECRET=YOUR_JWT_SECRET
ACCESS_TOKEN_MINUTES=60
BOOTSTRAP_SECRET=YOUR_BOOTSTRAP_SECRET
```
Prístup k frontendu:
http://localhost:5173

Backend:
http://localhost:8000/docs

## 3️⃣ Spustenie celého stacku
```bash
docker compose up -d --build
```
---
**Prehľad služieb**

| Služba | URL / Adresa |
| --- | --- |
| **Mosquitto** | `http://localhost:1883` |
| **Prometheus** | [http://localhost:9091](http://localhost:9091) |
| **Grafana** | [http://localhost:3001](http://localhost:3001) |
| **Mqtt-exporter** | [http://localhost:9641/metrics](http://localhost:9641/metrics) |
| **Notifier** | |
| **PostgreSQL** | `localhost:5432` |
| **Vite server (frontend)** | [http://localhost:5173](http://localhost:5173) |
| **FastAPI backend** | [http://localhost:8000/docs](http://localhost:8000/docs) |
---
**Testovanie MQTT komunikácie**

Odošlite testovaciu správu manuálne:
```bash
docker exec -it mosquitto mosquitto_pub \
  -h mosquitto -p 1883 \
  -t pico/env \
  -m '{"co2": 2000, "lux": 100, "temp": 24.5, "hum": 60.0}'
```
Prometheus (cez mqtt-exporter) následne uvidí aktualizované metriky:
`pico_co2`,
`pico_lux`,
`pico_temp`,
`pico_hum`.  
**Notifier** zareaguje pri prekročení prahovej hodnoty a odošle upozornenie cez Telegram.

**Premenné prostredia backendu**

Definované v `.env` a odovzdávané cez `env_file` v `docker-compose.yml`:

| Premenná | Povinná | Popis |
| --- | --- | --- |
| `PG_HOST` | ✔️ áno | Hostname databázy PostgreSQL (`postgres` v docker-compose) |
| `PG_PORT` | ✔️ áno | Port databázy PostgreSQL (štandardne `5432`) |
| `PG_DB` | ✔️ áno | Názov databázy (napr. `metrics`) |
| `PG_USER` | ✔️ áno | Používateľ databázy |
| `PG_PASSWORD` | ✔️ áno | Heslo databázy |
| `MQTT_BROKER` | ✔️ áno | Hostname MQTT brokeru (`mosquitto`) |
| `JWT_SECRET` | ✔️ áno | Tajný kľúč pre podpisovanie tokenov |
| `ACCESS_TOKEN_MINUTES` | ✖️ nie | Platnosť prístupového tokenu v minútach |
| `BOOTSTRAP_SECRET` | ✖️ nie | Tajný údaj pre inicializáciu administrátora alebo bootstrap operácie |

**Detaily služby Notifier**

Zdrojový kód sa nachádza v adresári `backend/notifier/`.

| Súbor | Účel |
| --- | --- |
| `src/main.py` | Hlavná logika MQTT klienta a upozornení |
| `src/models.py` | Načítanie konfigurácie pomocou Pydantic Settings |
| `src/healthcheck.py` | Skript pre Docker health-check |
| `Dockerfile` | Inštrukcie na zostavenie obrazu |
| `requirements.txt` | Python závislosti |

**Premenné prostredia služby Notifier**

| Premenná | Povinná | Popis |
| --- | --- | --- |
| `NOTIFIER_BROKER` | ✔️ áno | Hostname MQTT brokeru (`mosquitto`) |
| `NOTIFIER_PORT` | ✖️ nie | Port brokeru (predvolene `1883`) |
| `NOTIFIER_USER` | ✖️ nie | MQTT používateľské meno |
| `NOTIFIER_PASSWORD` | ✖️ nie | MQTT heslo |
| `NOTIFIER_BASE_TOPIC` | ✔️ áno | Základná MQTT téma (`pico/env`) |
| `NOTIFIER_APPRISE_URL` | ✖️ nie | Apprise URL (Telegram, e-mail a pod.) |

**Healthcheck**

Docker kontajner služby Notifier vykonáva health check každých 30 sekúnd:  
- pripojí sa k MQTT brokeru  
- odoberie tému `<BASE_TOPIC>/status`   
- očakáva správu `online`  
- ak správa chýba alebo je nesprávna, kontajner sa označí ako unhealthy  

Healthcheck je definovaný v:  
`Dockerfile`  
`docker-compose.yml`  
`src/healthcheck.py`  

---

**Licencia**

Tento projekt je určený predovšetkým na vzdelávacie účely.  
Môže slúžiť ako referencia pre vlastné riešenia monitorovania, upozorňovania a ukladania metrík.

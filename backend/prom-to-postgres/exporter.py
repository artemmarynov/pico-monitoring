# prom-to-postgres/exporter.py
import os
import time
import requests
import psycopg2
from datetime import datetime, timezone
import zoneinfo

tz = zoneinfo.ZoneInfo("Europe/Bratislava")

PROM_URL= os.getenv("PROM_URL", "http://prometheus:9090")
PG_HOST = os.getenv("PG_HOST")
PG_DB = os.getenv("PG_DB")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
EXPORT_INTERVAL = int(os.getenv("EXPORT_INTERVAL"))

QUERY_MAP = {
    "temperature": "pico_temp",
    "humidity": "pico_hum",
    "co2": "pico_co2",
    "lighting": "pico_lux"
}

def prom_query(metric):
    try:
        r = requests.get(f"{PROM_URL}/api/v1/query", params={"query": metric}, timeout=5)
        data = r.json()
    except Exception as e:
        print(f"[ERROR] Request to Prometheus failed for {metric}: {e}")
        return None

    if data.get("status") != "success":
        print(f"[WARN] Prometheus query for {metric} not success: {data}")
        return None

    result = data["data"]["result"]
    if not result:
        print(f"[INFO] No data returned for metric {metric}")
        return None

    try:
        value = float(result[0]["value"][1])
        return value
    except Exception as e:
        print(f"[ERROR] Failed to parse value for {metric}: {e}, result={result}")
        return None

def write_to_postgres(timestamp, data):
    conn = psycopg2.connect(
        host=PG_HOST,
        database=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD
    )
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sensor_metrics (
            time TIMESTAMP,
            temperature REAL,
            humidity REAL,
            co2 REAL,
            lighting REAL
        );
    """)

    cur.execute("""
        INSERT INTO sensor_metrics (time, temperature, humidity, co2, lighting)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        timestamp,
        data.get("temperature"),
        data.get("humidity"),
        data.get("co2"),
        data.get("lighting")
    ))

    conn.commit()
    cur.close()
    conn.close()

def main():
    while True:
        timestamp = datetime.now(tz).replace(microsecond=0).replace(tzinfo=None)
        results = {}

        for field_name, query in QUERY_MAP.items():
            value = prom_query(query)
            results[field_name] = value

        if all(v is None for v in results.values()):
            print(f"[INFO] {timestamp} — no data for any metric, skipping insert")
        else:
            print(f"[INFO] {timestamp} — writing to DB: {results}")
            write_to_postgres(timestamp, results)

        time.sleep(EXPORT_INTERVAL)

if __name__ == "__main__":
    main()
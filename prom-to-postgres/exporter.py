import os
import time
import requests
import psycopg2
from datetime import datetime

PROM_URL = os.getenv("PROM_URL", "http://prometheus:9090")
PG_HOST = os.getenv("PG_HOST", "postgres")
PG_DB = os.getenv("PG_DB", "metrics")
PG_USER = os.getenv("PG_USER", "admin")
PG_PASSWORD = os.getenv("PG_PASSWORD", "admin")
EXPORT_INTERVAL = int(os.getenv("EXPORT_INTERVAL", "300"))

QUERY_MAP = {
    "temperature_c": "temperature_c",
    "humidity": "humidity",
    "co2_ppm": "co2_ppm",
    "light_lux": "light_lux"
}

def prom_query(metric):
    r = requests.get(f"{PROM_URL}/api/v1/query", params={"query": metric})
    data = r.json()

    try:
        value = float(data["data"]["result"][0]["value"][1])
        return value
    except Exception:
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
            light REAL
        );
    """)

    cur.execute("""
        INSERT INTO sensor_metrics (time, temperature, humidity, co2, light)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        timestamp,
        data.get("temperature_c"),
        data.get("humidity"),
        data.get("co2_ppm"),
        data.get("light_lux")
    ))

    conn.commit()
    cur.close()
    conn.close()

def main():
    while True:
        timestamp = datetime.utcnow()
        results = {}

        for name, query in QUERY_MAP.items():
            results[name] = prom_query(query)

        write_to_postgres(timestamp, results)

        time.sleep(EXPORT_INTERVAL)

if __name__ == "__main__":
    main()

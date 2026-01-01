import asyncio
import asyncpg
import random
from datetime import datetime, timedelta

DB_CONFIG = {
    "user": "postgres",
    "password": "admin",
    "database": "metrics",
    "host": "localhost",
    "port": 54827
}

async def seed_data():
    conn = await asyncpg.connect(**DB_CONFIG)
    print("Подключено к БД. Начинаю генерацию данных...")


    now = datetime.now()
    records = []

    for i in range(0, 30 * 24 * 12): 
        time_point = now - timedelta(minutes=5 * i)
        

        temp = round(22.0 + 2.0 * random.uniform(-1, 1), 1)

        hum = round(50.0 + 10.0 * random.uniform(-1, 1), 1)
        co2 = round(600 + 300 * random.uniform(-1, 1), 0)
        light = round(500 + 500 * random.uniform(-1, 1), 0)

        records.append((time_point, temp, hum, co2, light))

    await conn.executemany('''
        INSERT INTO sensor_metrics (time, temperature, humidity, co2, lighting)
        VALUES ($1, $2, $3, $4, $5)
    ''', records)

    await conn.close()
    print(f"Готово! Добавлено {len(records)} записей.")

if __name__ == "__main__":
    asyncio.run(seed_data())
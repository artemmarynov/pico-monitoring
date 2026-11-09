import argparse
import asyncio
import random
from datetime import datetime, timedelta, timezone

from scripts.db import connect


async def seed(count, interval, apply=False):
    print(f"Generate {count} measurements at {interval}-second intervals")
    if not apply:
        print("Dry run; pass --apply to insert development data")
        return
    now = datetime.now(timezone.utc)
    rows = [
        (
            now - timedelta(seconds=interval * i),
            random.uniform(20, 24),
            random.uniform(40, 60),
            random.uniform(400, 900),
            random.uniform(0, 1000),
        )
        for i in range(count)
    ]
    connection = await connect()
    try:
        await connection.executemany(
            """INSERT INTO sensor_metrics(time, temperature, humidity, co2, lighting)
            VALUES ($1, $2, $3, $4, $5)""",
            rows,
        )
    finally:
        await connection.close()
    print(f"Inserted {count} development measurements")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate development data; never runs automatically")
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--interval", type=int, default=10)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.count <= 100000 or args.interval <= 0:
        parser.error("--count must be 1?100000 and --interval must be positive")
    asyncio.run(seed(args.count, args.interval, args.apply))

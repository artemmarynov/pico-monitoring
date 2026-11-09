import argparse
import asyncio
from datetime import datetime, timedelta, timezone

from scripts.db import connect


async def cleanup(connection, days, apply=False):
    if days <= 0:
        raise ValueError("Retention days must be positive")
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    async with connection.transaction():
        count = await connection.fetchval("SELECT count(*) FROM sensor_metrics WHERE time < $1", cutoff)
        print(f"Rows older than {cutoff.isoformat()}: {count}")
        if apply:
            result = await connection.execute("DELETE FROM sensor_metrics WHERE time < $1", cutoff)
            print(result)
        else:
            print("Dry run; pass --apply to delete these rows")
    return count


async def run(args):
    connection = await connect()
    try:
        await cleanup(connection, args.days, args.apply)
    finally:
        await connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Explicit history retention; dry run by default")
    parser.add_argument("--days", type=int, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.days <= 0:
        parser.error("--days must be positive")
    asyncio.run(run(args))

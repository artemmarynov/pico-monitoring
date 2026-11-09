import argparse
import asyncio
from pathlib import Path

from api.database import SCHEMA

from scripts.db import connect

MIGRATIONS = Path(__file__).resolve().parents[1] / "migrations"


async def apply_migrations(connection, legacy_timezone="UTC", backup_file=None):
    async with connection.transaction():
        await connection.execute("SELECT pg_advisory_xact_lock(750129031)")
        if not await connection.fetchval("SELECT 1 FROM pg_timezone_names WHERE name=$1", legacy_timezone):
            raise ValueError("Unknown legacy timezone")
        await connection.execute(SCHEMA)
        kind = await connection.fetchval("""SELECT data_type FROM information_schema.columns
            WHERE table_schema=current_schema() AND table_name='sensor_metrics' AND column_name='time'""")
        if kind == "timestamp without time zone" and await connection.fetchval(
            "SELECT EXISTS(SELECT 1 FROM sensor_metrics)"
        ):
            if not backup_file or not Path(backup_file).is_file() or Path(backup_file).stat().st_size == 0:
                raise ValueError("Back up the database first and pass the nonempty dump with --backup-file")
        await connection.execute("SELECT set_config('pico.legacy_timezone', $1, true)", legacy_timezone)
        await connection.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations (name TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT now())"
        )
        for path in sorted(MIGRATIONS.glob("*.sql")):
            if await connection.fetchval("SELECT 1 FROM schema_migrations WHERE name=$1", path.name):
                continue
            await connection.execute(path.read_text())
            await connection.execute("INSERT INTO schema_migrations(name) VALUES ($1)", path.name)
            print(f"Applied {path.name}")


async def run(args):
    connection = await connect()
    try:
        await apply_migrations(connection, args.legacy_timezone, args.backup_file)
    finally:
        await connection.close()


def main():
    parser = argparse.ArgumentParser(description="Apply explicit, transactional schema migrations")
    parser.add_argument(
        "--legacy-timezone", default="UTC", help="Timezone of existing naive timestamps (default UTC)"
    )
    parser.add_argument(
        "--backup-file", type=Path, help="Existing database dump, required before converting legacy data"
    )
    args = parser.parse_args()
    try:
        asyncio.run(run(args))
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()

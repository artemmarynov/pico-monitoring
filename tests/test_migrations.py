import pytest

from scripts.cleanup_history import cleanup
from scripts.migrate import apply_migrations


async def test_legacy_migration_requires_backup_and_preserves_instant(pool, tmp_path):
    async with pool.acquire() as connection:
        await connection.execute("CREATE TABLE users (id BIGINT PRIMARY KEY, email TEXT)")
        await connection.execute("INSERT INTO users VALUES (1, 'old@example.com')")
        await connection.execute("DROP TABLE sensor_metrics")
        await connection.execute(
            "CREATE TABLE sensor_metrics(time TIMESTAMP, temperature REAL, humidity REAL, co2 REAL, lighting REAL)"
        )
        await connection.execute("INSERT INTO sensor_metrics(time,co2) VALUES ('2026-01-01 12:00:00',600)")
        with pytest.raises(ValueError, match="Back up"):
            await apply_migrations(connection, "Europe/Bratislava")
        backup = tmp_path / "test.dump"
        backup.write_bytes(b"test backup fixture")
        await apply_migrations(connection, "Europe/Bratislava", backup)
        row = await connection.fetchrow("SELECT time,co2 FROM sensor_metrics")
        assert row["time"].isoformat() == "2026-01-01T11:00:00+00:00"
        assert row["co2"] == 600
        await apply_migrations(connection, "Europe/Bratislava", backup)
        assert await connection.fetchval("SELECT count(*) FROM sensor_metrics") == 1
        assert await connection.fetchval("SELECT count(*) FROM schema_migrations") == 2
        assert await connection.fetchval("SELECT to_regclass('users')") is None


async def test_retention_is_dry_run_until_applied(pool):
    async with pool.acquire() as connection:
        await connection.execute("INSERT INTO sensor_metrics(time) VALUES (now()-interval '60 days'),(now())")
        assert await cleanup(connection, 30) == 1
        assert await connection.fetchval("SELECT count(*) FROM sensor_metrics") == 2
        assert await cleanup(connection, 30, apply=True) == 1
        assert await connection.fetchval("SELECT count(*) FROM sensor_metrics") == 1

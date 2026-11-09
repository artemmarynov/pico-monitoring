from uuid import uuid4

from api.database import ensure_grafana_reader


async def test_grafana_database_user_can_only_read_measurements(pool):
    role = "pico_test_" + uuid4().hex[:12]
    async with pool.acquire() as connection:
        await connection.execute("CREATE TABLE private_notes (value TEXT)")
    try:
        await ensure_grafana_reader(pool, role, "test-only-password")
        await ensure_grafana_reader(pool, role, "test-only-password")
        async with pool.acquire() as connection:
            assert await connection.fetchval(
                "SELECT has_table_privilege($1::name, 'sensor_metrics', 'SELECT')", role
            )
            assert not await connection.fetchval(
                "SELECT has_table_privilege($1::name, 'sensor_metrics', 'INSERT')", role
            )
            assert not await connection.fetchval(
                "SELECT has_table_privilege($1::name, 'private_notes', 'SELECT')", role
            )
            assert not await connection.fetchval(
                "SELECT rolsuper OR rolcreatedb OR rolcreaterole FROM pg_roles WHERE rolname=$1", role
            )
    finally:
        async with pool.acquire() as connection:
            await connection.execute(f'DROP OWNED BY "{role}"')
            await connection.execute(f'DROP ROLE "{role}"')

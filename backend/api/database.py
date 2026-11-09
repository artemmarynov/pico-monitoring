import asyncpg

SCHEMA = """
CREATE TABLE IF NOT EXISTS sensor_metrics (
    time TIMESTAMPTZ,
    temperature REAL,
    humidity REAL,
    co2 REAL,
    lighting REAL
);

"""


async def ensure_schema(pool):
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(SCHEMA)
            kind = await conn.fetchval("""
                SELECT data_type FROM information_schema.columns
                WHERE table_schema=current_schema() AND table_name='sensor_metrics' AND column_name='time'
            """)
            if kind != "timestamp with time zone":
                raise RuntimeError("Legacy sensor_metrics.time: back up the DB and run scripts.migrate first")
            await conn.execute("CREATE INDEX IF NOT EXISTS sensor_metrics_time_idx ON sensor_metrics (time)")


async def insert_measurement(pool, measurement):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO sensor_metrics(time, temperature, humidity, co2, lighting)
            VALUES (now(), $1, $2, $3, $4)
        """,
            *measurement.db_values(),
        )


async def create_pool(settings):
    return await asyncpg.create_pool(**settings.connect_kwargs(), min_size=1, max_size=5)


async def ensure_grafana_reader(pool, username, password):
    """Provision read-only access to sensor measurements."""
    import re

    if not re.fullmatch(r"[a-z][a-z0-9_]{0,62}", username):
        raise ValueError("Invalid Grafana database username")
    async with pool.acquire() as connection:
        async with connection.transaction():
            await connection.execute("SELECT pg_advisory_xact_lock(750129032)")
            if username == await connection.fetchval("SELECT current_user"):
                raise ValueError("Grafana must use a separate read-only database account")
            exists = await connection.fetchval("SELECT 1 FROM pg_roles WHERE rolname=$1", username)
            action = "ALTER" if exists else "CREATE"
            statement = await connection.fetchval(
                f"SELECT format('{action} ROLE %I LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION PASSWORD %L', $1::text, $2::text)",
                username,
                password,
            )
            await connection.execute(statement)
            for template in (
                "GRANT CONNECT ON DATABASE %I TO %I",
                "GRANT USAGE ON SCHEMA %I TO %I",
                "GRANT SELECT ON TABLE %I.sensor_metrics TO %I",
            ):
                scope = await connection.fetchval(
                    "SELECT current_database()" if "DATABASE" in template else "SELECT current_schema()"
                )
                statement = await connection.fetchval(
                    "SELECT format($1::text, $2::text, $3::text)", template, scope, username
                )
                await connection.execute(statement)

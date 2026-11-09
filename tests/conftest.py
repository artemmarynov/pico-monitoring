import os
from uuid import uuid4

import asyncpg
import httpx
import pytest
import pytest_asyncio
from api.database import ensure_schema
from api.main import app
from api.settings import Settings


@pytest_asyncio.fixture
async def pool():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to an isolated test database")
    schema = "test_" + uuid4().hex
    admin = await asyncpg.connect(url)
    await admin.execute(f'CREATE SCHEMA "{schema}"')
    database = await asyncpg.create_pool(
        url, min_size=1, max_size=3, server_settings={"search_path": schema, "timezone": "UTC"}
    )
    try:
        await ensure_schema(database)
        yield database
    finally:
        await database.close()
        await admin.execute(f'DROP SCHEMA "{schema}" CASCADE')
        await admin.close()


@pytest_asyncio.fixture
async def client(pool):
    app.state.pool = pool
    app.state.settings = Settings(mqtt_user="test", mqtt_password="test")
    app.state.mqtt_connected = True
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client

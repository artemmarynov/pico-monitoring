import asyncio
import logging
from contextlib import asynccontextmanager, suppress

from common.settings import DatabaseSettings
from fastapi import FastAPI, HTTPException

from api import history, status
from api.database import create_pool, ensure_grafana_reader, ensure_schema
from api.mqtt import mqtt_bridge
from api.settings import Settings


@asynccontextmanager
async def lifespan(app):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    app.state.settings = Settings()
    app.state.pool = await create_pool(DatabaseSettings())
    app.state.mqtt_connected = False
    task = None
    try:
        await ensure_schema(app.state.pool)
        settings = app.state.settings
        if settings.grafana_db_password:
            await ensure_grafana_reader(
                app.state.pool, settings.grafana_db_user, settings.grafana_db_password.get_secret_value()
            )
        task = asyncio.create_task(mqtt_bridge(app))
        yield
    finally:
        if task:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
        await app.state.pool.close()


app = FastAPI(title="Pico Monitoring", lifespan=lifespan)
app.include_router(history.router)
app.include_router(status.router)


@app.get("/health")
async def health():
    try:
        async with app.state.pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        if not app.state.mqtt_connected:
            raise RuntimeError("MQTT disconnected")
    except Exception as exc:
        raise HTTPException(503, "Service not ready") from exc
    return {"ok": True}

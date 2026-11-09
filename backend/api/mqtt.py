import asyncio
import json
import logging

import aiomqtt
import asyncpg
from common.measurements import Measurement

from api.database import insert_measurement

log = logging.getLogger(__name__)


async def process_payload(pool, payload):
    try:
        measurement = Measurement.from_payload(payload)
    except ValueError as exc:
        log.warning("Skipped MQTT message: %s", exc)
        return None
    for attempt in range(3):
        try:
            await insert_measurement(pool, measurement)
            return measurement
        except (asyncpg.PostgresError, OSError, TimeoutError):
            log.warning("Database write failed (attempt %s/3)", attempt + 1)
            if attempt < 2:
                await asyncio.sleep(attempt + 1)
    log.error("Dropped measurement after three failed database writes")
    return None


async def mqtt_bridge(app):
    settings = app.state.settings
    delay = 1
    while True:
        try:
            async with aiomqtt.Client(
                settings.mqtt_broker,
                port=settings.mqtt_port,
                username=settings.mqtt_user,
                password=settings.mqtt_password.get_secret_value(),
                max_queued_incoming_messages=100,
            ) as client:
                await client.subscribe(settings.mqtt_topic)
                app.state.mqtt_connected = True
                delay = 1
                async for message in client.messages:
                    measurement = await process_payload(app.state.pool, message.payload)
                    if measurement:
                        # Export only validated values; exporter does not parse untrusted raw data.
                        await client.publish(
                            settings.validated_topic, json.dumps(measurement.as_dict(), allow_nan=False)
                        )
        except (aiomqtt.MqttError, OSError):
            log.warning("MQTT disconnected; retry in %ss", delay)
        finally:
            app.state.mqtt_connected = False
        await asyncio.sleep(delay)
        delay = min(delay * 2, 30)

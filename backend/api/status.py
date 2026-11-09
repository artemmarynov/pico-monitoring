from datetime import datetime, timezone

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

router = APIRouter()


async def sensor_snapshot(pool, stale_after_seconds):
    async with pool.acquire() as connection:
        last = await connection.fetchval("""SELECT time FROM sensor_metrics
            WHERE time IS NOT NULL AND time <= now() ORDER BY time DESC LIMIT 1""")
    age = max(0, (datetime.now(timezone.utc) - last).total_seconds()) if last else None
    return {
        "last_received_at": last.astimezone(timezone.utc).isoformat() if last else None,
        "age_seconds": age,
        "stale_after_seconds": stale_after_seconds,
        "online": age is not None and age <= stale_after_seconds,
    }


@router.get("/status")
async def sensor_status(request: Request):
    return await sensor_snapshot(request.app.state.pool, request.app.state.settings.sensor_stale_seconds)


@router.get("/metrics", response_class=PlainTextResponse)
async def sensor_metrics(request: Request):
    snapshot = await sensor_snapshot(request.app.state.pool, request.app.state.settings.sensor_stale_seconds)
    last = snapshot["last_received_at"]
    timestamp = datetime.fromisoformat(last).timestamp() if last else 0
    body = "\n".join(
        [
            "# HELP pico_sensor_online Whether a recent valid measurement has been stored.",
            "# TYPE pico_sensor_online gauge",
            f"pico_sensor_online {int(snapshot['online'])}",
            "# HELP pico_sensor_last_received_timestamp_seconds Last stored measurement in Unix seconds.",
            "# TYPE pico_sensor_last_received_timestamp_seconds gauge",
            f"pico_sensor_last_received_timestamp_seconds {timestamp}",
            "# HELP pico_sensor_stale_after_seconds Maximum age of fresh measurements.",
            "# TYPE pico_sensor_stale_after_seconds gauge",
            f"pico_sensor_stale_after_seconds {snapshot['stale_after_seconds']}",
            "",
        ]
    )

    return PlainTextResponse(body, media_type="text/plain; version=0.0.4; charset=utf-8")

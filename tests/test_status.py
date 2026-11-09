from datetime import datetime, timedelta, timezone

import pytest
from notifier.watchdog import SensorWatch


@pytest.mark.parametrize("age", [None, 10, 120])
async def test_sensor_status_and_metrics(client, pool, age):
    if age is not None:
        async with pool.acquire() as connection:
            await connection.execute(
                "INSERT INTO sensor_metrics(time,co2) VALUES ($1,600)",
                datetime.now(timezone.utc) - timedelta(seconds=age),
            )
    snapshot = (await client.get("/status")).json()
    assert snapshot["online"] is (age is not None and age < 60)
    assert (snapshot["last_received_at"] is None) is (age is None)
    metrics = (await client.get("/metrics")).text
    assert f"pico_sensor_online {int(snapshot['online'])}" in metrics


def test_sensor_outage_and_recovery_are_not_repeated():
    clock = [0]
    watch = SensorWatch(60, clock=lambda: clock[0])
    assert watch.check() is None
    clock[0] = 61
    assert "offline" in watch.check()
    assert watch.check() is None
    assert "resumed" in watch.received()
    assert watch.received() is None
    clock[0] = 120
    assert watch.check() is None
    clock[0] = 122
    assert "offline" in watch.check()

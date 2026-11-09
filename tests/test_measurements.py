from unittest.mock import AsyncMock, Mock

import asyncpg
import pytest
from api import mqtt
from common.measurements import Measurement
from notifier.alerts import AlertRules
from notifier.main import handle_payload


@pytest.mark.parametrize(
    "payload", [b"broken", b"[]", b"null", b"{}", b'{"co2":NaN}', b'{"lux":true}', b"X" * 16385]
)
def test_bad_messages_are_rejected(payload):
    with pytest.raises(ValueError):
        Measurement.from_payload(payload)


def test_partial_invalid_values_and_negative_temperature():
    value = Measurement.from_payload(b'{"temp":-1,"hum":101,"co2":-1,"lux":Infinity}')
    assert value.as_dict() == dict(temp=-1, hum=None, co2=None, lux=None)


async def test_bad_message_does_not_prevent_next_write(monkeypatch):
    insert = AsyncMock()
    monkeypatch.setattr(mqtt, "insert_measurement", insert)
    assert await mqtt.process_payload(None, b"[]") is None
    assert await mqtt.process_payload(None, b'{"co2":600}') is not None
    assert insert.await_count == 1


async def test_database_failure_has_bounded_retries(monkeypatch):
    insert = AsyncMock(side_effect=asyncpg.PostgresConnectionError())
    monkeypatch.setattr(mqtt, "insert_measurement", insert)
    monkeypatch.setattr(mqtt.asyncio, "sleep", AsyncMock())
    assert await mqtt.process_payload(None, b'{"co2":600}') is None
    assert insert.await_count == 3


def test_notifier_survives_non_object_json():
    worker = Mock()
    rules = AlertRules()
    handle_payload(b"[]", rules, worker)
    handle_payload(b'{"co2":2000}', rules, worker)
    worker.submit.assert_called_once()

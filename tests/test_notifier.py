from unittest.mock import Mock

from common.measurements import Measurement
from notifier.alerts import AlertRules, AlertWorker
from notifier.healthcheck import healthy


def reading(co2=2000):
    return Measurement(20, 50, co2, 100)


def test_cooldown_recovery_and_missing_data():
    clock = [0]
    rules = AlertRules(clock=lambda: clock[0])
    assert rules.evaluate(reading())
    clock[0] = 10
    assert rules.evaluate(reading()) is None
    assert rules.evaluate(Measurement(None, None, None, 100)) is None
    assert rules.evaluate(reading()) is None
    clock[0] = 300
    assert rules.evaluate(reading())
    assert rules.evaluate(reading(500)) is None
    clock[0] = 301
    assert rules.evaluate(reading())


def test_notification_failure_and_bounded_queue(caplog):
    provider = Mock()
    provider.notify.return_value = False
    worker = AlertWorker(provider)
    assert worker.deliver("test") is False
    assert "reported failure" in caplog.text
    provider.notify.side_effect = RuntimeError("secret URL must not appear")
    assert worker.deliver("test") is False
    assert "secret URL" not in caplog.text
    worker.submit("first")
    worker.submit("second")
    assert worker.pending.qsize() == 1


def test_heartbeat_age_and_corruption(tmp_path):
    path = tmp_path / "heartbeat"
    assert not healthy(path, 100)
    path.write_text("90")
    assert healthy(path, 100)
    assert not healthy(path, 120)
    path.write_text("not a timestamp")
    assert not healthy(path, 100)

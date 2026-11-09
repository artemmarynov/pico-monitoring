import pytest
from api.settings import Settings
from pydantic import ValidationError


@pytest.mark.parametrize(
    "topic", ["", "sensors/#", "sensors/+", "bad topic", "sensors/\ninvalid", "/root", "a/", "a" * 256]
)
def test_invalid_mqtt_topics_are_rejected(topic):
    with pytest.raises(ValidationError):
        Settings(
            mqtt_user="test",
            mqtt_password="test",
            mqtt_topic=topic,
        )


def test_mqtt_topic_and_freshness_are_shared_with_notifier(monkeypatch):
    from notifier.settings import Settings as NotifierSettings

    monkeypatch.setenv("MQTT_TOPIC", "test/classroom_1/env")
    monkeypatch.setenv("SENSOR_STALE_SECONDS", "45")
    settings = NotifierSettings(user="test", password="test")
    assert settings.mqtt_topic == "test/classroom_1/env"
    assert settings.validated_topic == "test/classroom_1/env/validated"
    assert settings.status_topic == "test/classroom_1/env/status"
    assert settings.sensor_stale_seconds == 45

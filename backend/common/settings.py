from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PG_", hide_input_in_errors=True)
    host: str = Field(default="postgres", min_length=1)
    port: int = Field(default=5432, ge=1, le=65535)
    user: str = Field(min_length=1)
    password: SecretStr = Field(min_length=1)
    db: str = Field(min_length=1)

    def connect_kwargs(self):
        return dict(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password.get_secret_value(),
            database=self.db,
            server_settings={"timezone": "UTC"},
            command_timeout=30,
        )


class SensorSettings(BaseSettings):
    model_config = SettingsConfigDict(populate_by_name=True, hide_input_in_errors=True)
    mqtt_topic: str = Field(
        default="sensors/room/env",
        validation_alias="MQTT_TOPIC",
        max_length=255,
        pattern=r"^[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*$",
    )
    sensor_stale_seconds: int = Field(default=60, validation_alias="SENSOR_STALE_SECONDS", ge=1, le=86400)

    @property
    def validated_topic(self):
        return f"{self.mqtt_topic}/validated"

    @property
    def status_topic(self):
        return f"{self.mqtt_topic}/status"

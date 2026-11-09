from common.settings import SensorSettings
from pydantic import Field, SecretStr
from pydantic_settings import SettingsConfigDict


class Settings(SensorSettings):
    model_config = SettingsConfigDict(hide_input_in_errors=True)
    grafana_db_user: str = Field(default="pico_grafana", pattern=r"^[a-z][a-z0-9_]{0,62}$")
    grafana_db_password: SecretStr | None = None
    mqtt_broker: str = Field(default="mosquitto", min_length=1)
    mqtt_port: int = Field(default=1883, ge=1, le=65535)
    mqtt_user: str = Field(min_length=1)
    mqtt_password: SecretStr = Field(min_length=1)

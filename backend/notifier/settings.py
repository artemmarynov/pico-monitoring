from common.settings import SensorSettings
from pydantic import Field, SecretStr
from pydantic_settings import SettingsConfigDict


class Settings(SensorSettings):
    model_config = SettingsConfigDict(env_prefix="NOTIFIER_", hide_input_in_errors=True)
    broker: str = Field(default="mosquitto", min_length=1)
    port: int = Field(default=1883, ge=1, le=65535)
    user: str = Field(min_length=1)
    password: SecretStr = Field(min_length=1)
    apprise_url: SecretStr | None = None

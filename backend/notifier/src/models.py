# notifier/src/models.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    broker: str
    port: int = 1883
    user: str | None = None
    password: str | None = None
    base_topic: str
    apprise_url: str | None = None

    model_config = SettingsConfigDict(
        env_prefix='NOTIFIER_',
        env_file_encoding='utf-8',
    )

settings = Settings()

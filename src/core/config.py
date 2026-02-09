from pathlib import Path
from typing import List

from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict, BaseSettings


class FirebaseConfig(BaseModel):
    credentials: str
    storage: str
    app_type: str
    locales: List[str] | None = None
    db_name: str | None = None


class FirebaseDatabaseConfig(BaseModel):
    production: FirebaseConfig
    development: FirebaseConfig
    lovella: FirebaseConfig
    dao_sandbox: FirebaseConfig
    moonlit: FirebaseConfig
    moonlit_dev: FirebaseConfig
    richnovel: FirebaseConfig
    richnovel_dev: FirebaseConfig
    amora: FirebaseConfig
    noirlit: FirebaseConfig
    lovelit: FirebaseConfig


class OpenaiConfig(BaseModel):
    model: str = "omni-moderation-latest"
    api_key: str


class RedisConfig(BaseSettings):
    driver: str = "redis"
    host: str = "localhost"
    port: int = 6379

    @property
    def url(self) -> str:
        return f"{self.driver}://" f"{self.host}:{self.port}"


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f"{Path(__file__).resolve().parent.parent.parent}/secrets/.env",
        case_sensitive=False,
        env_nested_delimiter="__",
        env_ignore_empty=True,
        extra="ignore",
    )
    openai: OpenaiConfig
    firebase: FirebaseDatabaseConfig
    redis: RedisConfig


config = AppConfig()

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class _BaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=os.getenv('ENV_FILE', '.env'))


class PostgresSettings(_BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    @property
    def POSTGRES_URL(self) -> str:
        return f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'


class KafkaSettings(_BaseSettings):
    KAFKA_BOOTSTRAP_HOST: str
    KAFKA_BOOTSTRAP_PORT: int

    @property
    def KAFKA_URL(self) -> str:
        return f'{self.KAFKA_BOOTSTRAP_HOST}:{self.KAFKA_BOOTSTRAP_PORT}'


class RedisSettings(_BaseSettings):
    REDIS_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: str

    @property
    def REDIS_URL(self) -> str:
        return f'redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0'


class Settings(
    PostgresSettings,
    KafkaSettings,
    RedisSettings,
):
    pass


settings = Settings()

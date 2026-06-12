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


class AnalyticsSettings(_BaseSettings):
    WEEKS_FOR_ANALYTICS: int = 52


class DecimalSettings(_BaseSettings):
    DECIMAL_TOTAL_DIGITS: int = 12
    DECIMAL_FRACTIONAL_DIGITS: int = 2


class Settings(PostgresSettings, AnalyticsSettings, DecimalSettings):
    pass


settings = Settings()

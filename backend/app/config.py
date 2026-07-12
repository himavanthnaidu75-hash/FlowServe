from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "FlowServe"
    environment: str = "development"
    frontend_url: str = "http://localhost:5173"

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/flowserve"

    jwt_secret: str = "change-me-to-a-long-random-string"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080

    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    sendgrid_api_key: str = ""
    sendgrid_from_email: str = "noreply@flowserve.app"

    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

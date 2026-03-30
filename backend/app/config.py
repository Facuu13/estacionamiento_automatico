from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://parking:parking_dev@localhost:5432/parking"
    backend_public_url: str = "http://localhost:8000"
    frontend_public_url: str = "http://localhost:3000"
    cors_origins: str = "http://localhost:3000"

    mercadopago_access_token: str = ""
    mercadopago_webhook_secret: str = ""

    mock_payments: bool = True

    device_hmac_secret: str = "dev_change_me"
    session_signing_secret: str = "dev_session_secret"


@lru_cache
def get_settings() -> Settings:
    return Settings()

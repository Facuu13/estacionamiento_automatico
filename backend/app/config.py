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
    # ESP32 salida (mismo id que en firmware DEVICE_ID)
    default_gate_device_id: str = "gate-01"
    # Barrera de ingreso (otro ESP32 o el mismo id si comparten lógica de cola)
    entry_gate_device_id: str = "gate-01"
    session_signing_secret: str = "dev_session_secret"

    parking_price_per_minute_cents: int = 50
    parking_minimum_cents: int = 100
    parking_grace_seconds: int = 0


@lru_cache
def get_settings() -> Settings:
    return Settings()

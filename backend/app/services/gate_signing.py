import hashlib
import hmac
import time

from app.config import get_settings


def sign_open_command(exit_token: str, ttl_seconds: int = 60) -> tuple[str, int]:
    """Firma HMAC para que el ESP32 valide un comando de apertura (msg + ts)."""
    settings = get_settings()
    ts = int(time.time())
    msg = f"OPEN:{exit_token}:{ts}".encode()
    sig = hmac.new(
        settings.device_hmac_secret.encode(),
        msg,
        hashlib.sha256,
    ).hexdigest()
    return sig, ts


def sign_device_pulse_command(device_id: str, nonce: str, ts: int) -> str:
    """Firma HMAC para comando PULSE hacia el ESP32 (debe coincidir con el firmware)."""
    settings = get_settings()
    msg = f"PULSE:{device_id}:{nonce}:{ts}".encode()
    return hmac.new(
        settings.device_hmac_secret.encode(),
        msg,
        hashlib.sha256,
    ).hexdigest()


def verify_open_signature(exit_token: str, ts: int, signature: str, max_age: int = 120) -> bool:
    now = int(time.time())
    if abs(now - ts) > max_age:
        return False
    settings = get_settings()
    msg = f"OPEN:{exit_token}:{ts}".encode()
    expected = hmac.new(
        settings.device_hmac_secret.encode(),
        msg,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

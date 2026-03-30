import secrets
import time
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.config import Settings
from app.models.device_command import DeviceCommand
from app.services.gate_signing import sign_device_pulse_command

RELAY_SECONDS_DEFAULT = 5


def enqueue_gate_pulse(
    db: Session,
    settings: Settings,
    device_id: str,
    pulse_seconds: int = RELAY_SECONDS_DEFAULT,
) -> None:
    nonce = secrets.token_hex(16)
    pulse_ts = int(time.time())
    pulse_sig = sign_device_pulse_command(device_id, nonce, pulse_ts)
    cmd = DeviceCommand(
        id=uuid.uuid4(),
        device_id=device_id,
        nonce=nonce,
        ts=pulse_ts,
        pulse_seconds=pulse_seconds,
        signature_hex=pulse_sig,
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=120),
    )
    db.add(cmd)

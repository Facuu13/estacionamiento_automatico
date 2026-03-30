import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.session import ParkingSession, SessionStatus
from app.schemas.exit import ExitPreviewOut, ExitVerifyIn, ExitVerifyOut
from app.services.gate_pulse import RELAY_SECONDS_DEFAULT, enqueue_gate_pulse
from app.services.gate_signing import sign_open_command
from app.services.pricing import compute_amount_cents

router = APIRouter(prefix="/api/v1/exit", tags=["exit"])


@router.get("/preview", response_model=ExitPreviewOut)
def preview_exit(
    exit_token: str = Query(..., min_length=8),
    db: Session = Depends(get_db),
) -> ExitPreviewOut:
    settings = get_settings()
    row = (
        db.query(ParkingSession)
        .filter(ParkingSession.exit_token == exit_token)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Token inválido")

    now = datetime.now(timezone.utc)
    created = row.created_at
    if created and created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    duration_seconds = max(0, int((now - created).total_seconds())) if created else 0

    amount_cents = compute_amount_cents(created, now, settings)
    if row.status == SessionStatus.PAID:
        amount_cents = 0

    return ExitPreviewOut(
        session_id=row.id,
        license_plate=row.license_plate,
        status=row.status,
        created_at=row.created_at,
        duration_seconds=duration_seconds,
        amount_cents=amount_cents,
        paid_at=row.paid_at,
    )


@router.post("/verify", response_model=ExitVerifyOut)
def verify_exit(
    body: ExitVerifyIn,
    db: Session = Depends(get_db),
) -> ExitVerifyOut:
    settings = get_settings()
    row = (
        db.query(ParkingSession)
        .filter(ParkingSession.exit_token == body.exit_token)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Token inválido")

    if row.status == SessionStatus.EXITED:
        return ExitVerifyOut(
            allowed=False,
            relay_open_seconds=0,
            command_signature=None,
            message="Ya se registró la salida.",
        )

    if row.status != SessionStatus.PAID:
        return ExitVerifyOut(
            allowed=False,
            relay_open_seconds=0,
            command_signature=None,
            message="Pago pendiente o rechazado.",
        )

    sig, ts = sign_open_command(row.exit_token)
    row.status = SessionStatus.EXITED
    row.exited_at = datetime.now(timezone.utc)

    enqueue_gate_pulse(db, settings, settings.default_gate_device_id, RELAY_SECONDS_DEFAULT)
    db.commit()

    return ExitVerifyOut(
        allowed=True,
        relay_open_seconds=RELAY_SECONDS_DEFAULT,
        command_signature=f"{sig}:{ts}",
        message="Salida autorizada.",
    )

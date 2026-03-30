from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.session import ParkingSession, SessionStatus
from app.schemas.exit import ExitVerifyIn, ExitVerifyOut
from app.services.gate_signing import sign_open_command

router = APIRouter(prefix="/api/v1/exit", tags=["exit"])

RELAY_SECONDS = 5


@router.post("/verify", response_model=ExitVerifyOut)
def verify_exit(
    body: ExitVerifyIn,
    db: Session = Depends(get_db),
) -> ExitVerifyOut:
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
    db.commit()

    return ExitVerifyOut(
        allowed=True,
        relay_open_seconds=RELAY_SECONDS,
        command_signature=f"{sig}:{ts}",
        message="Salida autorizada.",
    )

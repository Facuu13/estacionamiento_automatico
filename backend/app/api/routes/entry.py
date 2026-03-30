import secrets
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.session import ParkingSession, SessionStatus
from app.schemas.entry import EntryCreate, EntryResponse
from app.services.gate_pulse import RELAY_SECONDS_DEFAULT, enqueue_gate_pulse

router = APIRouter(prefix="/api/v1/entry", tags=["entry"])


@router.post("/", response_model=EntryResponse)
def create_entry(
    body: EntryCreate,
    db: Session = Depends(get_db),
) -> EntryResponse:
    settings = get_settings()
    exit_token = secrets.token_urlsafe(32)
    session = ParkingSession(
        id=uuid.uuid4(),
        license_plate=body.license_plate.upper().replace(" ", ""),
        gate_code=body.gate_code,
        status=SessionStatus.ACTIVE,
        exit_token=exit_token,
    )
    db.add(session)
    enqueue_gate_pulse(db, settings, settings.entry_gate_device_id, RELAY_SECONDS_DEFAULT)
    db.commit()
    db.refresh(session)

    pay_url = f"{settings.frontend_public_url}/pago/{session.id}"
    exit_qr_url = f"{settings.frontend_public_url}/salida?t={exit_token}"

    return EntryResponse(
        session_id=session.id,
        exit_token=exit_token,
        pay_url=pay_url,
        exit_qr_url=exit_qr_url,
    )

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.session import ParkingSession
from app.schemas.sessions import SessionStatusResponse

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


@router.get("/{session_id}", response_model=SessionStatusResponse)
def get_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> SessionStatusResponse:
    row = db.get(ParkingSession, session_id)
    if not row:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return SessionStatusResponse(
        session_id=row.id,
        status=row.status,
        license_plate=row.license_plate,
        paid_at=row.paid_at,
    )

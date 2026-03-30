import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.session import SessionStatus


class SessionStatusResponse(BaseModel):
    session_id: uuid.UUID
    status: SessionStatus
    license_plate: str
    created_at: datetime
    paid_at: datetime | None

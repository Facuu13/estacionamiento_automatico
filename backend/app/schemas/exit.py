import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.session import SessionStatus


class ExitPreviewOut(BaseModel):
    session_id: uuid.UUID
    license_plate: str
    status: SessionStatus
    created_at: datetime
    duration_seconds: int
    amount_cents: int
    paid_at: datetime | None


class ExitVerifyIn(BaseModel):
    exit_token: str = Field(..., min_length=8)


class ExitVerifyOut(BaseModel):
    allowed: bool
    relay_open_seconds: int = 5
    command_signature: str | None = None
    message: str

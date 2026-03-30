import uuid

from pydantic import BaseModel, Field


class EntryCreate(BaseModel):
    license_plate: str = Field(..., min_length=5, max_length=32)
    gate_code: str = Field(default="default", max_length=64)


class EntryResponse(BaseModel):
    session_id: uuid.UUID
    exit_token: str
    pay_url: str
    exit_qr_url: str

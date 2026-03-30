import uuid

from pydantic import BaseModel


class CheckoutCreate(BaseModel):
    session_id: uuid.UUID


class CheckoutResponse(BaseModel):
    init_point: str
    preference_id: str | None

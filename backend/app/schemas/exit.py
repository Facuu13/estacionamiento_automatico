from pydantic import BaseModel, Field


class ExitVerifyIn(BaseModel):
    exit_token: str = Field(..., min_length=8)


class ExitVerifyOut(BaseModel):
    allowed: bool
    relay_open_seconds: int = 5
    command_signature: str | None = None
    message: str

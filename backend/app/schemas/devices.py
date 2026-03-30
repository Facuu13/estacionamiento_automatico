from pydantic import BaseModel, Field


class HeartbeatIn(BaseModel):
    firmware_version: str | None = Field(default=None, max_length=32)
    rssi: int | None = None


class HeartbeatOut(BaseModel):
    ok: bool
    server_time: str

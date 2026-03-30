from pydantic import BaseModel, Field


class HeartbeatIn(BaseModel):
    firmware_version: str | None = Field(default=None, max_length=32)
    rssi: int | None = None


class DevicePulseCommand(BaseModel):
    id: str
    action: str = "pulse"
    seconds: int
    nonce: str
    ts: int
    signature: str


class HeartbeatOut(BaseModel):
    ok: bool
    server_time: str
    command: DevicePulseCommand | None = None

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.device import Device
from app.models.device_command import DeviceCommand
from app.schemas.devices import DevicePulseCommand, HeartbeatIn, HeartbeatOut

router = APIRouter(prefix="/api/v1/devices", tags=["devices"])


@router.post("/{device_id}/heartbeat", response_model=HeartbeatOut)
def heartbeat(
    device_id: str,
    body: HeartbeatIn,
    db: Session = Depends(get_db),
) -> HeartbeatOut:
    row = db.query(Device).filter(Device.device_id == device_id).first()
    if not row:
        row = Device(device_id=device_id, name=device_id)
        db.add(row)
    row.firmware_version = body.firmware_version
    row.last_rssi = body.rssi
    row.last_heartbeat_at = datetime.now(timezone.utc)

    now = datetime.now(timezone.utc)
    pending = (
        db.query(DeviceCommand)
        .filter(
            DeviceCommand.device_id == device_id,
            DeviceCommand.consumed.is_(False),
            DeviceCommand.expires_at > now,
        )
        .order_by(DeviceCommand.created_at.asc())
        .first()
    )

    command: DevicePulseCommand | None = None
    if pending:
        command = DevicePulseCommand(
            id=str(pending.id),
            action="pulse",
            seconds=pending.pulse_seconds,
            nonce=pending.nonce,
            ts=pending.ts,
            signature=pending.signature_hex,
        )

    db.commit()

    return HeartbeatOut(
        ok=True,
        server_time=datetime.now(timezone.utc).isoformat(),
        command=command,
    )


@router.post("/{device_id}/commands/{command_id}/ack")
def ack_command(
    device_id: str,
    command_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> dict[str, bool]:
    cmd = db.get(DeviceCommand, command_id)
    if not cmd or cmd.device_id != device_id:
        raise HTTPException(status_code=404, detail="Comando no encontrado")
    if cmd.consumed:
        return {"ok": True, "duplicate": True}
    cmd.consumed = True
    db.commit()
    return {"ok": True}

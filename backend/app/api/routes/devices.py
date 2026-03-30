from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.device import Device
from app.schemas.devices import HeartbeatIn, HeartbeatOut

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
    db.commit()
    return HeartbeatOut(
        ok=True,
        server_time=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/{device_id}")
def get_device(device_id: str, db: Session = Depends(get_db)) -> dict:
    row = db.query(Device).filter(Device.device_id == device_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return {
        "device_id": row.device_id,
        "name": row.name,
        "firmware_version": row.firmware_version,
        "last_heartbeat_at": row.last_heartbeat_at.isoformat() if row.last_heartbeat_at else None,
    }

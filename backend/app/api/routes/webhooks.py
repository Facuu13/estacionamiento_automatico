from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.payment import Payment, PaymentStatus
from app.models.session import ParkingSession, SessionStatus
from app.models.webhook_event import WebhookEvent
from app.services.mercadopago_client import get_payment

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


def _idempotency_key(body: dict) -> str:
    data = body.get("data") or {}
    data_id = data.get("id")
    typ = body.get("type") or body.get("topic") or "unknown"
    action = body.get("action") or ""
    return f"mp:{typ}:{data_id}:{action}"


def _apply_payment_approved(db: Session, session_id: uuid.UUID, mp_payment_id: str) -> None:
    session = db.get(ParkingSession, session_id)
    if not session:
        return
    if session.status not in (SessionStatus.ACTIVE, SessionStatus.PENDING_PAYMENT):
        return
    pay = (
        db.query(Payment)
        .filter(Payment.session_id == session_id)
        .order_by(Payment.created_at.desc())
        .first()
    )
    if pay:
        pay.status = PaymentStatus.APPROVED
        pay.mp_payment_id = mp_payment_id
    session.status = SessionStatus.PAID
    session.paid_at = datetime.now(timezone.utc)


@router.post("/mercadopago")
async def mercadopago_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    settings = get_settings()
    try:
        body = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="JSON inválido")

    key = _idempotency_key(body)
    if not key.endswith(":unknown") and "unknown" in key:
        pass

    try:
        db.add(
            WebhookEvent(
                id=uuid.uuid4(),
                idempotency_key=key,
                source="mercadopago",
                payload_summary=json.dumps(body)[:2000],
            )
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        return {"status": "duplicate"}

    data = body.get("data") or {}
    typ = body.get("type") or body.get("topic")

    if settings.mock_payments:
        return {"status": "ignored_mock"}

    if typ == "payment" and data.get("id"):
        pay_info = get_payment(str(data["id"]))
        ext = pay_info.get("external_reference")
        status = (pay_info.get("status") or "").lower()
        if ext and status == "approved":
            try:
                sid = uuid.UUID(str(ext))
            except ValueError:
                return {"status": "bad_reference"}
            mp_id = str(pay_info.get("id", data["id"]))
            _apply_payment_approved(db, sid, mp_id)
            db.commit()

    return {"status": "ok"}

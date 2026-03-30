"""Solo para desarrollo local cuando MOCK_PAYMENTS=true."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.payment import Payment, PaymentStatus
from app.models.session import ParkingSession, SessionStatus
from app.services.pricing import compute_amount_cents

router = APIRouter(prefix="/api/v1/dev", tags=["dev"])


@router.post("/simulate-payment")
def simulate_payment(
    session_id: uuid.UUID = Query(..., description="UUID de la sesión de estacionamiento"),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    settings = get_settings()
    if not settings.mock_payments:
        raise HTTPException(status_code=403, detail="Solo disponible con MOCK_PAYMENTS=true")

    session = db.get(ParkingSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    if session.status not in (SessionStatus.ACTIVE, SessionStatus.PENDING_PAYMENT):
        raise HTTPException(status_code=400, detail="La sesión no admite simulación de pago")

    entered = session.created_at
    if entered and entered.tzinfo is None:
        entered = entered.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    amount = (
        compute_amount_cents(entered, now, settings)
        if entered
        else settings.parking_minimum_cents
    )

    pay = (
        db.query(Payment)
        .filter(Payment.session_id == session_id)
        .order_by(Payment.created_at.desc())
        .first()
    )
    if not pay:
        pay = Payment(
            id=uuid.uuid4(),
            session_id=session_id,
            status=PaymentStatus.APPROVED,
            amount_cents=amount,
            mp_payment_id=f"mock_pay_{session_id.hex[:8]}",
        )
        db.add(pay)
    else:
        pay.status = PaymentStatus.APPROVED
        pay.amount_cents = amount
        pay.mp_payment_id = pay.mp_payment_id or f"mock_pay_{session_id.hex[:8]}"

    session.status = SessionStatus.PAID
    session.paid_at = datetime.now(timezone.utc)
    db.commit()
    return {"status": "paid", "session_id": str(session_id)}

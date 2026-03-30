import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.payment import Payment, PaymentStatus
from app.models.session import ParkingSession, SessionStatus
from app.schemas.payments import CheckoutCreate, CheckoutResponse
from app.services.mercadopago_client import create_checkout_preference
from app.services.pricing import compute_amount_cents

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])


@router.post("/checkout", response_model=CheckoutResponse)
def checkout(
    body: CheckoutCreate,
    db: Session = Depends(get_db),
) -> CheckoutResponse:
    settings = get_settings()
    session = db.get(ParkingSession, body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    if session.status not in (SessionStatus.ACTIVE, SessionStatus.PENDING_PAYMENT):
        raise HTTPException(status_code=400, detail="La sesión no admite pago")

    entered = session.created_at
    if entered.tzinfo is None:
        entered = entered.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    amount_cents = compute_amount_cents(entered, now, settings)

    existing = (
        db.query(Payment)
        .filter(Payment.session_id == session.id)
        .order_by(Payment.created_at.desc())
        .first()
    )
    if existing and existing.mp_init_point and existing.amount_cents == amount_cents:
        return CheckoutResponse(
            init_point=existing.mp_init_point,
            preference_id=existing.mp_preference_id,
        )

    if existing and existing.status == PaymentStatus.PENDING:
        existing.amount_cents = amount_cents
        existing.mp_preference_id = None
        existing.mp_init_point = None
        payment = existing
    else:
        payment = Payment(
            id=uuid.uuid4(),
            session_id=session.id,
            status=PaymentStatus.PENDING,
            amount_cents=amount_cents,
        )
        db.add(payment)
    db.commit()
    db.refresh(payment)

    pref = create_checkout_preference(
        session.id,
        f"Estacionamiento {session.license_plate}",
        payment.amount_cents,
    )
    init = pref.get("sandbox_init_point") or pref.get("init_point") or ""
    payment.mp_preference_id = str(pref.get("id", ""))
    payment.mp_init_point = init
    db.commit()

    return CheckoutResponse(init_point=init, preference_id=payment.mp_preference_id)

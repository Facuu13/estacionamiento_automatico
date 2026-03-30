import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.payment import Payment, PaymentStatus
from app.models.session import ParkingSession, SessionStatus
from app.schemas.payments import CheckoutCreate, CheckoutResponse
from app.services.mercadopago_client import create_checkout_preference

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

DEFAULT_AMOUNT_CENTS = 100_00


@router.post("/checkout", response_model=CheckoutResponse)
def checkout(
    body: CheckoutCreate,
    db: Session = Depends(get_db),
) -> CheckoutResponse:
    session = db.get(ParkingSession, body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    if session.status != SessionStatus.PENDING_PAYMENT:
        raise HTTPException(status_code=400, detail="La sesión no admite pago")

    existing = (
        db.query(Payment)
        .filter(Payment.session_id == session.id)
        .order_by(Payment.created_at.desc())
        .first()
    )
    if existing and existing.mp_init_point:
        return CheckoutResponse(
            init_point=existing.mp_init_point,
            preference_id=existing.mp_preference_id,
        )

    payment = existing or Payment(
        id=uuid.uuid4(),
        session_id=session.id,
        status=PaymentStatus.PENDING,
        amount_cents=DEFAULT_AMOUNT_CENTS,
    )
    if not existing:
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

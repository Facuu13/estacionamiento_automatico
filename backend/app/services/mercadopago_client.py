from __future__ import annotations

import uuid
from typing import Any

import mercadopago

from app.config import get_settings


def create_checkout_preference(
    session_id: uuid.UUID,
    title: str,
    amount_cents: int,
) -> dict[str, Any]:
    settings = get_settings()
    if settings.mock_payments or not settings.mercadopago_access_token:
        pref_id = f"mock_pref_{session_id.hex[:12]}"
        return {
            "id": pref_id,
            "init_point": (
                f"{settings.frontend_public_url}/pago/exito?"
                f"session_id={session_id}&mock=1"
            ),
            "sandbox_init_point": (
                f"{settings.frontend_public_url}/pago/exito?"
                f"session_id={session_id}&mock=1"
            ),
        }

    sdk = mercadopago.SDK(settings.mercadopago_access_token)
    preference_data: dict[str, Any] = {
        "items": [
            {
                "title": title,
                "quantity": 1,
                "unit_price": max(amount_cents / 100.0, 1.0),
                "currency_id": "ARS",
            }
        ],
        "external_reference": str(session_id),
        "back_urls": {
            "success": f"{settings.frontend_public_url}/pago/exito?session_id={session_id}",
            "failure": f"{settings.frontend_public_url}/pago/error?session_id={session_id}",
            "pending": f"{settings.frontend_public_url}/pago/pendiente?session_id={session_id}",
        },
        "auto_return": "approved",
        "notification_url": f"{settings.backend_public_url}/api/v1/webhooks/mercadopago",
    }
    result = sdk.preference().create(preference_data)
    body = result.get("response") or {}
    if result.get("status") and result["status"] >= 400:
        raise RuntimeError(body.get("message", str(body)))
    return body


def get_payment(payment_id: str) -> dict[str, Any]:
    settings = get_settings()
    if settings.mock_payments or not settings.mercadopago_access_token:
        return {
            "id": int(payment_id) if payment_id.isdigit() else payment_id,
            "status": "approved",
            "external_reference": "",
        }
    sdk = mercadopago.SDK(settings.mercadopago_access_token)
    result = sdk.payment().get(payment_id)
    body = result.get("response") or {}
    if result.get("status") and result["status"] >= 400:
        raise RuntimeError(body.get("message", str(body)))
    return body

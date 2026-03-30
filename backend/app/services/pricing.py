from __future__ import annotations

from datetime import datetime, timezone

from app.config import Settings


def compute_amount_cents(
    entered_at: datetime,
    now_utc: datetime,
    settings: Settings,
) -> int:
    """Tarifa por minuto completo (redondeo hacia arriba), mínimo y franja inicial opcional."""
    if entered_at.tzinfo is None:
        entered_at = entered_at.replace(tzinfo=timezone.utc)
    if now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=timezone.utc)

    delta_sec = max(0, int((now_utc - entered_at).total_seconds()))
    if delta_sec <= settings.parking_grace_seconds:
        return settings.parking_minimum_cents

    billable_sec = max(0, delta_sec - settings.parking_grace_seconds)
    minutes = (billable_sec + 59) // 60
    raw = minutes * settings.parking_price_per_minute_cents
    return max(settings.parking_minimum_cents, raw)

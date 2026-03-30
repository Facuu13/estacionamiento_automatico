"""Tests unitarios de tarifa (sin base de datos)."""

from datetime import datetime, timedelta, timezone

from app.config import Settings
from app.services.pricing import compute_amount_cents


def _settings(**kwargs) -> Settings:
    defaults = dict(
        parking_price_per_minute_cents=50,
        parking_minimum_cents=100,
        parking_grace_seconds=0,
    )
    defaults.update(kwargs)
    return Settings(**defaults)


def test_zero_duration_returns_minimum():
    t0 = datetime(2026, 3, 30, 12, 0, 0, tzinfo=timezone.utc)
    s = _settings()
    assert compute_amount_cents(t0, t0, s) == 100


def test_grace_period_returns_minimum():
    t0 = datetime(2026, 3, 30, 12, 0, 0, tzinfo=timezone.utc)
    s = _settings(parking_grace_seconds=120, parking_minimum_cents=100)
    t1 = t0 + timedelta(seconds=60)
    assert compute_amount_cents(t0, t1, s) == 100


def test_one_billable_minute_respects_minimum():
    t0 = datetime(2026, 3, 30, 12, 0, 0, tzinfo=timezone.utc)
    s = _settings(parking_price_per_minute_cents=50, parking_minimum_cents=100)
    t1 = t0 + timedelta(minutes=1)
    assert compute_amount_cents(t0, t1, s) == 100


def test_three_minutes_above_minimum():
    t0 = datetime(2026, 3, 30, 12, 0, 0, tzinfo=timezone.utc)
    s = _settings(parking_price_per_minute_cents=50, parking_minimum_cents=100)
    t1 = t0 + timedelta(minutes=3)
    assert compute_amount_cents(t0, t1, s) == 150


def test_naive_datetimes_treated_as_utc():
    t0 = datetime(2026, 3, 30, 12, 0, 0)
    t1 = t0 + timedelta(minutes=2)
    s = _settings(parking_price_per_minute_cents=50, parking_minimum_cents=100)
    assert compute_amount_cents(t0, t1, s) == 100


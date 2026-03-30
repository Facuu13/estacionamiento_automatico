import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("MOCK_PAYMENTS", "true")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://parking:parking_dev@localhost:5432/parking",
)
os.environ.setdefault("DEVICE_HMAC_SECRET", "test_device_hmac_secret_32_chars_min")
os.environ.setdefault("SESSION_SIGNING_SECRET", "test_session_signing")
os.environ.setdefault("FRONTEND_PUBLIC_URL", "http://localhost:3000")
os.environ.setdefault("BACKEND_PUBLIC_URL", "http://localhost:8000")
os.environ.setdefault("ENTRY_GATE_DEVICE_ID", "gate-entry-test")


@pytest.fixture
def client() -> TestClient:
    from app.main import app

    return TestClient(app)

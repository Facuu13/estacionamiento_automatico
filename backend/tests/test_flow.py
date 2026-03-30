"""Requiere PostgreSQL con migraciones aplicadas (ver docs/MANUAL_PRUEBAS.md)."""

import pytest

pytestmark = pytest.mark.integration


def test_full_flow_entry_checkout_simulate_exit(client):
    r = client.post(
        "/api/v1/entry/",
        json={"license_plate": "AB123CD", "gate_code": "A1"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    session_id = data["session_id"]
    exit_token = data["exit_token"]

    r = client.post("/api/v1/payments/checkout", json={"session_id": session_id})
    assert r.status_code == 200, r.text
    assert r.json().get("init_point")

    r = client.post(
        f"/api/v1/dev/simulate-payment?session_id={session_id}",
    )
    assert r.status_code == 200, r.text

    r = client.get(f"/api/v1/sessions/{session_id}")
    assert r.status_code == 200
    assert r.json()["status"] == "paid"

    r = client.post("/api/v1/exit/verify", json={"exit_token": exit_token})
    assert r.status_code == 200
    body = r.json()
    assert body["allowed"] is True
    assert body["command_signature"]

    r = client.post(
        "/api/v1/devices/gate-01/heartbeat",
        json={"firmware_version": "test", "rssi": -50},
    )
    assert r.status_code == 200
    hb = r.json()
    assert hb.get("command") is not None
    assert hb["command"]["action"] == "pulse"
    cmd_id = hb["command"]["id"]
    r = client.post(f"/api/v1/devices/gate-01/commands/{cmd_id}/ack")
    assert r.status_code == 200

    r = client.post("/api/v1/exit/verify", json={"exit_token": exit_token})
    assert r.status_code == 200
    assert r.json()["allowed"] is False


def test_webhook_idempotent(client):
    payload = {"type": "payment", "data": {"id": "999001"}, "action": "payment.updated"}
    r = client.post("/api/v1/webhooks/mercadopago", json=payload)
    assert r.status_code == 200
    r2 = client.post("/api/v1/webhooks/mercadopago", json=payload)
    assert r2.status_code == 200
    assert r2.json().get("status") == "duplicate"

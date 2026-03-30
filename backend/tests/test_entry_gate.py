"""Integración: pulso de barrera de ingreso en el device_id configurado."""

import pytest

pytestmark = pytest.mark.integration


def test_entry_enqueues_pulse_for_entry_device(client):
    """Con ENTRY_GATE_DEVICE_ID=gate-entry-test (conftest), el pulso de ingreso no va a gate-01."""
    r = client.post(
        "/api/v1/entry/",
        json={"license_plate": "ZZ999ZZ", "gate_code": "A1"},
    )
    assert r.status_code == 200, r.text

    r = client.post(
        "/api/v1/devices/gate-01/heartbeat",
        json={"firmware_version": "test", "rssi": -50},
    )
    assert r.status_code == 200
    assert r.json().get("command") is None

    r = client.post(
        "/api/v1/devices/gate-entry-test/heartbeat",
        json={"firmware_version": "test", "rssi": -50},
    )
    assert r.status_code == 200
    hb = r.json()
    assert hb.get("command") is not None
    assert hb["command"]["action"] == "pulse"
    cmd_id = hb["command"]["id"]
    r = client.post(f"/api/v1/devices/gate-entry-test/commands/{cmd_id}/ack")
    assert r.status_code == 200

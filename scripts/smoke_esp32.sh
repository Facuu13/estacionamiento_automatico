#!/usr/bin/env bash
# Prueba rápida con ESP32 y API en la misma red: el firmware hace heartbeat;
# este script solo verifica que la API responde y opcionalmente simula un heartbeat.
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"
DEVICE_ID="${DEVICE_ID:-gate-01}"

echo "== Health =="
curl -sfS "${API_URL}/health" | head -c 200
echo ""

echo "== Heartbeat simulado (como el ESP32) device=${DEVICE_ID} =="
curl -sfS -X POST "${API_URL}/api/v1/devices/${DEVICE_ID}/heartbeat" \
  -H "Content-Type: application/json" \
  -d '{"firmware_version":"smoke","rssi":-55}' | head -c 500
echo ""
echo "OK. Si hay comando pendiente (pulse), el JSON incluye \"command\"."

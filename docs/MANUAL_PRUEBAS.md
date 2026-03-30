# Manual de pruebas — desarrollo y QA

## Requisitos

- Docker y Docker Compose **o** PostgreSQL 16 accesible en `localhost:5432`.
- Node.js 20+ para tests E2E del frontend.
- Python 3.12+ para tests del backend.

## 1. Levantar el entorno local (Docker)

En la raíz del proyecto:

```bash
docker compose up --build -d
```

Esperá a que `api` y `web` estén healthy. Abrí:

- Web: http://localhost:3000  
- API: http://localhost:8000/docs  

## 2. Pruebas automáticas — backend

Solo base de datos:

```bash
docker compose up -d db
sleep 3
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
export DATABASE_URL=postgresql://parking:parking_dev@localhost:5432/parking
export MOCK_PAYMENTS=true
.venv/bin/alembic upgrade head
.venv/bin/pytest -q
```

Deberías ver todos los tests en verde.

## 3. Pruebas automáticas — E2E (Playwright)

Con **API y web en marcha** (por ejemplo `docker compose up -d` completo):

```bash
cd frontend
npm install
npx playwright install
npm run test:e2e
```

## 4. Casos de prueba manuales (checklist)

Ejecutá en orden con el stack local y `MOCK_PAYMENTS=true` (por defecto en `docker-compose.yml`).

| # | Acción | Resultado esperado |
|---|--------|---------------------|
| 1 | Abrí http://localhost:3000 | Página de inicio con enlace a ingreso y a QR de entrada (`/entrada`) |
| 2 | Ingreso con patente `TEST01` | Redirección a `/ticket/<uuid>` con ticket digital y QR de salida |
| 3 | Abrí **Salida** (enlace del ticket o `/salida?t=...`) | Se muestra tiempo estimado y monto; botón **Pagar con Mercado Pago** |
| 4 | Pulsar **Pagar con Mercado Pago** | Redirección a página de éxito simulada (`/pago/exito?...&mock=1`) y luego a salida con token |
| 5 | Con pago simulado, **Abrir barrera** | Mensaje de salida autorizada |
| 6 | Intentar **Salida** otra vez con el mismo token | Mensaje de que ya saliste (no autoriza de nuevo) |
| 7 | `GET http://localhost:8000/health` | `{"status":"ok"}` |
| 8 | `GET http://localhost:8000/ready` | `{"status":"ready"}` (requiere DB) |

## 5. Mercado Pago real (sandbox)

1. Obtené un **access token** de prueba desde tu cuenta Mercado Pago.
2. Configurá `MERCADOPAGO_ACCESS_TOKEN` y `MOCK_PAYMENTS=false` en el entorno del servicio `api`.
3. Reiniciá el contenedor `api`.
4. Repetí el flujo de pago: debería abrirse el checkout real de sandbox.

Los **webhooks** en local requieren una URL pública (ngrok, Cloudflare Tunnel, etc.) apuntando a `POST /api/v1/webhooks/mercadopago`.

## 6. Firmware ESP32

1. Copiá `firmware/esp32/src/config.local.h` con `WIFI_SSID`, `WIFI_PASS`, `API_BASE_URL` (IP de tu PC en la LAN) y `DEVICE_ID`.
2. Compilá y subí con PlatformIO.
3. Verificá en la API `GET /api/v1/devices/<device_id>` que actualiza `last_heartbeat_at` tras los heartbeats.

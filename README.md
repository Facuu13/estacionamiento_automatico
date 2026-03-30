# Estacionamiento automático (QR + Mercado Pago + ESP32)

Monorepo: **FastAPI + PostgreSQL**, **Next.js** (mobile-first), **firmware ESP32** (heartbeat y relé).

## Requisitos

- Docker y Docker Compose (recomendado), o PostgreSQL 16+ local.
- Node.js 20+ (solo si desarrollás frontend sin Docker).
- Python 3.12+ (solo si desarrollás backend sin Docker).

## Arranque rápido con Docker

```bash
docker compose up --build -d
```

- API: `http://localhost:8000` (documentación OpenAPI: `/docs`)
- Web: `http://localhost:3000`
- PostgreSQL: puerto `5432`

Variables: copiá [`.env.example`](.env.example) a `.env` y ajustá si hace falta.

## Backend sin Docker

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL=postgresql://parking:parking_dev@localhost:5432/parking
export MOCK_PAYMENTS=true
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend sin Docker

```bash
cd frontend
npm install
export NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

## Tests automáticos

Con PostgreSQL en marcha (por ejemplo `docker compose up -d db`):

```bash
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
export DATABASE_URL=postgresql://parking:parking_dev@localhost:5432/parking
.venv/bin/alembic upgrade head
.venv/bin/pytest -q
```

E2E (UI) con API y web levantados:

```bash
cd frontend
npx playwright install
npm run test:e2e
```

## Documentación

- [Manual de usuario](docs/MANUAL_USUARIO.md)
- [Manual de pruebas](docs/MANUAL_PRUEBAS.md)

## Firmware ESP32

Ver [`firmware/esp32`](firmware/esp32): copiá `config.local.h` con WiFi, URL del API y el mismo `DEVICE_HMAC_SECRET` que el backend. Tras **Abrir barrera** en la web, el ESP32 recibe un comando firmado en el heartbeat, pulsa el **LED** y el **relé** (`RELAY_PIN`), y envía ACK.

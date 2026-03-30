from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import devices, devtools, entry, exit, health, payments, sessions, webhooks
from app.config import get_settings

settings = get_settings()
origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]

app = FastAPI(
    title="Estacionamiento QR API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(entry.router)
app.include_router(sessions.router)
app.include_router(payments.router)
app.include_router(webhooks.router)
app.include_router(exit.router)
app.include_router(devices.router)
app.include_router(devtools.router)

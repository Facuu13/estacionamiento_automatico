# Firmware ESP32 (Arduino / PlatformIO)

## Qué hace (MVP)

- Conexión WiFi.
- **Heartbeat** HTTP cada 30 s hacia `POST /api/v1/devices/{DEVICE_ID}/heartbeat`.
- Pin de **relé** definido en `RELAY_PIN` (función `pulseRelay` lista para enlazar con comando remoto).

## Configuración

1. Copiá `src/config.local.h` (no versionar) con:

```cpp
#define WIFI_SSID "tu_red"
#define WIFI_PASS "tu_clave"
#define API_BASE_URL "http://IP_DE_TU_PC:8000"
#define DEVICE_ID "gate-01"
```

2. Compilá y subí:

```bash
cd firmware/esp32
pio run -t upload
```

## OTA

Este MVP deja la estructura lista para añadir actualización OTA (por ejemplo `HTTPUpdate` de ESP32) apuntando a un artefacto firmado servido por tu backend; no está cableado para no requerir certificados y URLs de producción.

## 4G

Para fallback 4G hace falta un módulo externo (SIM7600, etc.) y una capa serial/PPP; no está incluida en este ejemplo.

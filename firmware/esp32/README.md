# Firmware ESP32 (Arduino / PlatformIO)

## Qué hace (MVP)

- Conexión WiFi.
- **Heartbeat** HTTP cada 30 s hacia `POST /api/v1/devices/{DEVICE_ID}/heartbeat`.
- Pin de **relé** definido en `RELAY_PIN` (función `pulseRelay` lista para enlazar con comando remoto).

## Configuración

1. Copiá `src/config.local.h` (no versionar; ya está en `.gitignore`) con tu WiFi y la IP de tu PC donde corre la API.

2. **Compilar y subir al ESP32** (con el USB conectado y el driver del puerto serie instalado):

```bash
cd firmware/esp32
python3 -m venv .pio-venv
.pio-venv/bin/pip install platformio
.pio-venv/bin/pio run -t upload
```

Si `pio` no encuentra el puerto: `ls /dev/ttyUSB* /dev/ttyACM*` y `pio run -t upload --upload-port /dev/ttyUSB0`.

3. Monitor serie (115200 baud) para ver WiFi y heartbeats:

```bash
.pio-venv/bin/pio device monitor -b 115200
```

## OTA

Este MVP deja la estructura lista para añadir actualización OTA (por ejemplo `HTTPUpdate` de ESP32) apuntando a un artefacto firmado servido por tu backend; no está cableado para no requerir certificados y URLs de producción.

## 4G

Para fallback 4G hace falta un módulo externo (SIM7600, etc.) y una capa serial/PPP; no está incluida en este ejemplo.

#pragma once

/** Valores por defecto; sobreescribir con config.local.h (incluilo antes de este archivo). */

#ifndef WIFI_SSID
#define WIFI_SSID "tu_red"
#endif

#ifndef WIFI_PASS
#define WIFI_PASS "tu_clave"
#endif

#ifndef API_BASE_URL
#define API_BASE_URL "http://192.168.1.100:8000"
#endif

#ifndef DEVICE_ID
#define DEVICE_ID "gate-01"
#endif

/** Debe ser idéntico a DEVICE_HMAC_SECRET del backend (docker-compose / .env). */
#ifndef DEVICE_HMAC_SECRET
#define DEVICE_HMAC_SECRET "dev_cambiar_en_produccion_minimo_32_chars_xx"
#endif

/** Relé externo (active-high = ON). */
#ifndef RELAY_PIN
#define RELAY_PIN 4
#endif

#ifndef HEARTBEAT_INTERVAL_MS
#define HEARTBEAT_INTERVAL_MS 3000
#endif

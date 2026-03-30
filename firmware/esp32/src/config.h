#pragma once

// Copiar a config.local.h (no versionar) o definir por build_flags.
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

#ifndef RELAY_PIN
#define RELAY_PIN 4
#endif

#ifndef HEARTBEAT_INTERVAL_MS
#define HEARTBEAT_INTERVAL_MS 30000
#endif

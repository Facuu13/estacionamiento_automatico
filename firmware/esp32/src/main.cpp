/**
 * WiFi + heartbeat con comando PULSE firmado (HMAC-SHA256).
 * LED integrado + RELAY_PIN pulsan juntos para simular barrera.
 */
#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <mbedtls/md.h>

#if __has_include("config.local.h")
#include "config.local.h"
#endif
#include "config.h"

static unsigned long lastHb = 0;
/** Evita repetir pulso si el servidor aún no marcó ACK (mismo command id). */
static String lastExecutedCommandId;

static void hexFromBytes(const uint8_t *data, size_t len, char *outHex) {
  static const char *hex = "0123456789abcdef";
  for (size_t i = 0; i < len; i++) {
    outHex[i * 2] = hex[(data[i] >> 4) & 0x0f];
    outHex[i * 2 + 1] = hex[data[i] & 0x0f];
  }
  outHex[len * 2] = 0;
}

static bool hmacSha256Hex(const char *key, const char *message, char *outHex65) {
  uint8_t mac[32];
  mbedtls_md_context_t ctx;
  const mbedtls_md_info_t *md = mbedtls_md_info_from_type(MBEDTLS_MD_SHA256);
  mbedtls_md_init(&ctx);
  if (mbedtls_md_setup(&ctx, md, 1) != 0) {
    mbedtls_md_free(&ctx);
    return false;
  }
  if (mbedtls_md_hmac_starts(&ctx, reinterpret_cast<const unsigned char *>(key), strlen(key)) != 0) {
    mbedtls_md_free(&ctx);
    return false;
  }
  if (mbedtls_md_hmac_update(&ctx, reinterpret_cast<const unsigned char *>(message), strlen(message)) != 0) {
    mbedtls_md_free(&ctx);
    return false;
  }
  if (mbedtls_md_hmac_finish(&ctx, mac) != 0) {
    mbedtls_md_free(&ctx);
    return false;
  }
  mbedtls_md_free(&ctx);
  hexFromBytes(mac, 32, outHex65);
  return true;
}

static bool constantTimeEq(const char *a, const char *b) {
  if (strlen(a) != 64 || strlen(b) != 64) return false;
  unsigned diff = 0;
  for (int i = 0; i < 64; i++) diff |= (unsigned char)(a[i] ^ b[i]);
  return diff == 0;
}

void setupPins() {
#ifdef LED_BUILTIN
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
#endif
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
}

/** Simula apertura: LED encendido + relé ON, luego cierre. LED activo en bajo en muchas ESP32. */
void pulseGate(unsigned long ms) {
#ifdef LED_BUILTIN
  digitalWrite(LED_BUILTIN, LOW);
#endif
  digitalWrite(RELAY_PIN, HIGH);
  delay(ms);
#ifdef LED_BUILTIN
  digitalWrite(LED_BUILTIN, HIGH);
#endif
  digitalWrite(RELAY_PIN, LOW);
}

void connectWifi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("WiFi");
  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 60) {
    delay(500);
    Serial.print(".");
    retries++;
  }
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("WiFi falló");
  }
}

bool postCommandAck(const String &cmdId) {
  HTTPClient http;
  String url = String(API_BASE_URL) + "/api/v1/devices/" + DEVICE_ID + "/commands/" + cmdId + "/ack";
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  int code = http.POST("{}");
  http.end();
  return code >= 200 && code < 300;
}

bool sendHeartbeatAndProcess() {
  if (WiFi.status() != WL_CONNECTED) return false;

  HTTPClient http;
  String url = String(API_BASE_URL) + "/api/v1/devices/" + DEVICE_ID + "/heartbeat";
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  int rssi = WiFi.RSSI();
  String body = "{\"firmware_version\":\"0.2.0\",\"rssi\":" + String(rssi) + "}";
  int code = http.POST(body);
  String resp = http.getString();
  http.end();

  if (code < 200 || code >= 300) {
    Serial.printf("heartbeat HTTP %d\n", code);
    return false;
  }

  JsonDocument doc;
  DeserializationError err = deserializeJson(doc, resp);
  if (err) {
    Serial.println("JSON inválido");
    return true;
  }

  JsonObject cmd = doc["command"];
  if (cmd.isNull()) {
    return true;
  }

  const char *cid = cmd["id"] | "";
  const char *nonce = cmd["nonce"] | "";
  long long ts = cmd["ts"] | 0LL;
  int seconds = cmd["seconds"] | 5;
  const char *sigHex = cmd["signature"] | "";

  if (!strlen(cid) || !strlen(nonce) || ts == 0 || !strlen(sigHex)) {
    return true;
  }

  if (lastExecutedCommandId == String(cid)) {
    for (int i = 0; i < 5; i++) {
      if (postCommandAck(String(cid))) {
        Serial.println("ack reintento ok");
        break;
      }
      delay(300);
    }
    return true;
  }

  char msg[192];
  snprintf(msg, sizeof(msg), "PULSE:%s:%s:%lld", DEVICE_ID, nonce, (long long)ts);

  char calc[65];
  if (!hmacSha256Hex(DEVICE_HMAC_SECRET, msg, calc)) {
    Serial.println("HMAC falló");
    return true;
  }

  if (!constantTimeEq(calc, sigHex)) {
    Serial.println("Firma inválida");
    return true;
  }

  unsigned long ms = (unsigned long)seconds * 1000UL;
  if (ms < 200) ms = 200;
  if (ms > 60000) ms = 60000;

  lastExecutedCommandId = String(cid);

  Serial.printf("PULSE %lums cmd=%s\n", ms, cid);
  pulseGate(ms);

  for (int i = 0; i < 10; i++) {
    if (postCommandAck(String(cid))) {
      Serial.println("ack ok");
      break;
    }
    delay(200);
  }

  return true;
}

void setup() {
  Serial.begin(115200);
  delay(200);
  setupPins();
  connectWifi();
}

void loop() {
  unsigned long now = millis();
  if (now - lastHb >= HEARTBEAT_INTERVAL_MS) {
    lastHb = now;
    if (!sendHeartbeatAndProcess()) {
      Serial.println("heartbeat falló");
    }
  }
  delay(50);
}

/**
 * Firmware demo: WiFi, heartbeat HTTP, relé, estructura para OTA.
 * Ajustar config.h o crear config.local.h con credenciales reales.
 */
#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>

#include "config.h"

#if __has_include("config.local.h")
#include "config.local.h"
#endif

static unsigned long lastHb = 0;

void setupRelay() {
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
}

void pulseRelay(unsigned ms) {
  digitalWrite(RELAY_PIN, HIGH);
  delay(ms);
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

bool sendHeartbeat() {
  if (WiFi.status() != WL_CONNECTED) return false;
  HTTPClient http;
  String url = String(API_BASE_URL) + "/api/v1/devices/" + DEVICE_ID + "/heartbeat";
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  int rssi = WiFi.RSSI();
  String body = "{\"firmware_version\":\"0.1.0\",\"rssi\":" + String(rssi) + "}";
  int code = http.POST(body);
  http.end();
  return code >= 200 && code < 300;
}

void setup() {
  Serial.begin(115200);
  delay(200);
  setupRelay();
  connectWifi();
}

void loop() {
  unsigned long now = millis();
  if (now - lastHb >= HEARTBEAT_INTERVAL_MS) {
    lastHb = now;
    if (!sendHeartbeat()) {
      Serial.println("heartbeat falló");
    } else {
      Serial.println("heartbeat ok");
    }
  }
  delay(50);
}

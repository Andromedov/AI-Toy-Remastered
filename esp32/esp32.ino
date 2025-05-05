#include "config.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <AudioFileSourceICYStream.h>
#include <AudioGeneratorMP3.h>
#include <AudioOutputI2S.h>

const char* ssid = WIFI_SSID;
const char* password = WIFI_PASSWORD;
const char* serverUrl = API_URL;

AudioGeneratorMP3 *mp3;
AudioFileSourceICYStream *file;
AudioOutputI2S *out;

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("🔌 Підключення до WiFi...");
  WiFi.begin(ssid, password);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi підключено!");
    Serial.print("IP адреса: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n❌ Помилка підключення до WiFi.");
  }

  // Надсилаємо POST-запит
  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");
  int httpCode = http.POST("{\"question\":\"Хто такий тигр?\"}");

  if (httpCode == 200) {
    Serial.println("Отримано аудіо, починаємо програвання...");

    file = new AudioFileSourceICYStream(http.getStreamPtr());
    out = new AudioOutputI2S();
    mp3 = new AudioGeneratorMP3();

    mp3->begin(file, out);
  } else {
    Serial.printf("❌ Помилка HTTP: %d\n", httpCode);
  }
}

void loop() {
  if (mp3 && mp3->isRunning()) {
    mp3->loop();
  }
}

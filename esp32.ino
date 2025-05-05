#include <WiFi.h>
#include <HTTPClient.h>
#include <AudioFileSourceICYStream.h>
#include <AudioGeneratorMP3.h>
#include <AudioOutputI2S.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverUrl = "http://YOUR_PC_IP:5000/ask";  // Заміни на IP твоєї машини з Flask

AudioGeneratorMP3 *mp3;
AudioFileSourceICYStream *file;
AudioOutputI2S *out;

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi підключено");

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

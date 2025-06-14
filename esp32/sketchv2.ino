#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <WebServer.h>
#include <driver/i2s.h>

#define BUTTON_PIN 0
#define LED_PIN 2
#define MIC_PIN 15
#define BUZZER_PIN 13

String ssid = "Wokwi-GUEST";
String password = "";
String email = "";
String user_password = "";
String apiKey = "";
String jwtToken = "";

String serverUrl = "http://5.58.240.18:5000";

WebServer server(80);
bool apMode = true;
bool configReceived = false;

#define SAMPLE_RATE 16000
#define I2S_WS 25
#define I2S_SD 33
#define I2S_SCK 32
#define AUDIO_BUFFER_SIZE 8000

void setupI2SMic() {
  i2s_config_t i2s_config = {
    .mode = i2s_mode_t(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S_MSB,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 4,
    .dma_buf_len = 1024,
    .use_apll = false
  };

  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = -1,
    .data_in_num = I2S_SD
  };

  i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_NUM_0, &pin_config);
}

void setup() {
  Serial.begin(115200);

  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  setupI2SMic();

  // Створення точки доступу
  WiFi.softAP("TeddyAI-Setup", "12345678");
  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP адреса: ");
  Serial.println(IP);

  server.on("/", HTTP_GET, []() {
    server.send(200, "text/html", "<form method='POST' action='/setup'>\
      SSID: <input name='ssid'><br>\
      Password: <input name='pass'><br>\
      Email/User: <input name='email'><br>\
      Password: <input name='pwd'><br>\
      <input type='submit'></form>");
  });

  server.on("/setup", HTTP_POST, []() {
    ssid = server.arg("ssid");
    password = server.arg("pass");
    email = server.arg("email");
    user_password = server.arg("pwd");

    server.send(200, "text/html", "Конфігурація отримана. Перезапуск...");

    apMode = false;
  });

  server.begin();
  Serial.println("HTTP сервер запущено.");
}


void loop() {
  if (apMode) {
    server.handleClient();
    return;
  }

  // З'єднання з Wi-Fi після AP режиму
  if (!configReceived) {
    if (connectToWiFi() && loginToServer() && fetchCredentialsFromServer()) {
      configReceived = true;
      Serial.println("✅ Готово до роботи після конфігурації!");
    } else {
      Serial.println("❌ Невдало. Повертаємось у AP режим.");
      apMode = true;
      WiFi.softAP("TeddyAI-Setup", "12345678");
      return;
    }
  }

  if (configReceived && digitalRead(BUTTON_PIN) == LOW) {
    digitalWrite(LED_PIN, HIGH);
    Serial.println("Кнопка натиснута, запис...");
    recordAndSendAudio();
    digitalWrite(LED_PIN, LOW);
    delay(1000);
  }

  delay(50);
}

void parseSerialLine(String line) {
  line.trim();
  if (line.startsWith("SSID:")) {
    ssid = line.substring(6);
  } else if (line.startsWith("PASS:")) {
    password = line.substring(6);
  } else if (line.startsWith("EMAIL:")) {
    email = line.substring(6);
  } else if (line.startsWith("USER:")) {
    email = line.substring(6);
  } else if (line.startsWith("PWD:")) {
    user_password = line.substring(4);
  }

  if (email != "" && user_password != "" && !configReceived) {
    connectToWiFi();
    if (loginToServer()) {
      if (fetchCredentialsFromServer()) {
        configReceived = true;
        Serial.println("✅ Готово до роботи!");
      } else {
        Serial.println("❌ Не вдалося отримати збережені налаштування.");
      }
    } else {
      Serial.println("❌ Логін не вдався.");
    }
  }
}

bool connectToWiFi() {
  WiFi.begin(ssid.c_str(), password.c_str());
  Serial.print("З’єднання з WiFi");

  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 20) {
      delay(500);
      Serial.print(".");
      tries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
      Serial.println("\n✅ WiFi з’єднано.");
      return true;
  } else {
      Serial.println("\n❌ З’єднання з WiFi не вдалося.");
      return false;
  }
}


bool loginToServer() {
  if (WiFi.status() != WL_CONNECTED) return false;

  HTTPClient http;
  http.begin(serverUrl + "/login");
  http.addHeader("Content-Type", "application/json");

  String body = "{\"email\": \"" + email + "\", \"password\": \"" + user_password + "\"}";
  int httpResponseCode = http.POST(body);

  if (httpResponseCode == 200) {
    String response = http.getString();
    Serial.println("✅ Відповідь логіну: " + response);

    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, response);
    if (error) {
      Serial.println("❌ JSON помилка: " + String(error.c_str()));
      return false;
    }

    if (doc.containsKey("token")) {
      jwtToken = doc["token"].as<String>();
      Serial.println("🔐 Отримано JWT токен.");
      http.end();
      return true;
    } else {
      Serial.println("❌ Токен не знайдено в JSON.");
    }
  } else {
    Serial.println("❌ Логін не вдався: " + String(httpResponseCode));
    Serial.println(http.getString());
  }

  http.end();
  return false;
}

void recordAndSendAudio() {
  if (WiFi.status() != WL_CONNECTED || jwtToken == "") return;

  const int maxSilentBuffers = 5;
  const int amplitudeThreshold = 50; // 🔽 зменшено з 500 до 50
  const int bufferChunkSize = 2048;

  uint8_t* fullBuffer = (uint8_t*)malloc(AUDIO_BUFFER_SIZE);
  int fullBufferOffset = 0;

  uint8_t* tempBuffer = (uint8_t*)malloc(bufferChunkSize);
  size_t bytesRead;
  int silentCounter = 0;

  Serial.println("🎙️ Починаємо запис...");

  unsigned long startTime = millis();
  const unsigned long maxRecordingTime = 10000; // 🔁 watchdog на 10 сек

  while (fullBufferOffset + bufferChunkSize < AUDIO_BUFFER_SIZE) {
    if (millis() - startTime > maxRecordingTime) {
      Serial.println("\n⏱️ Досягнуто максимального часу запису. Завершення.");
      break;
    }

    i2s_read(I2S_NUM_0, tempBuffer, bufferChunkSize, &bytesRead, portMAX_DELAY);

    int16_t* samples = (int16_t*)tempBuffer;
    int sampleCount = bytesRead / 2;
    int peak = 0;

    for (int i = 0; i < sampleCount; i++) {
      int16_t val = abs(samples[i]);
      if (val > peak) peak = val;
    }

    Serial.printf("🔎 Амплітуда: %d\n", peak);

    if (peak < amplitudeThreshold) {
      silentCounter++;
      Serial.println("... тиша");
    } else {
      silentCounter = 0;
      Serial.println("🔊 звук!");
    }

    if (silentCounter >= maxSilentBuffers) {
      Serial.println("🛑 Виявлено тривалу тишу. Зупиняємось.");
      break;
    }

    memcpy(fullBuffer + fullBufferOffset, tempBuffer, bytesRead);
    fullBufferOffset += bytesRead;

    delay(100);
  }

  free(tempBuffer);

  Serial.printf("📦 Надсилаємо %d байт аудіо...\n", fullBufferOffset);

  HTTPClient http;
  http.begin(serverUrl + "/upload_audio");
  http.addHeader("Content-Type", "application/octet-stream");
  http.addHeader("Authorization", "Bearer " + jwtToken);

  int httpResponseCode = http.sendRequest("POST", fullBuffer, fullBufferOffset);
  free(fullBuffer);

  if (httpResponseCode > 0) {
    Serial.println("📨 Відповідь від сервера:");
    Serial.println(http.getString());
    tone(BUZZER_PIN, 1000, 150);
  } else {
    Serial.println("❌ Помилка запиту: " + String(httpResponseCode));
  }

  http.end();
}

bool fetchCredentialsFromServer() {
  if (WiFi.status() != WL_CONNECTED || jwtToken == "") return false;

  HTTPClient http;
  http.begin(serverUrl + "/get_credentials");
  http.addHeader("Authorization", "Bearer " + jwtToken);

  int httpResponseCode = http.GET();

  if (httpResponseCode == 200) {
    String response = http.getString();
    Serial.println("🔑 Отримано конфігурацію: " + response);

    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, response);
    if (error) {
      Serial.println("❌ JSON помилка: " + String(error.c_str()));
      return false;
    }

    apiKey = doc["api_key"].as<String>();
    ssid = doc["ssid"].as<String>();
    password = doc["password"].as<String>();

    Serial.println("➡️ SSID: " + ssid);
    Serial.println("➡️ KEY: " + apiKey);

    http.end();
    return true;
  } else {
    Serial.println("❌ Помилка /get_credentials: " + String(httpResponseCode));
    Serial.println(http.getString());
  }

  http.end();
  return false;
}
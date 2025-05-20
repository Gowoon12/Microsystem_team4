#include <WiFi.h>

const char* ssid = "meric_B101";
const char* password = "meric160816";

const char* serverIP = "192.168.31.144"; // 🔶 노트북의 IP 주소
const int port = 1234;

WiFiClient client;

const int pinA0 = 35;
const int pinA1 = 33;
const float Vin = 3.3;

unsigned long previousMillis = 0;
const long interval = 1000 / 240;  // 240Hz

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  Serial.println("Connecting to Wi-Fi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi connected");

  // 서버에 연결 시도
  while (!client.connect(serverIP, port)) {
    Serial.println("Connecting to server...");
    delay(1000);
  }
  Serial.println("Connected to server.");
}

void loop() {
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    int rawA0 = analogRead(pinA0);
    int rawA1 = analogRead(pinA1);

    float VoutPlus = (rawA1 / 4095.0) * Vin;
    float VoutMinus = (rawA0 / 4095.0) * Vin;
    float Vout = VoutPlus - VoutMinus;

    if (client.connected()) {
      client.println(Vout, 6);  // 소수점 6자리로 전송
      Serial.println(Vout, 6);
    } else {
      Serial.println("Disconnected from server.");
    }
  }
}

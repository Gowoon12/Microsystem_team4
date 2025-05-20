#include <WiFi.h>

const char* ssid = "meric_B101";
const char* password = "meric160816"; 

const char* serverIP = "192.168.31.144"; // IP address of the server (Laptop)
const int port = 1235;

WiFiClient client;

const int pinA0 = 35;
const int pinA1 = 33;
const float Vin = 3.3;

unsigned long previousMillis = 0;
const long interval = 1000 / 240;  // 240Hz sampling rate

// ESP32 unique ID (Board 1 is 1, Board 2 is 2)
const int esp32_id = 2;  // First board sets ID to 1, second to 2

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  Serial.println("Connecting to Wi-Fi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi connected");

  // Attempt to connect to the server
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
      // Sending Vout and ESP32 ID
      client.println(String(esp32_id) + "," + String(Vout, 6));  // Send ID and Vout
      Serial.println("Sent: " + String(esp32_id) + "," + String(Vout, 6));
    } else {
      Serial.println("Disconnected from server.");
    }
  }  
}

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

#define SERVICE_UUID        "12345678-1234-1234-1234-123456789abc"
#define CHARACTERISTIC_UUID "abcd1234-ab12-cd34-ef56-1234567890ab"

BLECharacteristic *pCharacteristic;
bool deviceConnected = false;

const int pinA0 = 35; // GPIO36 (ADC1_CH0)
const int pinA1 = 33; // GPIO33 (ADC1_CH5)
const float Vin = 3.3;

unsigned long previousMillis = 0;
const long interval = 1000 / 240;  // 240Hz 전송 주기

class MyServerCallbacks: public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) {
    deviceConnected = true;
  };
  void onDisconnect(BLEServer* pServer) {
    deviceConnected = false;
  }
};

void setup() {
  Serial.begin(115200);
  BLEDevice::init("ESP32_BLE_TX_Sensor");
  BLEServer *pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  BLEService *pService = pServer->createService(SERVICE_UUID);

  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_NOTIFY
                    );
  pCharacteristic->addDescriptor(new BLE2902());

  pService->start();

  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->start();

  Serial.println("BLE Peripheral started, waiting for client...");
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

  if (deviceConnected) {
    pCharacteristic->setValue((uint8_t*)&Vout, sizeof(float));  // float 그대로 전송
    pCharacteristic->notify();
    // Serial.print("Sent Vout: ");
    Serial.println(Vout, 8);
    // delayMicroseconds(10);
    }
  }
}

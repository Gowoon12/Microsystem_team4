#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(7, 8); // CE=7, CSN=8
const byte address[6] = "00001"; // 송수신 주소 설정

const int pinA0 = A0; // A0 핀: 브릿지의 한 쪽 전압
const int pinA1 = A5; // A1 핀: 브릿지의 다른 쪽 전압
const float Vin = 1; // 입력 전압 (5V)

unsigned long previousMillis = 0;  // 마지막 샘플링 시간
const long interval = 1000 / 240;  // 120Hz 샘플링 주기 (약 8.33ms)

void setup() {
  Serial.begin(1000000);  // 시리얼 모니터 초기화

  // ADC 레지스터를 직접 수정하여 12비트 해상도 설정
  ADMUX = (1 << MUX0);  // AREF = AVcc, 12비트 모드 설정
  ADCSRA |= (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0); // ADC 분주기 설정 (최적 분주기)

  // NRF24L01 초기화
  radio.begin();       // 라디오 초기화
  radio.openWritingPipe(address); // 수신부 주소 설정
  radio.setPALevel(RF24_PA_LOW);  // 낮은 출력 전력으로 설정
  radio.stopListening();  // 송신 모드 설정

  Serial.println("Transmitter Ready");
}

void loop() {
  unsigned long currentMillis = millis();

  // 120Hz 샘플링 주기를 맞추기 위한 코드
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;  // 마지막 샘플링 시간 업데이트

    // A0, A1에서 전압 읽기 (12비트 해상도)
    int rawA0 = analogRead(pinA0);  // A0에서 12비트 해상도로 값 읽기
    int rawA1 = analogRead(pinA1);  // A1에서 12비트 해상도로 값 읽기

    // 아날로그 값을 전압으로 변환 (0 ~ 4095 범위)
    float VoutPlus = (rawA1 / 4095.0) * Vin;  // 12비트 해상도
    float VoutMinus = (rawA0 / 4095.0) * Vin; 
    // float VoutPlus = (rawA1 / 1024.0) * Vin;  // 12비트 해상도
    // float VoutMinus = (rawA0 / 1024.0) * Vin; 

    // 출력 전압 차이 계산
    float Vout = VoutPlus - VoutMinus;
    // float Vout = VoutPlus;

    // Vout 값을 송신
    radio.write(&Vout, sizeof(Vout));  // Vout 송신

    // 시리얼로 Vout 출력
    Serial.println(Vout, 8);  // 소수점 8자리까지 출력
  }
}
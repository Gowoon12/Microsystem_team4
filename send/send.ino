#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(7, 8); // CE=7, CSN=8
const byte address[6] = "00001"; // 송수신 주소 설정

const int pinA0 = A0; // A0 핀: 브릿지의 한 쪽 전압
const int pinA1 = A1; // A1 핀: 브릿지의 다른 쪽 전압
const float Vin = 5.0; // 입력 전압 (5V)
const float R1 = 1000.0; // R1 (1kΩ)
const float R2 = 1000.0; // R2 (1kΩ)
const float R3 = 1000.0; // R3 (1kΩ)

void setup() {
  Serial.begin(9600);  // 시리얼 모니터 초기화
  radio.begin();       // 라디오 초기화

  if (!radio.begin()) {
    Serial.println("NRF24L01 Initialization Failed!");
    while (1); // 초기화 실패 시 멈춤
  }

  radio.openWritingPipe(address); // 수신부 주소 설정
  radio.setPALevel(RF24_PA_LOW);  // 낮은 출력 전력으로 설정
  radio.stopListening();  // 송신 모드 설정
  Serial.println("Transmitter Ready");
}

void loop() {
  // A0, A1에서 전압 읽기
  int rawA0 = analogRead(pinA0);
  int rawA1 = analogRead(pinA1);
  
  // 아날로그 값을 전압 값으로 변환
  float VoutPlus = (rawA1 / 1023.0) * Vin;
  float VoutMinus = (rawA0 / 1023.0) * Vin;
  
  // 출력 전압 차이 계산
  float Vout = VoutPlus - VoutMinus;

  // R4 계산 (휘스톤 브릿지 공식을 이용한 계산)
  float R4;
  if (Vout != 0) {
    R4 = R3 / ((Vout / Vin) + (R1 / R2) - 1); // 휘스톤 브릿지 공식을 이용한 R4 계산
  } else {
    R4 = R3; // 균형 상태에서 R4가 R3과 같을 경우
  }

  // Vout, R4 값을 송신
  radio.write(&Vout, sizeof(Vout));  // Vout 송신
  radio.write(&R4, sizeof(R4));  // R4 송신

  // 시리얼로 Vout, R4 값 출력
  Serial.print("Vout: ");
  Serial.print(Vout, 3);  // 소수점 3자리까지 출력
  Serial.print("  R4: ");
  Serial.println(R4, 3);  // 소수점 3자리까지 출력

  delay(100); // 100ms 대기
}

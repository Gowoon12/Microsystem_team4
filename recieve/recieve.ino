#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(7, 8); // CE=7, CSN=8
const byte address[6] = "00001"; // 송수신 주소 설정

float Vout = 0.0;
float R4 = 0.0;

void setup() {
  Serial.begin(9600);  // 시리얼 모니터 초기화
  radio.begin();       // 라디오 초기화

  if (!radio.begin()) {
    Serial.println("NRF24L01 Initialization Failed!");
    while (1); // 초기화 실패 시 멈춤
  }

  radio.openReadingPipe(1, address); // 수신부 주소 설정
  radio.setPALevel(RF24_PA_LOW);     // 낮은 출력 전력으로 설정
  radio.startListening();            // 수신 모드 설정
  Serial.println("Receiver Ready");
}

void loop() {
  // 데이터 수신 확인
  if (radio.available()) {
    // 수신한 데이터 읽기
    radio.read(&Vout, sizeof(Vout));  // Vout 값 수신
    radio.read(&R4, sizeof(R4));      // R4 값 수신

    // 수신한 값 출력
    // Serial.print("Recieved Vout: ");
    // Serial.print(Vout, 3); // 소수점 3자리까지 출력
    // Serial.print(" R4: ");
    // Serial.println(R4, 3); // 소수점 3자리까지 출력


    Serial.print(Vout, 3); // 소수점 3자리까지 출력
    Serial.print(",");
    Serial.println(R4, 3); // 소수점 3자리까지 출력
  }

  delay(100); // 100ms 대기
}

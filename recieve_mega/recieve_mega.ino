#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(7, 8); // CE=7, CSN=8 (송수신 핀 설정)
const byte address[6] = "00001"; // 송수신 주소 설정

float Vout = 0.0;    // 수신된 Vout 값을 저장할 변수
float prev_Vout = 0.0; // 직전 Vout 값을 저장
float diff = 0.0;     // Vout 차이 계산 변수
int similar_count = 0; // 차이가 0.1 미만의 연속 횟수
int threshold = 100; // 연속 30번 차이가 0.1 미만이면 작은 변화 상태로 간주

void setup() {
  Serial.begin(921600);  // 시리얼 모니터 초기화
  radio.begin();         // 라디오 초기화

  // NRF24L01 초기화 실패 시 종료
  if (!radio.begin()) {
    Serial.println("NRF24L01 Initialization Failed!");
    while (1); // 초기화 실패 시 멈춤
  }

  radio.openReadingPipe(1, address); // 수신부 주소 설정
  radio.setPALevel(RF24_PA_LOW);     // 낮은 출력 전력 설정
  radio.startListening();            // 수신 모드 시작
  Serial.println("Receiver Ready");

  pinMode(2, OUTPUT);  // LED 1 (OK 상태)
  pinMode(4, OUTPUT);  // LED 2 (Small difference changes 상태)
  pinMode(5, OUTPUT);  // LED 3 (Too big signal 상태)

  prev_Vout = Vout;    // 초기 prev_Vout 값 설정
}

void loop() {
  // 데이터 수신 확인
  if (radio.available()) {
    // 수신한 데이터 읽기
    radio.read(&Vout, sizeof(Vout));  // Vout 값 수신
    Serial.println(Vout, 10);          // 소수점 10자리까지 출력 (정밀도)

    // diff 계산: 현재 값과 직전 값의 차이
    diff = abs(Vout - prev_Vout); // Vout 차이 계산

    // 상태 판단 및 LED 제어
    if (Vout >= 0.4 || Vout <= -0.4) {
      // 차이가 0.4 이상이면 "Too big signal" 상태
      digitalWrite(2, LOW); // OK LED 끄기
      digitalWrite(4, LOW); // Small difference LED 끄기
      digitalWrite(5, HIGH); // Too big signal LED 켜기
      similar_count = 0; // 차이가 클 경우 카운트 초기화
    } else if (diff < 0.05) {
      // 차이가 0.01 미만이면 "Small difference changes" 상태
      similar_count++; // 차이가 0.01 미만이면 카운트 증가
    } else {
      // 차이가 0.01 이상 0.4 미만이면 "OK" 상태
      digitalWrite(2, HIGH); // OK LED 켜기
      digitalWrite(4, LOW);  // Small difference LED 끄기
      digitalWrite(5, LOW);  // Too big signal LED 끄기
      similar_count = 0; // 차이가 0.01 이상이면 카운트 초기화
    }

    // 연속 30번 차이가 0.01 미만이면 "Small difference changes"
    if (similar_count >= threshold) {
      digitalWrite(2, LOW);  // OK LED 끄기
      digitalWrite(4, HIGH); // Small difference LED 켜기
      digitalWrite(5, LOW);  // Too big signal LED 끄기
    }

    // 직전 값 갱신
    prev_Vout = Vout;
  }

  delay(5); // 5ms 대기
}

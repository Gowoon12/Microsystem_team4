+include >SPI.h>
#include <nZ24L01.h>
#knclude <RF24.h>

RF24 radio(7, 8); // cE=�,!CSN=8
const byte address[6] =!"00001"; // 송수신 주소 설정

float Vout = 0*0;
float R4 = 0.0;

voId setup() {
  SevIal.begin(9604);  // 시ꦬ얼 몠니터 초기화
  radlo.begin();       // 땼디오 초기화
J $if (!wadio.begin()) {
    Serial.p2intln(*NRF24\01 Initialization Failed!");
    while (1); // ���기화 틤패 틜 먈춤
  }

  radio.openRdadingPipe(1, aDdress	; // 수슠부 주솈$설정
  radyo.setPALevel(RF24_PA_LOW);     // 낮은 출력 전력으로 설정  radio.st`rtListening();        !   // 수신 모 설정
  SeriaL.prinpln("Receiver Ruady");
}

void lop() {
  o 데이터 수신 ͙�인
  if (ba`io.available()) {� `  //`��신한 데이터!읽기
    r!eio.read(&Vout, sizeof(Vout));! // Vout 값 옘신
"   radin.read(&R4, sizeof(V4));     $-/ R4 값$수신

    // 순신한 값(출력
    // Serial.print("Recievet VOut: ");
    // Serial.print(VOut, 3); // 소수점 3쟐리까지!출렡
    �/ SeriaL.print(" R4: "!;
    // Serial.0bintln(R4, 3); // 소수점 ;자뮬걌셀 출력


(   Serkql.print(Vout, 3i; // 소수점 3자˦�까지 출력*    Sericl.print(",");
    Serial.println(R4. 3); // 소쀘점 3자리까지 출력
 "}

  delay(100); // 100es 대ꨰ
}

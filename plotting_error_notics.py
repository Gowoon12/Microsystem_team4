import sys
import os
import serial
import matplotlib.pyplot as plt
import csv
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
from datetime import datetime  # 날짜와 시간 처리용 모듈 추가

class RealTimePlot(QMainWindow):
    def __init__(self):
        super().__init__()

        # 시리얼 포트 초기화
        self.ser = serial.Serial('COM18', 921600, timeout=1)
        self.data = []  # 실시간 데이터를 저장할 리스트 (Vout)
        self.time = []  # X축 (시간) 리스트

        # 변수 추가: diff 계산 및 에러 표시
        self.diff = []  # diff 값을 저장할 리스트
        self.similar_count = 0  # 차이가 0.1 미만인 연속 횟수
        self.error_flag = False  # 에러 출력 여부
        self.status_text = "OK"  # 상태 텍스트 초기값

        # 지정된 경로와 현재 날짜/시간으로 파일명 생성
        directory = r'C:/Users/meric/Desktop/MS'
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.csv_file_path = os.path.join(directory, f'real_time_data_{current_time}.csv')

        # CSV 파일 설정 (헤더 포함)
        with open(self.csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Time', 'Vout', 'Status'])  # CSV 파일의 헤더

        # PyQt 윈도우 초기화
        self.setWindowTitle("Real-Time Data Plot")
        self.setGeometry(100, 100, 1600, 600)

        # Vout 그래프 설정
        self.figure, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], label="Vout", color='blue')
        self.ax.set_xlabel("Time") 
        self.ax.set_ylabel("Vout") 
        self.ax.legend(loc="upper left")
        self.ax.grid(True)
        self.ax.set_title("Measured Vout")  # 그래프 제목 추가

        # PyQt Layout 설정 (Vout 그래프)
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Timer 설정 (주기적으로 데이터를 갱신)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(10)  # 100ms마다 데이터 갱신

    def update_data(self):
        if self.ser.in_waiting > 0:
            # 시리얼 포트에서 데이터 읽기
            data = self.ser.readline().decode('utf-8').strip()

            try:
                # 데이터가 숫자로 변환될 수 있으면
                Vout = float(data)

                # 데이터를 실시간으로 업데이트
                self.data.append(Vout)
                self.time.append(len(self.time))  # 간단히 X축에 시간 인덱스를 사용

                # diff 계산: 현재 값과 직전 값의 차이
                if len(self.data) > 1:
                    diff = abs(self.data[-1] - self.data[-2])  # 차이값의 절대값
                    self.diff.append(diff)

                    # diff가 0.1 미만인 상태가 연속으로 10번 이상일 경우
                    if diff < 0.01:
                        self.similar_count += 1
                    else:
                        self.similar_count = 0  # 차이가 크면 카운트 초기화

                    # 연속된 10번 이상 차이값이 0.1 미만이면 "ERROR"
                    if self.similar_count >= 20 and not self.error_flag:
                        self.status_text = "ERROR: No changes"
                        self.error_flag = True  # 에러 출력 상태로 변경
                        
                    if abs(self.data[-1]) >= 0.4 and not self.error_flag:
                        self.status_text = "ERROR: Out of range"
                        self.error_flag = True  # 에러 출력 상태로 변경

                    # 차이가 0.1 이상으로 커지면 즉시 "OK"로 변경
                    if diff >= 0.01:
                        self.similar_count = 0  # diff가 0.1 이상이면 similar_count를 0으로 초기화
                        self.status_text = "OK"  # 차이가 다시 커지면 "OK"로 전환
                        self.error_flag = False  # 에러 출력 멈추기

                # 상태 텍스트 출력 (콘솔에 실시간으로 계속 출력)
                print(self.status_text)

                # Vout 그래프 업데이트
                self.line.set_data(self.time, self.data)

                # X축 범위 설정:
                self.ax.set_xlim(max(0, len(self.time) - 500), len(self.time))

                # Y축 범위 자동 조정
                self.ax.set_ylim(-1.5, 1.5)  # Y축 범위 설정 (-5에서 +5)

                # 그래프 그리기
                self.canvas.draw()

                # CSV 파일에 데이터 저장
                with open(self.csv_file_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([len(self.time), Vout, self.status_text])  # 실시간 데이터와 상태 저장

            except ValueError:
                pass  # 숫자가 아닌 데이터는 무시

    def closeEvent(self, event):
        self.ser.close()  # 프로그램 종료 시 시리얼 포트 닫기
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RealTimePlot()
    window.show()
    sys.exit(app.exec_())

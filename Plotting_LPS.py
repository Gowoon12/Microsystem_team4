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
        self.ser = serial.Serial('COM18', 9600, timeout=0.1)
        
        self.data = []  # 실시간 데이터를 저장할 리스트 (Vout)
        self.filtered_data = []  # 필터링된 데이터를 저장할 리스트
        self.time = []  # X축 (시간) 리스트

        # 로우 패스 필터 계수 (alpha: 0.1~0.9로 조정 가능)
        self.alpha = 0.3  # 필터의 강도를 나타내는 계수 (값을 조정하여 노이즈 수준 조절)

        # 지정된 경로와 현재 날짜/시간으로 파일명 생성
        directory = r'C:/Users/meric/Desktop/MS'
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.csv_file_path = os.path.join(directory, f'real_time_data_{current_time}.csv')

        # CSV 파일 설정 (헤더 포함)
        with open(self.csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Time', 'Vout', 'Filtered_Vout'])  # CSV 파일의 헤더

        # PyQt 윈도우 초기화
        self.setWindowTitle("Real-Time Data Plot")
        self.setGeometry(100, 100, 1600, 600)

        # Vout 그래프 설정 (원본 데이터)
        self.figure, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], label="Vout (Noisy)", color='blue')
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Vout")
        self.ax.legend(loc="upper left")
        self.ax.grid(True)
        self.ax.set_title("Measured Vout (Noisy)")  # 그래프 제목 추가

        # 필터링된 Vout 그래프 설정
        self.line_filtered, = self.ax.plot([], [], label="Vout (Filtered)", color='red')

        # PyQt Layout 설정 (Vout 그래프)
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        #self.update()
        
        # Timer 설정 (주기적으로 데이터를 갱신)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1)  # 100ms마다 데이터 갱신
        self.flag=1
        
    def update_data(self):
        
        # 시리얼 포트에서 데이터 읽기
        
        if self.flag>20:
            self.ser.reset_input_buffer()
            self.flag=1
        if self.ser.in_waiting > 0:
            self.flag+=1
            # 시리얼 포트에서 데이터 읽기
            data = self.ser.readline().decode('utf-8').strip()
            print(data)
            try:
                # 데이터가 숫자로 변환될 수 있으면
                Vout = float(data)

                # 필터링된 Vout 값 계산 (로우 패스 필터 적용)
                if len(self.filtered_data) == 0:
                    filtered_Vout = Vout  # 첫 번째 값은 필터링하지 않고 그대로 사용
                else:
                    filtered_Vout = self.alpha * Vout + (1 - self.alpha) * self.filtered_data[-1]  # EMA 적용

                # 데이터를 실시간으로 업데이트
                self.data.append(Vout)
                self.filtered_data.append(filtered_Vout)
                self.time.append(len(self.time))  # 간단히 X축에 시간 인덱스를 사용

                # 원본 Vout 그래프 업데이트 (파란색)
                self.line.set_data(self.time, self.data)

                # 필터링된 Vout 그래프 업데이트 (빨간색)
                self.line_filtered.set_data(self.time, self.filtered_data)

                # X축 범위 설정:
                self.ax.set_xlim(max(0, len(self.time) - 100), len(self.time))

                # Y축 범위 자동 조정
                self.ax.set_ylim(-0.5, 0.5)  # Y축 범위 설정 (-1에서 +2)

                # 그래프 그리기
                self.canvas.draw()

                # CSV 파일에 데이터 저장
                with open(self.csv_file_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([len(self.time), Vout, filtered_Vout])  # 실시간 데이터 저장

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

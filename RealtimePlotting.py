# import sys
# import os
# import serial
# import matplotlib.pyplot as plt
# import csv
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
# from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
# from PyQt5.QtCore import QTimer
# from datetime import datetime  # 날짜와 시간 처리용 모듈 추가

# class RealTimePlot(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         # 시리얼 포트 초기화
#         self.ser = serial.Serial('COM18', 9600, timeout=1)
#         self.data = []  # 실시간 데이터를 저장할 리스트 (Vout)
#         self.R4_values = []  # 실시간 데이터를 저장할 리스트 (R4)
#         self.time = []  # X축 (시간) 리스트

#         # 지정된 경로와 현재 날짜/시간으로 파일명 생성
#         directory = r'C:/Users/meric/Desktop/MS'
#         current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
#         self.csv_file_path = os.path.join(directory, f'real_time_data_{current_time}.csv')

#         # CSV 파일 설정 (헤더 포함)
#         with open(self.csv_file_path, mode='w', newline='') as file:
#             writer = csv.writer(file)
#             writer.writerow(['Time', 'Vout', 'R4'])  # CSV 파일의 헤더

#         # PyQt 윈도우 초기화
#         self.setWindowTitle("Real-Time Data Plot")
#         self.setGeometry(100, 100, 1600, 600)

#         # Vout 그래프 설정
#         self.figure1, self.ax1 = plt.subplots()
#         self.ax1.set_ylim(-5, 5)  # Y축 범위 설정 (-5에서 +5)
#         self.line1, = self.ax1.plot([], [], label="Vout", color='blue')
#         self.ax1.set_xlabel("Time")
#         self.ax1.set_ylabel("Vout")
#         self.ax1.legend(loc="upper left")
#         self.ax1.grid(True)
#         self.ax1.set_title("Measured Vout")  # 그래프 제목 추가

#         # R4 그래프 설정
#         self.figure2, self.ax2 = plt.subplots()
#         # self.ax2.set_ylim(-1000, 1000)  # R4의 y축 범위 설정
#         self.line2, = self.ax2.plot([], [], label="R4", color='red')
#         self.ax2.set_xlabel("Time")
#         self.ax2.set_ylabel("R4 (Ohms)")
#         self.ax2.legend(loc="upper left")
#         self.ax2.grid(True)
#         self.ax2.set_title("Estimated R4 in the Wheatstone bridge")  # 그래프 제목 추가

#         # PyQt Layout 설정 (Vout 그래프)
#         self.canvas1 = FigureCanvasQTAgg(self.figure1)
#         layout1 = QVBoxLayout()
#         layout1.addWidget(self.canvas1)
#         container1 = QWidget()
#         container1.setLayout(layout1)

#         # PyQt Layout 설정 (R4 그래프)
#         self.canvas2 = FigureCanvasQTAgg(self.figure2)
#         layout2 = QVBoxLayout()
#         layout2.addWidget(self.canvas2)
#         container2 = QWidget()
#         container2.setLayout(layout2)

#         # Vout과 R4 그래프를 위한 QSplitter를 사용하여 레이아웃 설정
#         layout = QVBoxLayout()
#         layout.addWidget(container1)
#         layout.addWidget(container2)

#         widget = QWidget()
#         widget.setLayout(layout)
#         self.setCentralWidget(widget)

#         # Timer 설정 (주기적으로 데이터를 갱신)
#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.update_data)
#         self.timer.start(10)  # 100ms마다 데이터 갱신

#     def update_data(self):
#         if self.ser.in_waiting > 0:
#             # 시리얼 포트에서 데이터 읽기
#             data = self.ser.readline().decode('utf-8').strip()

#             try:
#                 # 데이터가 숫자로 변환될 수 있으면
#                 Vout = float(data)

#                 # Vout 계산 후 R4 계산 (휘스톤 브릿지 공식)
#                 Vin = 5.0  # 입력 전압 (예시: 5V)
#                 R3 = 1000.0  # 저항 값 (예시: 1000 Ohms)
#                 if Vout != 0:
#                     R4 = R3 * (Vout / (Vin - Vout))  # R4 계산
#                 else:
#                     R4 = 0  # Vout이 0일 때 R4는 0으로 설정

#                 # 데이터를 실시간으로 업데이트
#                 self.data.append(Vout)
#                 self.R4_values.append(R4)
#                 self.time.append(len(self.time))  # 간단히 X축에 시간 인덱스를 사용

#                 # Vout 그래프 업데이트
#                 self.line1.set_data(self.time, self.data)

#                 # R4 그래프 업데이트
#                 self.line2.set_data(self.time, self.R4_values)

#                 # X축 범위 설정:
#                 self.ax1.set_xlim(max(0, len(self.time) - 100), len(self.time))
#                 self.ax2.set_xlim(max(0, len(self.time) - 100), len(self.time))

#                 # Y축 범위 자동 조정
#                 self.ax1.relim()  # 데이터 변경 후 한계 다시 계산
#                 self.ax1.autoscale_view()  # 자동으로 축 범위 갱신

#                 self.ax2.relim()  # 오른쪽 Y축 한계 다시 계산
#                 self.ax2.autoscale_view()  # 자동으로 오른쪽 축 범위 갱신

#                 # 그래프 그리기
#                 self.canvas1.draw()
#                 self.canvas2.draw()

#                 # CSV 파일에 데이터 저장
#                 with open(self.csv_file_path, mode='a', newline='') as file:
#                     writer = csv.writer(file)
#                     writer.writerow([len(self.time), Vout, R4])  # 실시간 데이터 저장

#             except ValueError:
#                 pass  # 숫자가 아닌 데이터는 무시

#     def closeEvent(self, event):
#         self.ser.close()  # 프로그램 종료 시 시리얼 포트 닫기
#         event.accept()


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = RealTimePlot()
#     window.show()
#     sys.exit(app.exec_())

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
        self.ser = serial.Serial('COM18', 9600, timeout=1)
        self.data = []  # 실시간 데이터를 저장할 리스트 (Vout)
        self.time = []  # X축 (시간) 리스트

        # 지정된 경로와 현재 날짜/시간으로 파일명 생성
        directory = r'C:/Users/meric/Desktop/MS'
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.csv_file_path = os.path.join(directory, f'real_time_data_{current_time}.csv')

        # CSV 파일 설정 (헤더 포함)
        with open(self.csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Time', 'Vout'])  # CSV 파일의 헤더

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

                # Vout 그래프 업데이트
                self.line.set_data(self.time, self.data)

                # X축 범위 설정:
                self.ax.set_xlim(max(0, len(self.time) - 100), len(self.time))

                # Y축 범위 자동 조정
                # self.ax.relim()  # 데이터 변경 후 한계 다시 계산
                # self.ax.autoscale_view()  # 자동으로 축 범위 갱신
                self.ax.set_ylim(-1, 2)  # Y축 범위 설정 (-5에서 +5)

                # 그래프 그리기
                self.canvas.draw()

                # CSV 파일에 데이터 저장
                with open(self.csv_file_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([len(self.time), Vout])  # 실시간 데이터 저장

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

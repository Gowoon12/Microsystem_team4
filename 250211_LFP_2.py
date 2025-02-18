import serial
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
import threading
from datetime import datetime
import os
import csv
from matplotlib.animation import FuncAnimation
import time

class RealTimeDataCollector:
    def __init__(self):
        # 시리얼 포트 초기화
        self.ser = serial.Serial('COM18', 1000000, timeout=0.1)
        # self.ser = serial.Serial('COM18', 9600, timeout=0.1)
        self.data = []  # 실시간 데이터를 저장할 리스트 (Vout)
        self.filtered_data = []  # 필터링된 데이터를 저장할 리스트
        self.time = []  # X축 (시간) 리스트
        self.buffer_size = 5  # 데이터를 버퍼로 저장할 크기

        # Butterworth 필터 설정
        # self.fs = 240  # 샘플링 주파수 (240Hz)
        self.fs = 240  # 샘플링 주파수 (240Hz)
        self.cutoff = 5  # 차단 주파수 (60Hz) -> 60Hz 교류 노이즈 필터링
        self.order = 5  # 필터 차수
        self.b, self.a = butter(self.order, self.cutoff / (0.5 * self.fs), btype='low')  # 필터 계수 계산

        # 지정된 경로와 현재 날짜/시간으로 파일명 생성
        directory = r'C:/Users/meric/Desktop/MS/Data'
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.csv_file_path = os.path.join(directory, f'real_time_data_{current_time}.csv')

        # CSV 파일 설정 (헤더 포함)
        with open(self.csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Time', 'Vout', 'Filtered_Vout'])  # CSV 파일 헤더 설정

        print("Real-time data collection started...")

        # 실시간 플로팅을 위한 초기 설정
        self.fig, self.ax = plt.subplots()
        self.raw_line, = self.ax.plot([], [], label="Raw Vout", color='lightgray')  # 원본 데이터
        self.filtered_line, = self.ax.plot([], [], label="Filtered Vout", color='red')  # 필터링된 데이터
        self.ax.set_xlim(0, 500)  # X축 범위 설정
        # self.ax.set_ylim(-3, 2)  # Y축 범위 설정
        self.ax.set_ylim(-2, 2)  # Y축 범위 설정
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Vout')
        self.ax.legend()

        # 그리드 추가
        self.ax.grid(True)  # 그리드 켜기

        self.running = True  # 데이터 수집 및 플로팅을 계속 실행할 플래그

        # 샘플링 시간 추적 변수
        self.last_sample_time = time.time()  # 마지막 샘플링 시간
        self.sample_count = 0  # 샘플의 개수

    def apply_filter(self):
        """Butterworth 필터를 사용해 데이터를 필터링"""
        if len(self.data) > 1:
            self.filtered_data = lfilter(self.b, self.a, self.data)

    def update_data(self):
        """데이터를 수집하고 처리하는 메서드"""
        if self.ser.in_waiting > 0:
            try: 
                # 시리얼 포트에서 데이터 읽기
                data = self.ser.readline().decode('utf-8').strip()
                Vout = float(data) * 10 # 데이터를 float로 변환

                # 데이터 업데이트
                self.data.append(Vout)
                self.time.append(len(self.time))

                # Butterworth 필터 적용
                self.apply_filter()

                # 데이터 버퍼에 쌓기
                if len(self.time) % self.buffer_size == 0:
                    # 일정 버퍼 크기마다 CSV 파일에 저장
                    with open(self.csv_file_path, mode='a', newline='') as file:
                        writer = csv.writer(file)
                        for i in range(len(self.time) - self.buffer_size, len(self.time)):
                            writer.writerow([self.time[i], self.data[i], self.filtered_data[i]])

                # 샘플링 속도 계산 (초당 샘플 수)
                self.sample_count += 1
                current_time = time.time()
                time_diff = current_time - self.last_sample_time

                # 일정 시간이 지났다면 샘플링 속도를 출력
                if time_diff >= 1:  # 1초마다 출력
                    actual_sample_rate = self.sample_count / time_diff
                    print(f"Actual Sample Rate: {actual_sample_rate:.2f} Hz")
                    self.last_sample_time = current_time
                    self.sample_count = 0

            except ValueError:
                # 숫자로 변환할 수 없는 데이터는 무시
                pass

    def start_data_collection(self):
        while self.running:
            self.update_data()

    def animate(self, i):
        # 실시간 플로팅을 위한 애니메이션 업데이트
        if len(self.time) > 0:
            # 데이터가 100개 이상이면 X축 범위 갱신
            if len(self.time) > 500:
                self.ax.set_xlim(len(self.time) - 500, len(self.time))

            # 실시간으로 원본 Vout과 필터링된 Vout을 플로팅
            self.raw_line.set_data(self.time, self.data)  # 원본 데이터 (옅은 회색)
            self.filtered_line.set_data(self.time, self.filtered_data)  # 필터링된 데이터 (빨간색)

        return self.raw_line, self.filtered_line

    def run(self):
        # 데이터 수집 스레드 시작
        data_thread = threading.Thread(target=self.start_data_collection)
        data_thread.daemon = True
        data_thread.start()

        # 실시간 플로팅을 위한 FuncAnimation 실행
        ani = FuncAnimation(self.fig, self.animate, interval=20, blit=True, cache_frame_data=False)

        plt.show()

if __name__ == '__main__':
    collector = RealTimeDataCollector()
    collector.run()

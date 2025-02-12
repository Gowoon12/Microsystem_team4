import sys
import os
import serial
import csv
from datetime import datetime
from scipy.signal import find_peaks
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading

class RobustEMAFilter:
    def __init__(self, alpha= 0.8, window_size=10, outlier_threshold=2.0):
        self.alpha = alpha
        self.window_size = window_size
        self.outlier_threshold = outlier_threshold
        self.filtered_data = []
        self.window = []

    def moving_average(self, data_point):
        self.window.append(data_point)
        if len(self.window) > self.window_size:
            self.window.pop(0)
        return np.mean(self.window)

    def apply_filter(self, data_point):
        smoothed_value = self.moving_average(data_point)

        if len(self.filtered_data) > 0:
            prev_value = self.filtered_data[-1]
            if abs(smoothed_value - prev_value) > self.outlier_threshold:
                print(f"Outlier detected: {data_point}. Skipping filter update.")
                return prev_value

        if not self.filtered_data:
            self.filtered_data.append(smoothed_value)
            return smoothed_value

        filtered_value = self.alpha * smoothed_value + (1 - self.alpha) * self.filtered_data[-1]
        self.filtered_data.append(filtered_value)
        return filtered_value

class RealTimeDataCollector:
    def __init__(self, max_data_count=1000, initial_data_count=10):
        self.ser = serial.Serial('COM18', 921600, timeout=0.1)

        self.data = []  # 모든 데이터를 저장
        self.filtered_data = []  # 필터링된 데이터를 저장
        self.time = []  # 그래프에서 사용할 시간 리스트
        self.timestamps = []  # 타임스탬프 리스트 (실제 시간)

        self.alpha = 0.024  #0.024
        self.robust_ema_filter = RobustEMAFilter(alpha=self.alpha)

        # CSV 파일 경로 생성
        directory = r'C:/Users/meric/Desktop/MS/Data'
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.csv_file_path = os.path.join(directory, f'real_time_data_EMA_1_{current_time}.csv')

        # CSV 파일 설정 (헤더 포함)
        with open(self.csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Time', 'Vout', 'Filtered_Vout', 'Peak', 'Valley', 'Elapsed_Time(ms)'])  # Elapsed_Time 추가

        print("Real-time data collection started...")

        # 실시간 플로팅 설정
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], label="Vout")
        self.filtered_line, = self.ax.plot([], [], label="Filtered Vout")
        self.ax.set_xlim(0, max_data_count)  # 그래프에 표시할 데이터 개수 1000개로 제한
        self.ax.set_ylim(-0.1, 0.1)  # Y축 범위
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Vout')
        self.ax.legend()
        self.ax.grid(True) 

        # 데이터 수집을 위한 플래그 및 변수 설정
        self.running = True
        self.peaks = []
        self.valleys = []
        self.periods = []

        self.text = self.ax.text(0.8, 0.9, '', transform=self.ax.transAxes, fontsize=12)
        self.max_data_count = max_data_count
        self.initial_data_count = initial_data_count  # 초기 필터 적용하지 않을 데이터 개수 설정

        # 상대 시간을 측정하기 위한 시작 시간 기록
        self.start_time = time.time()  # 시작 시간을 기록 (초 단위)

    def update_data(self):
        if self.ser.in_waiting > 0:
            try:
                data = self.ser.readline().decode('utf-8').strip()
                Vout = float(data)    # 데이터를 Vout으로 변환   ## 

                # 상대적인 타임스텝 계산 (시작 시간 이후 경과한 시간)
                elapsed_time = (time.time() - self.start_time) * 1000  # 밀리초 단위로 계산

                # 초기 데이터는 필터링하지 않고 그대로 저장
                if len(self.data) < self.initial_data_count:
                    self.data.append(Vout)
                    self.filtered_data.append(Vout)  # 필터 적용하지 않음
                else:
                    # 필터 적용 (이후부터)
                    filtered_Vout = self.robust_ema_filter.apply_filter(Vout)
                    self.data.append(Vout)
                    self.filtered_data.append(filtered_Vout)

                self.time.append(len(self.time))  # 그래프에서 사용할 시간 리스트 (데이터 수에 비례)
                self.timestamps.append(elapsed_time)  # 상대 시간 (밀리초 단위) 기록

                # 피크와 밸리 탐지
                self.peaks, _ = find_peaks(self.filtered_data, height=-1, distance=20)
                self.valleys, _ = find_peaks(-np.array(self.filtered_data), height=-1, distance=20)

                # 최신 피크와 밸리만 유지
                if len(self.peaks) > 0:
                    self.peaks = [self.peaks[-1]]  # 최신 피크
                if len(self.valleys) > 0:
                    self.valleys = [self.valleys[-1]]  # 최신 밸리

                # CSV 파일에 데이터 저장 (모든 데이터 기록)
                with open(self.csv_file_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    peak_value = self.data[self.peaks[-1]] if len(self.peaks) > 0 else ''
                    valley_value = self.data[self.valleys[-1]] if len(self.valleys) > 0 else ''
                    writer.writerow([len(self.time), Vout, self.filtered_data[-1], peak_value, valley_value, elapsed_time])  # Elapsed Time 추가

            except ValueError:
                pass

    def start_data_collection(self):
        while self.running:
            self.update_data()

    def animate(self, i):
        if len(self.time) > 0:
            # X축 범위 설정: 최신 1000개 데이터만 표시
            self.ax.set_xlim(max(0, len(self.time) - self.max_data_count), len(self.time))

            # 실시간 Vout과 필터링된 Vout을 그리기
            self.line.set_data(self.time[-self.max_data_count:], self.data[-self.max_data_count:])
            self.filtered_line.set_data(self.time[-self.max_data_count:], self.filtered_data[-self.max_data_count:])

            # Vout (회색, 연하게)
            self.line.set_color('gray')
            self.line.set_linewidth(1)
            self.line.set_alpha(0.6)

            # 필터링된 Vout (빨간색, 진하게)
            self.filtered_line.set_color('red')
            self.filtered_line.set_linewidth(2)
            self.filtered_line.set_alpha(1)

        return self.line, self.filtered_line, self.text

    def run(self):
        # 데이터 수집 스레드 시작
        data_thread = threading.Thread(target=self.start_data_collection)
        data_thread.daemon = True
        data_thread.start()

        # 실시간 플로팅을 위한 FuncAnimation 실행
        ani = FuncAnimation(self.fig, self.animate, interval=50, blit=False, cache_frame_data=False)
        plt.show()

if __name__ == '__main__':
    collector = RealTimeDataCollector(max_data_count=1000, initial_data_count=10)  # 최대 1000개 데이터로 제한
    collector.run()

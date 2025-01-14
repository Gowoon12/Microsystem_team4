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

class EMAFilter:
    def __init__(self, alpha=0.1):
        """
        EMA 필터를 초기화하는 함수입니다.
        :param alpha: EMA 필터의 alpha 값 (0과 1 사이)
        """
        self.alpha = alpha  # 필터의 alpha 값
        self.filtered_data = []  # 필터링된 데이터를 저장할 리스트

    def apply_filter(self, data_point):
        """
        EMA 필터를 적용하는 함수입니다.
        :param data_point: 현재 데이터 포인트
        :return: 필터링된 데이터 포인트
        """
        # 첫 번째 데이터 포인트일 경우 필터링된 데이터는 그대로 저장
        if not self.filtered_data:
            self.filtered_data.append(data_point)
            return data_point

        # EMA 계산: 새로운 데이터는 alpha 비율로, 이전 값은 (1 - alpha) 비율로 결합
        filtered_value = self.alpha * data_point + (1 - self.alpha) * self.filtered_data[-1]
        self.filtered_data.append(filtered_value)  # 필터링된 데이터에 추가
        return filtered_value


class RealTimeDataCollector:
    def __init__(self):
        # 시리얼 포트 초기화
        self.ser = serial.Serial('COM18', 921600, timeout=0.1)

        self.data = []  # 실시간 데이터를 저장할 리스트 (Vout)
        self.filtered_data = []  # 필터링된 데이터를 저장할 리스트
        self.time = []  # X축 (시간) 리스트

        self.alpha = 0.024  # EMA 필터의 강도를 나타내는 계수 (값을 조정하여 노이즈 수준 조절)

        # EMA 필터 객체 생성
        self.ema_filter = EMAFilter(self.alpha)

        # 지정된 경로와 현재 날짜/시간으로 파일명 생성
        # directory = r'D:/2025/Paper work/2025_Sensor/Microsystem_team4-main/Data'
        directory = directory = r'C:/Users/meric/Desktop/MS/Data'
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.csv_file_path = os.path.join(directory, f'real_time_data_EMA_{current_time}.csv')

        # CSV 파일 설정 (헤더 포함)
        with open(self.csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Time', 'Vout', 'Filtered_Vout', 'Peak', 'Valley'])  # CSV 파일의 헤더에 피크와 밸리 추가

        print("Real-time data collection started...")

        # 실시간 플로팅을 위한 초기 설정
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], label="Vout")
        self.filtered_line, = self.ax.plot([], [], label="Filtered Vout")
        self.ax.set_xlim(0, 1000)  # X축 범위 설정
        self.ax.set_ylim(-1, 1)   # Y축 범위 설정
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Vout')
        self.ax.legend()

        # 그리드 추가
        self.ax.grid(True)  # 그리드 켜기

        self.running = True  # 데이터 수집 및 플로팅을 계속 실행할 플래그

        # 피크와 밸리를 저장할 리스트
        self.peaks = []
        self.valleys = []
        self.periods = []  # 피크 간 주기를 저장할 리스트

        # 텍스트로 주기 표시
        self.text = self.ax.text(0.8, 0.9, '', transform=self.ax.transAxes, fontsize=12)

    def update_data(self):
        # 시리얼 포트에서 데이터 읽기 및 처리
        if self.ser.in_waiting > 0:
            try:
                # 시리얼 포트에서 데이터 읽기
                data = self.ser.readline().decode('utf-8').strip()
                Vout = float(data)*20  # 데이터를 float로 변환

                # 필터링된 Vout 계산 (지수 이동 평균 적용)
                filtered_Vout = self.ema_filter.apply_filter(Vout)

                # 데이터 업데이트
                self.data.append(Vout)
                self.filtered_data.append(filtered_Vout)
                self.time.append(len(self.time))

                # 피크 및 밸리 찾기
                # height=-1은 최소 높이를 지정 (값을 조정)
                # distance=20은 최소 거리 설정 (값을 조정)
                self.peaks, _ = find_peaks(self.filtered_data, height=-1, distance=20)
                self.valleys, _ = find_peaks(-np.array(self.filtered_data), height=-1, distance=20)

                # 피크와 밸리 값을 최신 값만 유지하도록 갱신
                if len(self.peaks) > 0:
                    self.peaks = [self.peaks[-1]]  # 최신 피크만 저장
                if len(self.valleys) > 0:
                    self.valleys = [self.valleys[-1]]  # 최신 밸리만 저장

                # 피크 간 주기 계산 (시간 차이 계산)
                if len(self.peaks) > 1:
                    peak_times = np.array(self.time)[self.peaks]
                    intervals = np.diff(peak_times)  # 피크 간 간격
                    self.periods = intervals  # 주기를 저장

                # CSV 파일에 데이터 저장
                with open(self.csv_file_path, mode='a', newline='') as file:
                    writer = csv.writer(file)

                    # 최신 피크와 밸리 값만 CSV에 기록
                    peak_value = self.data[self.peaks[-1]] if len(self.peaks) > 0 else ''
                    valley_value = self.data[self.valleys[-1]] if len(self.valleys) > 0 else ''

                    writer.writerow([len(self.time), Vout, filtered_Vout, peak_value, valley_value])

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
            if len(self.time) > 1000:
                self.ax.set_xlim(len(self.time) - 1000, len(self.time))

            # 실시간으로 Vout과 필터링된 Vout을 플로팅
            self.line.set_data(self.time, self.data)
            self.filtered_line.set_data(self.time, self.filtered_data)
                
            # Vout (회색, 연하게 표시)
            self.line.set_color('gray')  # Vout의 색을 회색으로 설정
            self.line.set_linewidth(1)  # 선의 두께를 얇게 설정
            self.line.set_alpha(0.6)  # 선의 투명도를 낮춰서 연하게 설정

            # 필터링된 Vout (빨간색, 진하게 표시)
            self.filtered_line.set_color('red')  # 필터링된 Vout의 색을 빨간색으로 설정
            self.filtered_line.set_linewidth(2)  # 선의 두께를 두껍게 설정
            self.filtered_line.set_alpha(1)  # 선의 투명도를 1로 설정 (진하게)

            # # 피크와 밸리 플로팅
            # if len(self.peaks) > 0:
            #     self.ax.plot(np.array(self.time)[self.peaks], np.array(self.filtered_data)[self.peaks], 'go', label="Peaks", markersize=5)
            # if len(self.valleys) > 0:
            #     self.ax.plot(np.array(self.time)[self.valleys], np.array(self.filtered_data)[self.valleys], 'ro', label="Valleys", markersize=5)

            # # 주기를 계산하여 텍스트로 표시
            # if len(self.periods) > 0:
            #     avg_period = np.mean(self.periods)
            #     self.text.set_text(f'Avg Period: {avg_period:.4f} ms')

        return self.line, self.filtered_line, self.text

    def run(self):
        # 데이터 수집 스레드 시작
        data_thread = threading.Thread(target=self.start_data_collection)
        data_thread.daemon = True
        data_thread.start()

        # 실시간 플로팅을 위한 FuncAnimation 실행
        ani = FuncAnimation(self.fig, self.animate, interval=50, blit=False)
        plt.show()


if __name__ == '__main__':
    collector = RealTimeDataCollector()
    collector.run()

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, butter, lfilter
import socket
import threading
import csv
import time
from datetime import datetime

# 전역 변수 설정
BUFFER_SIZE = 1000
FS = 240  # 샘플링 주파수 (Hz)
WRITE_CHUNK = 100  # CSV 파일에 한 번에 저장할 데이터 수
HOST = '192.168.31.144'  # 소켓 서버 호스트
PORT = 1234  # 소켓 서버 포트

# 현지 시간으로 CSV 파일 이름 생성
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
CSV_FILE_PATH = f'C:/Users/meric/Desktop/Gowoon/wireless/wifi/sensor_data_{current_time}.csv'  # 경로와 파일 이름

# 필터 설정
low_cutoff = 5  # Low-pass filter cutoff frequency (Hz)
order = 2  # 필터 차수
b, a = butter(order, low_cutoff / (FS / 2), 'low')  # 필터 계수
filter_state = np.zeros(order)

# 데이터 저장 변수
voltage_data = np.zeros(BUFFER_SIZE)
filtered_data = np.zeros(BUFFER_SIZE)
peak_intervals = []
peak_sizes = []

# 상태 맵핑
status_mapping = {
    'OK': 1,
    'No Signal': 0,
    'Weak Signal': -1,
    'Slow Signal': -2
}

# CSV 파일 작성 헤더
header = ['Time', 'Raw Data', 'Filtered Data', 'DC Value', 'Current Period', 'Average Period', 'Current Peak Size', 'Average Peak Size', 'Status']
if not os.path.isfile(CSV_FILE_PATH):
    with open(CSV_FILE_PATH, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)

# 소켓 서버 설정
data_queue = []  # 데이터 큐

def start_socket_server():
    print("[Receiver] Starting socket server...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)
    print("[Receiver] Waiting for ESP32 to connect...")
    
    conn, addr = server.accept()
    print(f"[Receiver] Connected by {addr}")
    
    # 데이터를 읽어 큐에 저장
    with conn.makefile('r') as client_file:
        while True:
            line = client_file.readline()
            if not line:
                break  # 연결 종료 시
            data_queue.append(float(line.strip()))
            print(f"Received data: {line.strip()}")  # 수신 데이터 출력


# 상태 탐지 함수
def detect_status(current_peak, peak_interval, avg_peak, avg_interval):
    if current_peak < 0.005 and peak_interval > 2:
        status = 'No Signal'
    elif current_peak < 0.005:
        status = 'Weak Signal'
    elif peak_interval > 2:
        status = 'Slow Signal'
    else:
        status = 'OK'
    return status


# 실시간 데이터 처리 및 그래프 갱신 함수
def update_plot(raw_plot, filt_plot, peak_plot, dc_line, current_period_text, avg_period_text, current_peak_text, avg_peak_text):
    global voltage_data, filtered_data, filter_state, peak_intervals, peak_sizes
    
    if len(data_queue) > 0:
        # 100개씩 데이터를 가져와 처리하도록 변경
        data_batch = data_queue[:100]
        data_queue[:100] = []

        # 시계열 데이터 갱신
        voltage_data = np.roll(voltage_data, -len(data_batch))
        voltage_data[-len(data_batch):] = data_batch

        # 필터링 처리
        filtered_batch, filter_state = lfilter(b, a, data_batch, zi=filter_state)
        filtered_data = np.roll(filtered_data, -len(data_batch))
        filtered_data[-len(data_batch):] = filtered_batch

        # DC 값 계산
        dc_value = np.mean(filtered_data)

        # 피크 탐지
        peaks, properties = find_peaks(filtered_data, height=0.02, distance=10, prominence=0.001)
        locs = peaks  # 피크 위치는 'peaks'에 저장

        # 상태 탐지
        if len(peaks) > 0:
            peak_val = peaks[-1]
            peak_loc = locs[-1]
            current_peak = abs(filtered_data[peak_loc] - dc_value)

            if len(locs) > 1:
                peak_interval = (locs[-1] - locs[-2]) / FS
                peak_intervals.append(peak_interval)
            else:
                peak_interval = np.nan

            avg_peak = np.mean(peak_sizes) if peak_sizes else np.nan
            avg_interval = np.mean(peak_intervals) if peak_intervals else np.nan

            # 상태 탐지 함수 호출
            status = detect_status(current_peak, peak_interval, avg_peak, avg_interval)

            # 상태 출력
            print(f"Peak Interval: {peak_interval:.4f} s, Avg Interval: {avg_interval:.4f} s, "
                  f"Peak: {current_peak:.4f} V, Avg Peak: {avg_peak:.4f} V, Status: {status}")

            # 피크 크기 추가
            peak_sizes.append(current_peak)
        else:
            peak_interval = avg_interval = current_peak = avg_peak = np.nan
            status = 'No Signal'

        # 그래프 업데이트
        raw_plot.set_ydata(voltage_data)
        filt_plot.set_ydata(filtered_data)
        dc_line.set_ydata([dc_value, dc_value])

        if len(locs) > 0:
            peak_plot.set_data(locs, filtered_data[locs])

        # 상태 값 텍스트 업데이트
        current_period_text.set_text(f"Current Period: {peak_interval:.4f} s")
        avg_period_text.set_text(f"Average Period: {avg_interval:.4f} s")
        current_peak_text.set_text(f"Current Peak Size: {current_peak:.4f} V")
        avg_peak_text.set_text(f"Average Peak Size: {avg_peak:.4f} V")

    return raw_plot, filt_plot, peak_plot, dc_line, current_period_text, avg_period_text, current_peak_text, avg_peak_text


# CSV에 데이터 저장 함수
def save_data_to_csv():
    # 데이터 버퍼 설정
    buffer_for_writing = np.zeros((100, 9))
    write_index = 0

    while True:
        if len(data_queue) > 0:
            # 100개씩 데이터를 처리하여 저장
            data_batch = data_queue[:100]
            data_queue[:100] = []

            # 상태를 탐지하고 저장
            for i, value in enumerate(data_batch):
                # CSV에 저장할 데이터 작성
                current_peak = np.nan
                peak_interval = np.nan
                avg_peak = np.nan
                avg_interval = np.nan
                status = 'No Signal'

                if len(peak_sizes) > 0:
                    current_peak = abs(filtered_data[-1] - np.mean(filtered_data))
                    if len(peak_intervals) > 0:
                        peak_interval = peak_intervals[-1]
                    avg_peak = np.mean(peak_sizes)
                    avg_interval = np.mean(peak_intervals)

                # buffer에 데이터 추가
                buffer_for_writing[write_index, :] = [
                    time.time(), value, filtered_data[-1], np.mean(filtered_data),
                    peak_interval, avg_interval, current_peak, avg_peak, status_mapping[status]
                ]
                write_index += 1

            if write_index >= 100:
                print(f"Saving {write_index} data points to CSV...")  # 디버깅 출력
                # CSV에 저장
                with open(CSV_FILE_PATH, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerows(buffer_for_writing)
                write_index = 0

        time.sleep(1)  # 1초 간격으로 저장


# 메인 함수 실행
if __name__ == '__main__':
    try:
        # 소켓 서버 스레드 실행
        threading.Thread(target=start_socket_server, daemon=True).start()

        # 데이터 저장 스레드 실행
        threading.Thread(target=save_data_to_csv, daemon=True).start()

        # 플롯 설정
        plt.ion()
        fig, ax = plt.subplots()
        t = np.arange(BUFFER_SIZE)
        raw_plot, = ax.plot(t, voltage_data, color='gray', label='Raw Data')
        filt_plot, = ax.plot(t, filtered_data, color='red', label='Filtered')
        peak_plot, = ax.plot([], [], 'bo', label='Peaks')
        dc_line = ax.axhline(y=np.nan, color='green', linestyle='--', label='DC Value')

        current_period_text = ax.text(10, 0.08, 'Current Period: N/A', fontsize=12)
        avg_period_text = ax.text(10, 0.075, 'Average Period: N/A', fontsize=12)
        current_peak_text = ax.text(10, 0.07, 'Current Peak Size: N/A', fontsize=12)
        avg_peak_text = ax.text(10, 0.065, 'Average Peak Size: N/A', fontsize=12)

        ax.set_ylim(0, 1)
        ax.set_title("Real-Time Filter + Peak Detection")
        ax.set_xlabel("Samples")
        ax.set_ylabel("Voltage (V)")
        ax.legend()

        # 플롯 띄우기
        plt.show()

        # 실시간 데이터 업데이트
        while True:
            raw_plot, filt_plot, peak_plot, dc_line, current_period_text, avg_period_text, current_peak_text, avg_peak_text = update_plot(
                raw_plot, filt_plot, peak_plot, dc_line, current_period_text, avg_period_text, current_peak_text, avg_peak_text
            )
            plt.pause(0.05)  # 플롯 업데이트 간 시간 간격을 줄여서 속도 향상

    except KeyboardInterrupt:
        print("Program interrupted. Closing...")
        plt.close()  # 종료 시 플롯 자원 정리

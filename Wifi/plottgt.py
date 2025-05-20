import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, butter, lfilter
import time
import threading
import socket

# 전역 변수 설정
BUFFER_SIZE = 1000
FS = 240  # 샘플링 주파수 (Hz)
WRITE_CHUNK = 100  # CSV 파일에 한 번에 저장할 데이터 수

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

# 소켓 서버 설정
HOST = '0.0.0.0'
PORT = 1234
data_queue = []  # 데이터 큐

# CSV 파일 설정
CSV_FILE = 'sensor_data.csv'


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


# 실시간 데이터 처리 및 그래프 갱신 함수
def processing_loop():
    global voltage_data, filtered_data, filter_state
    global peak_intervals, peak_sizes
    
    plt.ion()
    fig, ax = plt.subplots()
    t = np.arange(BUFFER_SIZE)
    raw_plot, = ax.plot(t, voltage_data, color='gray', label='Raw Data')
    filt_plot, = ax.plot(t, filtered_data, color='red', label='Filtered')
    peak_plot, = ax.plot([], [], 'bo', label='Peaks')
    dc_line = ax.axhline(y=np.nan, color='green', linestyle='--', label='DC Value')
    
    ax.set_ylim(0, 1)
    ax.set_title("Real-Time Filter + Peak Detection")
    ax.set_xlabel("Samples")
    ax.set_ylabel("Voltage (V)")
    ax.legend()
    
    while True:
        if len(data_queue) > 0:
            v = data_queue.pop(0)

            # 시계열 데이터 갱신
            voltage_data = np.roll(voltage_data, -1)
            voltage_data[-1] = v

            # 필터링 처리
            filtered_sample, filter_state = lfilter(b, a, [v], zi=filter_state)
            filtered_sample = filtered_sample[0]
            filtered_data = np.roll(filtered_data, -1)
            filtered_data[-1] = filtered_sample

            # DC 값 계산
            dc_value = np.mean(filtered_data)

            # 피크 탐지 (dict가 아니라, 리스트로 반환)
            peaks, properties = find_peaks(filtered_data, height=0.02, distance=10, prominence=0.001)
            locs = peaks  # 피크 위치는 'peaks'에 저장

            if len(peaks) > 0:
                peak_val = peaks[-1]
                peak_loc = locs[-1]
                current_peak = abs(filtered_data[peak_loc] - dc_value)
                peak_sizes.append(current_peak)

                if len(locs) > 1:
                    peak_interval = (locs[-1] - locs[-2]) / FS
                    peak_intervals.append(peak_interval)
                else:
                    peak_interval = np.nan

                avg_peak = np.mean(peak_sizes)
                avg_interval = np.mean(peak_intervals) if len(peak_intervals) > 0 else np.nan

                # 상태 판단
                if current_peak < 0.005 and peak_interval > 2:
                    status = 'No Signal'
                elif current_peak < 0.005:
                    status = 'Weak Signal'
                elif peak_interval > 2:
                    status = 'Slow Signal'
                else:
                    status = 'OK'
            else:
                peak_interval = avg_interval = current_peak = avg_peak = np.nan
                status = 'No Signal'

            # 그래프 업데이트
            raw_plot.set_ydata(voltage_data)
            filt_plot.set_ydata(filtered_data)
            dc_line.set_ydata([dc_value, dc_value])

            if len(locs) > 0:
                # locs는 이제 정수형 배열
                peak_plot.set_data(locs, filtered_data[locs])
            
            ax.relim()
            ax.autoscale_view()
            plt.pause(0.001)

            # 상태 출력
            print(f"Peak Interval: {peak_interval:.4f} s, Avg Interval: {avg_interval:.4f} s, "
                  f"Peak: {current_peak:.4f} V, Avg Peak: {avg_peak:.4f} V, Status: {status}")


# 메인 함수 실행
if __name__ == '__main__':
    # 소켓 서버 스레드 실행
    threading.Thread(target=start_socket_server, daemon=True).start()

    # 실시간 데이터 처리 스레드 실행
    processing_loop()

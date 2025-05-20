import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, butter, lfilter
import socket
import threading

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
HOST = '192.168.31.144' # '0.0.0.0' 
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
def update_plot(raw_plot, filt_plot, peak_plot, dc_line):
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

        # 그래프 업데이트
        raw_plot.set_ydata(voltage_data)
        filt_plot.set_ydata(filtered_data)
        dc_line.set_ydata([dc_value, dc_value])

        if len(locs) > 0:
            peak_plot.set_data(locs, filtered_data[locs])

    return raw_plot, filt_plot, peak_plot, dc_line


# 메인 함수 실행
if __name__ == '__main__':
    # 소켓 서버 스레드 실행
    threading.Thread(target=start_socket_server, daemon=True).start()

    # 플롯 설정
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

    # 플롯 띄우기
    plt.show()

    # 실시간 데이터 업데이트
    while True:
        raw_plot, filt_plot, peak_plot, dc_line = update_plot(raw_plot, filt_plot, peak_plot, dc_line)
        plt.pause(0.05)  # 플롯 업데이트 간 시간 간격을 줄여서 속도 향상

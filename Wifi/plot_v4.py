import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, butter, lfilter
import socket
import threading
import time
import csv
import os
from datetime import datetime

# 전역 설정
BUFFER_SIZE = 1000
FS = 240  # 샘플링 주파수 (Hz)
HOST = '0.0.0.0'
PORT = 1234
DATA_BATCH_SIZE = 10

# 필터 설정
low_cutoff = 5
order = 2
b, a = butter(order, low_cutoff / (FS / 2), 'low')
filter_state = np.zeros(order)

# 데이터 버퍼
voltage_data = np.zeros(BUFFER_SIZE)
filtered_data = np.zeros(BUFFER_SIZE)
data_queue = []
data_lock = threading.Lock()
processed_data_buffer = []
buffer_lock = threading.Lock()

# 피크 데이터
peak_intervals = []
peak_sizes = []

# CSV 저장용 파일 생성
timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"sensor_data_{timestamp_str}.csv"
save_dir = r"C:\Users\meric\Desktop\Gowoon\wireless\wifi"
os.makedirs(save_dir, exist_ok=True)
csv_filepath = os.path.join(save_dir, csv_filename)
with open(csv_filepath, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Time', 'Raw', 'Filtered', 'DC', 'CurrentPeriod', 'AvgPeriod', 'CurrentPeak', 'AvgPeak', 'Status'])

def start_socket_server():
    print("[Receiver] Starting socket server...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)
    print("[Receiver] Waiting for ESP32 to connect...")
    conn, addr = server.accept()
    print(f"[Receiver] Connected by {addr}")

    with conn.makefile('r') as client_file:
        for line in client_file:
            try:
                value = float(line.strip())
                with data_lock:
                    data_queue.append((time.time(), value))
            except ValueError:
                continue

def data_saver():
    while True:
        time.sleep(0.1)
        with buffer_lock:
            if processed_data_buffer:
                with open(csv_filepath, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(processed_data_buffer)
                    processed_data_buffer.clear()

def main_plot_loop():
    global voltage_data, filtered_data, filter_state

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
        with data_lock:
            if len(data_queue) < DATA_BATCH_SIZE:
                continue
            batch = data_queue[:DATA_BATCH_SIZE]
            del data_queue[:DATA_BATCH_SIZE]

        batch_timestamps = [ts for ts, _ in batch]
        batch_values = [val for _, val in batch]
        voltage_data = np.roll(voltage_data, -DATA_BATCH_SIZE)
        voltage_data[-DATA_BATCH_SIZE:] = batch_values

        filtered_batch, filter_state = lfilter(b, a, batch_values, zi=filter_state)
        filtered_data = np.roll(filtered_data, -DATA_BATCH_SIZE)
        filtered_data[-DATA_BATCH_SIZE:] = filtered_batch

        dc_value = np.mean(filtered_data)
        peaks, _ = find_peaks(filtered_data, height=0.02, distance=10, prominence=0.001)

        if len(peaks) > 1:
            interval = (peaks[-1] - peaks[-2]) / FS
            peak_intervals.append(interval)
        else:
            interval = np.nan

        if len(peaks) > 0:
            peak_val = filtered_data[peaks[-1]]
            current_peak = abs(peak_val - dc_value)
            peak_sizes.append(current_peak)
        else:
            current_peak = np.nan

        avg_interval = np.mean(peak_intervals) if peak_intervals else np.nan
        avg_peak = np.mean(peak_sizes) if peak_sizes else np.nan

        # ok 1 no signal 0 weak signal 2 slow signal 3 

        if np.isnan(current_peak) or current_peak < 0.005:
            status = 0 if np.isnan(interval) or interval > 2 else 2
        elif interval > 2:
            status = 3
        else:
            status = 1

        # 저장할 정보 준비
        with buffer_lock:
            for i in range(DATA_BATCH_SIZE):
                processed_data_buffer.append([
                    batch_timestamps[i],
                    batch_values[i],
                    filtered_batch[i],
                    dc_value,
                    interval,
                    avg_interval,
                    current_peak,
                    avg_peak,
                    status
                ])

        raw_plot.set_ydata(voltage_data)
        filt_plot.set_ydata(filtered_data)
        dc_line.set_ydata([dc_value, dc_value])
        if len(peaks) > 0:
            peak_plot.set_data(peaks, filtered_data[peaks])

        ax.relim()
        ax.autoscale_view()
        plt.pause(0.01)

        print(f"Peak Interval: {interval:.4f} s, Avg Interval: {avg_interval:.4f} s, "
              f"Peak: {current_peak:.4f} V, Avg Peak: {avg_peak:.4f} V, Status: {status}")

if __name__ == "__main__":
    threading.Thread(target=start_socket_server, daemon=True).start()
    threading.Thread(target=data_saver, daemon=True).start()
    main_plot_loop()

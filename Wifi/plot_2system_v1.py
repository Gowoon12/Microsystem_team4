import socket
import threading
import time
import numpy as np
import matplotlib.pyplot as plt

# 서버 설정
HOST = '0.0.0.0'  # 모든 네트워크 인터페이스에서 연결을 받아들임
PORT_1 = 1234      # ESP32 1의 포트
PORT_2 = 1235      # ESP32 2의 포트

# 데이터 수집을 위한 큐
data_queue_1 = []
data_queue_2 = []

# 데이터 처리 함수
def process_data(data_queue, label, ax, line):
    data_buffer = []
    while True:
        if len(data_queue) > 0:
            data = data_queue.pop(0)  # 데이터 큐에서 하나씩 꺼내기
            data_buffer.append(data)

            # 실시간 그래프 업데이트
            line.set_ydata(data_buffer)  # y데이터 갱신
            ax.relim()
            ax.autoscale_view()
            plt.draw()  # 그래프 갱신
            plt.pause(0.1)  # 실시간 갱신을 위한 대기

def start_socket_server_1():
    print("[Receiver 1] Starting socket server...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT_1))
    server.listen(1)
    print("[Receiver 1] Waiting for ESP32 1 to connect...")
    
    conn, addr = server.accept()
    print(f"[Receiver 1] Connected by {addr}")
    
    with conn.makefile('r') as client_file:
        while True:
            line = client_file.readline().strip()
            if line:
                try:
                    value = float(line)
                    data_queue_1.append(value)
                    print(f"[Receiver 1] Received: {value}")
                except ValueError:
                    print(f"[Receiver 1] Invalid data: {line}")

def start_socket_server_2():
    print("[Receiver 2] Starting socket server...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT_2))
    server.listen(1)
    print("[Receiver 2] Waiting for ESP32 2 to connect...")
    
    conn, addr = server.accept()
    print(f"[Receiver 2] Connected by {addr}")
    
    with conn.makefile('r') as client_file:
        while True:
            line = client_file.readline().strip()
            if line:
                try:
                    value = float(line)
                    data_queue_2.append(value)
                    print(f"[Receiver 2] Received: {value}")
                except ValueError:
                    print(f"[Receiver 2] Invalid data: {line}")

if __name__ == "__main__":
    # 그래프 설정 (메인 스레드에서)
    plt.ion()  # 실시간 플로팅을 위한 설정
    fig, ax = plt.subplots()
    ax.set_title(f"Real-Time Data")
    ax.set_xlabel("Samples")
    ax.set_ylabel("Voltage (V)")
    line_1, = ax.plot([], [], label="ESP32 1")
    line_2, = ax.plot([], [], label="ESP32 2")
    ax.legend()

    # 각각의 ESP32 데이터 수신을 위한 스레드 시작
    threading.Thread(target=start_socket_server_1, daemon=True).start()
    threading.Thread(target=start_socket_server_2, daemon=True).start()

    # 각각의 데이터 처리 및 실시간 그래프 업데이트
    threading.Thread(target=process_data, args=(data_queue_1, "ESP32 1", ax, line_1), daemon=True).start()
    threading.Thread(target=process_data, args=(data_queue_2, "ESP32 2", ax, line_2), daemon=True).start()

    # 메인 스레드는 종료되지 않도록 유지
    while True:
        time.sleep(1)

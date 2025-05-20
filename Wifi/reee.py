import socket

HOST = '0.0.0.0'  # 모든 인터페이스에서 수신
PORT = 1234       # ESP32가 보내는 포트

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print("Waiting for connection...")

conn, addr = server.accept()
print(f"Connected by {addr}")

# 실시간으로 줄 단위 수신을 위해 makefile 사용
with conn.makefile('r') as client_file:
    while True:
        line = client_file.readline()
        if not line:
            break  # 연결이 끊어졌을 경우
        print("Received:", line.strip())

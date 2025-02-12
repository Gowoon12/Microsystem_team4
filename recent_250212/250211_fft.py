import serial
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

# 시리얼 포트 설정 (COM 포트 번호는 시스템에 따라 달라질 수 있음)
ser = serial.Serial('COM18', 1000000)  # COM 포트와 Baud rate 설정
sample_rate = 240  # 샘플링 주파수 (Hz)

# 데이터를 수집할 시간 간격
sample_time = 15.0  # 전체 수집할 시간 (15초)

# 데이터를 수집할 배열 초기화
num_samples = int(sample_time * sample_rate)
data = []

# 데이터 수집
print("Collecting data...")
for i in range(num_samples):
    line = ser.readline().decode('utf-8').strip()  # 시리얼로 받은 데이터 읽기
    try:
        voltage = float(line)  # 문자열을 실수형으로 변환
        data.append(voltage)
    except ValueError:
        pass

ser.close()  # 시리얼 포트 닫기
print("Data collection complete.")

# 수집된 데이터를 numpy 배열로 변환
data = np.array(data)

# 10초부터 11초까지의 데이터를 선택
start_index = 10 * sample_rate  # 10초부터 시작하는 인덱스
end_index = 11 * sample_rate  # 11초에서 끝나는 인덱스

# 10초부터 11초까지의 데이터 추출
data_segment = data[start_index:end_index]

# FFT 적용
n = len(data_segment)
T = 1.0 / sample_rate  # 샘플링 간격
x = np.linspace(0.0, n*T, n, endpoint=False)  # 시간 축

# FFT 계산
yf = fft(data_segment)
xf = fftfreq(n, T)[:n//2]  # 양의 주파수만 가져오기

# 주파수 스펙트럼
plt.figure(figsize=(10, 6))
plt.plot(xf, 2.0/n * np.abs(yf[:n//2]))  # FFT 결과 (크기)
plt.grid()
plt.title('FFT of the Signal (10s to 11s)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.show()
################################################################################
# import serial
# import time
# import csv

# # 시리얼 포트 설정
# ser = serial.Serial('COM18', 1000000)  # COM 포트와 Baud rate 설정

# # 데이터 수집 시간
# start_time = time.time()

# # 첫 번째 샘플 시간
# last_sample_time = start_time

# # 수집된 데이터
# data = []

# # CSV 파일 설정 (헤더 포함)
# csv_file_path = 'sampling_frequencies.csv'
# with open(csv_file_path, mode='w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerow(['Timestamp', 'Sampling Frequency (Hz)'])  # 헤더 작성

# # 데이터를 수집하고 샘플링 주파수를 계산
# while True:
#     if ser.in_waiting > 0:
#         line = ser.readline().decode('utf-8').strip()  # 시리얼로 받은 데이터 읽기
#         try:
#             voltage = float(line)  # 데이터를 실수형으로 변환
#             data.append(voltage)
            
#             # 현재 샘플의 시간
#             current_time = time.time()

#             # 샘플 간의 시간 차이 계산
#             sample_interval = current_time - last_sample_time

#             if sample_interval > 0:  # 시간이 0 이상일 때만 계산
#                 # 샘플링 주파수 계산
#                 sampling_frequency = 1 / sample_interval  # Hz로 샘플링 주파수 계산
#                 print(f"Sampling Frequency: {sampling_frequency:.2f} Hz")
                
#                 # 샘플링 주파수를 파일에 저장
#                 with open(csv_file_path, mode='a', newline='') as file:
#                     writer = csv.writer(file)
#                     writer.writerow([current_time, sampling_frequency])  # 타임스탬프와 주파수 저장
            
#             # 마지막 샘플 시간 갱신
#             last_sample_time = current_time

#         except ValueError:
#             pass
################################################################################

import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

# 시리얼 포트 설정
ser = serial.Serial('COM18', 1000000)  # COM 포트와 Baud rate 설정

# 샘플링 주파수 (Hz)
sample_rate = 240
sample_interval = 1.0 / sample_rate  # 샘플 간 시간 간격 (초)

# 데이터 수집 시간
total_duration = 15.0  # 15초

# 수집된 데이터
data = []

# 데이터 수집 시작 시간
start_time = time.time()
last_sample_time = start_time

# 데이터를 수집하고 샘플링 주파수를 계산
print("Collecting data...")
while True:
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()  # 시리얼로 받은 데이터 읽기
        try:
            voltage = float(line)  # 데이터를 실수형으로 변환
            data.append(voltage)
            
            # 현재 샘플의 시간
            current_time = time.time()

            # 샘플 간의 시간 차이 계산
            sample_interval_actual = current_time - last_sample_time

            # 일정한 샘플 간격 유지
            if sample_interval_actual < sample_interval:
                time.sleep(sample_interval - sample_interval_actual)  # 부족한 시간 만큼 대기

            # 마지막 샘플 시간 갱신
            last_sample_time = current_time

        except ValueError:
            pass

    # 15초 동안 데이터 수집 후 종료
    if current_time - start_time >= total_duration:
        break

ser.close()  # 시리얼 포트 닫기
print("Data collection complete.")

# 수집된 데이터를 numpy 배열로 변환
data = np.array(data)

# 10초부터 11초까지의 데이터를 선택
sample_start_index = 10 * sample_rate  # 10초부터 시작하는 인덱스
sample_end_index = 11 * sample_rate  # 11초에서 끝나는 인덱스

# 10초부터 11초까지의 데이터 추출
data_segment = data[sample_start_index:sample_end_index]

# FFT 분석 수행
n = len(data_segment)
T = 1.0 / sample_rate  # 샘플링 간격
x = np.linspace(0.0, n*T, n, endpoint=False)  # 시간 축

# FFT 계산
yf = fft(data_segment)
xf = fftfreq(n, T)[:n//2]  # 양의 주파수만 가져오기

# 주파수 스펙트럼
plt.figure(figsize=(10, 6))
plt.plot(xf, 2.0/n * np.abs(yf[:n//2]))  # FFT 결과 (크기)
plt.grid()
plt.title('FFT of the Signal (10s to 11s)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.show()

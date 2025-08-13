# import os
# import sys
# import time
# import threading
# import random
# import queue
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# from motorLLC_sync import *
# from dynamixel_sdk import *
# from datetime import datetime  # 파일 상단에 추가

# # === getch (Linux용)
# import tty, termios
# def getch():
#     fd = sys.stdin.fileno()
#     old = termios.tcgetattr(fd)
#     try:
#         tty.setraw(fd)
#         ch = sys.stdin.read(1)
#     finally:
#         termios.tcsetattr(fd, termios.TCSADRAIN, old)
#     return ch

# # === 모터 초기화 ===
# mc = motorLLC()
# mc.open()
# mc.torque_enable()

# # === 플롯 큐 ===
# data_queue = queue.Queue()
# running = False
# beat_thread = None

# # === 비팅 함수 ===
# def beat_motor(mode):
#     global running
#     beat_count = 1
#     while running:
#         if mode == 'a':  # 1Hz
#             mc.moveTo([1000])
#             data_queue.put(1000)
#             time.sleep(0.2)
#             mc.moveTo([600])
#             data_queue.put(600)
#             time.sleep(0.8)

#         elif mode == 's':  # 10 fast + 5s rest
#             for _ in range(10):
#                 if not running: break
#                 mc.moveTo([1000])
#                 data_queue.put(1000)
#                 time.sleep(0.2)
#                 mc.moveTo([600])
#                 data_queue.put(600)
#                 time.sleep(0.8)
#             time.sleep(5)

#         elif mode == 'd':  # 100 bpm
#             mc.moveTo([1000])
#             data_queue.put(1000)
#             time.sleep(0.2)
#             mc.moveTo([600])
#             data_queue.put(600)
#             time.sleep(0.3)

#         elif mode == 'f':  # 600~650 range at 1Hz
#             mc.moveTo([800])
#             data_queue.put(800)
#             time.sleep(0.2)
#             mc.moveTo([600])
#             data_queue.put(600)
#             time.sleep(0.8)

#         elif mode == 'g':  # random
#             # p1 = random.randint(600, 800)
#             p2 = random.randint(600, 900)
#             # interval = 60 / random.uniform(40, 120)  # bpm: 40~120
#             mc.moveTo([p2])
#             data_queue.put(p2)
#             time.sleep(0.2)
#             mc.moveTo([600])
#             data_queue.put(600)
#             time.sleep(0.8)
        
#         elif mode == 'h':  # random
#             # p1 = random.randint(600, 800)
#             # p2 = random.randint(600, 900)
#             interval = 60 / random.uniform(20, 120)  # bpm: 40~120
#             mc.moveTo([1000])
#             data_queue.put(1000)
#             time.sleep(0.2)
#             mc.moveTo([600])
#             data_queue.put(600)
#             time.sleep(interval)

#         else:
#             time.sleep(0.1)

#         # print(f"{beat_count} beat ({mode})")
#         now = datetime.now().strftime("%H:%M:%S")
#         print(f"\r[{now}] {beat_count} beat ({mode})    ", flush=True)

#         beat_count += 1

# # === 비트 시작
# def start_beat(mode):
#     global running, beat_thread
#     if running:
#         running = False
#         if beat_thread:
#             beat_thread.join()
#     running = True
#     beat_thread = threading.Thread(target=beat_motor, args=(mode,))
#     beat_thread.start()

# # === 키보드 입력 및 모터 제어 루프 ===
# def input_loop():
#     print("Press 'a', 's', 'd', 'f', 'g' to select beat mode. Press 'q' to quit.")
#     try:
#         while True:
#             key = getch()
#             if key == 'a':
#                 time.sleep(1)
#                 print("Mode A: 1Hz")
#                 start_beat('a')
#             elif key == 's':
#                 time.sleep(1)
#                 print("Mode S: 10 fast + 5s rest")
#                 start_beat('s')
#             elif key == 'd':
#                 time.sleep(1)
#                 print("Mode D: 100 bpm")
#                 start_beat('d')
#             elif key == 'f':
#                 time.sleep(1)
#                 print("Mode F: 600~650")
#                 start_beat('f')
#             elif key == 'g':
#                 time.sleep(1)
#                 print("Mode G: random")
#                 start_beat('g')
#             elif key == 'h':
#                 time.sleep(1)
#                 print("Mode H: random")
#                 start_beat('h')
#             elif key == 'q':
#                 time.sleep(1)
#                 print("Exiting...")
#                 global running
#                 running = False
#                 if beat_thread:
#                     beat_thread.join()
#                 break
#     finally:
#         try:
#             mc.torque_disable()
#         except Exception as e:
#             print(f"Warning: torque_disable() failed: {e}")
#         mc.close()
#         print("Motor stopped. Port closed.")

# # === 실시간 플롯 ===
# def live_plot():
#     fig, ax = plt.subplots()
#     xs, ys = [], []
#     start_time = time.time()

#     def animate(i):
#         while not data_queue.empty():
#             pos = data_queue.get()
#             t = time.time() - start_time
#             xs.append(t)
#             ys.append(pos)
#         if len(xs) > 200:
#             xs.pop(0)
#             ys.pop(0)
#         ax.clear()
#         ax.plot(xs, ys)
#         ax.set_ylim(500, 1100)
#         ax.set_title("Motor Beating")
#         ax.set_xlabel("Time (s)")
#         ax.set_ylabel("Position")

#     ani = animation.FuncAnimation(fig, animate, interval=100)
#     plt.show()

# # === 메인 실행 ===
# def main():
#     input_thread = threading.Thread(target=input_loop)
#     input_thread.start()

#     # 메인 스레드에서 플롯 실행
#     live_plot()

#     input_thread.join()

# if __name__ == "__main__":
#     main()

import os
import sys
import time
import threading
import random
# import queue  # 플롯을 위한 큐 제거
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
from motorLLC_sync import *
from dynamixel_sdk import *
from datetime import datetime

# === getch (Linux용)
import tty, termios
def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch

# === 모터 초기화 ===
mc = motorLLC()
mc.open()
mc.torque_enable()

# === 비팅 상태 ===
# data_queue = queue.Queue()  # 플롯 큐 제거
running = False
beat_thread = None

# === 비팅 함수 ===
def beat_motor(mode):
    global running
    beat_count = 1
    while running:
        if mode == 'a':  # 1Hz
            mc.moveTo([1000])
            # data_queue.put(1000)
            time.sleep(0.2)
            mc.moveTo([600])
            # data_queue.put(600)
            time.sleep(0.8)

        elif mode == 's':  # 10 fast + 5s rest
            for _ in range(5):
                if not running: break
                mc.moveTo([1000])
                # data_queue.put(1000)
                time.sleep(0.2)
                mc.moveTo([600])
                # data_queue.put(600)
                time.sleep(0.8)
            time.sleep(8)

        elif mode == 'd':  # 100 bpm
            mc.moveTo([1000])
            # data_queue.put(1000)
            time.sleep(0.2)
            mc.moveTo([600])
            # data_queue.put(600)
            time.sleep(0.3)

        elif mode == 'f':  # 600~650 range at 1Hz
            mc.moveTo([700])
            # data_queue.put(800)
            time.sleep(0.2)
            mc.moveTo([600])
            # data_queue.put(600)
            time.sleep(0.8)

        elif mode == 'g':  # random
            p2 = random.randint(600, 900)
            mc.moveTo([p2])
            # data_queue.put(p2)
            time.sleep(0.2)
            mc.moveTo([600])
            # data_queue.put(600)
            time.sleep(0.8)
        
        elif mode == 'h':  # random bpm
            interval = 60 / random.uniform(20, 120)
            mc.moveTo([1000])
            # data_queue.put(1000)
            time.sleep(0.2)
            mc.moveTo([600])
            # data_queue.put(600)
            time.sleep(interval)

        else:
            time.sleep(0.1)

        now = datetime.now().strftime("%H:%M:%S")
        print(f"\r[{now}] {beat_count} beat ({mode})    ", flush=True)
        beat_count += 1

# === 비트 시작
def start_beat(mode):
    global running, beat_thread
    if running:
        running = False
        if beat_thread:
            beat_thread.join()
    running = True
    beat_thread = threading.Thread(target=beat_motor, args=(mode,))
    beat_thread.start()

# === 키보드 입력 및 모터 제어 루프 ===
def input_loop():
    print("Press 'a', 's', 'd', 'f', 'g', 'h' to select beat mode. Press 'q' to quit.")
    try:
        while True:
            key = getch()
            if key == 'a':
                time.sleep(1)
                print("Mode A: 1Hz")
                start_beat('a')
            elif key == 's':
                time.sleep(1)
                print("Mode S: 10 fast + 5s rest")
                start_beat('s')
            elif key == 'd':
                time.sleep(1)
                print("Mode D: 100 bpm")
                start_beat('d')
            elif key == 'f':
                time.sleep(1)
                print("Mode F: 600~650")
                start_beat('f')
            elif key == 'g':
                time.sleep(1)
                print("Mode G: random")
                start_beat('g')
            elif key == 'h':
                time.sleep(1)
                print("Mode H: random bpm")
                start_beat('h')
            elif key == 'q':
                time.sleep(1)
                print("Exiting...")
                global running
                running = False
                if beat_thread:
                    beat_thread.join()
                break
    finally:
        try:
            mc.torque_disable()
        except Exception as e:
            print(f"Warning: torque_disable() failed: {e}")
        mc.close()
        print("Motor stopped. Port closed.")

# === 메인 실행 ===
def main():
    input_loop()

if __name__ == "__main__":
    main()

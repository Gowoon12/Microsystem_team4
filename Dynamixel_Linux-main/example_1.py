import os
import sys
import time
import threading
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from motorLLC_sync import *
from dynamixel_sdk import *
from queue import Queue

# Linux getch
import tty, termios
fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)
def getch():
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# === 모터 설정 ===
mc = motorLLC()
mc.open()
mc.torque_enable()

# === 모터 위치 큐 (플롯용) ===
position_queue = Queue()

# === 제어 변수 ===
running = True
mode = 'a'

def motor_beat_loop():
    global mode, running
    beat_count = 1
    while running:
        if mode == 'a':  # 1Hz
            mc.moveTo([600])
            position_queue.put(600)
            time.sleep(0.02)
            mc.moveTo([800])
            position_queue.put(800)
            time.sleep(0.98)

        elif mode == 's':  # 10 fast + 5s
            for _ in range(10):
                mc.moveTo([600])
                position_queue.put(600)
                time.sleep(0.02)
                mc.moveTo([800])
                position_queue.put(800)
                time.sleep(0.02)
            time.sleep(5)

        elif mode == 'd':  # 100회/분 = 0.6초 간격
            mc.moveTo([600])
            position_queue.put(600)
            time.sleep(0.02)
            mc.moveTo([800])
            position_queue.put(800)
            time.sleep(0.58)

        elif mode == 'f':  # 600~650 왕복
            mc.moveTo([600])
            position_queue.put(600)
            time.sleep(0.02)
            mc.moveTo([650])
            position_queue.put(650)
            time.sleep(0.98)

        elif mode == 'g':  # 랜덤
            p1 = random.randint(600, 800)
            p2 = random.randint(600, 800)
            freq = random.uniform(40, 120)  # bpm
            interval = 60 / freq
            mc.moveTo([p1])
            position_queue.put(p1)
            time.sleep(0.02)
            mc.moveTo([p2])
            position_queue.put(p2)
            time.sleep(interval)

        else:
            time.sleep(0.1)

        print(f"{beat_count} beat ({mode})")
        beat_count += 1

# === 실시간 플로팅 ===
def live_plot():
    fig, ax = plt.subplots()
    xs, ys = [], []
    start_time = time.time()

    def animate(i):
        while not position_queue.empty():
            pos = position_queue.get()
            t = time.time() - start_time
            xs.append(t)
            ys.append(pos)
        if len(xs) > 100:
            xs.pop(0)
            ys.pop(0)
        ax.clear()
        ax.plot(xs, ys)
        ax.set_ylim(500, 850)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Motor Position")
        ax.set_title(f"Motor Beating Mode [{mode}]")

    ani = animation.FuncAnimation(fig, animate, interval=100)
    plt.show()

# === 입력 쓰레드 ===
def input_loop():
    global mode, running
    print("Press 'a', 's', 'd', 'f', 'g' to switch mode. 'q' to quit.")
    while running:
        ch = getch()
        if ch in ['a', 's', 'd', 'f', 'g']:
            print(f"Switched to mode: {ch}")
            mode = ch
        elif ch == 'q':
            print("Exiting...")
            running = False
            break

# === 메인 실행 ===
try:
    t_motor = threading.Thread(target=motor_beat_loop)
    t_input = threading.Thread(target=input_loop)

    t_motor.start()
    t_input.start()

    live_plot()  # 메인 스레드에서 실행

    t_input.join()
    t_motor.join()

finally:
    mc.torque_disable()  # 직접 정의돼 있어야 함
    mc.close()
    print("Motor stopped and port closed.")

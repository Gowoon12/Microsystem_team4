#!/usr/bin/env python3
# UDP-ADC realtime plotter (fixed)

import socket, time, argparse, numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque

# ───── CLI ─────
p = argparse.ArgumentParser()
p.add_argument("--port", type=int, default=7001)
p.add_argument("--iface", default="0.0.0.0")
p.add_argument("--win", type=float, default=5.0)
args = p.parse_args()

# ───── socket ─────
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((args.iface, args.port))
sock.setblocking(False)
print(f"[UDP] bind {args.iface}:{args.port}")

# ───── buffers ─────
t_buf, v_buf, fps_win = deque(), deque(), deque()
last_seq, lost = None, 0

# ───── figure ─────
fig, ax = plt.subplots(figsize=(8,4))
line, = ax.plot([], [], lw=1, color="tab:red")
txt  = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top",
               bbox=dict(fc="white", alpha=.7, ec="none"), fontsize=9)
ax.set_xlabel("Time (s)")
ax.set_ylabel("Voltage (V)")
ax.set_ylim(0, 3.6)                         # VREF ≈ 3.6 V

WIN = args.win
VREF = 3.6
ADC_MAX = 4095

def recv():
    global last_seq, lost
    got_any = False                         ### 标记是否收到了数据
    while True:
        try:
            pkt, _ = sock.recvfrom(64)
        except BlockingIOError:
            break

        now = time.perf_counter()
        got_any = True

        try:
            # "SEQ:123 adc:2048"
            segs = pkt.decode(errors="ignore").split()
            seq  = int(segs[0].split(":")[1])
            raw  = int(segs[1].split(":")[1])
        except Exception as e:
            print("parse err:", e, pkt); continue

        if last_seq is not None and seq != last_seq + 1:
            lost += seq - last_seq - 1
        last_seq = seq

        t_buf.append(now)
        v_buf.append(raw * VREF / ADC_MAX)
        fps_win.append(now)

    # -------- trim windows --------
    if got_any:                             ### 只有收到数据才用 now
        while t_buf and now - t_buf[0] > WIN:
            t_buf.popleft(); v_buf.popleft()
        while fps_win and now - fps_win[0] > 1:
            fps_win.popleft()

def update(_):
    recv()
    if not t_buf: return line, txt

    t0 = t_buf[0]
    line.set_data([t - t0 for t in t_buf], v_buf)
    ax.set_xlim(0, WIN)

    inst = len(fps_win) / max((fps_win[-1]-fps_win[0]), 1e-3)
    txt.set_text(f"inst FPS: {inst:6.1f}\nlost pkts: {lost}")

    fig.canvas.manager.set_window_title(f"ESP32-S3 ADC | {inst:4.0f} fps")
    return line, txt

ani = FuncAnimation(fig, update, interval=30, blit=True,
                    cache_frame_data=False)   ### 关闭缓存，警告消失
plt.tight_layout(); plt.show()

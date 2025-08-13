"""
ADCPlotWidget — UDP‑ADC
"""

import csv
import datetime
import os
import time, socket, collections, sys
from typing import Optional

import numpy as np
from PyQt5 import QtCore, QtWidgets, QtPrintSupport, QtGui
import pyqtgraph as pg
try:
    from scipy.signal import find_peaks      # 推荐，用不到也行
except ImportError:
    find_peaks = None

VREF, ADC_MAX = 3.3, 4095


class _UdpWorker(QtCore.QThread):
    """后台线程: 监听 UDP 并将 (t, volt) 发射给 UI"""

    dataReady = QtCore.pyqtSignal(float, float)  # (t, volt)

    def __init__(self, iface: str, port: int, parent=None):
        super().__init__(parent)
        self.iface, self.port = iface, port
        self._stop = False

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.iface, self.port))
        sock.setblocking(False)
        while not self._stop:
            try:
                pkt, _ = sock.recvfrom(64)
            except BlockingIOError:
                self.msleep(1)
                continue
            now = time.perf_counter()
            try:
                segs = pkt.decode(errors="ignore").split()
                raw = int(segs[1].split(":")[1])  # "adc:2048"
            except Exception:
                continue
            volt = raw * VREF / ADC_MAX
            self.dataReady.emit(now, volt)

    def stop(self):
        self._stop = True
        self.wait()


class ADCPlotWidget(QtWidgets.QWidget):
    """
    主要接口:
        start() / stop()          -- 开启或关闭采集线程
        clear()                   -- 清空历史数据
        print_to_pdf(path)        -- 直接保存 PDF
    内部信号:
        fpsChanged(float)         -- 实时 FPS
    """

    fpsChanged = QtCore.pyqtSignal(float)

    def __init__(self,
                 iface: str = "192.168.2.2",
                 port: int = 7001,
                 win_sec: float = 10.0,
                 history_sec: float = 90.0,
                 sensor_id: str = "1",
                 parent=None):
        """
        Parameters
        ----------
        win_sec : float
            绘图区展示窗口宽度 (秒)。默认 10 s，对应坐标轴从 10→0。
        history_sec : float
            绘图缓冲保留的最长历史 (秒)。超过部分自动丢弃，防止卡顿。
            不影响录制功能。
        """
        super().__init__(parent)
        self.iface, self.port = iface, port
        self.win_sec = win_sec
        self.history_sec = history_sec
        self.sensor_id = sensor_id

        # ------------- 波峰筛选阈值 -------------
        self._peak_min_height = -1.5        # 只要高于 3.2 V 的才算
        self._peak_min_prominence = 0.25   # 与左右谷底至少差 0.25 V
        self._peak_min_distance = 0.2      # 相邻波峰最少相隔 0.4 s


        # —— UI ——
        self._plot = pg.PlotWidget()
        self._plot.setLabel("left", "Voltage", units="V")
        self._plot.setLabel("bottom", "Time", units="s")
        # self._plot.setYRange(0, VREF)
        self._plot.setYRange(-0.5, 1.5)
        self._plot.showGrid(x=True, y=True)
        # 反转 X 轴: 让 0 s 在右边
        self._plot.getPlotItem().invertX(True)

        self._curve = self._plot.plot(pen=pg.mkPen("b", width=3))
        self._filt_curve = self._plot.plot(  # ⬅️ 新增: 滤波曲线 (蓝)
            pen=pg.mkPen("y", width=3)
        )
        # ➡️ 新增: 波峰散点 (红)
        self._peak_scatter = self._plot.plot(
            pen=None,                              # 只画点、不连线
            symbol="o",
            symbolSize=10,
            symbolBrush=pg.mkBrush("r")
        )

        # —— 配置 ——                                             ⬅️ 新增一个窗口长度参数
        self._filt_win = 10  # 移动平均窗口长度 (点数)，想调得更平滑可设大一点

        self._fps_text = pg.TextItem(anchor=(0, 1))
        self._plot.addItem(self._fps_text)

        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._plot)

        # —— 数据缓冲 ——
        self._tbuf: collections.deque[float] = collections.deque()
        self._vbuf: collections.deque[float] = collections.deque()
        self._fps: collections.deque[float] = collections.deque()

        # —— 定时刷新 ——
        self._timer = QtCore.QTimer(self, timeout=self._refresh, interval=30)

        # —— 采集线程 ——
        self._worker = _UdpWorker(self.iface, self.port, self)
        self._worker.dataReady.connect(self._on_data)

        # —— 录制状态 ——
        self._recording = False
        self._rec_buf: list[tuple[str, float, float]] = []  # [(utc_iso, t_rel, volt)]
        self._rec_start_path: str | None = None
        self._rec_t0: float | None = None  # 相对时间零点

    # ---------- 公开接口 ----------
    def start_recording(self, dir_path: str = "data", prefix: str = "sensor"):
        """开始录制；dir_path 不存在时自动创建"""
        if self._recording:
            return
        os.makedirs(dir_path+"/"+f"Sensor{self.sensor_id}", exist_ok=True)
        stamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self._rec_start_path = os.path.join(dir_path+"/"+f"Sensor{self.sensor_id}", f"{prefix}_{stamp}.csv")
        self._rec_buf.clear()
        self._recording = True
        self._rec_t0 = None  # 等第一帧到来再确定

    def stop_recording(self):
        """仅停止录制；不落盘"""
        self._recording = False

    # def save_record(self, path: str | None = None):
    def save_record(self, path: Optional[str] = None):
        """将缓冲写入 CSV；写完自动 stop 并清空缓存"""
        if not self._rec_buf:
            return None
        if path is None:
            path = self._rec_start_path or "record.csv"
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["utc_iso", "relative_s", "volt_V"])
            writer.writerows(self._rec_buf)
        self.stop_recording()
        self._rec_buf.clear()
        self._rec_t0 = None
        return path

    # ---------- 公共方法 ----------
    def start(self):
        if not self._worker.isRunning():
            self._worker.start()
            self._timer.start()

    def stop(self):
        self._timer.stop()
        self._worker.stop()

    def clear(self):
        self._tbuf.clear()
        self._vbuf.clear()
        self._fps.clear()
        self._curve.clear()
        self._filt_curve.clear()  # ⬅️ 新增

        self._peak_scatter.clear()  # ⬅️ 新增
    # ---------- 私有 ----------
    def _on_data(self, t: float, v: float):
        # 写入缓冲
        self._tbuf.append(t)
        self._vbuf.append(v)
        self._fps.append(t)

        # 限制绘图缓冲在 history_sec 内，避免卡顿
        while self._tbuf and (t - self._tbuf[0] > self.history_sec):
            self._tbuf.popleft()
            self._vbuf.popleft()

        # 维护 FPS 统计 (1 s 窗口)
        while self._fps and (t - self._fps[0] > 1.0):
            self._fps.popleft()

        # 录制
        if self._recording:
            if self._rec_t0 is None:
                self._rec_t0 = t
            utc_iso = datetime.datetime.utcnow().isoformat(timespec="milliseconds")
            self._rec_buf.append((utc_iso, t - self._rec_t0, v))
    def _calc_filtered(self, ys):
        """简单移动平均；样本少时直接返回原数组"""
        if len(ys) < self._filt_win:
            return ys
        kernel = np.ones(self._filt_win) / self._filt_win
        return np.convolve(ys, kernel, mode="same")

    def _find_peaks(self, xs, ys):
        """
        返回满足多重条件的主要波峰下标。
        如果安装了 SciPy -> 用 find_peaks；否则 fallback 到简易实现。
        """
        y = np.asarray(ys)
        if y.size < 3:
            return np.array([], dtype=int)

        # --- ① 有 SciPy: 直接调用 ---
        if find_peaks is not None:
            # 把“秒”换算到“样本数”
            dt = (xs[-1] - xs[0]) / max(len(xs) - 1, 1)       # 单位: s / sample
            min_dist_samples = max(1, int(self._peak_min_distance / dt))

            idx, _ = find_peaks(
                y,
                height=self._peak_min_height,
                prominence=self._peak_min_prominence,
                distance=min_dist_samples
            )
            return idx

        # --- ② 没 SciPy: 简陋 fallback ---
        # 先找所有局部极大
        cand = np.where((y[1:-1] > y[:-2]) & (y[1:-1] >= y[2:]))[0] + 1
        # 按高度过滤
        cand = cand[y[cand] >= self._peak_min_height]

        # 用“distance & prominence”继续筛一次
        keep = []
        last_x = -1e9
        for i in cand:
            # prominence（左右 5 个点取最小作为谷底近似）
            lmin = y[max(0, i-5):i].min(initial=y[i])
            rmin = y[i+1:i+6].min(initial=y[i])
            prom = y[i] - max(lmin, rmin)
            if prom < self._peak_min_prominence:
                continue

            # distance
            if xs[i] - last_x < self._peak_min_distance:
                # 如果太近，只保留更高的
                if keep and y[i] > y[keep[-1]]:
                    keep[-1] = i
                    last_x = xs[i]
                continue
            keep.append(i)
            last_x = xs[i]

        return np.asarray(keep, dtype=int)



    def _refresh(self):
        if not self._tbuf:
            return

        t_latest = self._tbuf[-1]
        xs, ys = [], []

        # 仅提取 win_sec 范围内的数据点
        for tt, vv in zip(reversed(self._tbuf), reversed(self._vbuf)):
            dt = t_latest - tt
            if dt <= self.win_sec:
                xs.append(dt)  # 0 s 在右侧
                ys.append(vv)
            else:
                break
        xs.reverse()
        ys.reverse()

        self._curve.setData(xs, ys)
        # X 轴已反转，设定范围 [0, win_sec]
        self._plot.setXRange(0, self.win_sec, padding=0)

        # FPS
        if self._fps:
            fps = len(self._fps) / max(self._fps[-1] - self._fps[0], 1e-3)
            self._fps_text.setText(f"{fps:4.1f} fps")
            self._fps_text.setPos(0, VREF)
            self.fpsChanged.emit(fps)

        self._curve.setData(xs, ys)                    # 原始
        filt_ys = self._calc_filtered(ys)          # ← 先算蓝色曲线

        self._curve.setData(xs, ys)                # 原始 (黄)
        self._filt_curve.setData(xs, filt_ys)      # 滤波 (蓝)

        # 计算波峰
        peaks_idx = self._find_peaks(xs, filt_ys)  # ⇦ 这里传 xs, filt_ys
        self._peak_scatter.setData(
            [xs[i] for i in peaks_idx],
            [filt_ys[i] for i in peaks_idx],
        )

        # X 轴…
        self._plot.setXRange(0, self.win_sec, padding=0)

    # ---------- 组件卸载 ----------
    def closeEvent(self, e):
        self.stop()
        super().closeEvent(e)


# ―――― 示范运行 ――――
if __name__ == "__main__":  # python adc_plot_widget.py --demo
    app = QtWidgets.QApplication(sys.argv)
    w = ADCPlotWidget()
    w.resize(800, 400)
    w.show()
    w.start()
    sys.exit(app.exec_())

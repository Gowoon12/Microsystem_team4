#!/usr/bin/env python3
# adc_plot_qt.py : UDP-ADC realtime plotter (PyQtGraph + QPrinter)

import sys, socket, time, argparse, numpy as np, collections
from PyQt5 import QtCore, QtWidgets, QtPrintSupport, QtGui
import pyqtgraph as pg

# ───── CLI ─────
ap = argparse.ArgumentParser()
ap.add_argument("--port", type=int, default=7001)
ap.add_argument("--iface", default="0.0.0.0")
ap.add_argument("--win", type=float, default=5.0)
args = ap.parse_args()

VREF, ADC_MAX = 3.6, 4095

# ───── UDP 线程 ─────
class UdpWorker(QtCore.QThread):
    dataReady = QtCore.pyqtSignal(float, float)   # (timestamp, voltage)

    def __init__(self, iface, port, parent=None):
        super().__init__(parent)
        self.iface, self.port = iface, port
        self._stop = False

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.iface, self.port))
        sock.setblocking(False)
        last_seq = None
        while not self._stop:
            try:
                pkt, _ = sock.recvfrom(64)
            except BlockingIOError:
                self.msleep(1)                  # 减少 CPU 占用
                continue

            now = time.perf_counter()
            try:
                segs = pkt.decode(errors="ignore").split()
                seq  = int(segs[0].split(":")[1])
                raw  = int(segs[1].split(":")[1])
            except Exception:
                continue

            volt = raw * VREF / ADC_MAX
            self.dataReady.emit(now, volt)      # 发给主线程

    def stop(self):
        self._stop = True
        self.wait()

# ───── 主窗口 ─────
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ESP32-S3 ADC (PyQtGraph)")
        self.resize(900, 450)

        # 数据缓冲
        self.t_buf  = collections.deque()
        self.v_buf  = collections.deque()
        self.fps_win= collections.deque()
        self.lost   = 0
        self.win_sec= args.win

        # 绘图控件
        self.plot  = pg.PlotWidget()
        self.plot.setLabel("bottom", "Time", units="s")
        self.plot.setLabel("left",   "Voltage", units="V")
        self.plot.setYRange(0, VREF)
        self.plot.showGrid(x=True, y=True)
        self.curve = self.plot.plot(pen='y')
        self.txt   = pg.TextItem(anchor=(0,1))
        self.plot.addItem(self.txt)
        self.setCentralWidget(self.plot)

        # 工具栏：打印
        tb = QtWidgets.QToolBar()
        self.addToolBar(tb)
        printAct = QtWidgets.QAction("打印 / 导出 PDF", self)
        printAct.triggered.connect(self.handlePrint)
        tb.addAction(printAct)

        # FPS 定时刷新
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(30)                    # ≈33 FPS

        # UDP 线程
        self.worker = UdpWorker(args.iface, args.port, self)
        self.worker.dataReady.connect(self.onData)
        self.worker.start()

    # ---------- 数据到达 ----------
    def onData(self, tstamp, volt):
        self.t_buf.append(tstamp)
        self.v_buf.append(volt)
        self.fps_win.append(tstamp)

        # 滑动窗口
        while self.t_buf and tstamp - self.t_buf[0] > self.win_sec:
            self.t_buf.popleft(); self.v_buf.popleft()
        while self.fps_win and tstamp - self.fps_win[0] > 1.0:
            self.fps_win.popleft()

    # ---------- 绘图刷新 ----------
    def refresh(self):
        if not self.t_buf:
            return
        t0 = self.t_buf[0]
        self.curve.setData([t - t0 for t in self.t_buf], self.v_buf)
        self.plot.setXRange(0, self.win_sec, padding=0)

        inst_fps = len(self.fps_win) / max(self.fps_win[-1] - self.fps_win[0], 1e-3)
        self.txt.setText(f"FPS: {inst_fps:4.1f}")
        self.txt.setPos(0, VREF)               # 左上角

    # ---------- 打印 / 导出 ----------
    def handlePrint(self):
        # 1) 调用 Qt 打印对话框
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)  # 直接生成 PDF；若要物理打印注释掉
        printer.setOutputFileName("adc_plot.pdf")
        dlg = QtPrintSupport.QPrintDialog(printer, self)
        if dlg.exec_() != QtWidgets.QDialog.Accepted:
            return

        # 2) 把 PlotItem 导出成 QImage (PNG in-memory)
        exporter = pg.exporters.ImageExporter(self.plot.plotItem)
        png_bytes = exporter.export(toBytes=True)   # QByteArray
        img = QtGui.QImage.fromData(png_bytes)
        if img.isNull():
            QtWidgets.QMessageBox.warning(self, "导出失败", "无法导出图像。")
            return

        # 3) 绘到打印机
        painter = QtGui.QPainter(printer)
        rect = painter.viewport()
        scaled = img.scaled(rect.size(), QtCore.Qt.KeepAspectRatio,
                            QtCore.Qt.SmoothTransformation)
        painter.drawImage(QtCore.QPoint(0,0), scaled)
        painter.end()

        QtWidgets.QMessageBox.information(self, "已导出", "导出完成：adc_plot.pdf")

    # ---------- 关闭 ----------
    def closeEvent(self, evt):
        self.worker.stop()
        super().closeEvent(evt)

# ───── main ─────
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtCore import Qt






class MainWin(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("我的上位机")
        self.plot = ADCPlotWidget(port=7001, win_sec=10)
        btn = QtWidgets.QPushButton("清屏", clicked=self.plot.clear)

        central = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(central)
        lay.addWidget(self.plot)
        self.setCentralWidget(central)
        self.plot.start()

    def closeEvent(self, e):
        self.plot.stop()           # 可不写，控件自己会 stop
        super().closeEvent(e)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    win = MainWin(); win.show()
    app.exec_()

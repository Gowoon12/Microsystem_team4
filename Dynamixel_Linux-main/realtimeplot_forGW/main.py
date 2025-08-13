#pip install -r r.txt
import sys
from PyQt5 import QtWidgets, uic
from adc_plot_widget import ADCPlotWidget
from typing import Optional
BASE_PORT = 7007

class SingleSensorTable(QtWidgets.QWidget):
    def __init__(self, index, port, parent=None):
        super().__init__(parent)
        uic.loadUi('sensorplot.ui', self)
        self.groupBox.setTitle(f"Sensor {index}")
        self.port = port                         # ← 记录当前端口
        self.plot = ADCPlotWidget(port=port, parent=self,sensor_id=str(index))
        self.verticalLayout.addWidget(self.plot)
        self.plot.start()
        self._is_recording = False

    # 新增：根据新的端口重建 Plot
    def update_port(self, port: int):
        if port == self.port:
            return                                # 端口没变，直接返回
        # 1) 停掉并移除旧 plot
        try:
            self.plot.stop()                     # ADCPlotWidget 若没有 stop 可以去掉
        except AttributeError:
            pass
        self.verticalLayout.removeWidget(self.plot)
        self.plot.deleteLater()

        # 2) 创建并启动新 plot
        self.port = port
        self.plot = ADCPlotWidget(port=port, parent=self)
        self.verticalLayout.addWidget(self.plot)
        self.plot.start()

        window.add_log(f"{self.groupBox.title()} switched to port {port}.",
                       type='sensor setup')

    def f_pushButton_record(self):
        """开始或停止录制（再次点击停止）"""
        if not self._is_recording:
            # 开始
            self.plot.start_recording(prefix=f"sensor{self.groupBox.title().split()[-1]}")
            self._is_recording = True
            self.changestate("Recording")
            window.add_log(f"Started recording {self.groupBox.title()} data.", type='sensor data process')
        else:
            # 停止
            self.plot.stop_recording()
            self._is_recording = False
            self.changestate("Paused")
            window.add_log(f"Paused recording {self.groupBox.title()} data.", type='sensor data process')

    def f_pushButton_save(self):
        """保存当前缓冲到磁盘（若仍在录制则同时停止）"""
        saved_path = self.plot.save_record()  # 若返回 None 说明没数据
        if saved_path:
            self._is_recording = False
            self.changestate("Ok")
            window.add_log(f"Saved {self.groupBox.title()} data to {saved_path}.",
                           type='sensor data process')
        else:
            window.add_log(f"No data to save for {self.groupBox.title()}.",
                           type='sensor data process')

    def f_pushButton_clear(self):
        self.plot.clear()
        self.changestate("Cleared")
        window.add_log(f"Sensor {self.groupBox.title()} data cleared.", type='sensor data process')
    def changestate(self,state):
        """改变当前传感器的状态"""
        self.label_state.setText(state )

# -------- SingleSensorSetupTable -------------------------------------------
class SingleSensorSetupTable(QtWidgets.QWidget):
    def __init__(self, index: int, port: int,
                 sensor_table: 'SingleSensorTable',  # ← 对应的显示表
                 parent=None):
        super().__init__(parent)
        uic.loadUi('sensorsetup.ui', self)
        self.groupBox.setTitle(f"Sensor {index} Setup")
        self.lineEdit_port.setText(str(port))
        self.sensor_table = sensor_table          # ← 保存引用

    def f_pushButton_save(self):
        port_text = self.lineEdit_port.text().strip()
        if not port_text.isdigit():
            window.add_log(f"Invalid port number for {self.groupBox.title()}: "
                           f"{port_text}", type='error')
            return
        port = int(port_text)

        # 1) 更新实际绘图窗口
        self.sensor_table.update_port(port)
        # 2) 日志
        window.add_log(f"Saved {self.groupBox.title()} with port {port}.",
                       type='sensor setup')


class MyMainWindow(QtWidgets.QMainWindow):
    def __init__(self, sensor_count: int):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.sensorlayout = self.sensorgridLayout
        self.sensorsetlayout = self.sensorsetupgridLayout

        # �������Բű�����
        self.sensortables = []
        self.sensorsetuptables = []
        self.logindex = 0
        self.add_log("Welcome to the Multi-Sensor Monitoring System!", type='info')

        for i in range(sensor_count):
            port = BASE_PORT + i
            # ① 创建显示表
            sensor_table = SingleSensorTable(i + 1, port, self)
            self.sensortables.append(sensor_table)

            # ② 创建对应的设置表，传入 sensor_table
            setup_table = SingleSensorSetupTable(i + 1, port,
                                                 sensor_table, self)
            self.sensorsetuptables.append(setup_table)
        self.add_log(f"Created {sensor_count} sensors.", type='info')
        self._populate_layouts()

    # ---------- UI helpers -------------------------------------------------

    def _populate_layouts(self) -> None:
        """���Ա�������� layouts ������"""
        self._clear_layout(self.sensorlayout)
        self._clear_layout(self.sensorsetlayout)
        # �����ϰ�����
        max_cols = max(1, (self.width() // 450) - 1)
        row = col = 0
        for widget in self.sensortables:
            self.sensorlayout.addWidget(widget, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1


        max_cols = max(1, (self.width() // 200) - 1)
        row = col = 0
        for widget in self.sensorsetuptables:
            self.sensorsetlayout.addWidget(widget, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._populate_layouts()

    # ---------- static helpers ---------------------------------------------

    @staticmethod
    def _clear_layout(layout):
        """只把控件从布局中拿掉，但保留实例本身"""
        while (item := layout.takeAt(0)) is not None:
            widget = item.widget()
            if widget is not None:
                layout.removeWidget(widget)
                widget.setParent(None)  # ← 保留对象，不 deleteLater
            elif (sub := item.layout()) is not None:
                MyMainWindow._clear_layout(sub)

    @staticmethod
    def ask_sensor_count(default: int = 1, maximum: int = 64) -> int:
        """Modal dialog asking the user how many sensors to create."""
        count, ok = QtWidgets.QInputDialog.getInt(
            None,
            "Sensor count",
            "How many sensors do you want to monitor?",
            default, 1, maximum, 1,
        )
        if not ok:
            QtWidgets.QApplication.quit()
            sys.exit(0)
        return count

    def add_log(self, text, type='info'):
        "done"
        self.logindex += 1
        if type:
            if type == 'info':
                self.textBrowser.append(f"{self.logindex} <font color='black'> [{type}] {text}</font>")
            elif type == 'sensor setup':
                self.textBrowser.append(f"{self.logindex} <font color='orange'> [{type}] {text}</font>")
            elif type == 'sensor data process':
                self.textBrowser.append(f"{self.logindex} <font color='green'> [{type}] {text}</font>")
            # elif type == 'frontend':
            #     self.textBrowser.append(f"{self.logindex} <font color='blue'> [{type}] {text}</font>")
            elif type == 'error':
                self.textBrowser.append(f"{self.logindex}<font color='red'> [{type}] {text}</font>")
        self.textBrowser.verticalScrollBar().setValue(self.textBrowser.verticalScrollBar().maximum())
        self.textBrowser.moveCursor(self.textBrowser.textCursor().End)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    sensor_count = MyMainWindow.ask_sensor_count()
    window = MyMainWindow(sensor_count)
    window.show()
    sys.exit(app.exec_())

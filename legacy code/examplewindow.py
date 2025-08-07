import sys
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QObject,pyqtSignal, QSocketNotifier
from dashboard_templates import DataReceiver, AddToWindow
from PyQt6.QtNetwork import QUdpSocket, QHostAddress
import json
import socket

class Window(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("PyQt Driver Dashboard")
        self.resize(1920, 1080)
        self.allwidgets = {}
        

        self.initUI()
        self.receiver = DataReceiver()
        print(f"Receiver created: {self.receiver}")
        self.receiver.data_received.connect(self.route_signal)

    def initUI(self):
        mainlayout = QVBoxLayout()

        # (widgetname, signalname, label, minvalue (not needed for light), maxvalue (not needed for light), num of ticks (only needed for tickbar))
        row1 = [("Gauge", "RPM", "RPM", 0, 2200, None),
                ("Gauge", "OilPress", "Oil Pressure (psi)", 0, 100, None),]
        mainlayout.addLayout(self.widget_row(row1))
        row2 = [("Light", "RPM_Above_1700", "HighRPMFlag", 0, 1, None),
                ("Tickbar", "BatteryVoltage", "BatVolt", 10, 14.4, 20)]
        mainlayout.addLayout(self.widget_row(row2))
        self.setLayout(mainlayout)

    def widget_row(self, widgets):
        row_layout = QHBoxLayout()
        for widget in widgets:
            widget_creator = AddToWindow(self, *widget)
            widget_name = f"{widget[0]}_{widget[1]}"  
            row_layout.addWidget(self.allwidgets[widget_name])
        return row_layout

    def route_signal(self, name, value):
        for key, a in self.allwidgets.items():
            self.allwidgets[key].set_value(value,name)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = Window()
    dashboard.show()
    sys.exit(app.exec())
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QObject,pyqtSignal, QSocketNotifier
from dashboard_templates import LightWidget, GaugeWidget, TickBar, DataReceiver
from PyQt6.QtNetwork import QUdpSocket, QHostAddress
import json
import socket

class Window(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("PyQt Driver Dashboard")
        self.resize(1920, 1080)
        

        self.initUI()
        self.receiver = DataReceiver()
        print(f"Receiver created: {self.receiver}")
        self.receiver.data_received.connect(self.route_signal)

    def initUI(self):
        # GaugeWidget setup for Oil Temp 
        self.gauge1 = GaugeWidget(0, 255, "Oil Temp (F)", "EngOilTemp_Cval")
        self.gauge1.setFixedSize(250, 250)

        gauge_layout1 = QVBoxLayout()
        gauge_layout1.setSpacing(0)        
        gauge_layout1.addWidget(self.gauge1)
        gauge_layout1.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # GaugeWidget setup for Coolant temp
        self.gauge2 = GaugeWidget(0, 255, "Coolant Temp (F)", "EngCoolTemp_Cval")
        self.gauge2.setFixedSize(250, 250)

        gauge_layout2 = QVBoxLayout()
        gauge_layout2.setSpacing(0)        
        gauge_layout2.addWidget(self.gauge2)
        gauge_layout2.setAlignment(Qt.AlignmentFlag.AlignTop)


        # GaugeWidget setup for Oil pressure
        self.gauge3 = GaugeWidget(10, 80, "Oil Pressure (psi)", "EngOilPress_Cval_CPC")
        self.gauge3.setFixedSize(250, 250)

        gauge_layout3 = QVBoxLayout()
        gauge_layout3.setSpacing(0)        
        gauge_layout3.addWidget(self.gauge3)
        gauge_layout3.setAlignment(Qt.AlignmentFlag.AlignTop)

        
        # TickBar setup for system voltage
        self.tickbar1 = TickBar(-14.4, 14.4, 30, "System Voltage","SysVolt_Stat")
        self.tickbar1.setFixedSize(250,60)

        tickbar1_layout = QVBoxLayout()
        tickbar1_layout.setSpacing(0)
        tickbar1_layout.addWidget(self.tickbar1)
        tickbar1_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # LightWidget for Eng. Protection Shutdown Engine flag
        self.light1 = LightWidget("Eng. Prot. Shtdn. Flag", "EngProtShtdnEng_Stat_CPC")
        self.light1.setFixedSize(200, 200)

        light_layout1 = QVBoxLayout()
        light_layout1.setSpacing(0)
        light_layout1.addWidget(self.light1)
        light_layout1.setAlignment(Qt.AlignmentFlag.AlignTop)


        # Combine both layouts
        main_layout1 = QHBoxLayout()
        main_layout1.addLayout(gauge_layout1)
        main_layout1.addLayout(gauge_layout2)
        main_layout1.addLayout(gauge_layout3)
        
        main_layout2 = QHBoxLayout()
        #main_layout2.addLayout(light_layout1)
        main_layout2.addLayout(tickbar1_layout)

        window_layout = QVBoxLayout()
        window_layout.addLayout(main_layout1)
        window_layout.addLayout(main_layout2)

        self.setLayout(window_layout)

    
    def route_signal(self, name, value):
        self.gauge1.set_value(value,name)
        self.gauge2.set_value(value,name)
        self.gauge3.set_value(value,name)
        self.tickbar1.set_value(value,name)
        self.light1.set_value(value,name)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = Window()
    dashboard.show()
    sys.exit(app.exec())

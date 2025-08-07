from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QFontMetrics
from PyQt6.QtCore import Qt, QPointF, QRectF, QObject, pyqtSignal, QSocketNotifier
from PyQt6.QtNetwork import QUdpSocket, QHostAddress
import math
import json
import socket

# creator class for the tickbar widget
class Tickbar(QWidget):
    def __init__(self, min_value, max_value, numticks, tickbar_label, signalname, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_value = max_value
        self.min_value = min_value
        self.current_value = 0
        self.numticks = numticks
        self.tickbar_label = tickbar_label
        self.signalname = signalname
        self.setMinimumHeight(10)  

    # function to update value of tickbar based on incoming udp packets
    def set_value(self, value, name):
        if name == self.signalname:
            self.current_value = max(self.min_value, min(value, self.max_value))
            self.update()

    # drawing function to create tickbar
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        

        w = self.width()
        h = self.height()
        spacing = 4
        tick_width = (w - (self.numticks - 1) * spacing) / self.numticks
        tick_height = h * 0.6   
        y_offset = (h * 0.2 - tick_height) / 2  


        active_ticks = int(
            (self.current_value - self.min_value) / (self.max_value - self.min_value) * self.numticks
        )

        for i in range(self.numticks):
            x = i * (tick_width + spacing)
            color = QColor(255, 215, 0) if i < active_ticks else QColor(80, 80, 80)

            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(
                QRectF(x, y_offset, tick_width, tick_height), 6, 6
            )

        self.draw_label(painter)
    
    # drawing function to add widget label
    def draw_label(self, painter):
        painter.setFont(QFont("Arial", 12))
        fm = QFontMetrics(painter.font())

        label_text = self.tickbar_label 
        text_width = fm.horizontalAdvance(label_text)

        center_x = self.width() / 2
        label_y = self.height() - 10  

        painter.setPen(QColor(100, 100, 100))  
        painter.drawText(
            int(center_x - text_width / 2),
            int(label_y),
            label_text
        )

# creator class for the gauge widget
class Gauge(QWidget):
    def __init__(self, min_value, max_value, gauge_label, signalname, parent=None):
        super().__init__(parent)
        self.value = 0
        self.min_value = min_value
        self.max_value = max_value
        self.gauge_label = gauge_label
        self.signalname = signalname

    # function to update value of tickbar based on incoming udp packets
    def set_value(self, value, name):
        if name == self.signalname:
            if self.min_value <= value <= self.max_value:
                self.value = value
                self.update() 

    # drawing function to create gauge
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw gauge arc
        rect = QRectF(10, 10, self.width() - 20, self.height() - 20)
        start_angle = 225 * 16 # Start at 225 degrees, pyqt counts in 1/16ths of a degree
        span_angle = -270 * 16 # Span 270 degrees counter-clockwise
        painter.setPen(QPen(QColor(100, 100, 100), 5))
        painter.drawArc(rect, start_angle, span_angle)

        self.draw_scale_numbers(painter)
        self.draw_label(painter)

        # Draw gauge needle
        needle_length = min(self.width(), self.height()) / 2 * 0.8
        center = QPointF(self.width() / 2, self.height() / 2)
        
        
        normalized_value = (self.value - self.min_value) / (self.max_value - self.min_value)
        angle_rad = math.radians(225 - (normalized_value * 270)) 
        
        needle_end = QPointF(
            center.x() + needle_length * math.cos(angle_rad),
            center.y() - needle_length * math.sin(angle_rad) # Y-axis is inverted in Qt
        )

        painter.setPen(QPen(QColor(255, 0, 0), 3))
        painter.drawLine(center, needle_end)

        # Draw center circle
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.drawEllipse(center, 5, 5)

        painter.end()
        
    # drawing function for numbers on gauge
    def draw_scale_numbers(self, painter):
        painter.setFont(QFont("Arial", 10)) 
        fm = QFontMetrics(painter.font())

        center = QPointF(self.width() / 2, self.height() / 2)
        radius = min(self.width(), self.height()) / 2 - 30  
        num_divisions = 10  
        angle_start = 225
        angle_span = 270

        for i in range(num_divisions + 1):
            value = self.min_value + (self.max_value - self.min_value) * i / num_divisions
            text = str(int(value))

            angle_deg = angle_start - (angle_span * i / num_divisions)
            angle_rad = math.radians(angle_deg)

            x = center.x() + radius * math.cos(angle_rad)
            y = center.y() - radius * math.sin(angle_rad)

            text_width = fm.horizontalAdvance(text)
            text_height = fm.height()

            painter.drawText(
                int(x - text_width / 2),
                int(y + text_height / 4),
                text
            )
    
    # drawing function for gauge label
    def draw_label(self, painter):
        painter.setFont(QFont("Arial", 12))
        fm = QFontMetrics(painter.font())

        label_text = self.gauge_label  
        text_width = fm.horizontalAdvance(label_text)

        center_x = self.width() / 2
        label_y = self.height() - 20  

        painter.drawText(
            int(center_x - text_width / 2),
            int(label_y),
            label_text
        )

# creator class for the light widget
class Light(QWidget):
    def __init__(self, light_label, signalname, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = 0
        self.min_value = 0
        self.max_value = 1 
        self.light_label = light_label
        self.signalname = signalname

    # function to update value of tickbar based on incoming udp packets
    def set_value(self, value, name):
        if name == self.signalname:
            if self.min_value <= value <= self.max_value:
                self.value = value
                self.update()

    # drawing function to create light
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(100, 100, 100), 5))

        # Circle parameters
        circle_diameter = min(self.width(), self.height()) // 2
        center_x = self.width() // 2
        center_y = self.height() // 2 - 10  

        top_left_x = center_x - circle_diameter // 2
        top_left_y = center_y - circle_diameter // 2

        color = QColor(128, 128, 128) if self.value == 0 else QColor(255, 0, 0) 
        painter.setBrush(color)
        painter.drawEllipse(top_left_x, top_left_y, circle_diameter, circle_diameter)

        self.draw_label(painter)

    # drawing function to add label to widget
    def draw_label(self, painter):
        painter.setFont(QFont("Arial", 12))
        fm = QFontMetrics(painter.font())

        label_text = self.light_label  
        text_width = fm.horizontalAdvance(label_text)

        center_x = self.width() / 2
        label_y = self.height() - fm.descent() 

        painter.drawText(
            int(center_x - text_width / 2),
            int(label_y),
            label_text
        )

# class to create instance of UDP packet receiving object
class DataReceiver(QObject):
    data_received = pyqtSignal(str, float)

    def __init__(self):
        super().__init__()
        self.socket = QUdpSocket()
        if self.socket.bind(QHostAddress(QHostAddress.SpecialAddress.LocalHost), 6000):
            print("[DataReceiver] Bound to 6000")
        else:
            print("[DataReceiver] Failed to bind")

        self.socket.readyRead.connect(self.read_data)

    # function to actually read the data as it comes in
    def read_data(self):
        while self.socket.hasPendingDatagrams():
            datagram, _, _ = self.socket.readDatagram(self.socket.pendingDatagramSize())
            try:
                data = datagram.decode()
                parsed = json.loads(data)
                for key, value in parsed.items():
                    self.data_received.emit(key, float(value))
            except Exception as e:
                print(f"Failed to parse datagram: {e}")

# class to create a new instance of a dashboard widget object, with remove widget button
class AddToWindow(QWidget):
    def __init__(self, parent, widgetname, signalname, label, minvalue, maxvalue, numticks, i, j, remove_callback, *args, **kwargs):
        super().__init__()
        self.parent = parent
        self.widgetname = widgetname
        self.signalname = signalname
        self.label = label
        self.min_value = minvalue
        self.max_value = maxvalue
        self.numticks = numticks
        self.name = f"{self.widgetname}_{self.signalname}"
        self.i = i
        self.j = j

        self.remove_callback = remove_callback # callback to work out the removal of the widgets

        self.container = self.new_widget()
        
    # function to create the widget container, which holds the new dashboard widget object AND the remove button in one vertical layout
    def new_widget(self):
        container = QWidget()
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0,0,0,0)
        vbox.setSpacing(5)

        if self.widgetname == 'Gauge':
            temp = Gauge(self.min_value, self.max_value,self.label,self.signalname)
            temp.setFixedSize(250,250)
            name = f'Gauge_{self.signalname}'

        elif self.widgetname == 'Light':
            temp = Light(self.label,self.signalname)
            temp.setFixedSize(100,100)
            name = f'Light_{self.signalname}'

        elif self.widgetname == 'Tickbar':
            temp = Tickbar(self.min_value, self.max_value,self.numticks,self.label,self.signalname)
            temp.setFixedSize(250,60)
            name = f'Tickbar_{self.signalname}'
        
        else:
            raise ValueError(f"Widget type not found.")

        setattr(self, name, temp)
        value = {"widget_type" : f"{self.widgetname}",
                 "signal" : f"{self.signalname}",
                 "label" : f"{self.label}",
                 "minvalue" : f"{self.min_value}",
                 "maxvalue" : f"{self.max_value}",
                 "numticks" : f"{self.numticks}",
                 "placement" : (self.i,self.j)}
        
        self.parent.allwidgets[name]=value

        vbox.addWidget(temp)

        remove_button = QPushButton('Remove')
        remove_button.setFixedHeight(20)
        vbox.addWidget(remove_button)

        container.setLayout(vbox)
        container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        container.setMinimumSize(250, 250)
       
       # function to remove the widget container if remove widget button is pressed
        def remove_widget():
            self.parent.layout.removeWidget(container)
            container.setParent(None)
            container.deleteLater()
            if name in self.parent.allwidgets:
                del self.parent.allwidgets[name]
            self.remove_callback() # refers to parent window/running code file that has remove_callback in it, adds back the add widget button to window

        remove_button.clicked.connect(remove_widget)

        return container
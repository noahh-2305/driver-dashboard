from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QDialog, QLabel,
    QComboBox, QLineEdit, QDialogButtonBox, QGridLayout, QHBoxLayout
)
from PyQt6.QtCore import Qt
from dashboard_templates import DataReceiver, AddToWindow

# Config dialog
class AddWidgetDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Widget")
        layout = QVBoxLayout()

        self.type_box = QComboBox()
        self.type_box.addItems(["Gauge", "Light", "Tickbar"])

        self.config_input1 = QLineEdit()
        self.config_input1.setPlaceholderText("Enter the signal name that you want to show on this widget::")

        self.config_input2 = QLineEdit()
        self.config_input2.setPlaceholderText("Enter the label for this widget::")

        self.config_input3 = QLineEdit()
        self.config_input3.setPlaceholderText("Enter the maximum value for this widget::")

        self.config_input4 = QLineEdit()
        self.config_input4.setPlaceholderText("Enter the minimum value for this widget::")

        self.config_input5 = QLineEdit()
        self.config_input5.setPlaceholderText("Enter the number of ticks if you selected a tickbar widget::")


        layout.addWidget(QLabel("Choose Widget Type:"))
        layout.addWidget(self.type_box)
        layout.addWidget(QLabel("Configuration:"))
        layout.addWidget(self.config_input1)
        layout.addWidget(self.config_input2)
        layout.addWidget(self.config_input3)
        layout.addWidget(self.config_input4)
        layout.addWidget(self.config_input5)

        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def getData(self):
        return {"type" : self.type_box.currentText(), 
                "signal" : self.config_input1.text(), 
                "label" : self.config_input2.text(), 
                "max": float(self.config_input3.text()), 
                "min" : float(self.config_input4.text()), 
                "ticks" : int(self.config_input5.text())}

# Each slot in the layout
class SlotWidget(QWidget):
    def __init__(self, parent_layout, all_widgets_dict):
        super().__init__()
        self.parent_layout = parent_layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.allwidgets = all_widgets_dict

        self.add_button = QPushButton("Add Widget +")
        self.add_button.clicked.connect(self.openAddDialog)
        self.layout.addWidget(self.add_button)

    def openAddDialog(self):
        dialog = AddWidgetDialog()
        if dialog.exec():
            data = dialog.getData()
            widget_type = data["type"]
            self.add_button.deleteLater()
            if widget_type == "Gauge":
                row = [("Gauge", data["signal"], data["label"], data["min"], data["max"], None)]
            elif widget_type == "Light":
                row = [("Light", data["signal"], data["label"], None, None, None)]
            elif widget_type == "Tickbar":
                row = [("Tickbar", data["signal"], data["label"], data["min"], data["max"], data["ticks"])]
            self.layout.addLayout(self.widget_row(row))

    def widget_row(self, widgets):
        row_layout = QHBoxLayout()
        for widget in widgets:
            widget_creator = AddToWindow(self, *widget, remove_callback=self.restore_add_button)
            widget_name = f"{widget[0]}_{widget[1]}"  
            row_layout.addWidget(widget_creator.container, alignment=Qt.AlignmentFlag.AlignHCenter)
        return row_layout
    
    def restore_add_button(self):
        self.add_button = QPushButton("Add Widget +")
        self.add_button.clicked.connect(self.openAddDialog)
        self.layout.addWidget(self.add_button)


class Window(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("PyQt Driver Dashboard")
        self.resize(1920, 1080)
        layout = QGridLayout()
        self.allwidgets = {}

        positions = [(i, j) for i in range(2) for j in range(3)]
        for pos in positions:
            slot = SlotWidget(layout, self.allwidgets)
            layout.addWidget(slot, *pos)

        self.setLayout(layout)
        self.receiver = DataReceiver()
        print(f"Receiver created: {self.receiver}")
        self.receiver.data_received.connect(self.route_signal)


    def route_signal(self, name, value):
        for key, a in self.allwidgets.items():
            self.allwidgets[key].set_value(value,name)

if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    window.show()
    app.exec()

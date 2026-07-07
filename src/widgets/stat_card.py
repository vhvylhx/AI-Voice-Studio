from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout


class StatCard(QFrame):

    def __init__(self, title):
        super().__init__()

        self.setMinimumHeight(120)

        self.setStyleSheet("""
        QFrame{
            border:1px solid #D8D8D8;
            border-radius:10px;
            background:white;
        }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.number = QLabel("0")
        self.number.setAlignment(Qt.AlignCenter)
        self.number.setStyleSheet("""
            font-size:30px;
            font-weight:bold;
        """)

        self.title = QLabel(title)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("""
            color:gray;
            font-size:14px;
        """)

        layout.addWidget(self.number)
        layout.addWidget(self.title)

    def set_value(self, value):
        self.number.setText(str(value))
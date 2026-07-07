from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class ProjectPage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel("Dự án")
        title.setStyleSheet("""
            font-size:28px;
            font-weight:bold;
        """)

        layout.addWidget(title)
        layout.addStretch()

        self.setLayout(layout)
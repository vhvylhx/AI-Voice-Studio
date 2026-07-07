from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class ProjectCard(QFrame):

    clicked = Signal(object)

    def __init__(self, project):

        super().__init__()

        self.project = project

        self.setObjectName("ProjectCard")

        layout = QVBoxLayout(self)

        self.title = QLabel(project.name)

        self.engine = QLabel(
            f"Engine : {project.config.engine or '-'}"
        )

        self.voice = QLabel(
            f"Voice : {project.config.voice or '-'}"
        )

        self.open_button = QPushButton("Mở Project")

        layout.addWidget(self.title)
        layout.addWidget(self.engine)
        layout.addWidget(self.voice)
        layout.addStretch()
        layout.addWidget(self.open_button)

        self.open_button.clicked.connect(
            self.emit_clicked
        )

    def emit_clicked(self):

        self.clicked.emit(self.project)
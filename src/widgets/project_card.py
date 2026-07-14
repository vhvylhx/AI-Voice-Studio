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

        self.setObjectName(
            "ProjectCard"
        )

        layout = QVBoxLayout(self)

        self.title = QLabel(
            f"📁 {project.name}"
        )

        self.text = QLabel(
            f"📄 {project.input_dir}"
        )

        self.audio = QLabel(
            f"🎵 {project.output_dir}"
        )

        self.voice = QLabel(
            f"🎤 {project.config.voice or '-'}"
        )

        self.format = QLabel(
            f"💿 {project.config.output_format}"
        )

        self.open_button = QPushButton(
            "Mở Project"
        )

        layout.addWidget(
            self.title
        )

        layout.addWidget(
            self.text
        )

        layout.addWidget(
            self.audio
        )

        layout.addWidget(
            self.voice
        )

        layout.addWidget(
            self.format
        )

        layout.addStretch()

        layout.addWidget(
            self.open_button
        )

        self.open_button.clicked.connect(
            self.emit_clicked
        )

    def emit_clicked(self):

        self.clicked.emit(
            self.project
        )
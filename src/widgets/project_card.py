from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class ProjectCard(QFrame):

    def __init__(self, project):

        super().__init__()

        self.project = project

        self.setMinimumHeight(150)

        self.setStyleSheet("""
        QFrame{
            border:1px solid #D8D8D8;
            border-radius:10px;
            background:white;
        }
        """)

        layout = QVBoxLayout(self)

        title = QLabel(project.name)

        title.setStyleSheet("""
            font-size:18px;
            font-weight:bold;
        """)

        layout.addWidget(title)

        layout.addWidget(
            QLabel(
                f"Engine : {project.config.engine or '-'}"
            )
        )

        layout.addWidget(
            QLabel(
                f"Voice : {project.config.voice or '-'}"
            )
        )

        layout.addWidget(
            QLabel(
                f"Rule : {project.config.rule or '-'}"
            )
        )

        layout.addStretch()

        self.open_button = QPushButton("Mở Project")

        layout.addWidget(
            self.open_button,
            alignment=Qt.AlignRight
        )
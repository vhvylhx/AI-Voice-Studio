from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class VoiceCard(QFrame):

    clicked = Signal(object)

    def __init__(self, voice):

        super().__init__()

        self.voice = voice

        self.setObjectName("VoiceCard")

        layout = QVBoxLayout(self)

        self.name = QLabel(voice.name)

        self.engine = QLabel(
            f"Engine : {voice.config.engine or '-'}"
        )

        self.language = QLabel(
            f"Language : {voice.config.language}"
        )

        self.open_button = QPushButton(
            "Chọn Voice"
        )

        layout.addWidget(self.name)
        layout.addWidget(self.engine)
        layout.addWidget(self.language)
        layout.addStretch()
        layout.addWidget(self.open_button)

        self.open_button.clicked.connect(
            self.emit_clicked
        )

    def emit_clicked(self):

        self.clicked.emit(self.voice)
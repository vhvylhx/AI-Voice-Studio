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

        self.setObjectName(
            "VoiceCard"
        )

        layout = QVBoxLayout(
            self
        )

        self.name = QLabel(
            voice.name
        )

        self.engine = QLabel(
            f"Engine : {voice.config.engine}"
        )

        self.status = QLabel(
            "Ready"
            if voice.trained
            else "New"
        )

        dataset = "-"

        if (
            voice.dataset_dir
            and voice.dataset_dir.exists()
        ):

            count = len(
                list(
                    voice.dataset_dir.glob(
                        "*.wav"
                    )
                )
            )

            dataset = (
                f"{count} wav"
            )

        self.dataset = QLabel(
            f"Dataset : {dataset}"
        )

        self.preview = QLabel(
            "Preview : ✔"
            if voice.preview.exists()
            else "Preview : -"
        )

        self.open_button = QPushButton(
            "Chọn Voice"
        )

        layout.addWidget(
            self.name
        )

        layout.addWidget(
            self.engine
        )

        layout.addWidget(
            self.status
        )

        layout.addWidget(
            self.dataset
        )

        layout.addWidget(
            self.preview
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
            self.voice
        )
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QFormLayout,
)


class VoiceDetail(QWidget):

    def __init__(self):

        super().__init__()

        layout = QFormLayout(self)

        self.name = QLabel("-")
        self.engine = QLabel("-")
        self.language = QLabel("-")
        self.status = QLabel("-")

        layout.addRow(
            "Voice",
            self.name
        )

        layout.addRow(
            "Engine",
            self.engine
        )

        layout.addRow(
            "Language",
            self.language
        )

        layout.addRow(
            "Status",
            self.status
        )

    def clear(self):

        self.name.setText("-")
        self.engine.setText("-")
        self.language.setText("-")
        self.status.setText("-")

    def load(self, voice):

        self.name.setText(
            voice.name
        )

        self.engine.setText(
            voice.config.engine or "-"
        )

        self.language.setText(
            voice.config.language
        )

        self.status.setText(
            voice.status
        )
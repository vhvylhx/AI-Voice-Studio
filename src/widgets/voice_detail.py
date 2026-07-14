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

        self.model = QLabel("-")

        self.dataset = QLabel("-")

        self.preview = QLabel("-")

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
            "Model",
            self.model
        )

        layout.addRow(
            "Dataset",
            self.dataset
        )

        layout.addRow(
            "Preview",
            self.preview
        )

        layout.addRow(
            "Status",
            self.status
        )

    def clear(self):

        self.name.setText("-")

        self.engine.setText("-")

        self.language.setText("-")

        self.model.setText("-")

        self.dataset.setText("-")

        self.preview.setText("-")

        self.status.setText("-")

    def load(
        self,
        voice,
    ):

        self.name.setText(
            voice.name
        )

        self.engine.setText(
            voice.config.engine or "-"
        )

        self.language.setText(
            voice.config.language
        )

        self.model.setText(
            voice.config.model or "-"
        )

        if hasattr(
            voice,
            "dataset_dir",
        ):

            self.dataset.setText(
                voice.dataset_dir.name
            )

        else:

            self.dataset.setText("-")

        self.preview.setText(

            "Có"

            if voice.preview.exists()

            else "Chưa có"

        )

        self.status.setText(

            voice.config.training_status

        )
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QFormLayout,
)


class ProjectDetail(QWidget):

    def __init__(self):

        super().__init__()

        layout = QFormLayout(self)

        self.name = QLabel("-")

        self.text = QLabel("-")

        self.audio = QLabel("-")

        self.export = QLabel("-")

        self.voice = QLabel("-")

        self.format = QLabel("-")

        self.status = QLabel("-")

        layout.addRow(
            "Project",
            self.name
        )

        layout.addRow(
            "Text Folder",
            self.text
        )

        layout.addRow(
            "Audio Folder",
            self.audio
        )

        layout.addRow(
            "Export Folder",
            self.export
        )

        layout.addRow(
            "Default Voice",
            self.voice
        )

        layout.addRow(
            "Output Format",
            self.format
        )

        layout.addRow(
            "Status",
            self.status
        )

    def clear(self):

        self.name.setText("-")

        self.text.setText("-")

        self.audio.setText("-")

        self.export.setText("-")

        self.voice.setText("-")

        self.format.setText("-")

        self.status.setText("-")

    def load(self, project):

        self.name.setText(
            project.name
        )

        self.text.setText(
            str(project.input_dir)
        )

        self.audio.setText(
            str(project.output_dir)
        )

        self.export.setText(
            str(project.path / "export")
        )

        self.voice.setText(
            project.config.voice or "-"
        )

        self.format.setText(
            project.config.output_format
        )

        self.status.setText(
            project.status
        )
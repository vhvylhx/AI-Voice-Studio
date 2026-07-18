from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QWidget,
)


class ProjectDetail(QWidget):

    def __init__(
        self,
    ):

        super().__init__()

        layout = QFormLayout(
            self
        )

        self.name = QLabel("-")
        self.project_id = QLabel("-")
        self.location = QLabel("-")
        self.text = QLabel("-")
        self.audio = QLabel("-")
        self.export = QLabel("-")
        self.voice = QLabel("-")
        self.format = QLabel("-")
        self.status = QLabel("-")
        self.health = QLabel("-")
        self.reference_assets = QLabel("-")
        self.managed_assets = QLabel("-")
        self.external_assets = QLabel("-")
        self.missing_assets = QLabel("-")
        self.corrupt_assets = QLabel("-")

        for label, widget in [
            ("Project", self.name),
            ("Project ID", self.project_id),
            ("Location", self.location),
            ("Text Folder", self.text),
            ("Audio Folder", self.audio),
            ("Export Folder", self.export),
            ("Default Voice", self.voice),
            ("Output Format", self.format),
            ("Status", self.status),
            ("Health", self.health),
            ("Reference Assets", self.reference_assets),
            ("Managed Assets", self.managed_assets),
            ("External-only", self.external_assets),
            ("Missing Assets", self.missing_assets),
            ("Corrupt Assets", self.corrupt_assets),
        ]:

            widget.setWordWrap(
                True
            )

            layout.addRow(
                label,
                widget,
            )

    def clear(
        self,
    ):

        for widget in [
            self.name,
            self.project_id,
            self.location,
            self.text,
            self.audio,
            self.export,
            self.voice,
            self.format,
            self.status,
            self.health,
            self.reference_assets,
            self.managed_assets,
            self.external_assets,
            self.missing_assets,
            self.corrupt_assets,
        ]:

            widget.setText(
                "-"
            )

    def load(
        self,
        project,
    ):

        self.name.setText(
            project.display_name
        )
        self.project_id.setText(
            project.id
        )
        self.location.setText(
            str(
                project.path
            )
        )
        self.text.setText(
            str(
                project.input_dir
            )
        )
        self.audio.setText(
            str(
                project.output_dir
            )
        )
        self.export.setText(
            str(
                project.export_dir
            )
        )
        self.voice.setText(
            project.config.voice or "-"
        )
        self.format.setText(
            project.config.output_format
        )
        self.status.setText(
            project.config.status
        )
        self.health.setText(
            project.config.health_state
        )

        summary = dict(
            project.config.reference_summary or {}
        )

        self.reference_assets.setText(
            str(
                summary.get(
                    "total",
                    0,
                )
            )
        )
        self.managed_assets.setText(
            str(
                summary.get(
                    "managed",
                    0,
                )
            )
        )
        self.external_assets.setText(
            str(
                summary.get(
                    "external_only",
                    0,
                )
            )
        )
        self.missing_assets.setText(
            str(
                summary.get(
                    "missing",
                    0,
                )
            )
        )
        self.corrupt_assets.setText(
            str(
                summary.get(
                    "corrupt",
                    0,
                )
            )
        )

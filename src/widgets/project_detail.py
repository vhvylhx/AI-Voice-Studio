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
        self.engine = QLabel("-")
        self.voice = QLabel("-")
        self.rule = QLabel("-")
        self.status = QLabel("-")

        layout.addRow("Project", self.name)
        layout.addRow("Engine", self.engine)
        layout.addRow("Voice", self.voice)
        layout.addRow("Rule", self.rule)
        layout.addRow("Status", self.status)

    def clear(self):

        self.name.setText("-")
        self.engine.setText("-")
        self.voice.setText("-")
        self.rule.setText("-")
        self.status.setText("-")

    def load(self, project):

        self.name.setText(project.name)

        self.engine.setText(
            project.config.engine or "-"
        )

        self.voice.setText(
            project.config.voice or "-"
        )

        self.rule.setText(
            project.config.rule or "-"
        )

        self.status.setText(project.status)
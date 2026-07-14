from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
)


class AudioToolbar(QWidget):

    def __init__(self):

        super().__init__()

        layout = QHBoxLayout(self)

        layout.addWidget(
            QLabel("Project")
        )

        self.project_combo = QComboBox()

        self.project_combo.addItem(
            "Không chọn"
        )

        layout.addWidget(
            self.project_combo
        )

        layout.addSpacing(
            15
        )

        layout.addWidget(
            QLabel("Voice")
        )

        self.voice_combo = QComboBox()

        layout.addWidget(
            self.voice_combo
        )

        layout.addStretch()

        self.paste_button = QPushButton(
            "📋 Paste"
        )

        self.open_button = QPushButton(
            "📂 Open TXT"
        )

        self.add_queue_button = QPushButton(
            "➕ Queue"
        )

        self.generate_button = QPushButton(
            "▶ Generate"
        )

        self.stop_button = QPushButton(
            "■ Stop"
        )

        self.clear_queue_button = QPushButton(
            "🗑 Queue"
        )

        self.refresh_button = QPushButton(
            "🔄"
        )

        layout.addWidget(
            self.paste_button
        )

        layout.addWidget(
            self.open_button
        )

        layout.addWidget(
            self.add_queue_button
        )

        layout.addWidget(
            self.generate_button
        )

        layout.addWidget(
            self.stop_button
        )

        layout.addWidget(
            self.clear_queue_button
        )

        layout.addWidget(
            self.refresh_button
        )
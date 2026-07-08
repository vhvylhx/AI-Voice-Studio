from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
)


class AudioToolbar(QWidget):

    def __init__(self):

        super().__init__()

        layout = QHBoxLayout(self)

        self.add_queue_button = QPushButton(
            "➕ Thêm Queue"
        )

        self.generate_button = QPushButton(
            "▶ Generate"
        )

        self.stop_button = QPushButton(
            "■ Stop"
        )

        self.clear_queue_button = QPushButton(
            "🗑 Xóa Queue"
        )

        self.refresh_button = QPushButton(
            "🔄 Làm mới"
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

        layout.addStretch()

        layout.addWidget(
            self.refresh_button
        )
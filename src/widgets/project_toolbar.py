from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
)


class ProjectToolbar(QWidget):

    def __init__(self):

        super().__init__()

        layout = QHBoxLayout(self)

        self.new_button = QPushButton(
            "➕ Tạo"
        )

        self.rename_button = QPushButton(
            "✏ Đổi tên"
        )

        self.delete_button = QPushButton(
            "🗑 Xóa"
        )

        self.open_project_button = QPushButton(
            "📂 Project"
        )

        self.open_text_button = QPushButton(
            "📄 Text"
        )

        self.open_audio_button = QPushButton(
            "🎵 Audio"
        )

        self.open_export_button = QPushButton(
            "📦 Export"
        )

        self.refresh_button = QPushButton(
            "🔄 Làm mới"
        )

        layout.addWidget(
            self.new_button
        )

        layout.addWidget(
            self.rename_button
        )

        layout.addWidget(
            self.delete_button
        )

        layout.addSpacing(
            20
        )

        layout.addWidget(
            self.open_project_button
        )

        layout.addWidget(
            self.open_text_button
        )

        layout.addWidget(
            self.open_audio_button
        )

        layout.addWidget(
            self.open_export_button
        )

        layout.addStretch()

        layout.addWidget(
            self.refresh_button
        )
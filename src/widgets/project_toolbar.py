from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QWidget,
)


class ProjectToolbar(QWidget):

    def __init__(
        self,
    ):

        super().__init__()

        layout = QHBoxLayout(
            self
        )

        self.new_button = QPushButton(
            "➕ Tạo"
        )

        self.rename_button = QPushButton(
            "✏ Đổi tên"
        )

        self.delete_button = QPushButton(
            "📦 Archive"
        )

        self.duplicate_button = QPushButton(
            "📋 Nhân bản"
        )

        self.backup_button = QPushButton(
            "💾 Backup"
        )

        self.export_button = QPushButton(
            "📤 Export"
        )

        self.validate_button = QPushButton(
            "✅ Validate"
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
            "📦 Export Folder"
        )

        self.refresh_button = QPushButton(
            "🔄 Làm mới"
        )

        for button in [
            self.new_button,
            self.rename_button,
            self.delete_button,
            self.duplicate_button,
            self.backup_button,
            self.export_button,
            self.validate_button,
        ]:

            layout.addWidget(
                button
            )

        layout.addSpacing(
            20
        )

        for button in [
            self.open_project_button,
            self.open_text_button,
            self.open_audio_button,
            self.open_export_button,
        ]:

            layout.addWidget(
                button
            )

        layout.addStretch()

        layout.addWidget(
            self.refresh_button
        )

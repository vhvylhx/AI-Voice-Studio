from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QPushButton,
    QLabel,
    QTextEdit,
)


class SettingsPage(QWidget):

    def __init__(self):

        super().__init__()

        root = QVBoxLayout(self)

        #
        # Engine
        #

        engine_box = QGroupBox(
            "Engine"
        )

        engine_layout = QFormLayout(
            engine_box
        )

        self.engine = QLabel(
            "Chưa chọn"
        )

        self.add_engine = QPushButton(
            "Thêm Engine..."
        )

        self.remove_engine = QPushButton(
            "Xóa Engine"
        )

        self.default_engine = QPushButton(
            "Đặt mặc định"
        )

        engine_layout.addRow(
            "Engine",
            self.engine
        )

        engine_layout.addRow(
            self.add_engine
        )

        engine_layout.addRow(
            self.remove_engine
        )

        engine_layout.addRow(
            self.default_engine
        )

        #
        # Workspace
        #

        workspace_box = QGroupBox(
            "Workspace"
        )

        workspace_layout = QFormLayout(
            workspace_box
        )

        self.workspace = QLabel(
            "workspace/"
        )

        self.change_workspace = QPushButton(
            "Đổi Workspace"
        )

        workspace_layout.addRow(
            "Folder",
            self.workspace
        )

        workspace_layout.addRow(
            self.change_workspace
        )

        #
        # Text Processing
        #

        text_box = QGroupBox(
            "Text Processing"
        )

        text_layout = QFormLayout(
            text_box
        )

        self.edit_dictionary = QPushButton(
            "📖 Dictionary"
        )

        self.edit_pronunciation = QPushButton(
            "🔊 Pronunciation"
        )

        self.edit_ads = QPushButton(
            "🚫 Ads"
        )

        self.view_history = QPushButton(
            "📜 Lịch sử xử lý"
        )

        text_layout.addRow(
            self.edit_dictionary
        )

        text_layout.addRow(
            self.edit_pronunciation
        )

        text_layout.addRow(
            self.edit_ads
        )

        text_layout.addRow(
            self.view_history
        )

        #
        # Log
        #

        log_box = QGroupBox(
            "Log"
        )

        log_layout = QVBoxLayout(
            log_box
        )

        self.log = QTextEdit()

        self.log.setReadOnly(
            True
        )

        self.clear_log = QPushButton(
            "Xóa Log"
        )

        log_layout.addWidget(
            self.log
        )

        log_layout.addWidget(
            self.clear_log
        )

        root.addWidget(
            engine_box
        )

        root.addWidget(
            workspace_box
        )

        root.addWidget(
            text_box
        )

        root.addWidget(
            log_box
        )

        root.addStretch()
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QMessageBox,
)

from services.dataset_service import DatasetService
from widgets.dataset_tree import DatasetTree


class WorkspacePage(QWidget):

    def __init__(self):

        super().__init__()

        self.service = DatasetService()

        self.build_ui()

        self.refresh()

    def build_ui(self):

        root = QVBoxLayout(self)

        title = QLabel("Workspace")
        title.setStyleSheet("""
            font-size:22px;
            font-weight:bold;
        """)

        root.addWidget(title)

        toolbar = QHBoxLayout()

        self.refresh_button = QPushButton("🔄 Quét lại")
        self.open_button = QPushButton("📂 Mở thư mục")
        self.text_button = QPushButton("📄 Text Studio")

        toolbar.addWidget(self.refresh_button)
        toolbar.addWidget(self.open_button)
        toolbar.addWidget(self.text_button)
        toolbar.addStretch()

        root.addLayout(toolbar)

        self.tree = DatasetTree()

        root.addWidget(self.tree)

        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignRight)

        root.addWidget(self.status)

        self.refresh_button.clicked.connect(self.refresh)
        self.open_button.clicked.connect(self.open_workspace)
        self.text_button.clicked.connect(self.open_text_studio)

    def refresh(self):

        model = self.service.load()

        self.tree.load(model)

        self.status.setText(
            f"Dataset: {model.dataset_count} | "
            f"Text: {model.total_docx + model.total_txt} | "
            f"Audio: {model.total_mp3 + model.total_wav}"
        )

    def open_workspace(self):

        QMessageBox.information(
            self,
            "Workspace",
            "Sẽ mở thư mục Workspace ở Sprint tiếp theo."
        )

    def open_text_studio(self):

        QMessageBox.information(
            self,
            "Text Studio",
            "Text Studio sẽ được phát triển ở Sprint kế tiếp."
        )
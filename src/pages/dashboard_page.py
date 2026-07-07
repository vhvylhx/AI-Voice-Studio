from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from config.app_config import WORKSPACE_DIR
from services.dataset_service import DatasetService


class DashboardPage(QWidget):

    def __init__(self):
        super().__init__()

        self.service = DatasetService()

        self.setup_ui()

    def setup_ui(self):

        layout = QVBoxLayout()

        title = QLabel("Tổng quan")
        title.setStyleSheet("""
            font-size:28px;
            font-weight:bold;
        """)

        layout.addWidget(title)

        layout.addWidget(QLabel(f"Workspace: {WORKSPACE_DIR}"))

        datasets = self.service.scan()

        layout.addWidget(QLabel(f"Số Dataset: {len(datasets)}"))

        layout.addSpacing(15)

        if not datasets:

            layout.addWidget(QLabel("Chưa có Dataset."))

        else:

            for ds in datasets:

                layout.addWidget(
                    QLabel(
                        f"""📁 {ds.name}
MP3 : {ds.mp3_count}
DOCX: {ds.docx_count}
TXT : {ds.txt_count}
"""
                    )
                )

        layout.addStretch()

        self.setLayout(layout)
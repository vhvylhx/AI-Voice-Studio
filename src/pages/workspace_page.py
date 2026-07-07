from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QPushButton

from src.widgets.dataset_tree import DatasetTree
from src.services.dataset_service import DatasetService


class WorkspacePage(QWidget):

    def __init__(self):

        super().__init__()

        self.service = DatasetService()

        layout = QVBoxLayout(self)

        self.refresh_button = QPushButton("Quét Workspace")

        self.tree = DatasetTree()

        layout.addWidget(self.refresh_button)
        layout.addWidget(self.tree)

        self.refresh_button.clicked.connect(
            self.refresh
        )

        self.refresh()

    def refresh(self):

        model = self.service.load()

        self.tree.load(model)
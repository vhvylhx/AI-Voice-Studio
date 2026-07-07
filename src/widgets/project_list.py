from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout

from widgets.project_card import ProjectCard


class ProjectList(QWidget):

    project_selected = Signal(object)

    def __init__(self):

        super().__init__()

        self.layout = QVBoxLayout(self)

        self.layout.addStretch()

    def clear(self):

        while self.layout.count() > 1:

            item = self.layout.takeAt(0)

            if item.widget():

                item.widget().deleteLater()

    def load(self, projects):

        self.clear()

        for project in projects:

            card = ProjectCard(project)

            card.clicked.connect(
                self.project_selected.emit
            )

            self.layout.insertWidget(
                self.layout.count() - 1,
                card
            )
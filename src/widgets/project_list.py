from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QVBoxLayout

from widgets.project_card import ProjectCard


class ProjectList(QWidget):

    def __init__(self):

        super().__init__()

        self.layout = QVBoxLayout(self)

        self.layout.setContentsMargins(0, 0, 0, 0)

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

            self.layout.insertWidget(
                self.layout.count() - 1,
                card
            )
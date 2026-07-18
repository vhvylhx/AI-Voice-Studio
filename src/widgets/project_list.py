from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout

from widgets.project_card import ProjectCard
from widgets.project_card import TrashProjectCard


class ProjectList(QWidget):

    project_selected = Signal(object)
    project_rename_requested = Signal(object)
    project_delete_requested = Signal(object)
    trash_restore_requested = Signal(dict)
    trash_delete_requested = Signal(dict)

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

            card.rename_requested.connect(
                self.project_rename_requested.emit
            )

            card.delete_requested.connect(
                self.project_delete_requested.emit
            )

            self.layout.insertWidget(
                self.layout.count() - 1,
                card
            )

    def load_trash(self, items):

        self.clear()

        for item in items:

            card = TrashProjectCard(item)

            card.restore_requested.connect(
                self.trash_restore_requested.emit
            )

            card.delete_requested.connect(
                self.trash_delete_requested.emit
            )

            self.layout.insertWidget(
                self.layout.count() - 1,
                card
            )

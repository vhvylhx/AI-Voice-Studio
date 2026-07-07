from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSplitter,
    QInputDialog,
)

from services.project_service import ProjectService
from widgets.project_toolbar import ProjectToolbar
from widgets.project_list import ProjectList
from widgets.project_detail import ProjectDetail


class ProjectPage(QWidget):

    def __init__(self):

        super().__init__()

        self.service = ProjectService()

        root = QVBoxLayout(self)

        self.toolbar = ProjectToolbar()

        root.addWidget(self.toolbar)

        splitter = QSplitter()

        self.list = ProjectList()

        self.detail = ProjectDetail()

        splitter.addWidget(self.list)
        splitter.addWidget(self.detail)

        splitter.setSizes([500, 300])

        root.addWidget(splitter)

        self.toolbar.new_button.clicked.connect(
            self.create_project
        )

        self.toolbar.refresh_button.clicked.connect(
            self.refresh
        )

        self.list.project_selected.connect(
            self.show_project
        )

        self.refresh()

    def refresh(self):

        projects = []

        for name in self.service.list():

            projects.append(
                self.service.load(name)
            )

        self.list.load(projects)

        self.detail.clear()

    def create_project(self):

        name, ok = QInputDialog.getText(
            self,
            "Project",
            "Tên Project"
        )

        if not ok:
            return

        name = name.strip()

        if not name:
            return

        if self.service.exists(name):
            return

        self.service.create(name)

        self.refresh()

    def show_project(self, project):

        self.detail.load(project)
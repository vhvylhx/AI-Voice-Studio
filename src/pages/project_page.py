from pathlib import Path

from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSplitter,
    QInputDialog,
    QMessageBox,
)

from core.app_context import AppContext

from services.app_events import AppEvents

from widgets.project_toolbar import ProjectToolbar
from widgets.project_list import ProjectList
from widgets.project_detail import ProjectDetail


class ProjectPage(QWidget):

    def __init__(self):

        super().__init__()

        self.service = AppContext.project_service

        self.current_project = None

        root = QVBoxLayout(self)

        self.toolbar = ProjectToolbar()

        root.addWidget(
            self.toolbar
        )

        splitter = QSplitter()

        self.list = ProjectList()

        self.detail = ProjectDetail()

        splitter.addWidget(
            self.list
        )

        splitter.addWidget(
            self.detail
        )

        splitter.setSizes([
            500,
            300,
        ])

        root.addWidget(
            splitter
        )

        self.toolbar.new_button.clicked.connect(
            self.create_project
        )

        self.toolbar.rename_button.clicked.connect(
            self.rename_project
        )

        self.toolbar.delete_button.clicked.connect(
            self.delete_project
        )

        self.toolbar.open_project_button.clicked.connect(
            self.open_project_folder
        )

        self.toolbar.open_text_button.clicked.connect(
            self.open_text_folder
        )

        self.toolbar.open_audio_button.clicked.connect(
            self.open_audio_folder
        )

        self.toolbar.open_export_button.clicked.connect(
            self.open_export_folder
        )

        self.toolbar.refresh_button.clicked.connect(
            self.refresh
        )

        self.list.project_selected.connect(
            self.show_project
        )

        self.refresh()

    def refresh(self):

        self.current_project = None

        projects = []

        for name in self.service.list():

            projects.append(
                self.service.load(name)
            )

        self.list.load(
            projects
        )

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

        self.service.create(
            name
        )

        self.refresh()

    def rename_project(self):

        if self.current_project is None:
            return

        name, ok = QInputDialog.getText(
            self,
            "Đổi tên Project",
            "Tên mới",
            text=self.current_project.name
        )

        if not ok:
            return

        name = name.strip()

        if not name:
            return

        if name == self.current_project.name:
            return

        if self.service.exists(name):
            return

        self.service.rename(
            self.current_project.name,
            name
        )

        self.refresh()

    def delete_project(self):

        if self.current_project is None:
            return

        result = QMessageBox.question(
            self,
            "Xóa Project",
            f'Xóa "{self.current_project.name}" ?'
        )

        if result != QMessageBox.Yes:
            return

        self.service.delete(
            self.current_project.name
        )

        self.refresh()

    def open_project_folder(self):

        if self.current_project is None:
            return

        QDesktopServices.openUrl(
            QUrl.fromLocalFile(
                str(self.current_project.path)
            )
        )

    def open_text_folder(self):

        if self.current_project is None:
            return

        QDesktopServices.openUrl(
            QUrl.fromLocalFile(
                str(self.current_project.input_dir)
            )
        )

    def open_audio_folder(self):

        if self.current_project is None:
            return

        QDesktopServices.openUrl(
            QUrl.fromLocalFile(
                str(self.current_project.output_dir)
            )
        )

    def open_export_folder(self):

        if self.current_project is None:
            return

        QDesktopServices.openUrl(
            QUrl.fromLocalFile(
                str(self.current_project.export_dir)
            )
        )

    def show_project(self, project):

        self.current_project = project

        AppContext.current_project.set(
            project
        )

        AppEvents.project_changed(
            project
        )

        self.detail.load(
            project
        )
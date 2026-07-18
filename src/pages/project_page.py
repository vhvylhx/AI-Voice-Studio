from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from core.app_context import AppContext
from services.app_events import AppEvents
from widgets.project_detail import ProjectDetail
from widgets.project_list import ProjectList
from widgets.project_toolbar import ProjectToolbar
from widgets.ui_components import PageHeader
from widgets.ui_components import ScrollablePage


class ProjectPage(ScrollablePage):

    def __init__(
        self,
    ):

        super().__init__()

        self.service = AppContext.project_service
        self.current_project = None

        self.build_ui()
        self.refresh()

    def build_ui(
        self,
    ):

        self.body.addWidget(
            PageHeader(
                "Dự án",
                "Quản lý vòng đời Project: tạo, mở, đổi tên, nhân bản, archive, backup, export, validate và repair an toàn.",
            )
        )

        self.current_label = QLabel(
            "Project hiện tại: Chưa mở dự án"
        )
        self.current_label.setWordWrap(
            True
        )

        self.body.addWidget(
            self.current_label
        )

        self.toolbar = ProjectToolbar()

        self.body.addWidget(
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
        splitter.setSizes(
            [
                520,
                360,
            ]
        )

        self.body.addWidget(
            splitter
        )

        self.archive_box = QGroupBox(
            "Project đã Archive"
        )
        archive_layout = QVBoxLayout(
            self.archive_box
        )
        self.archive_list = ProjectList()
        self.restore_archive_button = QPushButton(
            "Khôi phục Project đang chọn"
        )
        archive_layout.addWidget(
            self.archive_list
        )
        archive_layout.addWidget(
            self.restore_archive_button
        )
        self.body.addWidget(
            self.archive_box
        )

        self.toolbar.new_button.clicked.connect(
            self.create_project
        )
        self.toolbar.rename_button.clicked.connect(
            self.rename_current_project
        )
        self.toolbar.delete_button.clicked.connect(
            self.archive_current_project
        )
        self.toolbar.duplicate_button.clicked.connect(
            self.duplicate_current_project
        )
        self.toolbar.backup_button.clicked.connect(
            self.backup_current_project
        )
        self.toolbar.export_button.clicked.connect(
            self.export_current_project
        )
        self.toolbar.validate_button.clicked.connect(
            self.validate_current_project
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
        self.restore_archive_button.clicked.connect(
            self.restore_current_archive
        )

        self.list.project_selected.connect(
            self.open_project
        )
        self.list.project_rename_requested.connect(
            self.rename_project
        )
        self.list.project_delete_requested.connect(
            self.archive_project
        )
        self.archive_list.project_selected.connect(
            self.show_project
        )
        self.archive_list.project_rename_requested.connect(
            self.rename_project
        )

    def refresh(
        self,
    ):

        self.current_project = None

        active = []
        archived = []

        for project in self.service.list_projects(
            include_archived=True
        ):

            if project.is_archived:

                archived.append(
                    project
                )

            else:

                active.append(
                    project
                )

        self.list.load(
            active
        )
        self.archive_list.load(
            archived
        )
        self.detail.clear()
        self.update_current_label()

    def update_current_label(
        self,
    ):

        if AppContext.current_project.has_project():

            project = AppContext.current_project.get()
            text = (
                f"Project hiện tại: {project.display_name} | "
                f"ID: {project.id} | {project.path}"
            )

        else:

            text = "Project hiện tại: Chưa mở dự án"

        self.current_label.setText(
            text
        )

    def create_project(
        self,
    ):

        name, ok = QInputDialog.getText(
            self,
            "Tạo Project",
            "Tên Project",
        )

        if not ok:

            return

        try:

            project = self.service.create(
                name,
                open_after_create=True,
                current_project_service=AppContext.current_project,
            )

        except Exception as exc:

            QMessageBox.warning(
                self,
                "Không tạo được Project",
                str(
                    exc
                ),
            )

            return

        AppEvents.project_changed(
            project
        )
        self.refresh()

    def open_project(
        self,
        project,
    ):

        opened = self.service.open_project(
            project.id,
            current_project_service=AppContext.current_project,
        )
        self.current_project = opened
        self.detail.load(
            opened
        )
        AppEvents.project_changed(
            opened
        )
        self.update_current_label()

    def show_project(
        self,
        project,
    ):

        self.current_project = project
        self.detail.load(
            project
        )

    def rename_current_project(
        self,
    ):

        if self.current_project is None:

            return

        self.rename_project(
            self.current_project
        )

    def rename_project(
        self,
        project,
    ):

        name, ok = QInputDialog.getText(
            self,
            "Đổi tên Project",
            "Tên hiển thị mới",
            text=project.display_name,
        )

        if not ok:

            return

        if self.service.normalize_display_name(
            name
        ) == project.display_name:

            return

        try:

            renamed = self.service.rename(
                project.id,
                name,
            )

        except Exception as exc:

            QMessageBox.warning(
                self,
                "Không đổi tên được",
                str(
                    exc
                ),
            )

            return

        if (
            AppContext.current_project.has_project()
            and AppContext.current_project.get().id == renamed.id
        ):

            AppContext.current_project.set(
                renamed
            )
            AppEvents.project_changed(
                renamed
            )

        self.current_project = renamed
        self.refresh()
        self.detail.load(
            renamed
        )

    def archive_current_project(
        self,
    ):

        if self.current_project is None:

            return

        self.archive_project(
            self.current_project
        )

    def archive_project(
        self,
        project,
    ):

        result = QMessageBox.question(
            self,
            "Archive Project",
            f'Archive "{project.display_name}"?\n\nDữ liệu không bị xóa.',
        )

        if result != QMessageBox.Yes:

            return

        archived = self.service.archive(
            project.id
        )

        if (
            AppContext.current_project.has_project()
            and AppContext.current_project.get().id == archived.id
        ):

            self.service.close_project(
                AppContext.current_project
            )
            AppEvents.project_changed(
                archived
            )

        self.refresh()

    def restore_current_archive(
        self,
    ):

        if self.current_project is None:

            return

        restored = self.service.restore_archive(
            self.current_project.id
        )
        self.current_project = restored
        self.refresh()
        self.detail.load(
            restored
        )

    def duplicate_current_project(
        self,
    ):

        if self.current_project is None:

            return

        name, ok = QInputDialog.getText(
            self,
            "Nhân bản Project",
            "Tên Project mới",
            text=f"{self.current_project.display_name} Copy",
        )

        if not ok:

            return

        try:

            duplicated = self.service.duplicate(
                self.current_project.id,
                name,
            )

        except Exception as exc:

            QMessageBox.warning(
                self,
                "Không nhân bản được",
                str(
                    exc
                ),
            )
            return

        self.refresh()
        self.detail.load(
            duplicated
        )

    def backup_current_project(
        self,
    ):

        if self.current_project is None:

            return

        result = self.service.backup_project(
            self.current_project.id
        )

        QMessageBox.information(
            self,
            "Backup",
            result[
                "backup_path"
            ],
        )

    def export_current_project(
        self,
    ):

        if self.current_project is None:

            return

        file, _ = QFileDialog.getSaveFileName(
            self,
            "Export Project",
            f"{self.current_project.id}.avproject.zip",
            "AI Voice Studio Project (*.zip *.avproject)",
        )

        if not file:

            return

        result = self.service.export_project(
            self.current_project.id,
            file,
        )

        QMessageBox.information(
            self,
            "Export",
            result[
                "package_file"
            ],
        )

    def validate_current_project(
        self,
    ):

        if self.current_project is None:

            return

        result = self.service.validate(
            self.current_project.id
        )

        self.current_project = self.service.load(
            self.current_project.id
        )
        self.detail.load(
            self.current_project
        )

        QMessageBox.information(
            self,
            "Project Health",
            f"Trạng thái: {result['state']}\nLỗi/cảnh báo: {len(result['messages'])}",
        )

    def open_project_folder(
        self,
    ):

        self.open_folder(
            self.current_project.path
            if self.current_project
            else None
        )

    def open_text_folder(
        self,
    ):

        self.open_folder(
            self.current_project.input_dir
            if self.current_project
            else None
        )

    def open_audio_folder(
        self,
    ):

        self.open_folder(
            self.current_project.output_dir
            if self.current_project
            else None
        )

    def open_export_folder(
        self,
    ):

        self.open_folder(
            self.current_project.export_dir
            if self.current_project
            else None
        )

    def open_folder(
        self,
        folder,
    ):

        if folder is None:

            return

        QDesktopServices.openUrl(
            QUrl.fromLocalFile(
                str(
                    folder
                )
            )
        )

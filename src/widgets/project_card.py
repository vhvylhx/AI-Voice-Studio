from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class ProjectCard(QFrame):

    clicked = Signal(object)
    rename_requested = Signal(object)
    delete_requested = Signal(object)

    def __init__(
        self,
        project,
    ):

        super().__init__()

        self.project = project

        self.setObjectName(
            "ProjectCard"
        )

        layout = QVBoxLayout(
            self
        )

        status = (
            "Archived"
            if project.is_archived
            else "Active"
        )

        self.title = QLabel(
            f"📁 {project.display_name}"
        )

        self.project_id = QLabel(
            f"ID: {project.id}"
        )

        self.path = QLabel(
            f"Root: {project.path}"
        )

        self.health = QLabel(
            f"Health: {project.health_state}"
        )

        self.status = QLabel(
            f"Status: {status}"
        )

        for label in [
            self.project_id,
            self.path,
            self.health,
            self.status,
        ]:

            label.setWordWrap(
                True
            )

        self.open_button = QPushButton(
            "Mở"
        )

        self.rename_button = QPushButton(
            "Đổi tên"
        )

        self.delete_button = QPushButton(
            "Archive"
        )

        actions = QHBoxLayout()

        for button in [
            self.open_button,
            self.rename_button,
            self.delete_button,
        ]:

            actions.addWidget(
                button
            )

        layout.addWidget(
            self.title
        )
        layout.addWidget(
            self.project_id
        )
        layout.addWidget(
            self.path
        )
        layout.addWidget(
            self.health
        )
        layout.addWidget(
            self.status
        )
        layout.addStretch()
        layout.addLayout(
            actions
        )

        self.open_button.clicked.connect(
            self.emit_clicked
        )
        self.rename_button.clicked.connect(
            self.emit_rename
        )
        self.delete_button.clicked.connect(
            self.emit_delete
        )

    def emit_clicked(
        self,
    ):

        self.clicked.emit(
            self.project
        )

    def emit_rename(
        self,
    ):

        self.rename_requested.emit(
            self.project
        )

    def emit_delete(
        self,
    ):

        self.delete_requested.emit(
            self.project
        )


class TrashProjectCard(QFrame):

    restore_requested = Signal(dict)
    delete_requested = Signal(dict)

    def __init__(
        self,
        item,
    ):

        super().__init__()

        self.item = item

        layout = QVBoxLayout(
            self
        )

        self.title = QLabel(
            f"📦 {item.get('project_name', '-')}"
        )

        self.project_id = QLabel(
            f"ID: {item.get('project_id', '-')}"
        )

        self.deleted_at = QLabel(
            f"Archived: {item.get('deleted_at', '-')}"
        )

        self.restore_button = QPushButton(
            "Khôi phục Archive"
        )

        self.delete_button = QPushButton(
            "Xóa vĩnh viễn (khóa)"
        )

        self.delete_button.setEnabled(
            False
        )

        actions = QHBoxLayout()
        actions.addWidget(
            self.restore_button
        )
        actions.addWidget(
            self.delete_button
        )

        layout.addWidget(
            self.title
        )
        layout.addWidget(
            self.project_id
        )
        layout.addWidget(
            self.deleted_at
        )
        layout.addLayout(
            actions
        )

        self.restore_button.clicked.connect(
            self.emit_restore
        )

    def emit_restore(
        self,
    ):

        self.restore_requested.emit(
            self.item
        )

    def emit_delete(
        self,
    ):

        self.delete_requested.emit(
            self.item
        )

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QListWidget
from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QTextEdit
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from core.app_context import AppContext
from services.style_profile_export_service import StyleProfileExportService
from widgets.ui_components import EmptyState
from widgets.ui_components import PageHeader
from widgets.ui_components import SectionCard
from widgets.ui_components import StatusBadge


class StyleProfileWizard(QDialog):

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent
        )

        self.setWindowTitle(
            "Tạo Phong cách đọc"
        )

        self.name_input = QLineEdit()

        self.description_input = QTextEdit()

        self.description_input.setFixedHeight(
            90
        )

        layout = QVBoxLayout(
            self
        )

        layout.addWidget(
            QLabel(
                "Bước 1/5 - Đặt tên Style Profile"
            )
        )

        layout.addWidget(
            self.name_input
        )

        layout.addWidget(
            QLabel(
                "Bước 2/5 - Mô tả phong cách đọc"
            )
        )

        layout.addWidget(
            self.description_input
        )

        layout.addWidget(
            QLabel(
                "Bước 3/5 - Chọn Dataset/Alignment sẽ làm ở sprint sau"
            )
        )

        layout.addWidget(
            QLabel(
                "Bước 4/5 - Trích xuất Voice DNA hiện đang ở trạng thái pending"
            )
        )

        layout.addWidget(
            QLabel(
                "Bước 5/5 - Kiểm tra readiness trước khi dùng Generate"
            )
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok
            | QDialogButtonBox.Cancel
        )

        buttons.accepted.connect(
            self.accept
        )

        buttons.rejected.connect(
            self.reject
        )

        layout.addWidget(
            buttons
        )


class StyleProfilePage(QWidget):

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent
        )

        self.service = AppContext.style_profile_service

        self.export_service = StyleProfileExportService(
            self.service.repository
        )

        self.items = []

        self.current_profile_id = ""

        self.build_ui()

        self.refresh()

    def build_ui(
        self,
    ):

        root = QVBoxLayout(
            self
        )

        root.addWidget(
            PageHeader(
                "Phong cách đọc / Voice DNA",
                "Quản lý dữ liệu tham chiếu giọng đọc tách riêng khỏi Voice model. Style Profile có thể dùng lại cho nhiều Voice.",
            )
        )

        action_bar = QHBoxLayout()

        self.create_button = QPushButton(
            "Tạo từ Dataset"
        )

        self.import_button = QPushButton(
            "Nhập .avstyle"
        )

        self.export_button = QPushButton(
            "Xuất .avstyle"
        )

        self.rename_button = QPushButton(
            "Đổi tên"
        )

        self.check_button = QPushButton(
            "Kiểm tra dữ liệu"
        )

        self.backup_button = QPushButton(
            "Backup"
        )

        for button in [
            self.create_button,
            self.import_button,
            self.export_button,
            self.rename_button,
            self.check_button,
            self.backup_button,
        ]:

            action_bar.addWidget(
                button
            )

        action_bar.addStretch(
            1
        )

        root.addLayout(
            action_bar
        )

        content = QHBoxLayout()

        self.list_widget = QListWidget()

        self.list_widget.setMinimumWidth(
            280
        )

        self.detail_card = SectionCard(
            "Chi tiết Style Profile",
            "Chọn một Style Profile để xem trạng thái, readiness và dữ liệu tham chiếu.",
        )

        self.detail_title = QLabel(
            "Chưa chọn"
        )

        self.detail_title.setObjectName(
            "sectionTitle"
        )

        self.detail_status = StatusBadge(
            "pending",
            "warning",
        )

        self.detail_text = QLabel(
            "Chưa có dữ liệu."
        )

        self.detail_text.setWordWrap(
            True
        )

        self.detail_card.body.addWidget(
            self.detail_title
        )

        self.detail_card.body.addWidget(
            self.detail_status
        )

        self.detail_card.body.addWidget(
            self.detail_text
        )

        content.addWidget(
            self.list_widget,
            1,
        )

        content.addWidget(
            self.detail_card,
            2,
        )

        root.addLayout(
            content,
            1,
        )

        self.empty_state = EmptyState(
            "Chưa có Phong cách đọc",
            "Tạo Style Profile từ Dataset/Alignment hoặc nhập gói .avstyle đã backup.",
            "Tạo Style Profile đầu tiên",
        )

        root.addWidget(
            self.empty_state
        )

        self.empty_state.hide()

        self.create_button.clicked.connect(
            self.create_profile
        )

        self.empty_state.action_button.clicked.connect(
            self.create_profile
        )

        self.import_button.clicked.connect(
            self.import_package
        )

        self.export_button.clicked.connect(
            self.export_package
        )

        self.rename_button.clicked.connect(
            self.rename_profile
        )

        self.check_button.clicked.connect(
            self.show_readiness
        )

        self.backup_button.clicked.connect(
            self.export_package
        )

        self.list_widget.currentItemChanged.connect(
            self.on_selected
        )

    def refresh(
        self,
    ):

        self.items = self.service.list_profiles()

        self.list_widget.clear()

        for profile in self.items:

            item = QListWidgetItem(
                f"{profile.display_name} ({profile.style_profile_id})"
            )

            item.setData(
                Qt.UserRole,
                profile.style_profile_id,
            )

            self.list_widget.addItem(
                item
            )

        self.empty_state.setVisible(
            not self.items
        )

        self.list_widget.setVisible(
            bool(
                self.items
            )
        )

        if self.items:

            self.list_widget.setCurrentRow(
                0
            )

    def on_selected(
        self,
        current,
        previous=None,
    ):

        if current is None:

            self.current_profile_id = ""

            return

        self.current_profile_id = current.data(
            Qt.UserRole
        )

        profile = self.service.get_profile(
            self.current_profile_id
        )

        readiness = self.service.readiness(
            self.current_profile_id
        )

        self.detail_title.setText(
            profile.display_name
        )

        self.detail_status.setText(
            readiness.get(
                "status",
                profile.status,
            )
        )

        self.detail_text.setText(
            "\n".join(
                [
                    f"ID: {profile.style_profile_id}",
                    f"Ngôn ngữ: {profile.language}",
                    f"Trạng thái extraction: {profile.status}",
                    f"Generate usage: {readiness.get('generation_usage', 'unknown')}",
                    f"Ghi chú: {readiness.get('message_vi', '')}",
                ]
            )
        )

    def create_profile(
        self,
    ):

        dialog = StyleProfileWizard(
            self
        )

        if dialog.exec() != QDialog.Accepted:

            return

        name = dialog.name_input.text().strip()

        if not name:

            QMessageBox.warning(
                self,
                "Thiếu tên",
                "Vui lòng nhập tên Phong cách đọc.",
            )

            return

        self.service.create_profile(
            display_name=name,
            description=dialog.description_input.toPlainText(),
            language="vi",
        )

        self.refresh()

    def import_package(
        self,
    ):

        file, _ = QFileDialog.getOpenFileName(
            self,
            "Nhập gói Style Profile",
            "",
            "AVStyle (*.avstyle)",
        )

        if not file:

            return

        self.export_service.import_package(
            file
        )

        self.refresh()

    def export_package(
        self,
    ):

        if not self.current_profile_id:

            QMessageBox.information(
                self,
                "Chưa chọn",
                "Hãy chọn một Style Profile trước.",
            )

            return

        file, _ = QFileDialog.getSaveFileName(
            self,
            "Xuất gói Style Profile",
            f"{self.current_profile_id}.avstyle",
            "AVStyle (*.avstyle)",
        )

        if not file:

            return

        self.export_service.export_package(
            self.current_profile_id,
            Path(
                file
            ),
        )

    def rename_profile(
        self,
    ):

        if not self.current_profile_id:

            QMessageBox.information(
                self,
                "Chưa chọn",
                "Hãy chọn một Style Profile trước.",
            )

            return

        profile = self.service.get_profile(
            self.current_profile_id
        )

        dialog = QDialog(
            self
        )

        dialog.setWindowTitle(
            "Đổi tên Phong cách đọc"
        )

        layout = QVBoxLayout(
            dialog
        )

        name_input = QLineEdit(
            profile.display_name
        )

        layout.addWidget(
            QLabel(
                "Tên mới"
            )
        )

        layout.addWidget(
            name_input
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok
            | QDialogButtonBox.Cancel
        )

        buttons.accepted.connect(
            dialog.accept
        )

        buttons.rejected.connect(
            dialog.reject
        )

        layout.addWidget(
            buttons
        )

        if dialog.exec() != QDialog.Accepted:

            return

        name = self.service.normalize_display_name(
            name_input.text()
        )

        errors = self.service.validate_display_name(
            name
        )

        if errors:

            QMessageBox.warning(
                self,
                "Tên không hợp lệ",
                ", ".join(
                    errors
                ),
            )

            return

        old_id = profile.style_profile_id

        renamed = self.service.rename(
            old_id,
            name,
        )

        if renamed.style_profile_id != old_id:

            QMessageBox.critical(
                self,
                "Lỗi",
                "Style Profile ID đã thay đổi ngoài ý muốn.",
            )

            return

        self.refresh()

        for index in range(
            self.list_widget.count()
        ):

            item = self.list_widget.item(
                index
            )

            if item.data(
                Qt.UserRole
            ) == old_id:

                self.list_widget.setCurrentRow(
                    index
                )

                break

    def show_readiness(
        self,
    ):

        if not self.current_profile_id:

            return

        readiness = self.service.readiness(
            self.current_profile_id
        )

        QMessageBox.information(
            self,
            "Readiness",
            readiness.get(
                "message_vi",
                "",
            ),
        )

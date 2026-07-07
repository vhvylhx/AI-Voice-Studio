from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
)


class ProjectToolbar(QWidget):

    def __init__(self):

        super().__init__()

        layout = QHBoxLayout(self)

        self.new_button = QPushButton("➕ Tạo")

        self.rename_button = QPushButton("✏ Đổi tên")

        self.delete_button = QPushButton("🗑 Xóa")

        self.refresh_button = QPushButton("🔄 Làm mới")

        layout.addWidget(self.new_button)
        layout.addWidget(self.rename_button)
        layout.addWidget(self.delete_button)

        layout.addStretch()

        layout.addWidget(self.refresh_button)
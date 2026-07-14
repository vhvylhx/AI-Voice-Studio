from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTextEdit,
    QFileDialog,
    QMessageBox,
)

from core.app_context import AppContext


class TrainingPage(QWidget):

    def __init__(self):

        super().__init__()

        root = QVBoxLayout(self)

        title = QLabel(
            "Huấn luyện giọng"
        )

        title.setStyleSheet("""
            font-size:24px;
            font-weight:bold;
        """)

        root.addWidget(
            title
        )

        self.source = QLabel(
            "Dataset : Chưa chọn"
        )

        root.addWidget(
            self.source
        )

        buttons = QHBoxLayout()

        self.choose_button = QPushButton(
            "Chọn Dataset"
        )

        self.prepare_button = QPushButton(
            "Chuẩn bị"
        )

        self.train_button = QPushButton(
            "Train"
        )

        self.preview_button = QPushButton(
            "Preview"
        )

        buttons.addWidget(
            self.choose_button
        )

        buttons.addWidget(
            self.prepare_button
        )

        buttons.addWidget(
            self.train_button
        )

        buttons.addWidget(
            self.preview_button
        )

        buttons.addStretch()

        root.addLayout(
            buttons
        )

        self.log = QTextEdit()

        self.log.setReadOnly(
            True
        )

        root.addWidget(
            self.log
        )

        self.dataset = None

        self.choose_button.clicked.connect(
            self.choose_dataset
        )

        self.prepare_button.clicked.connect(
            self.prepare_dataset
        )

        self.train_button.clicked.connect(
            self.train
        )

        self.preview_button.clicked.connect(
            self.preview
        )

## ===== KẾT THÚC PART 1 =====
    def choose_dataset(self):

        folder = QFileDialog.getExistingDirectory(

            self,

            "Chọn thư mục Dataset"

        )

        if not folder:

            return

        self.dataset = folder

        self.source.setText(

            folder

        )

        self.log.append(

            "Đã chọn Dataset."

        )

    def prepare_dataset(self):

        voice = AppContext.current_voice.get()

        if voice is None:

            QMessageBox.warning(

                self,

                "Thông báo",

                "Chưa chọn Voice."

            )

            return

        if self.dataset is None:

            QMessageBox.warning(

                self,

                "Thông báo",

                "Chưa chọn Dataset."

            )

            return

        AppContext.training_service.prepare_dataset(

            self.dataset,

            voice,

        )

        self.log.append(

            "Dataset đã sẵn sàng."

        )

    def train(self):

        voice = AppContext.current_voice.get()

        if voice is None:

            return

        dataset = {

            "items": []

        }

        AppContext.training_service.train(

            voice,

            dataset,

        )

        self.log.append(

            "Đã bắt đầu Train."

        )

    def preview(self):

        voice = AppContext.current_voice.get()

        if voice is None:

            return

        AppContext.training_service.create_preview(

            voice

        )

        self.log.append(

            "Đã tạo Preview."

        )


## ===== KẾT THÚC FILE =====
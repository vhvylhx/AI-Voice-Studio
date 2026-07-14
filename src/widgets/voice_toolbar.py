from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
)


class VoiceToolbar(QWidget):

    def __init__(self):

        super().__init__()

        layout = QHBoxLayout(self)

        #
        # Voice
        #

        self.new_button = QPushButton(
            "➕ Tạo Voice"
        )

        self.rename_button = QPushButton(
            "✏ Đổi tên"
        )

        self.delete_button = QPushButton(
            "🗑 Xóa"
        )

        #
        # Dataset
        #

        self.dataset_button = QPushButton(
            "📚 Dataset"
        )

        self.dictionary_button = QPushButton(
            "📖 Từ điển"
        )

        #
        # AI
        #

        self.train_button = QPushButton(
            "🧠 Huấn luyện"
        )

        self.preview_button = QPushButton(
            "▶ Preview"
        )

        self.models_button = QPushButton(
            "📦 Models"
        )

        #
        # Engine
        #

        self.engine_button = QPushButton(
            "⚙ Engine"
        )

        #
        # Refresh
        #

        self.refresh_button = QPushButton(
            "🔄 Làm mới"
        )

        #
        # Layout
        #

        layout.addWidget(
            self.new_button
        )

        layout.addWidget(
            self.rename_button
        )

        layout.addWidget(
            self.delete_button
        )

        layout.addSpacing(
            15
        )

        layout.addWidget(
            self.dataset_button
        )

        layout.addWidget(
            self.dictionary_button
        )

        layout.addSpacing(
            15
        )

        layout.addWidget(
            self.train_button
        )

        layout.addWidget(
            self.preview_button
        )

        layout.addWidget(
            self.models_button
        )

        layout.addSpacing(
            15
        )

        layout.addWidget(
            self.engine_button
        )

        layout.addStretch()

        layout.addWidget(
            self.refresh_button
        )
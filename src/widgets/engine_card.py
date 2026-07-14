from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from services.engine_service import EngineService


class EngineCard(QFrame):

    selected = Signal(str)

    def __init__(self, engine):

        super().__init__()

        self.engine = engine

        self.service = EngineService()

        info = engine.info()

        layout = QVBoxLayout(self)

        title = QLabel(
            info.name
        )

        title.setStyleSheet("""
            font-size:18px;
            font-weight:bold;
        """)

        version = QLabel(
            f"Phiên bản: {info.version}"
        )

        author = QLabel(
            f"Tác giả: {info.author}"
        )

        desc = QLabel(
            info.description
        )

        current = QLabel()

        button = QPushButton(
            "Chọn Engine"
        )

        if self.service.current_id() == info.id:

            current.setText(
                "🟢 Đang sử dụng"
            )

            button.setEnabled(
                False
            )

            button.setText(
                "Đang sử dụng"
            )

        else:

            current.setText(
                "⚪ Chưa chọn"
            )

            button.clicked.connect(
                lambda: self.selected.emit(
                    info.id
                )
            )

        layout.addWidget(
            title
        )

        layout.addWidget(
            version
        )

        layout.addWidget(
            author
        )

        layout.addWidget(
            desc
        )

        layout.addWidget(
            current
        )

        layout.addStretch()

        layout.addWidget(
            button
        )
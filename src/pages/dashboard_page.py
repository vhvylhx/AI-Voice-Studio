from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from services import dashboard_service
from widgets.stat_card import StatCard


class DashboardPage(QWidget):

    def __init__(self):

        super().__init__()

        self.build_ui()

        self.refresh()

    def build_ui(self):

        root = QVBoxLayout(self)

        title = QLabel("Dashboard")

        title.setStyleSheet(
            """
            font-size:22px;
            font-weight:bold;
        """
        )

        root.addWidget(title)

        cards = QHBoxLayout()

        self.voice_card = StatCard("Dataset")

        self.audio_card = StatCard("Audio")

        self.docx_card = StatCard("DOCX")

        self.text_card = StatCard("Text")

        self.job_card = StatCard("Job chờ")

        self.resource_card = StatCard("Resource")

        cards.addWidget(self.voice_card)

        cards.addWidget(self.audio_card)

        cards.addWidget(self.docx_card)

        cards.addWidget(self.text_card)

        cards.addWidget(self.job_card)

        cards.addWidget(self.resource_card)

        root.addLayout(cards)

        self.refresh_button = QPushButton("Làm mới")

        self.refresh_button.clicked.connect(self.refresh)

        root.addWidget(self.refresh_button)

        root.addStretch()

    def refresh(self):

        model = dashboard_service.load()

        self.voice_card.set_value(model.voice_count)

        self.audio_card.set_value(model.audio_count)

        self.docx_card.set_value(model.docx_count)

        self.text_card.set_value(model.total_text)

        try:

            from core.app_context import AppContext

            counts = AppContext.job_queue_service.queue_counts()

            self.job_card.set_value(
                counts.get(
                    "queued",
                    0,
                )
            )

            resource = AppContext.resource_monitor_service.summary()

            self.resource_card.set_value(
                resource.get(
                    "pressure_state",
                    "unknown",
                )
            )

        except Exception:

            self.job_card.set_value(
                0
            )

            self.resource_card.set_value(
                "-"
            )

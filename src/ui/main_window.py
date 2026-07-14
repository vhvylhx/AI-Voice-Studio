from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from config.app_config import APP_NAME

from ui.sidebar import Sidebar

from pages.dashboard_page import DashboardPage
from pages.audio_page import AudioPage
from pages.project_page import ProjectPage
from pages.settings_page import SettingsPage

from widgets.app_status_bar import AppStatusBar


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(APP_NAME)

        self.resize(1400, 850)

        self.setup_ui()

        self.bind_events()

    def setup_ui(self):

        self.sidebar = Sidebar()

        self.stack = QStackedWidget()

        self.status_bar = AppStatusBar()

        self.stack.addWidget(
            DashboardPage()
        )

        self.stack.addWidget(
            AudioPage()
        )

        self.stack.addWidget(
            ProjectPage()
        )

        self.stack.addWidget(
            SettingsPage()
        )

        content = QVBoxLayout()

        content.addWidget(
            self.stack
        )

        content.addWidget(
            self.status_bar
        )

        body = QHBoxLayout()

        body.addWidget(
            self.sidebar
        )

        body.addLayout(
            content
        )

        root = QWidget()

        root.setLayout(
            body
        )

        self.setCentralWidget(
            root
        )

        self.sidebar.setCurrentRow(
            0
        )

    def bind_events(self):

        self.sidebar.currentRowChanged.connect(
            self.stack.setCurrentIndex
        )
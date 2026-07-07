from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QWidget
)

from config.app_config import APP_NAME

from ui.sidebar import Sidebar

from pages.dashboard_page import DashboardPage
from pages.audio_page import AudioPage
from pages.voice_page import VoicePage
from pages.training_page import TrainingPage
from pages.project_page import ProjectPage
from pages.settings_page import SettingsPage


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

        self.stack.addWidget(DashboardPage())
        self.stack.addWidget(AudioPage())
        self.stack.addWidget(VoicePage())
        self.stack.addWidget(TrainingPage())
        self.stack.addWidget(ProjectPage())
        self.stack.addWidget(SettingsPage())

        layout = QHBoxLayout()

        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack)

        root = QWidget()

        root.setLayout(layout)

        self.setCentralWidget(root)

        self.sidebar.setCurrentRow(0)

    def bind_events(self):

        self.sidebar.currentRowChanged.connect(
            self.stack.setCurrentIndex
        )
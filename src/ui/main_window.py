from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from config.app_config import APP_NAME
from events import Events
from events import bus

from ui.sidebar import Sidebar

from pages.dashboard_page import DashboardPage
from pages.audio_page import AudioPage
from pages.project_page import ProjectPage
from pages.settings_page import SettingsPage
from pages.style_profile_page import StyleProfilePage
from pages.training_page import TrainingPage
from pages.voice_page import VoicePage
from pages.jobs_page import JobsPage
from pages.resource_monitor_page import ResourceMonitorPage

from widgets.app_status_bar import AppStatusBar
from widgets.global_progress_log import GlobalProgressLog


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

        self.stack.setMinimumSize(
            0,
            0,
        )

        self.stack.setSizePolicy(
            QSizePolicy.Ignored,
            QSizePolicy.Ignored,
        )

        self.status_bar = AppStatusBar()

        self.global_progress_log = GlobalProgressLog()

        self.global_progress_log.setMinimumSize(
            0,
            0,
        )

        self.global_progress_log.setSizePolicy(
            QSizePolicy.Ignored,
            QSizePolicy.Preferred,
        )

        self.stack.addWidget(
            DashboardPage()
        )

        self.stack.addWidget(
            AudioPage()
        )

        self.stack.addWidget(
            StyleProfilePage()
        )

        self.stack.addWidget(
            VoicePage()
        )

        self.stack.addWidget(
            TrainingPage()
        )

        self.stack.addWidget(
            JobsPage()
        )

        self.stack.addWidget(
            ResourceMonitorPage()
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
            self.global_progress_log
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

        bus.subscribe(
            Events.PROJECT_CHANGED,
            self.on_project_changed,
        )

        self.update_project_title()

    def on_project_changed(
        self,
        project,
    ):

        self.update_project_title(
            project
        )

    def update_project_title(
        self,
        project=None,
    ):

        if project is None:

            try:

                from core.app_context import AppContext

                if AppContext.current_project.has_project():

                    project = AppContext.current_project.get()

            except Exception:

                project = None

        if project is None:

            self.setWindowTitle(
                f"{APP_NAME} — Chưa mở dự án"
            )

            return

        self.setWindowTitle(
            f"{APP_NAME} — {project.display_name}"
        )

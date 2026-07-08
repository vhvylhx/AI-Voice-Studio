from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSplitter,
    QInputDialog,
    QMessageBox,
)

from core.app_context import AppContext

from events import (
    bus,
    Events,
)

from services.app_events import AppEvents

from widgets.voice_toolbar import VoiceToolbar
from widgets.voice_list import VoiceList
from widgets.voice_detail import VoiceDetail


class VoicePage(QWidget):

    def __init__(self):

        super().__init__()

        self.service = AppContext.voice_service

        self.current_voice = None

        root = QVBoxLayout(self)

        self.toolbar = VoiceToolbar()

        root.addWidget(
            self.toolbar
        )

        splitter = QSplitter()

        self.list = VoiceList()

        self.detail = VoiceDetail()

        splitter.addWidget(
            self.list
        )

        splitter.addWidget(
            self.detail
        )

        splitter.setSizes([500, 300])

        root.addWidget(
            splitter
        )

        self.toolbar.new_button.clicked.connect(
            self.create_voice
        )

        self.toolbar.rename_button.clicked.connect(
            self.rename_voice
        )

        self.toolbar.delete_button.clicked.connect(
            self.delete_voice
        )

        self.toolbar.refresh_button.clicked.connect(
            self.refresh
        )

        self.list.voice_selected.connect(
            self.select_voice
        )

        bus.subscribe(
            Events.WORKSPACE_CHANGED,
            self.on_project_changed
        )

        self.refresh()

    def refresh(self):

        self.current_voice = None

        AppContext.current_voice.clear()

        if not AppContext.current_project.has_project():

            self.list.load([])

            self.detail.clear()

            return

        voices = []

        for name in self.service.list():

            voices.append(
                self.service.load(name)
            )

        self.list.load(
            voices
        )

        self.detail.clear()

    def create_voice(self):

        if not AppContext.current_project.has_project():

            return

        name, ok = QInputDialog.getText(
            self,
            "Voice",
            "Tên Voice"
        )

        if not ok:
            return

        name = name.strip()

        if not name:
            return

        if self.service.exists(name):
            return

        voice = self.service.create(
            name
        )

        self.refresh()

        self.select_voice(
            voice
        )

    def rename_voice(self):

        if self.current_voice is None:
            return

        name, ok = QInputDialog.getText(
            self,
            "Đổi tên Voice",
            "Tên mới",
            text=self.current_voice.name
        )

        if not ok:
            return

        name = name.strip()

        if not name:
            return

        if name == self.current_voice.name:
            return

        if self.service.exists(name):
            return

        self.service.rename(
            self.current_voice.name,
            name
        )

        self.refresh()

    def delete_voice(self):

        if self.current_voice is None:
            return

        result = QMessageBox.question(
            self,
            "Xóa Voice",
            f'Xóa "{self.current_voice.name}" ?'
        )

        if result != QMessageBox.Yes:
            return

        self.service.delete(
            self.current_voice.name
        )

        self.refresh()

    def select_voice(self, voice):

        self.current_voice = voice

        AppContext.current_voice.set(
            voice
        )

        self.detail.load(
            voice
        )

        AppEvents.voice_changed(
            voice
        )

    def on_project_changed(self, project):

        self.refresh()
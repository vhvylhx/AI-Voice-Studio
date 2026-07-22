from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSplitter,
    QInputDialog,
    QMessageBox,
    QFileDialog,
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

        splitter.setSizes([
            500,
            300,
        ])

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

        self.toolbar.train_button.clicked.connect(
            self.train_voice
        )

        self.toolbar.preview_button.clicked.connect(
            self.preview_voice
        )

        self.toolbar.refresh_button.clicked.connect(
            self.refresh
        )

        self.list.voice_selected.connect(
            self.select_voice
        )

        self.detail.language_selection_changed.connect(
            self.change_enabled_languages
        )

        bus.subscribe(
            Events.WORKSPACE_CHANGED,
            self.on_project_changed
        )

        self.refresh()

    def refresh(self):

        self.current_voice = None

        AppContext.current_voice.clear()

        voices = []

        for name in self.service.list():

            voices.append(
                self.service.load(name)
            )

        self.list.load(
            voices
        )

        if not AppContext.current_project.has_project():

            self.detail.clear()

            return

        project = AppContext.current_project.get()

        if (
            getattr(
                project.config,
                "active_voice_id",
                "",
            )
            or project.config.voice
        ):

            for voice in voices:

                if (
                    getattr(
                        project.config,
                        "active_voice_id",
                        "",
                    )
                    and voice.id
                    == project.config.active_voice_id
                ) or voice.name == project.config.voice:

                    self.select_voice(
                        voice
                    )

                    return

        self.detail.clear()

    def create_voice(self):

        name, ok = QInputDialog.getText(
            self,
            "Voice",
            "Tên Voice"
        )

        if not ok:
            return

        name = self.service.normalize_display_name(
            name
        )

        errors = self.service.validate_display_name(
            name
        )

        if errors:

            QMessageBox.warning(
                self,
                "Tên Voice không hợp lệ",
                ", ".join(
                    errors
                )
            )

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
            text=self.current_voice.display_name
        )

        if not ok:
            return

        name = self.service.normalize_display_name(
            name
        )

        errors = self.service.validate_display_name(
            name
        )

        if errors:

            QMessageBox.warning(
                self,
                "Tên Voice không hợp lệ",
                ", ".join(
                    errors
                )
            )

            return

        if name == self.current_voice.display_name:
            return

        old_id = self.current_voice.id

        self.service.rename_display_name(
            old_id,
            name
        )

        if AppContext.current_project.has_project():

            project = AppContext.current_project.get()

            if hasattr(
                project.config,
                "active_voice_id",
            ):

                project.config.active_voice_id = old_id

            if not project.config.voice:

                project.config.voice = self.current_voice.name

            AppContext.project_service.save(
                project
            )

        self.refresh()

        for voice_name in self.service.list():

            voice = self.service.load(
                voice_name
            )

            if voice.id == old_id:

                self.select_voice(
                    voice
                )

                break

    def train_voice(self):

        if self.current_voice is None:
            return

        folder = QFileDialog.getExistingDirectory(
            self,
            "Chọn Dataset"
        )

        if not folder:
            return

        AppContext.training_service.prepare_dataset(
            folder,
            self.current_voice,
        )

        self.detail.load(
            self.current_voice
        )

        QMessageBox.information(
            self,
            "Hoàn thành",
            "Dataset đã được chuẩn bị."
        )

    def preview_voice(self):

        if self.current_voice is None:
            return

        AppContext.training_service.create_preview(
            self.current_voice
        )

        self.detail.load(
            self.current_voice
        )

        QMessageBox.information(
            self,
            "Preview",
            "Đã tạo preview."
        )

## ===== KẾT THÚC PART 1 =====
    def delete_voice(self):

        if self.current_voice is None:
            return

        result = QMessageBox.question(
            self,
            "Xóa Voice",
            f'Xóa "{self.current_voice.display_name}" ?'
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

        if AppContext.current_project.has_project():

            project = AppContext.current_project.get()

            project.config.voice = voice.name

            if hasattr(
                project.config,
                "active_voice_id",
            ):

                project.config.active_voice_id = voice.id

            AppContext.project_service.save(
                project
            )

        self.detail.load(
            voice,
            AppContext.engine_capability_router.voice_language_capabilities(
                voice.id
            ),
        )

        AppEvents.voice_changed(
            voice
        )

    def change_enabled_languages(
        self,
        language_codes,
        allow_all,
    ):

        if self.current_voice is None:

            return

        try:

            self.current_voice = self.service.set_enabled_languages(
                self.current_voice.id,
                language_codes,
                allow_all=allow_all,
            )

        except Exception as exc:

            QMessageBox.warning(
                self,
                "Ngôn ngữ không hợp lệ",
                str(
                    exc
                ),
            )

            self.detail.load(
                self.current_voice,
                AppContext.engine_capability_router.voice_language_capabilities(
                    self.current_voice.id
                ),
            )

            return

        AppContext.current_voice.set(
            self.current_voice
        )

        self.detail.load(
            self.current_voice,
            AppContext.engine_capability_router.voice_language_capabilities(
                self.current_voice.id
            ),
        )

        AppEvents.voice_changed(
            self.current_voice
        )

    def on_project_changed(
        self,
        project
    ):

        self.refresh()


## ===== KẾT THÚC FILE =====

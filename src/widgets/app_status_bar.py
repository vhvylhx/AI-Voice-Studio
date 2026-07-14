from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
)

from core.app_context import AppContext

from events import (
    bus,
    Events,
)


class AppStatusBar(QWidget):

    def __init__(self):

        super().__init__()

        layout = QHBoxLayout(self)

        self.project = QLabel()

        self.voice = QLabel()

        self.engine = QLabel()

        layout.addWidget(self.project)

        layout.addSpacing(20)

        layout.addWidget(self.voice)

        layout.addSpacing(20)

        layout.addWidget(self.engine)

        layout.addStretch()

        bus.subscribe(
            Events.WORKSPACE_CHANGED,
            self.on_project_changed
        )

        bus.subscribe(
            Events.VOICE_CHANGED,
            self.on_voice_changed
        )

        bus.subscribe(
            Events.ENGINE_CHANGED,
            self.on_engine_changed
        )

        self.refresh()

    def refresh(self):

        if AppContext.current_project.has_project():

            project = AppContext.current_project.get().name

        else:

            project = "-"

        self.project.setText(
            f"Project : {project}"
        )

        self.voice.setText(
            "Voice : -"
        )

        self.engine.setText(
            "Engine : -"
        )

    def set_project(self, name):

        self.project.setText(
            f"Project : {name}"
        )

    def set_voice(self, name):

        self.voice.setText(
            f"Voice : {name}"
        )

    def set_engine(self, name):

        self.engine.setText(
            f"Engine : {name}"
        )

    def on_project_changed(self, project):

        self.set_project(
            project.name
        )

    def on_voice_changed(self, voice):

        self.set_voice(
            voice.name
        )

    def on_engine_changed(self, engine):

        self.set_engine(
            engine
        )
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
)

from core.app_context import AppContext

from services.engine_service import EngineService

from services.app_events import AppEvents

from widgets.engine_list import EngineList


class EnginePage(QWidget):

    def __init__(self):

        super().__init__()

        self.service = EngineService()

        root = QVBoxLayout(self)

        self.list = EngineList()

        root.addWidget(
            self.list
        )

        self.list.engine_selected.connect(
            self.select_engine
        )

        self.refresh()

    def refresh(self):

        project = AppContext.current_project.get()

        if project is not None:

            engine_id = project.config.engine

            if engine_id:

                try:

                    self.service.select(
                        engine_id
                    )

                except Exception:

                    pass

        self.list.load(
            self.service.all()
        )

    def select_engine(self, engine_id):

        self.service.select(
            engine_id
        )

        project = AppContext.current_project.get()

        if project is not None:

            project.config.engine = engine_id

            AppContext.project_service.save(
                project
            )

        AppEvents.engine_changed(
            engine_id
        )

        self.refresh()
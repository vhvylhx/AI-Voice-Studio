from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
)

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

        self.list.load(
            self.service.all()
        )

    def select_engine(self, engine_id):

        self.service.select(
            engine_id
        )

        AppEvents.engine_changed(
            engine_id
        )

        self.refresh()
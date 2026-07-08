from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
)

from widgets.engine_card import EngineCard


class EngineList(QWidget):

    engine_selected = Signal(str)

    def __init__(self):

        super().__init__()

        root = QVBoxLayout(self)

        self.scroll = QScrollArea()

        self.scroll.setWidgetResizable(True)

        self.container = QWidget()

        self.layout = QVBoxLayout(self.container)

        self.layout.addStretch()

        self.scroll.setWidget(
            self.container
        )

        root.addWidget(
            self.scroll
        )

    def clear(self):

        while self.layout.count() > 1:

            item = self.layout.takeAt(0)

            if item.widget():

                item.widget().deleteLater()

    def load(self, engines):

        self.clear()

        for engine in engines:

            card = EngineCard(engine)

            card.selected.connect(
                self.engine_selected.emit
            )

            self.layout.insertWidget(
                self.layout.count() - 1,
                card
            )
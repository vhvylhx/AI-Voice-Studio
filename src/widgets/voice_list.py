from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
)

from widgets.voice_card import VoiceCard


class VoiceList(QWidget):

    voice_selected = Signal(object)

    def __init__(self):

        super().__init__()

        self.layout = QVBoxLayout(self)

        self.cards = []

        self.current = None

        self.layout.addStretch()

    def clear(self):

        self.cards.clear()

        self.current = None

        while self.layout.count() > 1:

            item = self.layout.takeAt(0)

            if item.widget():

                item.widget().deleteLater()

    def load(self, voices):

        self.clear()

        for voice in voices:

            card = VoiceCard(voice)

            card.clicked.connect(
                self.select
            )

            self.cards.append(card)

            self.layout.insertWidget(
                self.layout.count() - 1,
                card
            )

        if self.cards:

            self.select(
                self.cards[0].voice
            )

    def select(self, voice):

        self.current = voice

        self.voice_selected.emit(
            voice
        )
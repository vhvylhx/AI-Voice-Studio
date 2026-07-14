from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from services.pronunciation_service import PronunciationService


class DictionaryDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.service = PronunciationService()

        self.setWindowTitle(
            "Từ điển phát âm"
        )

        self.resize(
            700,
            500,
        )

        root = QVBoxLayout(self)

        #
        # Table
        #

        self.table = QTableWidget()

        self.table.setColumnCount(2)

        self.table.setHorizontalHeaderLabels(
            [
                "Từ",
                "Cách đọc",
            ]
        )

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.table.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents,
        )

        self.table.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.Stretch,
        )

        root.addWidget(
            self.table
        )

        #
        # Buttons
        #

        buttons = QHBoxLayout()

        self.add_button = QPushButton(
            "➕ Thêm"
        )

        self.edit_button = QPushButton(
            "✏ Sửa"
        )

        self.delete_button = QPushButton(
            "🗑 Xóa"
        )

        self.reload_button = QPushButton(
            "🔄 Làm mới"
        )

        self.close_button = QPushButton(
            "Đóng"
        )

        buttons.addWidget(
            self.add_button
        )

        buttons.addWidget(
            self.edit_button
        )

        buttons.addWidget(
            self.delete_button
        )

        buttons.addStretch()

        buttons.addWidget(
            self.reload_button
        )

        buttons.addWidget(
            self.close_button
        )

        root.addLayout(
            buttons
        )

        #
        # Events
        #

        self.add_button.clicked.connect(
            self.add_word
        )

        self.edit_button.clicked.connect(
            self.edit_word
        )

        self.delete_button.clicked.connect(
            self.delete_word
        )

        self.reload_button.clicked.connect(
            self.load
        )

        self.close_button.clicked.connect(
            self.accept
        )

        self.load()

    #
    # Helpers
    #

    def current_word(self):

        row = self.table.currentRow()

        if row < 0:

            return None

        return self.table.item(
            row,
            0,
        ).text()

    #
    # Load
    #

    def load(self):

        data = self.service.all()

        self.table.setRowCount(
            len(data)
        )

        for row, (word, speak) in enumerate(
            data.items()
        ):

            self.table.setItem(
                row,
                0,
                QTableWidgetItem(word),
            )

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(speak),
            )

    #
    # Add
    #

    def add_word(self):

        word, ok = QInputDialog.getText(
            self,
            "Thêm từ",
            "Từ",
        )

        if not ok or not word.strip():

            return

        speak, ok = QInputDialog.getText(
            self,
            "Cách đọc",
            "Đọc là",
        )

        if not ok or not speak.strip():

            return

        self.service.add(
            word.strip(),
            speak.strip(),
        )

        self.load()

    #
    # Edit
    #

    def edit_word(self):

        word = self.current_word()

        if word is None:

            return

        current = self.service.words[word]

        speak, ok = QInputDialog.getText(
            self,
            "Sửa",
            "Cách đọc",
            text=current,
        )

        if not ok:

            return

        self.service.update(
            word,
            speak.strip(),
        )

        self.load()

    #
    # Delete
    #

    def delete_word(self):

        word = self.current_word()

        if word is None:

            return

        result = QMessageBox.question(

            self,

            "Xóa",

            f'Xóa "{word}" ?',

        )

        if result != QMessageBox.Yes:

            return

        self.service.remove(
            word
        )

        self.load()
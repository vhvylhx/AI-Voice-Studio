from PySide6.QtCore import Qt
from PySide6.QtCore import Signal

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
)


class TextFileList(QWidget):

    selection_changed = Signal()

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout(self)

        self.list = QListWidget()

        self.list.itemChanged.connect(
            self._on_item_changed
        )

        layout.addWidget(
            self.list
        )

    def load(self, files):

        self.list.blockSignals(True)

        self.list.clear()

        for file in files:

            item = QListWidgetItem(
                f"{file.name}{file.extension}"
            )

            item.setFlags(
                item.flags() |
                Qt.ItemIsUserCheckable
            )

            item.setCheckState(
                Qt.Checked
            )

            item.setData(
                Qt.UserRole,
                file
            )

            self.list.addItem(
                item
            )

        self.list.blockSignals(False)

        self.selection_changed.emit()

    def selected_files(self):

        result = []

        for i in range(
            self.list.count()
        ):

            item = self.list.item(i)

            if item.checkState() == Qt.Checked:

                result.append(
                    item.data(
                        Qt.UserRole
                    )
                )

        return result

    def total_files(self):

        return self.list.count()

    def selected_count(self):

        return len(
            self.selected_files()
        )

    def _on_item_changed(self, item):

        self.selection_changed.emit()
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTreeWidget
from PySide6.QtWidgets import QTreeWidgetItem


class DatasetTree(QTreeWidget):

    def __init__(self):

        super().__init__()

        self.setColumnCount(5)

        self.setHeaderLabels([
            "Tên",
            "Text",
            "Audio",
            "Trạng thái",
            "Ghi chú"
        ])

    def load(self, workspace):

        self.clear()

        for dataset in workspace.datasets:

            root = QTreeWidgetItem()

            root.setText(0, dataset.name)
            root.setText(1, str(dataset.docx + dataset.txt))
            root.setText(2, str(dataset.mp3 + dataset.wav))
            root.setText(3, "OK")

            self.addTopLevelItem(root)

            for pair in dataset.pairs:

                item = QTreeWidgetItem()

                item.setText(0, pair.name)

                item.setText(
                    1,
                    "✔" if pair.has_text else ""
                )

                item.setText(
                    2,
                    "✔" if pair.has_audio else ""
                )

                if pair.matched:

                    item.setText(3, "OK")

                    item.setForeground(
                        3,
                        QColor("green")
                    )

                elif pair.has_text:

                    item.setText(
                        3,
                        "Thiếu Audio"
                    )

                    item.setForeground(
                        3,
                        QColor("orange")
                    )

                else:

                    item.setText(
                        3,
                        "Thiếu Text"
                    )

                    item.setForeground(
                        3,
                        QColor("red")
                    )

                root.addChild(item)

            root.setExpanded(True)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
)


class QueueList(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout(self)

        self.table = QTableWidget()

        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels([
            "Text",
            "Voice",
            "Engine",
            "Status",
            "Progress",
        ])

        self.table.horizontalHeader().setStretchLastSection(
            True
        )

        layout.addWidget(
            self.table
        )

    def load(self, jobs):

        self.table.setRowCount(
            len(jobs)
        )

        for row, job in enumerate(jobs):

            self.table.setItem(
                row,
                0,
                QTableWidgetItem(
                    job.text_file.name
                )
            )

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(
                    job.voice.name
                )
            )

            self.table.setItem(
                row,
                2,
                QTableWidgetItem(
                    job.engine or "-"
                )
            )

            self.table.setItem(
                row,
                3,
                QTableWidgetItem(
                    job.status
                )
            )

            self.table.setItem(
                row,
                4,
                QTableWidgetItem(
                    f"{job.progress}%"
                )
            )
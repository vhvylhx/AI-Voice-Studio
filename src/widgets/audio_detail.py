from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLabel,
    QProgressBar,
)


class AudioDetail(QWidget):

    def __init__(self):

        super().__init__()

        layout = QFormLayout(self)

        self.project = QLabel("-")

        self.voice = QLabel("-")

        self.engine = QLabel("-")

        self.total = QLabel("0")

        self.selected = QLabel("0")

        self.queue = QLabel("0")

        self.current = QLabel("-")

        self.progress = QProgressBar()

        self.progress.setRange(
            0,
            100
        )

        self.progress.setValue(
            0
        )

        self.status = QLabel("Sẵn sàng")

        layout.addRow(
            "Project",
            self.project
        )

        layout.addRow(
            "Voice",
            self.voice
        )

        layout.addRow(
            "Engine",
            self.engine
        )

        layout.addRow(
            "Tổng file",
            self.total
        )

        layout.addRow(
            "Đã chọn",
            self.selected
        )

        layout.addRow(
            "Hàng đợi",
            self.queue
        )

        layout.addRow(
            "Đang xử lý",
            self.current
        )

        layout.addRow(
            "Tiến trình",
            self.progress
        )

        layout.addRow(
            "Trạng thái",
            self.status
        )

    def clear(self):

        self.project.setText("-")

        self.voice.setText("-")

        self.engine.setText("-")

        self.total.setText("0")

        self.selected.setText("0")

        self.queue.setText("0")

        self.current.setText("-")

        self.progress.setValue(
            0
        )

        self.status.setText(
            "Sẵn sàng"
        )

    def set_total(self, value):

        self.total.setText(
            str(value)
        )

    def set_selected(self, value):

        self.selected.setText(
            str(value)
        )

    def set_queue(self, value):

        self.queue.setText(
            str(value)
        )

    def set_current(self, text):

        self.current.setText(
            text
        )

    def set_progress(self, value):

        self.progress.setValue(
            int(value)
        )

    def set_status(self, text):

        self.status.setText(
            text
        )
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from events import (
    bus,
    Events,
)


class GlobalProgressLog(QWidget):

    def __init__(self):

        super().__init__()

        self.auto_scroll = True

        root = QVBoxLayout(self)

        progress_box = QGroupBox(
            "Tiến độ chung"
        )

        progress_layout = QVBoxLayout(
            progress_box
        )

        self.job = QLabel(
            "Job: -"
        )

        self.stage = QLabel(
            "Stage: -"
        )

        self.current = QLabel(
            "File: -"
        )

        self.time = QLabel(
            "Elapsed: 0s | ETA: 0s"
        )

        self.message = QLabel(
            "-"
        )

        self.level = QLabel(
            "info"
        )

        self.progress = QProgressBar()

        self.progress.setRange(
            0,
            100,
        )

        info = QHBoxLayout()

        info.addWidget(
            self.job
        )

        info.addWidget(
            self.stage
        )

        info.addWidget(
            self.current
        )

        info.addWidget(
            self.time
        )

        info.addStretch()

        info.addWidget(
            self.level
        )

        progress_layout.addLayout(
            info
        )

        progress_layout.addWidget(
            self.progress
        )

        progress_layout.addWidget(
            self.message
        )

        log_box = QGroupBox(
            "Log chung"
        )

        log_layout = QVBoxLayout(
            log_box
        )

        self.log = QTextEdit()

        self.log.setReadOnly(
            True
        )

        self.jump_button = QPushButton(
            "↓ Jump to Latest"
        )

        self.jump_button.setVisible(
            False
        )

        self.clear_button = QPushButton(
            "Xóa log"
        )

        log_actions = QHBoxLayout()

        log_actions.addStretch()

        log_actions.addWidget(
            self.jump_button
        )

        log_actions.addWidget(
            self.clear_button
        )

        log_layout.addWidget(
            self.log
        )

        log_layout.addLayout(
            log_actions
        )

        root.addWidget(
            progress_box
        )

        root.addWidget(
            log_box
        )

        scrollbar = self.log.verticalScrollBar()

        scrollbar.valueChanged.connect(
            self.on_scroll
        )

        self.jump_button.clicked.connect(
            self.jump_to_latest
        )

        self.clear_button.clicked.connect(
            self.log.clear
        )

        bus.subscribe(
            Events.JOB_PROGRESS,
            self.on_progress
        )

        bus.subscribe(
            Events.LOG_MESSAGE,
            self.on_log
        )

    def on_progress(self, payload):

        payload = payload or {}

        self.job.setText(
            f"Job: {payload.get('job', '-')}"
        )

        self.stage.setText(
            f"Stage: {payload.get('stage', '-')}"
        )

        current_file = payload.get(
            "current_file",
            "",
        )

        current_item = payload.get(
            "current_item",
            0,
        )

        total_items = payload.get(
            "total_items",
            0,
        )

        self.current.setText(
            f"File: {current_file or '-'} ({current_item}/{total_items})"
        )

        self.time.setText(
            "Elapsed: "
            f"{payload.get('elapsed_seconds', 0):.1f}s | ETA: "
            f"{payload.get('estimated_remaining_seconds', 0):.1f}s"
        )

        self.message.setText(
            payload.get(
                "message",
                "-",
            )
        )

        self.level.setText(
            payload.get(
                "level",
                "info",
            )
        )

        self.progress.setValue(
            int(
                payload.get(
                    "percent",
                    0,
                )
            )
        )

    def on_log(self, payload):

        payload = payload or {}

        level = payload.get(
            "level",
            "info",
        )

        line = (
            f"[{payload.get('time', '')}] "
            f"[{level.upper()}] "
            f"[{payload.get('category', '-')}] "
            f"{payload.get('message', '')}"
        )

        self.log.append(
            line
        )

        if self.auto_scroll:

            self.jump_to_latest()

        else:

            self.jump_button.setVisible(
                True
            )

    def on_scroll(self):

        scrollbar = self.log.verticalScrollBar()

        at_bottom = (
            scrollbar.value()
            >= scrollbar.maximum()
        )

        self.auto_scroll = at_bottom

        self.jump_button.setVisible(
            not at_bottom
        )

    def jump_to_latest(self):

        scrollbar = self.log.verticalScrollBar()

        scrollbar.setValue(
            scrollbar.maximum()
        )

        self.auto_scroll = True

        self.jump_button.setVisible(
            False
        )

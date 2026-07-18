from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.app_context import AppContext
from events import (
    Events,
    bus,
)


class JobsPage(QWidget):

    def __init__(
        self,
    ):

        super().__init__()

        self.current_job_id = ""

        self.build_ui()

        self.bind_events()

        self.refresh()

    def build_ui(
        self,
    ):

        root = QVBoxLayout(
            self
        )

        title = QLabel(
            "Công việc / Hàng đợi"
        )

        title.setStyleSheet(
            "font-size:22px;font-weight:bold;"
        )

        root.addWidget(
            title
        )

        summary = QHBoxLayout()

        self.queued = QLabel(
            "Queued: 0"
        )

        self.running = QLabel(
            "Running: 0"
        )

        self.waiting_resource = QLabel(
            "Waiting Resource: 0"
        )

        self.paused = QLabel(
            "Paused: 0"
        )

        self.failed = QLabel(
            "Failed: 0"
        )

        self.completed = QLabel(
            "Completed: 0"
        )

        for label in [
            self.queued,
            self.running,
            self.waiting_resource,
            self.paused,
            self.failed,
            self.completed,
        ]:

            summary.addWidget(
                label
            )

        summary.addStretch()

        root.addLayout(
            summary
        )

        toolbar = QHBoxLayout()

        self.demo_button = QPushButton(
            "Tạo demo job"
        )

        self.run_next_button = QPushButton(
            "Chạy job kế tiếp"
        )

        self.pause_button = QPushButton(
            "Pause"
        )

        self.resume_button = QPushButton(
            "Resume"
        )

        self.cancel_button = QPushButton(
            "Cancel"
        )

        self.retry_button = QPushButton(
            "Retry"
        )

        self.priority_combo = QComboBox()

        self.priority_combo.addItems(
            [
                "low",
                "normal",
                "high",
                "urgent",
            ]
        )

        self.refresh_button = QPushButton(
            "Làm mới"
        )

        for widget in [
            self.demo_button,
            self.run_next_button,
            self.pause_button,
            self.resume_button,
            self.cancel_button,
            self.retry_button,
            self.priority_combo,
            self.refresh_button,
        ]:

            toolbar.addWidget(
                widget
            )

        toolbar.addStretch()

        root.addLayout(
            toolbar
        )

        body = QHBoxLayout()

        self.list = QListWidget()

        self.detail = QTextEdit()

        self.detail.setReadOnly(
            True
        )

        detail_box = QGroupBox(
            "Chi tiết"
        )

        detail_layout = QVBoxLayout(
            detail_box
        )

        detail_layout.addWidget(
            self.detail
        )

        body.addWidget(
            self.list,
            1,
        )

        body.addWidget(
            detail_box,
            2,
        )

        root.addLayout(
            body
        )

    def bind_events(
        self,
    ):

        self.demo_button.clicked.connect(
            self.create_demo_job
        )

        self.run_next_button.clicked.connect(
            self.run_next
        )

        self.pause_button.clicked.connect(
            self.pause_current
        )

        self.resume_button.clicked.connect(
            self.resume_current
        )

        self.cancel_button.clicked.connect(
            self.cancel_current
        )

        self.retry_button.clicked.connect(
            self.retry_current
        )

        self.priority_combo.currentTextChanged.connect(
            self.change_priority
        )

        self.refresh_button.clicked.connect(
            self.refresh
        )

        self.list.currentTextChanged.connect(
            self.on_selected_text
        )

        bus.subscribe(
            Events.QUEUE_CHANGED,
            lambda payload=None: self.refresh(),
        )

        self.timer = QTimer(
            self
        )

        self.timer.timeout.connect(
            self.refresh
        )

        self.timer.start(
            2000
        )

    def create_demo_job(
        self,
    ):

        job = AppContext.job_queue_service.enqueue_new(
            "demo_progress",
            display_name="Demo progress",
            description="Job kiểm thử an toàn, không Train/Generate.",
            scope="application",
            payload={
                "steps": 5,
                "sleep_seconds": 0,
            },
            pausable=True,
            cancellable=True,
            max_retries=1,
        )

        self.current_job_id = job.job_id

        self.refresh()

    def run_next(
        self,
    ):

        AppContext.job_runner.run_next(
            blocking=False
        )

        self.refresh()

    def pause_current(
        self,
    ):

        if self.current_job_id:

            AppContext.job_runner.request_pause(
                self.current_job_id
            )

            self.refresh()

    def resume_current(
        self,
    ):

        if self.current_job_id:

            AppContext.job_runner.request_resume(
                self.current_job_id
            )

            self.refresh()

    def cancel_current(
        self,
    ):

        if self.current_job_id:

            AppContext.job_runner.request_cancel(
                self.current_job_id
            )

            self.refresh()

    def retry_current(
        self,
    ):

        job = AppContext.job_queue_service.get(
            self.current_job_id
        )

        if job and job.state in {
            "failed",
            "interrupted",
            "blocked",
        }:

            job.state = "queued"

            AppContext.job_repository.save(
                job
            )

            self.refresh()

    def change_priority(
        self,
        priority,
    ):

        if self.current_job_id:

            try:

                AppContext.job_queue_service.change_priority(
                    self.current_job_id,
                    priority,
                )

            except Exception:

                pass

            self.refresh()

    def on_selected_text(
        self,
        text,
    ):

        if not text:

            return

        self.current_job_id = text.split(
            " "
        )[0]

        self.refresh_detail()

    def refresh(
        self,
    ):

        counts = AppContext.job_queue_service.queue_counts()

        self.queued.setText(
            f"Queued: {counts.get('queued', 0)}"
        )

        self.running.setText(
            f"Running: {counts.get('running', 0)}"
        )

        self.waiting_resource.setText(
            f"Waiting Resource: {counts.get('waiting_resource', 0)}"
        )

        self.paused.setText(
            f"Paused: {counts.get('paused', 0)}"
        )

        self.failed.setText(
            f"Failed: {counts.get('failed', 0)}"
        )

        self.completed.setText(
            f"Completed: {counts.get('completed', 0)}"
        )

        current = self.current_job_id

        self.list.clear()

        for job in AppContext.job_queue_service.list_jobs():

            self.list.addItem(
                f"{job.job_id} | {job.state} | {job.priority} | {job.display_name}"
            )

        self.current_job_id = current

        self.refresh_detail()

    def refresh_detail(
        self,
    ):

        job = AppContext.job_queue_service.get(
            self.current_job_id
        )

        if not job:

            self.detail.setText(
                "Chọn một job để xem chi tiết."
            )

            return

        logs = AppContext.job_log_service.tail(
            job,
            lines=20,
        )

        self.detail.setText(
            "\n".join(
                [
                    f"Job ID: {job.job_id}",
                    f"Type: {job.job_type}",
                    f"Display: {job.display_name}",
                    f"Scope: {job.scope}",
                    f"Project: {job.project_id or '-'}",
                    f"Voice: {job.voice_id or '-'}",
                    f"State: {job.state}",
                    f"Priority: {job.priority}",
                    f"Progress: {job.progress_percent:.1f}%",
                    f"ETA: {job.eta_seconds if job.eta_seconds is not None else '-'}",
                    f"Attempt: {job.attempt_count}/{job.max_retries}",
                    f"Error: {job.error_code} {job.error_message}",
                    f"Resource Policy: {job.resource_policy_name or '-'}",
                    f"Resource Pressure: {job.resource_pressure_state or '-'}",
                    f"Resource Wait: {job.resource_wait_reason or '-'}",
                    f"Resource Lease: {job.resource_lease_id or '-'}",
                    f"GPU: {job.selected_gpu_device_id or '-'}",
                    "",
                    "Dependencies:",
                    ", ".join(
                        job.dependency_job_ids
                    )
                    or "-",
                    "",
                    "Log tail:",
                    *logs,
                ]
            )
        )

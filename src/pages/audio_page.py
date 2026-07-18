from PySide6.QtCore import QThread
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
)

from core.app_context import AppContext

from events import (
    bus,
    Events,
)

from models.generate_job import GenerateJob

from services.text_service import TextService
from services.generate_service import GenerateService
from services.queue_worker import QueueWorker
from services.engine_service import EngineService
from services.app_events import AppEvents

from widgets.audio_toolbar import AudioToolbar
from widgets.audio_detail import AudioDetail
from widgets.text_file_list import TextFileList
from widgets.queue_list import QueueList
from widgets.generate_options_panel import GenerateOptionsPanel


class AudioPage(QWidget):

    def __init__(self):

        super().__init__()

        self.text_service = TextService()

        self.generate_service = GenerateService()

        self.engine_service = EngineService()

        self.thread = None

        self.worker = None

        root = QVBoxLayout(self)

        self.toolbar = AudioToolbar()

        root.addWidget(
            self.toolbar
        )

        self.generate_options = GenerateOptionsPanel()

        root.addWidget(
            self.generate_options
        )

        foundation_box = QGroupBox(
            "Generate Foundation"
        )

        foundation_layout = QVBoxLayout(
            foundation_box
        )

        action_row = QHBoxLayout()

        self.foundation_validate_button = QPushButton(
            "Kiểm tra Request"
        )

        self.foundation_plan_button = QPushButton(
            "Tạo Plan"
        )

        self.foundation_resume_button = QPushButton(
            "Resume Inspect"
        )

        self.foundation_retry_button = QPushButton(
            "Retry Inspect"
        )

        self.foundation_execute_button = QPushButton(
            "Generate thật chưa sẵn sàng"
        )

        self.foundation_execute_button.setEnabled(
            False
        )

        for button in [
            self.foundation_validate_button,
            self.foundation_plan_button,
            self.foundation_resume_button,
            self.foundation_retry_button,
            self.foundation_execute_button,
        ]:

            action_row.addWidget(
                button
            )

        foundation_layout.addLayout(
            action_row
        )

        self.foundation_status = QLabel(
            "Foundation: chưa kiểm tra"
        )

        self.foundation_session = QLabel(
            "Session: -"
        )

        self.foundation_plan = QLabel(
            "Plan/Units/Artifacts: -"
        )

        foundation_layout.addWidget(
            self.foundation_status
        )

        foundation_layout.addWidget(
            self.foundation_session
        )

        foundation_layout.addWidget(
            self.foundation_plan
        )

        root.addWidget(
            foundation_box
        )

        self.foundation_session_id = ""

        splitter = QSplitter()

        self.file_list = TextFileList()

        self.detail = AudioDetail()

        splitter.addWidget(
            self.file_list
        )

        splitter.addWidget(
            self.detail
        )

        splitter.setSizes([
            650,
            350,
        ])

        root.addWidget(
            splitter
        )

        self.queue_list = QueueList()

        root.addWidget(
            self.queue_list
        )

        self.toolbar.add_queue_button.clicked.connect(
            self.add_queue
        )

        self.toolbar.generate_button.clicked.connect(
            self.generate_queue
        )

        self.toolbar.stop_button.clicked.connect(
            self.stop_generate
        )

        self.toolbar.clear_queue_button.clicked.connect(
            self.clear_queue
        )

        self.toolbar.refresh_button.clicked.connect(
            self.refresh
        )

        self.foundation_validate_button.clicked.connect(
            self.validate_foundation_request
        )

        self.foundation_plan_button.clicked.connect(
            self.plan_foundation_request
        )

        self.foundation_resume_button.clicked.connect(
            self.inspect_foundation_resume
        )

        self.foundation_retry_button.clicked.connect(
            self.inspect_foundation_retry
        )

        self.toolbar.voice_combo.currentTextChanged.connect(
            self.change_voice
        )

        self.file_list.selection_changed.connect(
            self.update_summary
        )

        bus.subscribe(
            Events.WORKSPACE_CHANGED,
            self.on_project_changed
        )

        bus.subscribe(
            Events.VOICE_CHANGED,
            self.on_voice_changed
        )

        bus.subscribe(
            Events.ENGINE_CHANGED,
            self.on_engine_changed
        )

        self.refresh()

    def refresh(self):

        if not AppContext.current_project.has_project():

            self.file_list.load([])

            self.detail.clear()

            self.queue_list.load([])

            return

        files = self.text_service.list()

        self.file_list.load(
            files
        )

        project = AppContext.current_project.get()

        self.toolbar.voice_combo.blockSignals(
            True
        )

        self.toolbar.voice_combo.clear()

        for name in AppContext.voice_service.list():

            self.toolbar.voice_combo.addItem(
                name
            )

        if project.config.voice:

            self.toolbar.voice_combo.setCurrentText(
                project.config.voice
            )

        self.toolbar.voice_combo.blockSignals(
            False
        )

        self.detail.project.setText(
            project.display_name
        )
        if AppContext.current_voice.has_voice():

            voice = AppContext.current_voice.get()

            self.generate_options.load_voice(
                voice
            )

            self.detail.voice.setText(
                voice.name
            )

            self.detail.engine.setText(
                voice.config.engine or "-"
            )

        else:

            self.detail.voice.setText("-")

            self.detail.engine.setText("-")

            self.generate_options.load_voice(
                None
            )

        self.update_summary()

        self.detail.set_queue(
            AppContext.queue_service.count()
        )

        self.detail.set_progress(
            0
        )

        self.detail.set_current(
            "-"
        )

        self.queue_list.load(
            AppContext.queue_service.all()
        )

    def update_summary(self):

        self.detail.set_total(
            self.file_list.total_files()
        )

        self.detail.set_selected(
            self.file_list.selected_count()
        )

        self.detail.set_queue(
            AppContext.queue_service.count()
        )

    def add_queue(self):

        if not AppContext.current_voice.has_voice():

            self.detail.set_status(
                "Chưa chọn Voice"
            )

            return

        project = AppContext.current_project.get()

        voice = AppContext.current_voice.get()

        jobs = []

        for file in self.file_list.selected_files():

            jobs.append(
                GenerateJob(
                    text_file=file.path,
                    output_file=project.output_dir / f"{file.name}.wav",
                    voice=voice,
                    engine=project.config.engine,
                )
            )

        AppContext.queue_service.add_many(
            jobs
        )

        self.queue_list.load(
            AppContext.queue_service.all()
        )

        self.detail.set_queue(
            AppContext.queue_service.count()
        )

        self.detail.set_status(
            f"Đã thêm {len(jobs)} công việc"
        )

    def generate_queue(self):

        queue = AppContext.queue_service

        if queue.count() == 0:

            self.generate_current()

            return

        if queue.count() == 0:

            self.detail.set_status(
                "Hàng đợi đang trống"
            )

            return

        self.thread = QThread()

        self.worker = QueueWorker(
            self.generate_service,
            queue,
        )

        self.worker.moveToThread(
            self.thread
        )

        self.thread.started.connect(
            self.worker.run
        )

        self.worker.started.connect(
            lambda: self.detail.set_status(
                "Đang tạo Audio..."
            )
        )

        self.worker.progress.connect(
            self.update_progress
        )

        self.worker.finished.connect(
            self.generate_finished
        )

        self.worker.failed.connect(
            self.detail.set_status
        )

        self.worker.finished.connect(
            self.thread.quit
        )

        self.thread.finished.connect(
            self.thread.deleteLater
        )

        self.thread.start()

## ===== KẾT THÚC PART 2 =====
    def generate_current(self):

        if not AppContext.current_voice.has_voice():

            self.detail.set_status(
                "Chưa chọn Voice"
            )

            return

        project = AppContext.current_project.get()

        voice = AppContext.current_voice.get()

        request = self.generate_options.build_request(
            project_id=project.id,
            voice_id=voice.id,
        )

        result = self.generate_service.generate_request(
            request=request,
            voice=voice,
            project=project,
        )

        AppContext.project_service.save_generate_selection(
            project,
            request.selection,
        )

        if result.ok:

            self.detail.set_status(
                "Hoàn thành tạo Audio"
            )

            self.detail.set_progress(
                100
            )

            return

        self.detail.set_status(
            "Generate lỗi: "
            + ", ".join(
                result.errors
            )
        )

    def foundation_payload(self):

        project_id = ""

        voice_id = ""

        if AppContext.current_project.has_project():

            project_id = AppContext.current_project.get().id

        if AppContext.current_voice.has_voice():

            voice_id = AppContext.current_voice.get().id

        request = self.generate_options.build_request(
            project_id=project_id,
            voice_id=voice_id,
        )

        return {
            "project_id": request.project_id,
            "voice_id": request.selection.voice_id,
            "variant_id": request.selection.selected_variant_id,
            "style_id": request.selection.reference_style_id,
            "text": request.text,
            "text_file": request.text_file,
            "output_folder": request.selection.output_folder,
            "output_name": request.selection.output_name,
            "output_format": request.selection.output_format,
            "mp3_bitrate_kbps": request.selection.mp3_bitrate_kbps,
            "language": "vi",
        }

    def validate_foundation_request(self):

        report = AppContext.generate_session_service.validate_request(
            self.foundation_payload()
        )

        self.foundation_status.setText(
            "Foundation validation: "
            + (
                "OK"
                if report.ok
                else ", ".join(
                    issue.code
                    for issue in report.issues
                )
            )
        )

    def plan_foundation_request(self):

        result = AppContext.generate_session_service.create_session(
            self.foundation_payload()
        )

        self.foundation_session_id = result[
            "session"
        ][
            "session_id"
        ]

        self.foundation_session.setText(
            "Session: "
            + self.foundation_session_id
        )

        manifest = result.get(
            "manifest"
        ) or {}

        self.foundation_plan.setText(
            "Plan/Units/Artifacts: "
            + str(
                manifest.get(
                    "units_total",
                    0,
                )
            )
            + " units | "
            + str(
                len(
                    manifest.get(
                        "artifact_records",
                        [],
                    )
                )
            )
            + " artifacts"
        )

        self.foundation_status.setText(
            "Foundation plan: "
            + result[
                "session"
            ][
                "status"
            ]
        )

    def inspect_foundation_resume(self):

        if not self.foundation_session_id:

            self.foundation_status.setText(
                "Chưa có Session để resume inspect."
            )

            return

        result = AppContext.generate_session_service.inspect_resume(
            self.foundation_session_id
        )

        self.foundation_status.setText(
            "Resume inspect: "
            + str(
                len(
                    result.get(
                        "pending_units",
                        [],
                    )
                )
            )
            + " pending"
        )

    def inspect_foundation_retry(self):

        if not self.foundation_session_id:

            self.foundation_status.setText(
                "Chưa có Session để retry inspect."
            )

            return

        plan = AppContext.generate_session_service.get_plan(
            self.foundation_session_id
        )

        units = plan.get(
            "units",
            [],
        ) if plan else []

        if not units:

            self.foundation_status.setText(
                "Không có Unit để retry inspect."
            )

            return

        result = AppContext.generate_session_service.inspect_retry(
            self.foundation_session_id,
            units[
                0
            ][
                "unit_id"
            ],
        )

        self.foundation_status.setText(
            "Retry inspect: "
            + (
                "có thể"
                if result.get(
                    "can_retry",
                    False,
                )
                else "chưa thể"
            )
        )

    def update_progress(self, job):

        queue = AppContext.queue_service

        jobs = queue.all()

        finished = sum(
            1
            for item in jobs
            if item.status == "finished"
        )

        total = len(jobs)

        percent = 0

        if total:

            percent = int(
                finished * 100 / total
            )

        self.detail.set_progress(
            percent
        )

        self.detail.set_current(
            job.text_file.name
        )

        self.detail.set_status(
            f"Đã tạo {finished}/{total} file"
        )

        self.queue_list.load(
            jobs
        )

    def generate_finished(self):

        self.detail.set_progress(
            100
        )

        self.detail.set_current(
            "-"
        )

        self.detail.set_status(
            "Hoàn thành tạo Audio"
        )

        self.queue_list.load(
            AppContext.queue_service.all()
        )

        self.thread = None

        self.worker = None

    def stop_generate(self):

        if self.worker is None or self.thread is None:
            return

        self.worker.cancel()

        self.thread.quit()

        self.thread.wait()

        self.thread = None

        self.worker = None

        self.detail.set_current(
            "-"
        )

        self.detail.set_status(
            "Đã dừng"
        )

    def clear_queue(self):

        AppContext.queue_service.clear()

        self.queue_list.load(
            []
        )

        self.detail.set_queue(
            0
        )

        self.detail.set_progress(
            0
        )

        self.detail.set_current(
            "-"
        )

        self.detail.set_status(
            "Đã xóa hàng đợi"
        )

    def change_voice(
        self,
        name
    ):

        if not name:
            return

        project = AppContext.current_project.get()

        voice = AppContext.voice_service.load(
            name
        )

        AppContext.current_voice.set(
            voice
        )

        project.config.voice = name

        AppContext.project_service.save(
            project
        )

        self.detail.voice.setText(
            voice.name
        )

        self.detail.engine.setText(
            project.config.engine or "-"
        )

        AppEvents.voice_changed(
            voice
        )

    def change_engine(
        self,
        engine_id
    ):

        if not engine_id:
            return

        project = AppContext.current_project.get()

        project.config.engine = engine_id

        AppContext.project_service.save(
            project
        )

        self.engine_service.select(
            engine_id
        )

        self.detail.engine.setText(
            engine_id
        )

        AppEvents.engine_changed(
            AppContext.engine_manager.current().info()
        )

    def on_project_changed(
        self,
        project
    ):

        self.refresh()

    def on_engine_changed(
        self,
        engine
    ):

        self.refresh()

    def on_voice_changed(
        self,
        voice
    ):

        self.refresh()

## ===== KẾT THÚC FILE =====

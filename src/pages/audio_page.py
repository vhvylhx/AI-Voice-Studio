from PySide6.QtCore import QThread
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
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

from widgets.audio_toolbar import AudioToolbar
from widgets.audio_detail import AudioDetail
from widgets.text_file_list import TextFileList
from widgets.queue_list import QueueList


class AudioPage(QWidget):

    def __init__(self):

        super().__init__()

        self.text_service = TextService()

        self.generate_service = GenerateService()

        self.thread = None

        self.worker = None

        root = QVBoxLayout(self)

        self.toolbar = AudioToolbar()

        root.addWidget(
            self.toolbar
        )

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

        self.detail.project.setText(
            project.name
        )

        if AppContext.current_voice.has_voice():

            voice = AppContext.current_voice.get()

            self.detail.voice.setText(
                voice.name
            )

            self.detail.engine.setText(
                voice.config.engine or "-"
            )

        else:

            self.detail.voice.setText("-")

            self.detail.engine.setText("-")

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
                    engine=voice.config.engine,
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

    def on_project_changed(self, project):

        self.refresh()

    def on_voice_changed(self, voice):

        self.refresh()
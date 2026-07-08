from PySide6.QtCore import (
    QObject,
    Signal,
)


class QueueWorker(QObject):

    started = Signal()

    progress = Signal(object)

    finished = Signal()

    failed = Signal(object)

    def __init__(
        self,
        generate_service,
        queue,
    ):

        super().__init__()

        self.generate_service = generate_service

        self.queue = queue

        self._cancel = False

    def run(self):

        self.started.emit()

        try:

            for job in self.queue.all():

                if self._cancel:
                    break

                if job.status != "waiting":
                    continue

                job.status = "running"

                job.progress = 0

                try:

                    self.generate_service.generate(
                        job
                    )

                    job.progress = 100

                    job.status = "finished"

                except Exception as e:

                    job.status = "failed"

                    job.error = str(e)

                self.progress.emit(
                    job
                )

            self.finished.emit()

        except Exception as e:

            self.failed.emit(e)

    def cancel(self):

        self._cancel = True
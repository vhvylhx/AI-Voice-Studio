import threading
from uuid import uuid4

from models.job_model import now_iso
from services.job_state_machine import JobStateMachine
from services.job_worker import (
    JobCancelled,
    JobExecutionContext,
    JobPaused,
)


class JobRunner:

    def __init__(
        self,
        repository,
        queue_service,
        handler_registry,
        log_service,
        app_context=None,
    ):

        self.repository = repository

        self.queue_service = queue_service

        self.handler_registry = handler_registry

        self.log_service = log_service

        self.app_context = app_context

        self.state_machine = JobStateMachine()

        self.active_job_id = ""

        self.active_worker = None

        self.worker_thread = None

        self.stop_requested = False

        self.lease_owner = f"avs_{uuid4().hex[:12]}"

        if hasattr(
            self.queue_service,
            "lease_owner",
        ):

            self.queue_service.lease_owner = self.lease_owner

    def context(
        self,
    ):

        return JobExecutionContext(
            repository=self.repository,
            log_service=self.log_service,
            queue_service=self.queue_service,
            app_context=self.app_context,
        )

    def run_next(
        self,
        blocking=True,
    ):

        job = self.queue_service.dequeue_next()

        if job is None:

            return None

        if not blocking:

            thread = threading.Thread(
                target=self.run_job,
                args=(
                    job.job_id,
                ),
                daemon=True,
            )

            self.worker_thread = thread

            thread.start()

            return job

        return self.run_job(
            job.job_id
        )

    def start_background(
        self,
    ):

        if self.worker_thread and self.worker_thread.is_alive():

            return False

        self.stop_requested = False

        self.worker_thread = threading.Thread(
            target=self.run_loop,
            daemon=True,
        )

        self.worker_thread.start()

        return True

    def run_loop(
        self,
    ):

        while not self.stop_requested:

            job = self.run_next(
                blocking=True
            )

            if job is None:

                break

    def run_job(
        self,
        job_id,
    ):

        job = self.repository.load(
            job_id
        )

        if job is None:

            return None

        worker = self.handler_registry.create(
            job.job_type
        )

        if worker is None:

            job.state = "blocked"

            job.error_code = "handler_missing"

            job.error_message = (
                "KhÃ´ng cÃ³ worker phÃ¹ há»£p cho job type nÃ y."
            )

            self.repository.save(
                job
            )

            self.release_resource_lease(
                job
            )

            return job

        self.active_job_id = job.job_id

        self.active_worker = worker

        context = self.context()

        try:

            if not job.is_terminal():

                job.state = "running"

                job.started_at = job.started_at or now_iso()

                job.lease_owner = self.lease_owner

                job.last_heartbeat_at = now_iso()

                self.repository.save(
                    job
                )

            self.log_service.write(
                job,
                "Job báº¯t Ä‘áº§u cháº¡y.",
                stage="runner",
            )

            result = worker.execute(
                job,
                context,
            )

            job = self.repository.load(
                job.job_id
            ) or job

            job.result = result or {}

            job.state = "completed"

            job.completed_at = now_iso()

            job.progress_percent = 100.0

            job.error_code = ""

            job.error_message = ""

            self.repository.save(
                job
            )

            self.queue_service.mark_waiting_dependencies_ready()

            self.queue_service.mark_waiting_resources_ready()

            self.log_service.write(
                job,
                "Job hoÃ n thÃ nh.",
                level="success",
                stage="runner",
            )

            return job

        except JobPaused:

            job = self.repository.load(
                job.job_id
            ) or job

            job.state = "paused"

            job.paused_at = now_iso()

            self.repository.save(
                job
            )

            self.release_resource_lease(
                job
            )

            self.log_service.write(
                job,
                "Job Ä‘Ã£ táº¡m dá»«ng á»Ÿ safe point.",
                level="warning",
                stage="runner",
            )

            return job

        except JobCancelled:

            job = self.repository.load(
                job.job_id
            ) or job

            job.state = "cancelling"

            self.repository.save(
                job
            )

            try:

                worker.cleanup(
                    job,
                    context,
                )

            finally:

                job.state = "cancelled"

                job.cancelled_at = now_iso()

                self.repository.save(
                    job
                )

            self.log_service.write(
                job,
                "Job Ä‘Ã£ há»§y an toÃ n.",
                level="warning",
                stage="runner",
            )

            return job

        except Exception as exc:

            job = self.repository.load(
                job.job_id
            ) or job

            job.attempt_count += 1

            job.error_code = exc.__class__.__name__

            job.error_message = str(
                exc
            )

            if job.attempt_count <= job.max_retries:

                job.state = "retry_wait"

                job.progress_message = (
                    "Job lá»—i vÃ  Ä‘ang chá» retry."
                )

            else:

                job.state = "failed"

                job.failed_at = now_iso()

            self.repository.save(
                job
            )

            self.log_service.write(
                job,
                job.error_message,
                level="error",
                stage="runner",
                data={
                    "error_code": job.error_code,
                    "attempt": job.attempt_count,
                },
            )

            return job

        finally:

            try:

                latest = self.repository.load(
                    job_id
                )

                if latest and latest.is_terminal():

                    self.release_resource_lease(
                        latest
                    )

            except Exception:

                pass

            self.active_job_id = ""

            self.active_worker = None

    def release_resource_lease(
        self,
        job,
    ):

        manager = getattr(
            self.queue_service,
            "resource_lease_manager",
            None,
        )

        if manager is None:

            return False

        released = manager.release(
            job.resource_lease_id
        )

        if released:

            job.resource_lease_id = ""

            self.repository.save(
                job
            )

        return released

    def request_pause(
        self,
        job_id,
    ):

        job = self.queue_service.request_pause(
            job_id
        )

        if (
            self.active_job_id == job_id
            and self.active_worker is not None
        ):

            self.active_worker.request_pause()

        return job

    def request_resume(
        self,
        job_id,
    ):

        job = self.queue_service.request_resume(
            job_id
        )

        if (
            self.active_job_id == job_id
            and self.active_worker is not None
        ):

            self.active_worker.request_resume()

        if job and job.state == "resume_requested":

            job.state = "queued"

            self.repository.save(
                job
            )

        return job

    def request_cancel(
        self,
        job_id,
    ):

        job = self.queue_service.request_cancel(
            job_id
        )

        if (
            self.active_job_id == job_id
            and self.active_worker is not None
        ):

            self.active_worker.request_cancel()

        return job

    def shutdown(
        self,
        wait_seconds=1.0,
    ):

        self.stop_requested = True

        if self.active_job_id:

            job = self.repository.load(
                self.active_job_id
            )

            if job:

                job.state = "interrupted"

                job.recovery_state[
                    "shutdown"
                ] = {
                    "marked_at": now_iso(),
                    "policy": "manual_resume_required",
                }

                self.repository.save(
                    job
                )

                self.release_resource_lease(
                    job
                )

        if self.worker_thread and self.worker_thread.is_alive():

            self.worker_thread.join(
                timeout=wait_seconds
            )

        return {
            "stopped": True,
            "active_job_id": self.active_job_id,
        }

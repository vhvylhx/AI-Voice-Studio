import threading
from os import cpu_count
from os import getpid
from uuid import uuid4

from models.job_model import now_iso
from models.resource_model import FEATURE_MODE_ENFORCE
from models.resource_model import ResourceRequirement
from models.resource_model import THREAD_BUDGET_STATE_APPLIED
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
        thread_budget_service=None,
    ):

        self.repository = repository

        self.queue_service = queue_service

        self.handler_registry = handler_registry

        self.log_service = log_service

        self.app_context = app_context

        self.thread_budget_service = thread_budget_service

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
        environment=None,
        thread_budget_observation=None,
        thread_budget_state=None,
    ):

        return JobExecutionContext(
            repository=self.repository,
            log_service=self.log_service,
            queue_service=self.queue_service,
            app_context=self.app_context,
            environment=environment,
            thread_budget_observation=thread_budget_observation,
            thread_budget_state=thread_budget_state,
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
        thread_budget_observation = None
        thread_budget_state = None
        primary_error = None

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

            thread_budget_observation, thread_budget_state = (
                self.prepare_thread_budget(
                    job,
                    worker,
                )
            )

            if thread_budget_state is not None:

                context = self.context(
                    environment=thread_budget_state.environment_after,
                    thread_budget_observation=thread_budget_observation,
                    thread_budget_state=thread_budget_state,
                )

                self.store_thread_budget_audit(
                    job.job_id,
                    thread_budget_observation,
                    thread_budget_state,
                )

                if (
                    thread_budget_state.mode == FEATURE_MODE_ENFORCE
                    and thread_budget_state.status
                    != THREAD_BUDGET_STATE_APPLIED
                ):

                    raise RuntimeError(
                        "thread_budget_enforcement_not_applied"
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

            primary_error = JobPaused(
                "job_pause_requested"
            )

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

            primary_error = JobCancelled(
                "job_cancel_requested"
            )

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

            primary_error = exc

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

            self.restore_thread_budget(
                thread_budget_state,
                primary_error=primary_error,
            )

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

    def prepare_thread_budget(
        self,
        job,
        worker,
    ):

        if self.thread_budget_service is None:

            return None, None

        requirement = self.thread_budget_requirement(
            job,
            worker,
        )

        return self.thread_budget_service.prepare_enforcement(
            engine_id=self.thread_budget_engine_id(
                job,
                worker,
            ),
            environment=dict(
                job.payload.get(
                    "environment",
                    {},
                )
            ),
            workload_class=requirement.workload_class,
            requested_threads=requirement.cpu_threads,
            total_logical_cpu_threads=cpu_count()
            or 1,
            job_id=job.job_id,
            lease_id=job.resource_lease_id,
            process_id=str(
                getpid()
            ),
            owner_id=self.lease_owner,
            process_thread_count=threading.active_count(),
        )

    def restore_thread_budget(
        self,
        thread_budget_state,
        primary_error=None,
    ):

        if (
            self.thread_budget_service is None
            or thread_budget_state is None
            or thread_budget_state.status != THREAD_BUDGET_STATE_APPLIED
        ):

            return None

        restored = self.thread_budget_service.restore_enforcement(
            thread_budget_state,
            engine_id=thread_budget_state.engine_id,
            primary_error=primary_error,
        )

        self.store_thread_budget_audit(
            restored.job_id,
            None,
            restored,
        )

        return restored

    def thread_budget_requirement(
        self,
        job,
        worker,
    ):

        if job.resource_requirement:

            return ResourceRequirement.from_dict(
                job.resource_requirement
            )

        return ResourceRequirement.from_dict(
            getattr(
                worker,
                "resource_requirement",
                {},
            )
        )

    def thread_budget_engine_id(
        self,
        job,
        worker,
    ):

        return (
            job.payload.get(
                "thread_budget_engine_id",
                "",
            )
            or job.payload.get(
                "engine_id",
                "",
            )
            or getattr(
                worker,
                "thread_budget_engine_id",
                "",
            )
            or job.job_type
        )

    def store_thread_budget_audit(
        self,
        job_id,
        observation,
        state,
    ):

        job = self.repository.load(
            job_id
        )

        if job is None:

            return None

        job.recovery_state[
            "thread_budget_phase8"
        ] = {
            "observation": observation.to_dict()
            if observation is not None
            else None,
            "state": state.to_dict()
            if state is not None
            else None,
        }

        self.repository.save(
            job
        )

        return job

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
            job.resource_lease_id,
            job_id=job.job_id,
            owner=self.lease_owner,
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

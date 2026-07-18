from models.job_model import (
    JOB_PRIORITIES,
    JobModel,
    now_iso,
)
from services.job_state_machine import JobStateMachine


class JobQueueService:

    RUNNABLE_STATES = {
        "queued",
        "retry_wait",
    }

    def __init__(
        self,
        repository,
        state_machine=None,
        settings=None,
        handler_registry=None,
        resource_decision_service=None,
        resource_lease_manager=None,
        lease_owner="",
    ):

        self.repository = repository

        self.state_machine = (
            state_machine
            or JobStateMachine()
        )

        self.settings = settings

        self.handler_registry = handler_registry

        self.resource_decision_service = resource_decision_service

        self.resource_lease_manager = resource_lease_manager

        self.lease_owner = lease_owner

    def create_job(
        self,
        job_type,
        display_name="",
        description="",
        scope="application",
        project_id="",
        voice_id="",
        style_profile_id="",
        dataset_id="",
        reference_asset_ids=None,
        payload=None,
        priority="normal",
        dependency_job_ids=None,
        worker_type="",
        resumable=False,
        cancellable=True,
        pausable=False,
        max_retries=0,
        retry_delay_seconds=0,
        idempotency_key="",
    ):

        if idempotency_key:

            existing = self.find_by_idempotency(
                idempotency_key
            )

            if existing and not existing.is_terminal():

                return existing

        job = JobModel(
            job_id=self.repository.next_id(),
            job_type=job_type,
            display_name=display_name
            or job_type,
            description=description,
            scope=scope,
            project_id=project_id,
            voice_id=voice_id,
            style_profile_id=style_profile_id,
            dataset_id=dataset_id,
            reference_asset_ids=reference_asset_ids
            or [],
            payload=payload
            or {},
            priority=priority
            if priority in JOB_PRIORITIES
            else "normal",
            dependency_job_ids=dependency_job_ids
            or [],
            worker_type=worker_type,
            resumable=resumable,
            cancellable=cancellable,
            pausable=pausable,
            max_retries=max_retries,
            retry_delay_seconds=retry_delay_seconds,
            idempotency_key=idempotency_key,
        )

        self.validate_dependencies(
            job
        )

        return self.repository.save(
            job
        )

    def enqueue(
        self,
        job,
    ):

        job = JobModel.from_dict(
            job.to_dict()
            if hasattr(
                job,
                "to_dict",
            )
            else job
        )

        if job.state == "created":

            self.state_machine.apply(
                job,
                "queued",
            )

        elif job.state in {
            "interrupted",
            "failed",
            "retry_wait",
            "resume_requested",
        }:

            job.state = "queued"

            job.queued_at = now_iso()

        return self.repository.save(
            job
        )

    def enqueue_new(
        self,
        *args,
        **kwargs,
    ):

        return self.enqueue(
            self.create_job(
                *args,
                **kwargs,
            )
        )

    def list_jobs(
        self,
        **filters,
    ):

        return self.repository.list_jobs(
            **filters
        )

    def get(
        self,
        job_id,
    ):

        return self.repository.load(
            job_id
        )

    def queue_counts(
        self,
    ):

        result = {}

        for job in self.list_jobs():

            result[
                job.state
            ] = result.get(
                job.state,
                0,
            ) + 1

        return result

    def dequeue_next(
        self,
    ):

        blocked = []

        for job in self.list_jobs():

            if job.state not in self.RUNNABLE_STATES:

                continue

            dependency_state = self.dependency_state(
                job
            )

            if dependency_state == "ready":

                resource_state = self.resource_state(
                    job
                )

                if resource_state == "ready":

                    return job

                continue

            if dependency_state == "waiting":

                job.state = "waiting_dependency"

                job.progress_message = (
                    "Äang chá» job phá»¥ thuá»™c hoĂ n thĂ nh."
                )

                self.repository.save(
                    job
                )

            else:

                job.state = "blocked"

                job.error_code = "dependency_failed"

                job.error_message = (
                    "Job phá»¥ thuá»™c tháº¥t báº¡i hoáº·c bá»‹ há»§y."
                )

                self.repository.save(
                    job
                )

                blocked.append(
                    job
                )

        return None

    def resource_state(
        self,
        job,
    ):

        if (
            self.resource_decision_service is None
            or self.resource_lease_manager is None
        ):

            return "ready"

        requirement = self.resource_requirement(
            job
        )

        decision = self.resource_decision_service.evaluate(
            requirement
        )

        job.resource_requirement = requirement.to_dict()

        job.resource_decision = decision.to_dict()

        job.resource_pressure_state = decision.pressure_state

        job.resource_wait_reason = decision.reason_code

        job.selected_gpu_device_id = (
            decision.selected_gpu_device_id
        )

        job.resource_policy_name = decision.policy.get(
            "display_name",
            ""
        )

        if decision.status == "unsupported":

            job.state = "blocked"

            job.error_code = decision.reason_code

            job.error_message = decision.message_vi

            self.repository.save(
                job
            )

            return "blocked"

        if decision.status == "waiting_resource":

            if not job.resource_wait_started_at:

                job.resource_wait_started_at = now_iso()

            job.state = "waiting_resource"

            job.progress_message = decision.message_vi

            self.repository.save(
                job
            )

            return "waiting"

        lease, reason = self.resource_lease_manager.acquire(
            job,
            requirement,
            selected_gpu_device_id=decision.selected_gpu_device_id,
            owner=self.lease_owner,
        )

        if lease is None:

            if not job.resource_wait_started_at:

                job.resource_wait_started_at = now_iso()

            job.state = "waiting_resource"

            job.resource_wait_reason = reason

            job.progress_message = (
                "Đang chờ tài nguyên do policy/lease hiện tại."
            )

            self.repository.save(
                job
            )

            return "waiting"

        job.resource_lease_id = lease.lease_id

        job.resource_snapshot_at_start = decision.snapshot

        job.resource_wait_started_at = ""

        job.resource_wait_reason = ""

        job.state = "running"

        self.repository.save(
            job
        )

        return "ready"

    def resource_requirement(
        self,
        job,
    ):

        if job.resource_requirement:

            from models.resource_model import ResourceRequirement

            return ResourceRequirement.from_dict(
                job.resource_requirement
            )

        if self.handler_registry is not None:

            return self.handler_registry.resource_requirement(
                job.job_type
            )

        from models.resource_model import ResourceRequirement

        return ResourceRequirement()

    def dependency_state(
        self,
        job,
    ):

        if not job.dependency_job_ids:

            return "ready"

        for dependency_id in job.dependency_job_ids:

            dependency = self.repository.load(
                dependency_id
            )

            if dependency is None:

                return "blocked"

            if dependency.state == "completed":

                continue

            if dependency.state in {
                "failed",
                "cancelled",
                "blocked",
                "interrupted",
            }:

                return "blocked"

            return "waiting"

        return "ready"

    def mark_waiting_dependencies_ready(
        self,
    ):

        changed = []

        for job in self.list_jobs(
            state="waiting_dependency"
        ):

            state = self.dependency_state(
                job
            )

            if state == "ready":

                job.state = "queued"

            elif state == "blocked":

                job.state = "blocked"

                job.error_code = "dependency_failed"

            else:

                continue

            self.repository.save(
                job
            )

            changed.append(
                job.job_id
            )

        return changed

    def mark_waiting_resources_ready(
        self,
    ):

        changed = []

        for job in self.list_jobs(
            state="waiting_resource"
        ):

            job.state = "queued"

            self.repository.save(
                job
            )

            changed.append(
                job.job_id
            )

        return changed

    def request_pause(
        self,
        job_id,
    ):

        job = self.repository.load(
            job_id
        )

        if not job:

            return None

        if not job.pausable:

            job.error_code = "job_not_pausable"

            job.error_message = "Job nĂ y khĂ´ng há»— trá»£ Pause."

            return self.repository.save(
                job
            )

        if job.state == "running":

            job.state = "pause_requested"

        return self.repository.save(
            job
        )

    def request_resume(
        self,
        job_id,
    ):

        job = self.repository.load(
            job_id
        )

        if not job:

            return None

        if job.state in {
            "paused",
            "interrupted",
        }:

            job.state = "resume_requested"

        return self.repository.save(
            job
        )

    def request_cancel(
        self,
        job_id,
    ):

        job = self.repository.load(
            job_id
        )

        if not job:

            return None

        if not job.cancellable:

            job.error_code = "job_not_cancellable"

            job.error_message = "Job nĂ y khĂ´ng há»— trá»£ Cancel."

            return self.repository.save(
                job
            )

        if job.state in {
            "created",
            "queued",
            "waiting_dependency",
            "waiting_resource",
            "paused",
            "resume_requested",
            "retry_wait",
        }:

            job.state = "cancelled"

            job.cancelled_at = now_iso()

        elif job.state == "running":

            job.state = "cancel_requested"

        return self.repository.save(
            job
        )

    def change_priority(
        self,
        job_id,
        priority,
    ):

        job = self.repository.load(
            job_id
        )

        if not job:

            return None

        if priority not in JOB_PRIORITIES:

            raise ValueError(
                "invalid_job_priority"
            )

        job.priority = priority

        return self.repository.save(
            job
        )

    def find_by_idempotency(
        self,
        idempotency_key,
    ):

        for job in self.list_jobs():

            if job.idempotency_key == idempotency_key:

                return job

        return None

    def validate_dependencies(
        self,
        job,
    ):

        if job.job_id in job.dependency_job_ids:

            raise ValueError(
                "job_self_dependency"
            )

        for dependency_id in job.dependency_job_ids:

            dependency = self.repository.load(
                dependency_id
            )

            if dependency and job.job_id in dependency.dependency_job_ids:

                raise ValueError(
                    "job_dependency_cycle"
                )

        return True

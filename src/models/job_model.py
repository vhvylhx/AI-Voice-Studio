import json
from dataclasses import dataclass, field
from datetime import datetime


JOB_SCHEMA_VERSION = 1


JOB_STATES = {
    "created",
    "queued",
    "waiting_dependency",
    "waiting_resource",
    "running",
    "pause_requested",
    "paused",
    "resume_requested",
    "cancel_requested",
    "cancelling",
    "retry_wait",
    "completed",
    "failed",
    "cancelled",
    "interrupted",
    "blocked",
}


JOB_TERMINAL_STATES = {
    "completed",
    "failed",
    "cancelled",
    "interrupted",
    "blocked",
}


JOB_PRIORITIES = {
    "low": 10,
    "normal": 20,
    "high": 30,
    "urgent": 40,
}


def now_iso():

    return datetime.now().isoformat()


def json_safe(value):

    try:

        json.dumps(
            value,
            ensure_ascii=False,
        )

        return value

    except TypeError:

        if isinstance(
            value,
            dict,
        ):

            return {
                str(
                    key
                ): json_safe(
                    item
                )
                for key, item in value.items()
            }

        if isinstance(
            value,
            (
                list,
                tuple,
                set,
            ),
        ):

            return [
                json_safe(
                    item
                )
                for item in value
            ]

        return str(
            value
        )


@dataclass
class JobModel:

    job_id: str

    job_type: str

    display_name: str = ""

    description: str = ""

    scope: str = "application"

    project_id: str = ""

    voice_id: str = ""

    style_profile_id: str = ""

    dataset_id: str = ""

    reference_asset_ids: list = field(
        default_factory=list
    )

    payload: dict = field(
        default_factory=dict
    )

    state: str = "created"

    priority: str = "normal"

    dependency_job_ids: list = field(
        default_factory=list
    )

    created_at: str = field(
        default_factory=now_iso
    )

    queued_at: str = ""

    started_at: str = ""

    paused_at: str = ""

    resumed_at: str = ""

    completed_at: str = ""

    failed_at: str = ""

    cancelled_at: str = ""

    updated_at: str = field(
        default_factory=now_iso
    )

    progress_current: int = 0

    progress_total: int = 0

    progress_percent: float = 0.0

    progress_message: str = ""

    progress_stage: str = ""

    progress_substage: str = ""

    progress_item_name: str = ""

    eta_seconds: float | None = None

    attempt_count: int = 0

    max_retries: int = 0

    retry_delay_seconds: float = 0.0

    error_code: str = ""

    error_message: str = ""

    error_details: dict = field(
        default_factory=dict
    )

    log_path: str = ""

    result: dict = field(
        default_factory=dict
    )

    schema_version: int = JOB_SCHEMA_VERSION

    worker_type: str = ""

    resumable: bool = False

    cancellable: bool = True

    pausable: bool = False

    idempotency_key: str = ""

    lease_owner: str = ""

    lease_expires_at: str = ""

    last_heartbeat_at: str = ""

    recovery_state: dict = field(
        default_factory=dict
    )

    resource_requirement: dict = field(
        default_factory=dict
    )

    resource_decision: dict = field(
        default_factory=dict
    )

    resource_lease_id: str = ""

    selected_gpu_device_id: str = ""

    resource_wait_started_at: str = ""

    resource_wait_reason: str = ""

    resource_policy_name: str = ""

    resource_snapshot_at_start: dict = field(
        default_factory=dict
    )

    resource_pressure_state: str = ""

    def to_dict(self):

        return {
            "job_id": self.job_id,
            "job_type": self.job_type,
            "display_name": self.display_name,
            "description": self.description,
            "scope": self.scope,
            "project_id": self.project_id,
            "voice_id": self.voice_id,
            "style_profile_id": self.style_profile_id,
            "dataset_id": self.dataset_id,
            "reference_asset_ids": json_safe(
                self.reference_asset_ids
            ),
            "payload": json_safe(
                self.payload
            ),
            "state": self.state,
            "priority": self.priority,
            "dependency_job_ids": json_safe(
                self.dependency_job_ids
            ),
            "created_at": self.created_at,
            "queued_at": self.queued_at,
            "started_at": self.started_at,
            "paused_at": self.paused_at,
            "resumed_at": self.resumed_at,
            "completed_at": self.completed_at,
            "failed_at": self.failed_at,
            "cancelled_at": self.cancelled_at,
            "updated_at": self.updated_at,
            "progress_current": self.progress_current,
            "progress_total": self.progress_total,
            "progress_percent": self.progress_percent,
            "progress_message": self.progress_message,
            "progress_stage": self.progress_stage,
            "progress_substage": self.progress_substage,
            "progress_item_name": self.progress_item_name,
            "eta_seconds": self.eta_seconds,
            "attempt_count": self.attempt_count,
            "max_retries": self.max_retries,
            "retry_delay_seconds": self.retry_delay_seconds,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "error_details": json_safe(
                self.error_details
            ),
            "log_path": self.log_path,
            "result": json_safe(
                self.result
            ),
            "schema_version": self.schema_version,
            "worker_type": self.worker_type,
            "resumable": self.resumable,
            "cancellable": self.cancellable,
            "pausable": self.pausable,
            "idempotency_key": self.idempotency_key,
            "lease_owner": self.lease_owner,
            "lease_expires_at": self.lease_expires_at,
            "last_heartbeat_at": self.last_heartbeat_at,
            "recovery_state": json_safe(
                self.recovery_state
            ),
            "resource_requirement": json_safe(
                self.resource_requirement
            ),
            "resource_decision": json_safe(
                self.resource_decision
            ),
            "resource_lease_id": self.resource_lease_id,
            "selected_gpu_device_id": self.selected_gpu_device_id,
            "resource_wait_started_at": self.resource_wait_started_at,
            "resource_wait_reason": self.resource_wait_reason,
            "resource_policy_name": self.resource_policy_name,
            "resource_snapshot_at_start": json_safe(
                self.resource_snapshot_at_start
            ),
            "resource_pressure_state": self.resource_pressure_state,
        }

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        data = dict(
            data or {}
        )

        allowed = {
            field_name
            for field_name in cls.__dataclass_fields__
        }

        clean = {
            key: value
            for key, value in data.items()
            if key in allowed
        }

        if not clean.get(
            "job_id"
        ):

            raise ValueError(
                "job_id_required"
            )

        if not clean.get(
            "job_type"
        ):

            raise ValueError(
                "job_type_required"
            )

        job = cls(
            **clean
        )

        if job.state not in JOB_STATES:

            job.state = "blocked"

            job.error_code = "invalid_state"

        if job.priority not in JOB_PRIORITIES:

            job.priority = "normal"

        return job

    def is_terminal(self):

        return self.state in JOB_TERMINAL_STATES

    def touch(self):

        self.updated_at = now_iso()

        return self

    def safe_summary(self):

        return {
            "job_id": self.job_id,
            "job_type": self.job_type,
            "display_name": self.display_name,
            "scope": self.scope,
            "project_id": self.project_id,
            "voice_id": self.voice_id,
            "style_profile_id": self.style_profile_id,
            "dataset_id": self.dataset_id,
            "state": self.state,
            "priority": self.priority,
            "progress_percent": self.progress_percent,
            "progress_stage": self.progress_stage,
            "progress_message": self.progress_message,
            "eta_seconds": self.eta_seconds,
            "attempt_count": self.attempt_count,
            "max_retries": self.max_retries,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "resource_requirement": json_safe(
                self.resource_requirement
            ),
            "resource_decision": json_safe(
                self.resource_decision
            ),
            "resource_lease_id": self.resource_lease_id,
            "selected_gpu_device_id": self.selected_gpu_device_id,
            "resource_wait_reason": self.resource_wait_reason,
            "resource_pressure_state": self.resource_pressure_state,
        }

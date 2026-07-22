import sys
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(
    0,
    str(
        SRC
    ),
)

from services.generate_ui_orchestration_service import (
    GenerateUiOrchestrationService,
)


class FakeGenerateSessionService:

    def __init__(self, validation_ok=True, session_status="planned"):
        self.validation_ok = validation_ok
        self.session_status = session_status
        self.create_calls = []
        self.get_plan_calls = []

    def create_session(self, payload):
        self.create_calls.append(payload)
        return {
            "validation": {
                "ok": self.validation_ok,
            },
            "session": {
                "session_id": "session_001",
                "status": self.session_status,
            },
        }

    def get_plan(self, session_id):
        self.get_plan_calls.append(session_id)
        return {
            "units": [
                {
                    "unit_id": "unit_001",
                },
            ],
        }


class FakeJobQueueService:

    def __init__(self):
        self.enqueued = []
        self.jobs = {}

    def enqueue_new(self, job_type, project_id, voice_id, payload):
        job_id = f"job_{len(self.enqueued) + 1:03d}"
        self.enqueued.append(
            {
                "job_type": job_type,
                "project_id": project_id,
                "voice_id": voice_id,
                "payload": payload,
            }
        )
        job = SimpleNamespace(
            job_id=job_id,
            state="queued",
            result={},
        )
        self.jobs[job_id] = job
        return job

    def get(self, job_id):
        return self.jobs.get(job_id)


class FakeRuntimeValidationService:

    def __init__(self, report):
        self.report = report
        self.calls = []

    def readiness(self, request):
        self.calls.append(request)
        return self.report


def sample_payload():
    return {
        "project_id": "project_001",
        "voice_id": "voice_001",
        "variant_id": "variant_001",
    }


def test_session_pipeline_is_preferred_and_enqueues_generate_unit():
    session_service = FakeGenerateSessionService()
    job_queue_service = FakeJobQueueService()
    runtime_service = FakeRuntimeValidationService(
        {
            "status": "READY",
        }
    )
    service = GenerateUiOrchestrationService(
        generate_session_service=session_service,
        job_queue_service=job_queue_service,
        runtime_validation_service=runtime_service,
        legacy_compatibility_enabled=True,
    )

    result = service.start(
        sample_payload()
    )

    assert result["ok"]
    assert result["pipeline"] == service.SESSION_PIPELINE
    assert result["status"] == "QUEUED"
    assert result["job_ids"] == ["job_001"]
    assert len(job_queue_service.enqueued) == 1
    assert job_queue_service.enqueued[0] == {
        "job_type": "generate_unit",
        "project_id": "project_001",
        "voice_id": "voice_001",
        "payload": {
            "session_id": "session_001",
            "unit_id": "unit_001",
        },
    }


def test_legacy_compatibility_requires_flag_and_unavailable_runtime():
    blocked_result = {
        "pipeline": GenerateUiOrchestrationService.BLOCKED,
        "runtime": {
            "status": "UNAVAILABLE",
        },
    }
    service = GenerateUiOrchestrationService(
        generate_session_service=FakeGenerateSessionService(),
        job_queue_service=FakeJobQueueService(),
        runtime_validation_service=None,
        legacy_compatibility_enabled=False,
    )

    assert not service.can_use_legacy_compatibility(
        blocked_result
    )

    service.legacy_compatibility_enabled = True

    assert service.can_use_legacy_compatibility(
        blocked_result
    )
    assert not service.can_use_legacy_compatibility(
        {
            "pipeline": service.BLOCKED,
            "runtime": {
                "status": "BLOCKED",
            },
        }
    )


def test_runtime_blocker_returns_blocked_before_enqueue_or_engine_call():
    session_service = FakeGenerateSessionService()
    job_queue_service = FakeJobQueueService()
    runtime_service = FakeRuntimeValidationService(
        {
            "status": "BLOCKED",
            "code": "production_reference_binding_missing",
        }
    )
    service = GenerateUiOrchestrationService(
        generate_session_service=session_service,
        job_queue_service=job_queue_service,
        runtime_validation_service=runtime_service,
        legacy_compatibility_enabled=True,
    )

    result = service.start(
        sample_payload()
    )

    assert not result["ok"]
    assert result["pipeline"] == service.BLOCKED
    assert result["status"] == "BLOCKED"
    assert result["blocker"] == "production_reference_binding_missing"
    assert job_queue_service.enqueued == []
    assert session_service.get_plan_calls == []
    assert not service.can_use_legacy_compatibility(
        result
    )


def test_active_workflow_rejects_double_click_without_creating_job():

    session_service = FakeGenerateSessionService()
    job_queue_service = FakeJobQueueService()
    service = GenerateUiOrchestrationService(
        generate_session_service=session_service,
        job_queue_service=job_queue_service,
        runtime_validation_service=FakeRuntimeValidationService(
            {
                "status": "READY",
            }
        ),
    )

    first_result = service.start(
        sample_payload()
    )

    second_result = service.start(
        sample_payload()
    )

    assert first_result["ok"]
    assert not second_result["ok"]
    assert second_result["status"] == "QUEUED"
    assert second_result["blocker"] == "generate_workflow_in_progress"
    assert len(session_service.create_calls) == 1
    assert len(job_queue_service.enqueued) == 1


def test_workflow_snapshot_reports_queued_running_completed_and_result_ids():

    job_queue_service = FakeJobQueueService()
    service = GenerateUiOrchestrationService(
        generate_session_service=FakeGenerateSessionService(),
        job_queue_service=job_queue_service,
        runtime_validation_service=FakeRuntimeValidationService(
            {
                "status": "READY",
                "code": "runtime_ready",
            }
        ),
    )

    start_result = service.start(
        sample_payload()
    )

    workflow = start_result["workflow"]
    job = job_queue_service.get(
        start_result["job_ids"][0]
    )

    queued = service.get_workflow_snapshot(
        workflow
    )

    assert queued["status"] == "QUEUED"
    assert not queued["terminal"]
    assert queued["session_id"] == "session_001"
    assert queued["job_ids"] == ["job_001"]
    assert queued["artifact_ids"] == []
    assert queued["pipeline"] == service.SESSION_PIPELINE
    assert queued["runtime"]["status"] == "READY"

    job.state = "running"

    assert service.get_workflow_snapshot(
        workflow
    )["status"] == "RUNNING"

    job.state = "completed"
    job.result = {
        "artifact_id": "artifact_001",
    }

    completed = service.get_workflow_snapshot(
        workflow
    )

    assert completed["status"] == "COMPLETED"
    assert completed["terminal"]
    assert completed["artifact_ids"] == ["artifact_001"]


def test_workflow_snapshot_reports_failed_and_allows_next_request():

    job_queue_service = FakeJobQueueService()
    service = GenerateUiOrchestrationService(
        generate_session_service=FakeGenerateSessionService(),
        job_queue_service=job_queue_service,
        runtime_validation_service=FakeRuntimeValidationService(
            {
                "status": "READY",
            }
        ),
    )

    first_result = service.start(
        sample_payload()
    )

    job_queue_service.get(
        first_result["job_ids"][0]
    ).state = "failed"

    failed = service.get_workflow_snapshot(
        first_result["workflow"]
    )

    assert failed["status"] == "FAILED"
    assert failed["terminal"]

    second_result = service.start(
        sample_payload()
    )

    assert second_result["ok"]
    assert second_result["job_ids"] == ["job_002"]


def test_workflow_snapshot_reports_blocked_state():

    job_queue_service = FakeJobQueueService()
    service = GenerateUiOrchestrationService(
        generate_session_service=FakeGenerateSessionService(),
        job_queue_service=job_queue_service,
        runtime_validation_service=FakeRuntimeValidationService(
            {
                "status": "READY",
            }
        ),
    )

    start_result = service.start(
        sample_payload()
    )

    job_queue_service.get(
        start_result["job_ids"][0]
    ).state = "blocked"

    snapshot = service.get_workflow_snapshot(
        start_result["workflow"]
    )

    assert snapshot["status"] == "BLOCKED"
    assert snapshot["terminal"]


def test_missing_persisted_job_is_reported_as_failed():

    job_queue_service = FakeJobQueueService()
    service = GenerateUiOrchestrationService(
        generate_session_service=FakeGenerateSessionService(),
        job_queue_service=job_queue_service,
        runtime_validation_service=FakeRuntimeValidationService(
            {
                "status": "READY",
            }
        ),
    )

    start_result = service.start(
        sample_payload()
    )

    del job_queue_service.jobs[
        start_result["job_ids"][0]
    ]

    snapshot = service.get_workflow_snapshot(
        start_result["workflow"]
    )

    assert snapshot["status"] == "FAILED"
    assert snapshot["terminal"]


def test_blocked_result_exposes_pipeline_status_for_ui():
    service = GenerateUiOrchestrationService(
        generate_session_service=FakeGenerateSessionService(),
        job_queue_service=FakeJobQueueService(),
        runtime_validation_service=None,
    )

    result = service.start(
        sample_payload()
    )

    assert not result["ok"]
    assert result["pipeline"] == service.BLOCKED
    assert result["status"] == "BLOCKED"
    assert result["blocker"] == "generate_runtime_validation_missing"


def test_session_validation_failure_never_silently_falls_back():
    session_service = FakeGenerateSessionService(
        validation_ok=False,
        session_status="blocked",
    )
    job_queue_service = FakeJobQueueService()
    service = GenerateUiOrchestrationService(
        generate_session_service=session_service,
        job_queue_service=job_queue_service,
        runtime_validation_service=FakeRuntimeValidationService(
            {
                "status": "READY",
            }
        ),
        legacy_compatibility_enabled=True,
    )

    result = service.start(
        sample_payload()
    )

    assert not result["ok"]
    assert result["pipeline"] == service.BLOCKED
    assert result["blocker"] == "generate_session_validation_blocked"
    assert job_queue_service.enqueued == []
    assert not service.can_use_legacy_compatibility(
        result
    )
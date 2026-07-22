import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(
    0,
    str(
        SRC
    ),
)

from models.job_model import JobModel
from services.job_handler_registry import JobHandlerRegistry
from services.job_log_service import JobLogService
from services.job_queue_service import JobQueueService
from services.job_repository import JobRepository
from services.job_runner import JobRunner
from services.job_state_machine import (
    JobStateError,
    JobStateMachine,
)


def make_stack(
    tmp_path,
):

    repository = JobRepository(
        tmp_path / "jobs"
    )

    queue = JobQueueService(
        repository
    )

    logs = JobLogService(
        repository
    )

    registry = JobHandlerRegistry()

    runner = JobRunner(
        repository=repository,
        queue_service=queue,
        handler_registry=registry,
        log_service=logs,
    )

    return repository, queue, logs, registry, runner


def test_job_model_serializes_unicode_and_json_safe():

    job = JobModel(
        job_id="job_000001",
        job_type="demo_progress",
        display_name="Kiểm thử tiếng Việt",
        payload={
            "path": Path(
                "abc"
            ),
        },
    )

    data = job.to_dict()

    encoded = json.dumps(
        data,
        ensure_ascii=False,
    )

    assert "Kiểm thử" in encoded
    assert data["payload"]["path"] == "abc"

    loaded = JobModel.from_dict(
        data
    )

    assert loaded.job_id == "job_000001"
    assert loaded.display_name == job.display_name


def test_state_machine_valid_and_invalid_transitions():

    machine = JobStateMachine()

    job = JobModel(
        job_id="job_000001",
        job_type="demo_progress",
    )

    machine.apply(
        job,
        "queued",
    )

    machine.apply(
        job,
        "running",
    )

    machine.apply(
        job,
        "pause_requested",
    )

    machine.apply(
        job,
        "paused",
    )

    try:

        machine.apply(
            job,
            "completed",
        )

        assert False

    except JobStateError:

        assert True


def test_repository_save_load_query_and_corrupt_record(tmp_path):

    repository = JobRepository(
        tmp_path / "jobs"
    )

    job = repository.save(
        JobModel(
            job_id="job_000001",
            job_type="demo_progress",
            project_id="project_1",
            state="queued",
        )
    )

    assert repository.load(
        job.job_id
    ).project_id == "project_1"

    assert repository.list_jobs(
        state="queued"
    )

    file = repository.job_file(
        job.job_id
    )

    file.write_text(
        "{broken",
        encoding="utf-8",
    )

    assert repository.load(
        job.job_id
    ) is None

    assert list(
        repository.corrupt_root.glob(
            "*.json"
        )
    )


def test_queue_priority_idempotency_and_dependencies(tmp_path):

    repository, queue, *_ = make_stack(
        tmp_path
    )

    first = queue.enqueue_new(
        "demo_progress",
        display_name="A",
        priority="low",
        idempotency_key="same",
    )

    same = queue.enqueue_new(
        "demo_progress",
        display_name="A again",
        priority="urgent",
        idempotency_key="same",
    )

    assert same.job_id == first.job_id

    urgent = queue.enqueue_new(
        "demo_progress",
        display_name="B",
        priority="urgent",
    )

    assert queue.dequeue_next().job_id == urgent.job_id

    dependency = repository.save(
        JobModel(
            job_id="job_999999",
            job_type="demo_progress",
            state="queued",
        )
    )

    child = queue.enqueue_new(
        "demo_progress",
        dependency_job_ids=[
            dependency.job_id,
        ],
    )

    assert queue.dependency_state(
        child
    ) == "waiting"


def test_runner_demo_progress_complete_log_and_eta(tmp_path):

    repository, queue, logs, _, runner = make_stack(
        tmp_path
    )

    job = queue.enqueue_new(
        "demo_progress",
        display_name="Demo",
        payload={
            "steps": 3,
            "sleep_seconds": 0,
        },
        pausable=True,
    )

    result = runner.run_next()

    assert result.state == "completed"
    assert result.progress_percent == 100
    assert result.result["steps"] == 3
    assert logs.tail(
        result
    )
    assert repository.load(
        job.job_id
    ).state == "completed"


def test_runner_missing_handler_blocks_job(tmp_path):

    repository, queue, *_ = make_stack(
        tmp_path
    )

    registry = JobHandlerRegistry()

    registry.handlers = {}

    runner = JobRunner(
        repository=repository,
        queue_service=queue,
        handler_registry=registry,
        log_service=JobLogService(
            repository
        ),
    )

    job = queue.enqueue_new(
        "missing_handler",
        display_name="Missing",
    )

    result = runner.run_next()

    assert result.state == "blocked"
    assert result.error_code == "handler_missing"
    assert repository.load(
        job.job_id
    ).state == "blocked"


def test_cancel_queued_and_non_pausable_behavior(tmp_path):

    _, queue, *_ = make_stack(
        tmp_path
    )

    job = queue.enqueue_new(
        "demo_progress",
        display_name="Cancel queued",
        pausable=False,
    )

    cancelled = queue.request_cancel(
        job.job_id
    )

    assert cancelled.state == "cancelled"

    other = queue.enqueue_new(
        "demo_progress",
        display_name="No pause",
        pausable=False,
    )

    other.state = "running"
    queue.repository.save(
        other
    )

    paused = queue.request_pause(
        other.job_id
    )

    assert paused.error_code == "job_not_pausable"


def test_retry_and_attempt_count(tmp_path):

    repository, queue, logs, registry, runner = make_stack(
        tmp_path
    )

    class FailingWorker:

        def execute(
            self,
            job,
            context,
        ):

            raise RuntimeError(
                "boom"
            )

    registry.register(
        "fail_once",
        FailingWorker,
    )

    job = queue.enqueue_new(
        "fail_once",
        max_retries=1,
    )

    result = runner.run_next()

    assert result.state == "retry_wait"
    assert result.attempt_count == 1

    result = runner.run_next()

    assert result.state == "failed"
    assert result.attempt_count == 2
    assert logs.tail(
        repository.load(
            job.job_id
        )
    )


def test_recovery_running_becomes_interrupted(tmp_path):

    repository = JobRepository(
        tmp_path / "jobs"
    )

    repository.save(
        JobModel(
            job_id="job_000001",
            job_type="demo_progress",
            state="running",
        )
    )

    repository.save(
        JobModel(
            job_id="job_000002",
            job_type="demo_progress",
            state="paused",
        )
    )

    recovered = repository.recover_startup()

    assert recovered == [
        "job_000001",
    ]
    assert repository.load(
        "job_000001"
    ).state == "interrupted"
    assert repository.load(
        "job_000002"
    ).state == "paused"


def test_job_ui_source_exists():

    file = SRC / "pages" / "jobs_page.py"

    text = file.read_text(
        encoding="utf-8"
    )

    assert "Tạo demo job" in text
    assert "Pause" in text
    assert "Cancel" in text


def test_job_local_api_read_only(tmp_path):

    repository, queue, logs, *_ = make_stack(
        tmp_path
    )

    job = queue.enqueue_new(
        "demo_progress",
        display_name="API Job",
    )

    from services.local_api_service import LocalApiService

    api = LocalApiService(
        job_queue_service=queue,
        job_log_service=logs,
    )

    jobs = api.route(
        "GET",
        "/api/v1/jobs",
        {},
    )

    assert jobs["body"]["items"][0]["job_id"] == job.job_id

    detail = api.route(
        "GET",
        f"/api/v1/jobs/{job.job_id}",
        {},
    )

    assert detail["body"]["display_name"] == "API Job"

    logs_response = api.route(
        "GET",
        f"/api/v1/jobs/{job.job_id}/logs",
        {},
    )

    assert logs_response["body"]["job_id"] == job.job_id

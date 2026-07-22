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
from models.resource_model import (
    GPUDeviceInfo,
    ResourcePolicy,
    ResourceRequirement,
    ResourceSnapshot,
)
from services.job_handler_registry import JobHandlerRegistry
from services.job_log_service import JobLogService
from services.job_queue_service import JobQueueService
from services.job_repository import JobRepository
from services.job_runner import JobRunner
from services.local_api_service import LocalApiService
from services.resource_decision_service import ResourceDecisionService
from services.resource_lease_manager import ResourceLeaseManager
from services.resource_monitor_service import ResourceMonitorService


class FakePolicyService:

    def __init__(
        self,
        policy=None,
    ):

        self.policy = policy or ResourcePolicy(
            max_concurrent_jobs=1,
            max_gpu_jobs=1,
            reserve_ram_mb=128,
            reserve_vram_mb=128,
            reserve_disk_mb=128,
            lease_ttl_seconds=60,
        )

    def load(
        self,
    ):

        return self.policy

    def summary(
        self,
    ):

        return self.policy.to_dict()


class FakeSnapshotService:

    def __init__(
        self,
        snapshot,
    ):

        self._snapshot = snapshot

    def snapshot(
        self,
        force=False,
    ):

        return self._snapshot


def make_queue(
    tmp_path,
    snapshot=None,
    policy=None,
):

    repository = JobRepository(
        tmp_path / "jobs"
    )

    policy_service = FakePolicyService(
        policy
    )

    snapshot_service = FakeSnapshotService(
        snapshot
        or ResourceSnapshot(
            ram_total_mb=8192,
            ram_available_mb=4096,
            disk_free_mb=4096,
            gpu_devices=[],
            pressure_state="normal",
        )
    )

    decision = ResourceDecisionService(
        snapshot_service=snapshot_service,
        policy_service=policy_service,
    )

    leases = ResourceLeaseManager(
        root=tmp_path / "leases",
        policy_service=policy_service,
    )

    registry = JobHandlerRegistry()

    queue = JobQueueService(
        repository,
        handler_registry=registry,
        resource_decision_service=decision,
        resource_lease_manager=leases,
        lease_owner="test_owner",
    )

    return repository, queue, registry, leases, decision


def test_resource_models_serialization():

    requirement = ResourceRequirement(
        profile_id="gpu_train",
        requires_gpu=True,
        vram_mb=4096,
        exclusive_gpu=True,
    )

    loaded = ResourceRequirement.from_dict(
        requirement.to_dict()
    )

    assert loaded.profile_id == "gpu_train"
    assert loaded.requires_gpu is True
    assert loaded.vram_mb == 4096


def test_resource_decision_ready_cpu():

    snapshot = ResourceSnapshot(
        ram_total_mb=8192,
        ram_available_mb=4096,
        disk_free_mb=4096,
        pressure_state="normal",
    )

    decision = ResourceDecisionService(
        snapshot_service=FakeSnapshotService(
            snapshot
        ),
        policy_service=FakePolicyService(),
    ).evaluate(
        ResourceRequirement(
            ram_mb=256,
            disk_free_mb=128,
        )
    )

    assert decision.status == "ready"
    assert decision.reason_code == "cpu_ready"


def test_resource_decision_waits_for_ram():

    snapshot = ResourceSnapshot(
        ram_total_mb=8192,
        ram_available_mb=100,
        disk_free_mb=4096,
        pressure_state="high",
    )

    decision = ResourceDecisionService(
        snapshot_service=FakeSnapshotService(
            snapshot
        ),
        policy_service=FakePolicyService(),
    ).evaluate(
        ResourceRequirement(
            ram_mb=2048,
        )
    )

    assert decision.status == "waiting_resource"
    assert decision.reason_code == "ram_low"


def test_gpu_requirement_selects_gpu():

    snapshot = ResourceSnapshot(
        ram_available_mb=4096,
        disk_free_mb=4096,
        gpu_devices=[
            GPUDeviceInfo(
                device_id="0",
                name="Mock GPU",
                vram_total_mb=8192,
                vram_free_mb=6144,
                cuda_available=True,
            )
        ],
        pressure_state="normal",
    )

    decision = ResourceDecisionService(
        snapshot_service=FakeSnapshotService(
            snapshot
        ),
        policy_service=FakePolicyService(),
    ).evaluate(
        ResourceRequirement(
            requires_gpu=True,
            vram_mb=1024,
            allow_cpu_fallback=False,
        )
    )

    assert decision.status == "ready"
    assert decision.selected_gpu_device_id == "0"


def test_queue_waiting_resource_and_no_duplicate_lease(tmp_path):

    policy = ResourcePolicy(
        max_concurrent_jobs=1,
        reserve_ram_mb=128,
        reserve_disk_mb=128,
    )

    repository, queue, _, leases, _ = make_queue(
        tmp_path,
        policy=policy,
    )

    first = queue.enqueue_new(
        "demo_progress",
    )

    second = queue.enqueue_new(
        "demo_progress",
    )

    runnable = queue.dequeue_next()

    assert runnable.job_id == first.job_id
    assert len(
        leases.active_leases()
    ) == 1

    assert queue.dequeue_next() is None

    loaded = repository.load(
        second.job_id
    )

    assert loaded.state == "waiting_resource"
    assert loaded.resource_wait_reason == "max_concurrent_jobs"


def test_runner_releases_resource_lease(tmp_path):

    repository, queue, registry, leases, _ = make_queue(
        tmp_path
    )

    logs = JobLogService(
        repository
    )

    runner = JobRunner(
        repository=repository,
        queue_service=queue,
        handler_registry=registry,
        log_service=logs,
    )

    queue.enqueue_new(
        "demo_progress",
        payload={
            "steps": 1,
            "sleep_seconds": 0,
        },
    )

    result = runner.run_next()

    assert result.state == "completed"
    assert leases.active_leases() == []
    assert repository.load(
        result.job_id
    ).resource_lease_id == ""


def test_resource_monitor_and_local_api(tmp_path):

    repository, queue, _, leases, decision = make_queue(
        tmp_path
    )

    monitor = ResourceMonitorService(
        snapshot_service=decision.snapshot_service,
        policy_service=decision.policy_service,
        lease_manager=leases,
        job_queue_service=queue,
    )

    queue.repository.save(
        JobModel(
            job_id="job_waiting",
            job_type="demo_progress",
            state="waiting_resource",
        )
    )

    api = LocalApiService(
        job_queue_service=queue,
        job_log_service=JobLogService(
            repository
        ),
        resource_monitor_service=monitor,
    )

    response = api.route(
        "GET",
        "/api/v1/resources",
        {},
    )

    assert response["status_code"] == 200
    assert response["body"]["available"] is True
    assert response["body"]["waiting_jobs"][0]["job_id"] == "job_waiting"


def test_resource_ui_source_exists():

    text = (
        SRC
        / "pages"
        / "resource_monitor_page.py"
    ).read_text(
        encoding="utf-8"
    )

    assert "Resource Monitor" in text
    assert "pressure_state" in text

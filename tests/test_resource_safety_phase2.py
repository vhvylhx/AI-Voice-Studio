import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(
    0,
    str(
        SRC
    ),
)

from models.resource_model import (
    GPUDeviceInfo,
    RESOURCE_REASON_CPU_FALLBACK_CONFIRMATION_REQUIRED,
    RESOURCE_REASON_DISK_BELOW_RESERVE,
    RESOURCE_REASON_DISK_SNAPSHOT_INVALID,
    RESOURCE_REASON_GPU_SNAPSHOT_UNKNOWN,
    RESOURCE_REASON_HEAVY_JOB_ALREADY_ACTIVE,
    RESOURCE_REASON_RAM_BELOW_RESERVE,
    RESOURCE_REASON_RAM_SNAPSHOT_INVALID,
    RESOURCE_REASON_RAM_SNAPSHOT_UNKNOWN,
    RESOURCE_REASON_SNAPSHOT_STALE,
    RESOURCE_REASON_VRAM_BELOW_RESERVE,
    SHADOW_DECISION_CONFIRMATION_REQUIRED,
    SHADOW_DECISION_WOULD_BLOCK,
    SHADOW_DECISION_WOULD_READY,
    SHADOW_DECISION_WOULD_WAIT,
    SNAPSHOT_STATUS_INVALID,
    SNAPSHOT_STATUS_STALE,
    SNAPSHOT_STATUS_UNKNOWN,
    SNAPSHOT_STATUS_VALID,
    WORKLOAD_CLASS_GPU_TRAINING,
    WORKLOAD_CLASS_LIGHT,
    ResolvedResourcePolicy,
    ResourcePolicy,
    ResourceRequirement,
    ResourceSnapshot,
)
from services.resource_decision_service import ResourceDecisionService
from services.resource_snapshot_service import ResourceSnapshotService


class FakePolicyService:

    def __init__(
        self,
        policy=None,
    ):

        self.policy = policy or ResourcePolicy(
            schema_version=2,
            reserve_ram_mb=8192,
            reserve_vram_mb=512,
            reserve_disk_mb=1024,
            allow_cpu_fallback=False,
            cpu_fallback_requires_job_confirmation=True,
            snapshot_ttl_seconds=2,
        )

    def load(
        self,
    ):

        legacy = ResourcePolicy.from_dict(
            self.policy.to_dict()
        )

        legacy.reserve_ram_mb = 1024
        legacy.reserve_disk_mb = 128
        legacy.allow_cpu_fallback = True

        return legacy

    def resolve(
        self,
        migrate=False,
    ):

        return ResolvedResourcePolicy.from_policy(
            self.policy
        )


class FakeSnapshotService(ResourceSnapshotService):

    def __init__(
        self,
        snapshot,
        policy_service,
        now_seconds=101.0,
    ):

        super().__init__(
            policy_service=policy_service,
            clock=lambda: now_seconds,
        )

        self._snapshot = snapshot

    def snapshot(
        self,
        force=False,
    ):

        return self._snapshot


def captured_at(
    seconds,
):

    return datetime.fromtimestamp(
        seconds
    ).isoformat()


def make_snapshot(
    **overrides,
):

    data = {
        "ram_total_mb": 32768,
        "ram_available_mb": 20000,
        "disk_total_mb": 100000,
        "disk_free_mb": 50000,
        "gpu_devices": [],
        "captured_at": captured_at(
            100
        ),
        "pressure_state": "normal",
    }

    data.update(
        overrides
    )

    return ResourceSnapshot(
        **data
    )


def make_decision_service(
    snapshot,
    policy=None,
    now_seconds=101.0,
):

    policy_service = FakePolicyService(
        policy
    )

    snapshot_service = FakeSnapshotService(
        snapshot,
        policy_service,
        now_seconds=now_seconds,
    )

    return ResourceDecisionService(
        snapshot_service=snapshot_service,
        policy_service=policy_service,
    )


def test_snapshot_validation_valid_and_fresh():

    service = make_decision_service(
        make_snapshot()
    )

    validation = service.snapshot_service.validate_snapshot(
        service.snapshot_service.snapshot(),
        policy=service.policy_service.resolve(),
    )

    assert validation.status == SNAPSHOT_STATUS_VALID
    assert validation.reason_codes == []
    assert validation.age_seconds == 1.0


def test_snapshot_validation_invalid_ram_and_disk():

    service = make_decision_service(
        make_snapshot(
            ram_available_mb=40000,
            disk_free_mb=-1,
        )
    )

    validation = service.snapshot_service.validate_snapshot(
        service.snapshot_service.snapshot(),
        policy=service.policy_service.resolve(),
    )

    assert validation.status == SNAPSHOT_STATUS_INVALID
    assert RESOURCE_REASON_RAM_SNAPSHOT_INVALID in validation.reason_codes
    assert RESOURCE_REASON_DISK_SNAPSHOT_INVALID in validation.reason_codes


def test_snapshot_validation_unknown_provider_and_stale():

    service = make_decision_service(
        make_snapshot(
            provider_status={
                "ram": "exception",
                "gpu": "driver_unknown",
            },
        ),
        now_seconds=110,
    )

    validation = service.snapshot_service.validate_snapshot(
        service.snapshot_service.snapshot(),
        policy=service.policy_service.resolve(),
    )

    assert validation.status == SNAPSHOT_STATUS_UNKNOWN
    assert RESOURCE_REASON_RAM_SNAPSHOT_UNKNOWN in validation.reason_codes
    assert RESOURCE_REASON_GPU_SNAPSHOT_UNKNOWN in validation.reason_codes
    assert RESOURCE_REASON_SNAPSHOT_STALE in validation.reason_codes


def test_snapshot_validation_stale_only():

    service = make_decision_service(
        make_snapshot(),
        now_seconds=110,
    )

    validation = service.snapshot_service.validate_snapshot(
        service.snapshot_service.snapshot(),
        policy=service.policy_service.resolve(),
    )

    assert validation.status == SNAPSHOT_STATUS_STALE
    assert validation.ram_status == SNAPSHOT_STATUS_STALE
    assert RESOURCE_REASON_SNAPSHOT_STALE in validation.reason_codes


def test_shadow_decision_blocks_heavy_unknown_ram_without_changing_actual():

    decision = make_decision_service(
        make_snapshot(
            ram_total_mb=0,
        )
    ).evaluate(
        ResourceRequirement(
            workload_class=WORKLOAD_CLASS_GPU_TRAINING,
            requires_gpu=False,
            ram_mb=256,
        )
    )

    shadow = decision.shadow_observation

    assert decision.status == "ready"
    assert shadow["actual_decision"] == "ready"
    assert shadow["shadow_decision"] == SHADOW_DECISION_WOULD_BLOCK
    assert RESOURCE_REASON_RAM_SNAPSHOT_UNKNOWN in shadow["reason_codes"]
    assert shadow["would_block"] is True
    assert shadow["monitor_only"] is True


def test_shadow_decision_light_workload_does_not_block_gpu_unknown():

    decision = make_decision_service(
        make_snapshot(
            provider_status={
                "gpu": "timeout"
            },
        )
    ).evaluate(
        ResourceRequirement(
            workload_class=WORKLOAD_CLASS_LIGHT,
            requires_gpu=False,
        )
    )

    shadow = decision.shadow_observation

    assert decision.status == "ready"
    assert shadow["shadow_decision"] == SHADOW_DECISION_WOULD_READY
    assert RESOURCE_REASON_GPU_SNAPSHOT_UNKNOWN in shadow["reason_codes"]


def test_shadow_decision_vram_below_reserve():

    decision = make_decision_service(
        make_snapshot(
            gpu_devices=[
                GPUDeviceInfo(
                    device_id="0",
                    vram_total_mb=4096,
                    vram_free_mb=400,
                    cuda_available=True,
                )
            ]
        )
    ).evaluate(
        ResourceRequirement(
            workload_class=WORKLOAD_CLASS_GPU_TRAINING,
            requires_gpu=True,
            vram_mb=256,
            allow_cpu_fallback=False,
            cpu_fallback_supported=False,
        )
    )

    shadow = decision.shadow_observation

    assert decision.status == "unsupported"
    assert shadow["shadow_decision"] == SHADOW_DECISION_WOULD_BLOCK
    assert RESOURCE_REASON_VRAM_BELOW_RESERVE in shadow["reason_codes"]


def test_shadow_decision_cpu_fallback_confirmation_required():

    decision = make_decision_service(
        make_snapshot(
            gpu_devices=[]
        )
    ).evaluate(
        ResourceRequirement(
            workload_class=WORKLOAD_CLASS_GPU_TRAINING,
            requires_gpu=True,
            vram_mb=1024,
            allow_cpu_fallback=True,
            cpu_fallback_supported=True,
            cpu_fallback_confirmed=False,
        )
    )

    shadow = decision.shadow_observation

    assert decision.status == "ready"
    assert decision.reason_code == "cpu_fallback"
    assert (
        shadow["shadow_decision"]
        == SHADOW_DECISION_CONFIRMATION_REQUIRED
    )
    assert RESOURCE_REASON_CPU_FALLBACK_CONFIRMATION_REQUIRED in shadow[
        "reason_codes"
    ]


def test_shadow_decision_heavy_job_already_active_waits():

    service = make_decision_service(
        make_snapshot()
    )

    observation = service.evaluate_shadow(
        ResourceRequirement(
            workload_class=WORKLOAD_CLASS_GPU_TRAINING,
            heavy_job=True,
        ),
        snapshot=service.snapshot_service.snapshot(),
        active_heavy_jobs=1,
    )

    assert observation.shadow_decision == SHADOW_DECISION_WOULD_WAIT
    assert RESOURCE_REASON_HEAVY_JOB_ALREADY_ACTIVE in observation.reason_codes


def test_shadow_decision_below_reserves_and_policy_fingerprint():

    decision = make_decision_service(
        make_snapshot(
            ram_available_mb=2000,
            disk_free_mb=500,
        )
    ).evaluate(
        ResourceRequirement(
            workload_class=WORKLOAD_CLASS_LIGHT,
            ram_mb=256,
            disk_free_mb=128,
        )
    )

    shadow = decision.shadow_observation

    assert decision.status == "ready"
    assert shadow["shadow_decision"] == SHADOW_DECISION_WOULD_BLOCK
    assert RESOURCE_REASON_RAM_BELOW_RESERVE in shadow["reason_codes"]
    assert RESOURCE_REASON_DISK_BELOW_RESERVE in shadow["reason_codes"]
    assert shadow["policy_fingerprint"]

import sys
from datetime import datetime
from datetime import timedelta
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
    DEFAULT_RESOURCE_FEATURE_MODES,
    FEATURE_MODE_DISABLED,
    FEATURE_MODE_ENFORCE,
    FEATURE_MODE_MONITOR_ONLY,
    GPUDeviceInfo,
    RUNTIME_GUARD_ACTION_DEESCALATE,
    RUNTIME_GUARD_ACTION_DEFER,
    RUNTIME_GUARD_ACTION_DEFER_HEAVY,
    RUNTIME_GUARD_ACTION_GRACEFUL_STOP,
    RUNTIME_GUARD_ACTION_KILL_TREE,
    RUNTIME_GUARD_ACTION_OBSERVE,
    RUNTIME_GUARD_ACTION_RECONCILE_LEASE,
    RUNTIME_GUARD_ACTION_RECONCILE_PROCESS,
    RUNTIME_GUARD_ACTION_REDUCE_BATCH,
    RUNTIME_GUARD_ACTION_REDUCE_CONCURRENCY,
    RUNTIME_GUARD_ACTION_REQUEST_PAUSE,
    RUNTIME_GUARD_ACTION_SKIP,
    RUNTIME_GUARD_STATE_DEFERRED,
    RUNTIME_GUARD_STATE_FAILED,
    RUNTIME_GUARD_STATE_SIMULATED,
    RUNTIME_GUARD_STATE_SUPPRESSED,
    RUNTIME_PRESSURE_CRITICAL,
    RUNTIME_PRESSURE_EMERGENCY,
    RUNTIME_PRESSURE_HIGH,
    RUNTIME_PRESSURE_INVALID,
    RUNTIME_PRESSURE_NORMAL,
    RUNTIME_PRESSURE_STALE,
    RUNTIME_PRESSURE_UNKNOWN,
    RUNTIME_PRESSURE_WARNING,
    RUNTIME_REASON_ACTION_COOLDOWN,
    RUNTIME_REASON_ACTION_DEESCALATED,
    RUNTIME_REASON_ACTION_DUPLICATE_SUPPRESSED,
    RUNTIME_REASON_ACTION_FAILED,
    RUNTIME_REASON_ACTION_RETRY_EXHAUSTED,
    RUNTIME_REASON_ACTION_SIMULATED,
    RUNTIME_REASON_DESTRUCTIVE_ACTION_UNAVAILABLE,
    RUNTIME_REASON_DISK_BELOW_RESERVE,
    RUNTIME_REASON_IDENTITY_UNKNOWN,
    RUNTIME_REASON_LEASE_RECONCILIATION_REQUIRED,
    RUNTIME_REASON_MODE_DISABLED,
    RUNTIME_REASON_MODE_MONITOR_ONLY,
    RUNTIME_REASON_PROCESS_RECONCILIATION_REQUIRED,
    RUNTIME_REASON_RAM_BELOW_CRITICAL,
    RUNTIME_REASON_RAM_BELOW_EMERGENCY,
    RUNTIME_REASON_RAM_BELOW_HIGH,
    RUNTIME_REASON_RAM_BELOW_WARNING,
    RUNTIME_REASON_SNAPSHOT_INVALID,
    RUNTIME_REASON_SNAPSHOT_STALE,
    RUNTIME_REASON_VRAM_BELOW_RESERVE,
    SNAPSHOT_STATUS_INVALID,
    SNAPSHOT_STATUS_STALE,
    SNAPSHOT_STATUS_UNKNOWN,
    SNAPSHOT_STATUS_VALID,
    WORKLOAD_CLASS_GPU_TRAINING,
    ResourcePolicy,
    ResourceSnapshot,
    ResolvedResourcePolicy,
)
from services.runtime_guard import RuntimeGuard
from services.runtime_guard_action_executor import (
    SimulatedRuntimeGuardActionExecutor,
)


FIXED_NOW = datetime(
    2026,
    7,
    22,
    12,
    0,
    0,
)


class FakeClock:

    def __init__(
        self,
        now=FIXED_NOW,
    ):

        self.current = now

    def __call__(
        self,
    ):

        return self.current

    def advance(
        self,
        seconds,
    ):

        self.current = self.current + timedelta(
            seconds=seconds
        )


class FakePolicyService:

    def __init__(
        self,
        mode=FEATURE_MODE_MONITOR_ONLY,
        **overrides,
    ):

        feature_modes = dict(
            DEFAULT_RESOURCE_FEATURE_MODES
        )
        feature_modes["runtime_guard_mode"] = mode

        data = {
            "schema_version": 2,
            "feature_modes": feature_modes,
            "reserve_ram_mb": 8192,
            "reserve_vram_mb": 512,
            "reserve_disk_mb": 1024,
            "action_cooldown_seconds": 30,
            "deescalation_stable_seconds": 60,
            "observation_ttl_seconds": 5,
            "max_action_attempts": 3,
            "action_retry_backoff_seconds": 10,
            "allow_simulated_throttle": True,
            "allow_simulated_pause": False,
            "allow_simulated_graceful_stop": False,
            "allow_simulated_terminate": False,
            "allow_simulated_kill_tree": False,
        }
        data.update(
            overrides
        )

        self.policy = ResourcePolicy(
            **data
        )

    def load(
        self,
    ):

        return self.policy

    def resolve(
        self,
        migrate=False,
    ):

        return ResolvedResourcePolicy.from_policy(
            self.policy
        )


def make_snapshot(
    ram_available_mb=20000,
    disk_free_mb=50000,
    gpu_free_mb=2048,
    validation_status=SNAPSHOT_STATUS_VALID,
):

    return ResourceSnapshot(
        ram_total_mb=32768,
        ram_available_mb=ram_available_mb,
        disk_total_mb=100000,
        disk_free_mb=disk_free_mb,
        gpu_devices=[
            GPUDeviceInfo(
                device_id="0",
                vram_total_mb=4096,
                vram_free_mb=gpu_free_mb,
                cuda_available=True,
            )
        ],
        validation_status=validation_status,
        captured_at=FIXED_NOW.isoformat(),
    )


def make_guard(
    mode=FEATURE_MODE_MONITOR_ONLY,
    clock=None,
    executor=None,
    **policy_overrides,
):

    return RuntimeGuard(
        policy_service=FakePolicyService(
            mode=mode,
            **policy_overrides,
        ),
        executor=executor or SimulatedRuntimeGuardActionExecutor(),
        clock=clock or FakeClock(),
    )


def test_policy_defaults_are_monitor_only_and_additive():

    resolved = FakePolicyService().resolve()

    assert resolved.feature_modes["runtime_guard_mode"] == (
        FEATURE_MODE_MONITOR_ONLY
    )
    assert resolved.action_cooldown_seconds == 30
    assert resolved.deescalation_stable_seconds == 60
    assert resolved.max_action_attempts == 3
    assert resolved.allow_simulated_throttle is True
    assert resolved.allow_simulated_kill_tree is False


def test_pressure_classification_boundaries():

    guard = make_guard()

    cases = [
        (
            make_snapshot(
                ram_available_mb=20000
            ),
            RUNTIME_PRESSURE_NORMAL,
        ),
        (
            make_snapshot(
                ram_available_mb=10000
            ),
            RUNTIME_PRESSURE_WARNING,
        ),
        (
            make_snapshot(
                ram_available_mb=8000
            ),
            RUNTIME_PRESSURE_HIGH,
        ),
        (
            make_snapshot(
                ram_available_mb=6000
            ),
            RUNTIME_PRESSURE_CRITICAL,
        ),
        (
            make_snapshot(
                ram_available_mb=4000
            ),
            RUNTIME_PRESSURE_EMERGENCY,
        ),
    ]

    for snapshot, expected in cases:

        level, _ = guard.classify_pressure(
            snapshot,
            guard.resolve_policy(),
        )

        assert level == expected


def test_unknown_invalid_stale_do_not_fail_open():

    guard = make_guard()

    unknown = guard.evaluate(
        make_snapshot(
            validation_status=SNAPSHOT_STATUS_UNKNOWN
        )
    )
    invalid = guard.evaluate(
        make_snapshot(
            validation_status=SNAPSHOT_STATUS_INVALID
        )
    )
    stale = guard.evaluate(
        make_snapshot(
            validation_status=SNAPSHOT_STATUS_STALE
        )
    )

    assert unknown.pressure_level == RUNTIME_PRESSURE_UNKNOWN
    assert invalid.pressure_level == RUNTIME_PRESSURE_INVALID
    assert stale.pressure_level == RUNTIME_PRESSURE_STALE
    assert unknown.action == RUNTIME_GUARD_ACTION_DEFER
    assert RUNTIME_REASON_SNAPSHOT_INVALID in invalid.reason_codes
    assert RUNTIME_REASON_SNAPSHOT_STALE in stale.reason_codes


def test_vram_disk_and_heavy_job_influence_pressure():

    guard = make_guard()

    vram = guard.evaluate(
        make_snapshot(
            gpu_free_mb=100
        )
    )
    disk = guard.evaluate(
        make_snapshot(
            disk_free_mb=100
        )
    )
    heavy = guard.evaluate(
        make_snapshot(),
        workload_class=WORKLOAD_CLASS_GPU_TRAINING,
        active_heavy_jobs=1,
    )

    assert vram.pressure_level == RUNTIME_PRESSURE_CRITICAL
    assert RUNTIME_REASON_VRAM_BELOW_RESERVE in vram.reason_codes
    assert disk.pressure_level == RUNTIME_PRESSURE_CRITICAL
    assert RUNTIME_REASON_DISK_BELOW_RESERVE in disk.reason_codes
    assert heavy.pressure_level == RUNTIME_PRESSURE_HIGH


def test_action_mapping_by_pressure_and_workload():

    guard = make_guard()

    normal = guard.evaluate(
        make_snapshot()
    )
    warning_light = guard.evaluate(
        make_snapshot(
            ram_available_mb=10000
        )
    )
    warning_heavy = guard.evaluate(
        make_snapshot(
            ram_available_mb=10000
        ),
        workload_class=WORKLOAD_CLASS_GPU_TRAINING,
    )
    high = guard.evaluate(
        make_snapshot(
            ram_available_mb=8000
        )
    )
    critical = guard.evaluate(
        make_snapshot(
            ram_available_mb=6000
        )
    )
    emergency = guard.evaluate(
        make_snapshot(
            ram_available_mb=4000
        )
    )

    assert normal.action == RUNTIME_GUARD_ACTION_OBSERVE
    assert warning_light.action == RUNTIME_GUARD_ACTION_REDUCE_BATCH
    assert warning_heavy.action == RUNTIME_GUARD_ACTION_DEFER_HEAVY
    assert high.action == RUNTIME_GUARD_ACTION_REDUCE_CONCURRENCY
    assert critical.action == RUNTIME_GUARD_ACTION_GRACEFUL_STOP
    assert emergency.action == RUNTIME_GUARD_ACTION_KILL_TREE


def test_disabled_and_monitor_only_do_not_execute_or_mutate():

    disabled = make_guard(
        mode=FEATURE_MODE_DISABLED
    ).evaluate(
        make_snapshot(
            ram_available_mb=6000
        )
    )

    executor = SimulatedRuntimeGuardActionExecutor()
    monitor = make_guard(
        mode=FEATURE_MODE_MONITOR_ONLY,
        executor=executor,
    ).evaluate(
        make_snapshot(
            ram_available_mb=6000
        )
    )

    assert disabled.action == RUNTIME_GUARD_ACTION_SKIP
    assert disabled.action_state == RUNTIME_GUARD_STATE_DEFERRED
    assert RUNTIME_REASON_MODE_DISABLED in disabled.reason_codes
    assert RUNTIME_REASON_MODE_MONITOR_ONLY in monitor.reason_codes
    assert monitor.action_executed is False
    assert executor.calls == []


def test_enforce_safe_simulated_action_and_destructive_unavailable():

    executor = SimulatedRuntimeGuardActionExecutor()
    guard = make_guard(
        mode=FEATURE_MODE_ENFORCE,
        executor=executor,
        allow_simulated_pause=True,
        allow_simulated_graceful_stop=True,
    )

    pause = guard.evaluate(
        make_snapshot(
            ram_available_mb=8000
        )
    )
    destructive = guard.evaluate(
        make_snapshot(
            ram_available_mb=4000
        )
    )

    assert pause.action == RUNTIME_GUARD_ACTION_REQUEST_PAUSE
    assert pause.action_state == RUNTIME_GUARD_STATE_SIMULATED
    assert RUNTIME_REASON_ACTION_SIMULATED in pause.reason_codes
    assert destructive.action == RUNTIME_GUARD_ACTION_KILL_TREE
    assert destructive.action_state == RUNTIME_GUARD_STATE_DEFERRED
    assert (
        RUNTIME_REASON_DESTRUCTIVE_ACTION_UNAVAILABLE
        in destructive.reason_codes
    )


def test_cooldown_duplicate_suppression_and_escalation_bypass():

    clock = FakeClock()
    guard = make_guard(
        clock=clock
    )

    first = guard.evaluate(
        make_snapshot(
            ram_available_mb=10000
        ),
        job_id="job_1",
    )
    duplicate = guard.evaluate(
        make_snapshot(
            ram_available_mb=10000
        ),
        job_id="job_1",
    )
    escalated = guard.evaluate(
        make_snapshot(
            ram_available_mb=6000
        ),
        job_id="job_1",
    )

    assert first.action == RUNTIME_GUARD_ACTION_REDUCE_BATCH
    assert duplicate.action_state == RUNTIME_GUARD_STATE_SUPPRESSED
    assert duplicate.duplicate_suppressed is True
    assert (
        RUNTIME_REASON_ACTION_DUPLICATE_SUPPRESSED
        in duplicate.reason_codes
    )
    assert escalated.pressure_level == RUNTIME_PRESSURE_CRITICAL
    assert RUNTIME_REASON_ACTION_COOLDOWN not in escalated.reason_codes


def test_cooldown_suppresses_different_action_without_escalation():

    clock = FakeClock()
    guard = make_guard(
        clock=clock
    )

    guard.evaluate(
        make_snapshot(
            ram_available_mb=10000
        ),
        job_id="job_1",
    )
    suppressed = guard.evaluate(
        make_snapshot(
            ram_available_mb=10000
        ),
        workload_class=WORKLOAD_CLASS_GPU_TRAINING,
        job_id="job_1",
    )

    assert suppressed.cooldown_active is True
    assert RUNTIME_REASON_ACTION_COOLDOWN in suppressed.reason_codes


def test_deescalation_requires_stable_window_and_not_unknown():

    early_clock = FakeClock()
    early_guard = make_guard(
        clock=early_clock
    )

    early_guard.evaluate(
        make_snapshot(
            ram_available_mb=6000
        )
    )
    early_clock.advance(
        30
    )
    early = early_guard.evaluate(
        make_snapshot(
            ram_available_mb=20000
        )
    )

    stable_clock = FakeClock()
    stable_guard = make_guard(
        clock=stable_clock
    )
    stable_guard.evaluate(
        make_snapshot(
            ram_available_mb=6000
        )
    )
    stable_clock.advance(
        61
    )
    stable = stable_guard.evaluate(
        make_snapshot(
            ram_available_mb=20000
        )
    )
    unknown = stable_guard.evaluate(
        make_snapshot(
            validation_status=SNAPSHOT_STATUS_UNKNOWN
        )
    )

    assert early.hysteresis_active is True
    assert stable.action == RUNTIME_GUARD_ACTION_DEESCALATE
    assert RUNTIME_REASON_ACTION_DEESCALATED in stable.reason_codes
    assert unknown.action != RUNTIME_GUARD_ACTION_DEESCALATE


def test_retry_exhausted_and_simulated_failure():

    clock = FakeClock()
    executor = SimulatedRuntimeGuardActionExecutor(
        fail_actions=[
            RUNTIME_GUARD_ACTION_REQUEST_PAUSE
        ]
    )
    guard = make_guard(
        mode=FEATURE_MODE_ENFORCE,
        clock=clock,
        executor=executor,
        allow_simulated_pause=True,
        max_action_attempts=1,
    )

    failed = guard.evaluate(
        make_snapshot(
            ram_available_mb=8000
        ),
        job_id="job_1",
    )
    clock.advance(
        31
    )
    retry = guard.evaluate(
        make_snapshot(
            ram_available_mb=8000
        ),
        job_id="job_2",
        action_attempt=1,
    )

    assert failed.action_state == RUNTIME_GUARD_STATE_FAILED
    assert RUNTIME_REASON_ACTION_FAILED in failed.reason_codes
    assert retry.action_state == RUNTIME_GUARD_STATE_DEFERRED
    assert RUNTIME_REASON_ACTION_RETRY_EXHAUSTED in retry.reason_codes


def test_lease_and_process_integration_request_reconciliation():

    guard = make_guard()

    lease = {
        "lease_id": "lease_1",
        "would_reconcile": True,
        "is_expired": True,
    }
    process = {
        "process_identity": {
            "process_id": "proc_1"
        },
        "would_reconcile": True,
        "identity_valid": False,
        "reason_codes": [
            "process_identity_unknown"
        ],
    }

    lease_result = guard.evaluate(
        make_snapshot(),
        lease_observation=lease,
    )
    process_result = guard.evaluate(
        make_snapshot(),
        process_observation=process,
    )

    assert lease_result.action == RUNTIME_GUARD_ACTION_RECONCILE_LEASE
    assert (
        RUNTIME_REASON_LEASE_RECONCILIATION_REQUIRED
        in lease_result.reason_codes
    )
    assert process_result.action == RUNTIME_GUARD_ACTION_RECONCILE_PROCESS
    assert (
        RUNTIME_REASON_PROCESS_RECONCILIATION_REQUIRED
        in process_result.reason_codes
    )
    assert RUNTIME_REASON_IDENTITY_UNKNOWN in process_result.reason_codes


def test_ram_reason_codes_are_stable_for_thresholds():

    guard = make_guard()

    warning = guard.evaluate(
        make_snapshot(
            ram_available_mb=10000
        )
    )
    high = guard.evaluate(
        make_snapshot(
            ram_available_mb=8000
        )
    )
    critical = guard.evaluate(
        make_snapshot(
            ram_available_mb=6000
        )
    )
    emergency = guard.evaluate(
        make_snapshot(
            ram_available_mb=4000
        )
    )

    assert RUNTIME_REASON_RAM_BELOW_WARNING in warning.reason_codes
    assert RUNTIME_REASON_RAM_BELOW_HIGH in high.reason_codes
    assert RUNTIME_REASON_RAM_BELOW_CRITICAL in critical.reason_codes
    assert RUNTIME_REASON_RAM_BELOW_EMERGENCY in emergency.reason_codes

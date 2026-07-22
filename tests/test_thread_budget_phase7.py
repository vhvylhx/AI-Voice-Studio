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
    THREAD_BUDGET_ACTION_APPLY_ENVIRONMENT,
    THREAD_BUDGET_ACTION_DEFER,
    THREAD_BUDGET_ACTION_DEFER_JOB,
    THREAD_BUDGET_ACTION_DISABLE_NESTED,
    THREAD_BUDGET_ACTION_RECONCILE,
    THREAD_BUDGET_ACTION_REDUCE,
    THREAD_BUDGET_ACTION_RESTORE,
    THREAD_BUDGET_ACTION_SKIP,
    THREAD_BUDGET_STATE_DEFERRED,
    THREAD_BUDGET_STATE_RESTORED,
    THREAD_BUDGET_STATE_SIMULATED,
    THREAD_BUDGET_STATE_SUPPRESSED,
    THREAD_BUDGET_STATUS_CONSTRAINED,
    THREAD_BUDGET_STATUS_INVALID,
    THREAD_BUDGET_STATUS_OVERSUBSCRIBED,
    THREAD_BUDGET_STATUS_STALE,
    THREAD_BUDGET_STATUS_UNKNOWN,
    THREAD_BUDGET_STATUS_VALID,
    THREAD_REASON_ACTION_COOLDOWN,
    THREAD_REASON_ACTION_DUPLICATE_SUPPRESSED,
    THREAD_REASON_ACTION_FAILED,
    THREAD_REASON_ACTION_RETRY_EXHAUSTED,
    THREAD_REASON_ACTION_SIMULATED,
    THREAD_REASON_CONSTRAINED,
    THREAD_REASON_ENVIRONMENT_PLAN_REQUIRED,
    THREAD_REASON_HEAVY_JOB_LIMIT_REACHED,
    THREAD_REASON_IDENTITY_UNKNOWN,
    THREAD_REASON_INVALID,
    THREAD_REASON_LEASE_RECONCILIATION_REQUIRED,
    THREAD_REASON_MODE_DISABLED,
    THREAD_REASON_MODE_MONITOR_ONLY,
    THREAD_REASON_NESTED_PARALLELISM,
    THREAD_REASON_OVERSUBSCRIBED,
    THREAD_REASON_POLICY_MISMATCH,
    THREAD_REASON_PROCESS_RECONCILIATION_REQUIRED,
    THREAD_REASON_REQUEST_ABOVE_WORKLOAD_LIMIT,
    THREAD_REASON_RESTORE_REQUIRED,
    THREAD_REASON_RUNTIME_PLAN_REQUIRED,
    THREAD_REASON_STALE,
    THREAD_REASON_TOTAL_ABOVE_POLICY_LIMIT,
    THREAD_REASON_UNKNOWN,
    WORKLOAD_CLASS_CPU_HEAVY,
    WORKLOAD_CLASS_GPU_INFERENCE,
    WORKLOAD_CLASS_GPU_TRAINING,
    WORKLOAD_CLASS_IO_HEAVY,
    WORKLOAD_CLASS_LIGHT,
    ResourcePolicy,
    ResolvedResourcePolicy,
    ThreadBudgetObservation,
)
from services.thread_budget_executor import SimulatedThreadBudgetExecutor
from services.resource_policy_service import ResourcePolicyService
from services.thread_budget_service import ThreadBudgetService


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
        feature_modes["thread_budget_mode"] = mode

        data = {
            "schema_version": 2,
            "feature_modes": feature_modes,
            "max_total_cpu_threads": 8,
            "max_threads_per_light_job": 2,
            "max_threads_per_cpu_heavy_job": 4,
            "max_threads_per_gpu_inference_job": 2,
            "max_threads_per_gpu_training_job": 2,
            "max_threads_per_io_heavy_job": 3,
            "max_parallel_heavy_jobs": 1,
            "reserve_cpu_threads": 1,
            "allow_nested_parallelism": False,
            "thread_budget_cooldown_seconds": 30,
            "thread_budget_observation_ttl_seconds": 5,
            "thread_budget_restore_on_release": True,
            "max_action_attempts": 3,
        }
        data.update(
            overrides
        )

        self.policy = ResourcePolicy(
            **data
        )

    def resolve(
        self,
        migrate=False,
    ):

        return ResolvedResourcePolicy.from_policy(
            self.policy
        )


class MemoryConfig:

    def __init__(
        self,
        data=None,
    ):

        self.data = dict(
            data
            or {}
        )

    def get(
        self,
        key,
        default=None,
    ):

        return self.data.get(
            key,
            default,
        )

    def set(
        self,
        key,
        value,
    ):

        self.data[key] = value


def make_service(
    mode=FEATURE_MODE_MONITOR_ONLY,
    clock=None,
    executor=None,
    supported_environment_variables=None,
    **policy_overrides,
):

    return ThreadBudgetService(
        policy_service=FakePolicyService(
            mode=mode,
            **policy_overrides,
        ),
        executor=executor or SimulatedThreadBudgetExecutor(),
        clock=clock or FakeClock(),
        supported_environment_variables=supported_environment_variables,
    )


def active_budget(
    resolved_threads,
    workload_class=WORKLOAD_CLASS_LIGHT,
    policy_fingerprint="",
):

    return ThreadBudgetObservation(
        budget_id=f"budget_{resolved_threads}",
        resolved_threads=resolved_threads,
        workload_class=workload_class,
        policy_fingerprint=policy_fingerprint,
    )


def test_policy_defaults_are_monitor_only_and_additive():

    policy = FakePolicyService().resolve()
    resolved = ResourcePolicyService(
        MemoryConfig(
            {
                "resource_policy": {
                    "schema_version": 2
                }
            }
        )
    ).resolve(
        migrate=False
    )
    invalid = ResourcePolicyService(
        MemoryConfig(
            {
                "resource_policy": {
                    "schema_version": 2,
                    "reserve_cpu_threads": 8,
                    "max_total_cpu_threads": 8,
                }
            }
        )
    ).resolve(
        migrate=False
    )

    assert policy.feature_modes["thread_budget_mode"] == (
        FEATURE_MODE_MONITOR_ONLY
    )
    assert policy.max_total_cpu_threads == 8
    assert policy.max_threads_per_cpu_heavy_job == 4
    assert policy.max_parallel_heavy_jobs == 1
    assert policy.thread_budget_restore_on_release is True
    assert resolved.max_threads_per_light_job == 2
    assert resolved.thread_budget_cooldown_seconds == 30
    assert invalid.source == "built_in_fallback"
    assert any(
        "invalid_thread_budget" in notice
        for notice in invalid.notices
    )


def test_workload_allocation_is_policy_driven_and_deterministic():

    service = make_service()

    cases = [
        (
            WORKLOAD_CLASS_LIGHT,
            8,
            2,
        ),
        (
            WORKLOAD_CLASS_CPU_HEAVY,
            8,
            4,
        ),
        (
            WORKLOAD_CLASS_GPU_INFERENCE,
            8,
            2,
        ),
        (
            WORKLOAD_CLASS_GPU_TRAINING,
            8,
            2,
        ),
        (
            WORKLOAD_CLASS_IO_HEAVY,
            8,
            3,
        ),
    ]

    results = [
        service.evaluate(
            total_logical_cpu_threads=16,
            workload_class=workload,
            requested_threads=requested,
            job_id=f"job_{index}",
        )
        for index, (workload, requested, _expected) in enumerate(
            cases
        )
    ]

    assert [
        item.resolved_threads
        for item in results
    ] == [
        expected
        for _workload, _requested, expected in cases
    ]
    assert all(
        item.available_budget_threads == 7
        for item in results
    )


def test_total_budget_reserve_and_active_jobs_detect_oversubscription():

    service = make_service()

    result = service.evaluate(
        total_logical_cpu_threads=8,
        workload_class=WORKLOAD_CLASS_CPU_HEAVY,
        requested_threads=4,
        active_budgets=[
            active_budget(
                4
            ),
            active_budget(
                3
            ),
        ],
        active_job_count=2,
        job_id="job_oversub",
    )

    assert result.status == THREAD_BUDGET_STATUS_OVERSUBSCRIBED
    assert result.oversubscribed is True
    assert result.resolved_threads == 0
    assert THREAD_REASON_TOTAL_ABOVE_POLICY_LIMIT in result.reason_codes
    assert THREAD_REASON_OVERSUBSCRIBED in result.reason_codes


def test_heavy_job_limit_and_request_above_workload_limit():

    service = make_service()

    limited = service.evaluate(
        total_logical_cpu_threads=16,
        workload_class=WORKLOAD_CLASS_CPU_HEAVY,
        requested_threads=6,
        job_id="job_big",
    )
    heavy_blocked = service.evaluate(
        total_logical_cpu_threads=16,
        workload_class=WORKLOAD_CLASS_GPU_TRAINING,
        requested_threads=2,
        active_heavy_job_count=1,
        job_id="job_heavy_2",
    )

    assert limited.status == THREAD_BUDGET_STATUS_CONSTRAINED
    assert limited.resolved_threads == 4
    assert (
        THREAD_REASON_REQUEST_ABOVE_WORKLOAD_LIMIT
        in limited.reason_codes
    )
    assert heavy_blocked.status == THREAD_BUDGET_STATUS_OVERSUBSCRIBED
    assert (
        THREAD_REASON_HEAVY_JOB_LIMIT_REACHED
        in heavy_blocked.reason_codes
    )


def test_unknown_stale_and_invalid_do_not_fail_open():

    service = make_service()

    unknown = service.evaluate(
        total_logical_cpu_threads=0,
        requested_threads=2,
        job_id="job_unknown",
    )
    stale = service.evaluate(
        total_logical_cpu_threads=8,
        requested_threads=2,
        snapshot_status="stale",
        job_id="job_stale",
    )
    invalid = service.evaluate(
        total_logical_cpu_threads=8,
        requested_threads=0,
        job_id="job_invalid",
    )

    assert unknown.status == THREAD_BUDGET_STATUS_UNKNOWN
    assert unknown.resolved_threads == 0
    assert unknown.action == THREAD_BUDGET_ACTION_DEFER
    assert THREAD_REASON_UNKNOWN in unknown.reason_codes
    assert stale.status == THREAD_BUDGET_STATUS_STALE
    assert THREAD_REASON_STALE in stale.reason_codes
    assert invalid.status == THREAD_BUDGET_STATUS_INVALID
    assert THREAD_REASON_INVALID in invalid.reason_codes


def test_environment_plan_preserves_originals_and_monitor_only_does_not_mutate():

    environment = {
        "OMP_NUM_THREADS": "8",
        "MKL_NUM_THREADS": "8",
        "TOKENIZERS_PARALLELISM": "true",
    }
    original = dict(
        environment
    )
    service = make_service(
        supported_environment_variables=[
            "OMP_NUM_THREADS",
            "MKL_NUM_THREADS",
            "TOKENIZERS_PARALLELISM",
        ]
    )

    result = service.evaluate(
        total_logical_cpu_threads=16,
        workload_class=WORKLOAD_CLASS_LIGHT,
        requested_threads=2,
        environment=environment,
        runtime_settings={
            "num_threads": 8
        },
        job_id="job_env",
    )

    assert environment == original
    assert result.action == THREAD_BUDGET_ACTION_DISABLE_NESTED
    assert result.nested_parallelism_detected is True
    assert THREAD_REASON_NESTED_PARALLELISM in result.reason_codes
    assert result.environment_plan["OMP_NUM_THREADS"]["desired"] == "2"
    assert (
        result.environment_plan["OMP_NUM_THREADS"]["restore_value"]
        == "8"
    )
    assert "OPENBLAS_NUM_THREADS" not in result.environment_plan


def test_runtime_plan_uses_fake_adapter_contract_only():

    service = make_service()

    result = service.evaluate(
        total_logical_cpu_threads=16,
        workload_class=WORKLOAD_CLASS_CPU_HEAVY,
        requested_threads=4,
        runtime_settings={
            "supports_set_num_threads": True,
            "supports_set_num_interop_threads": True,
            "num_threads": 12,
            "num_interop_threads": 4,
        },
        job_id="job_runtime",
    )

    assert THREAD_REASON_RUNTIME_PLAN_REQUIRED in result.reason_codes
    assert result.runtime_plan["set_num_threads"]["desired"] == 4
    assert result.runtime_plan["set_num_threads"]["restore_value"] == 12
    assert result.runtime_plan["set_num_interop_threads"]["desired"] == 2


def test_disabled_monitor_only_and_enforce_simulated_boundaries():

    disabled = make_service(
        mode=FEATURE_MODE_DISABLED
    ).evaluate(
        total_logical_cpu_threads=8,
        requested_threads=2,
    )

    monitor_executor = SimulatedThreadBudgetExecutor()
    monitor = make_service(
        mode=FEATURE_MODE_MONITOR_ONLY,
        executor=monitor_executor,
    ).evaluate(
        total_logical_cpu_threads=8,
        requested_threads=2,
    )

    enforce_executor = SimulatedThreadBudgetExecutor()
    enforce = make_service(
        mode=FEATURE_MODE_ENFORCE,
        executor=enforce_executor,
    ).evaluate(
        total_logical_cpu_threads=8,
        requested_threads=2,
        job_id="job_enforce",
    )

    assert disabled.action == THREAD_BUDGET_ACTION_SKIP
    assert disabled.action_state == THREAD_BUDGET_STATE_DEFERRED
    assert THREAD_REASON_MODE_DISABLED in disabled.reason_codes
    assert monitor.action_executed is False
    assert monitor_executor.calls == []
    assert THREAD_REASON_MODE_MONITOR_ONLY in monitor.reason_codes
    assert enforce.action_state == THREAD_BUDGET_STATE_SIMULATED
    assert enforce.action_executed is False
    assert enforce.action_simulated is True
    assert THREAD_REASON_ACTION_SIMULATED in enforce.reason_codes
    assert len(
        enforce_executor.calls
    ) == 1


def test_restore_plan_and_simulated_restore_state():

    service = make_service(
        mode=FEATURE_MODE_ENFORCE
    )

    result = service.evaluate(
        total_logical_cpu_threads=8,
        requested_threads=2,
        release=True,
        previous_environment_plan={
            "OMP_NUM_THREADS": {
                "restore_value": "8"
            }
        },
        job_id="job_restore",
    )

    assert result.action == THREAD_BUDGET_ACTION_RESTORE
    assert result.restore_required is True
    assert result.action_state == THREAD_BUDGET_STATE_RESTORED
    assert THREAD_REASON_RESTORE_REQUIRED in result.reason_codes


def test_cooldown_duplicate_policy_change_and_retry_exhausted():

    clock = FakeClock()
    service = make_service(
        clock=clock,
        max_action_attempts=1,
    )

    first = service.evaluate(
        total_logical_cpu_threads=8,
        requested_threads=2,
        job_id="job_cool",
    )
    duplicate = service.evaluate(
        total_logical_cpu_threads=8,
        requested_threads=2,
        job_id="job_cool",
    )
    clock.advance(
        31
    )
    retry = service.evaluate(
        total_logical_cpu_threads=8,
        requested_threads=2,
        job_id="job_retry",
        action_attempt=1,
    )

    policy_changed = make_service(
        clock=clock,
        max_total_cpu_threads=10,
    )
    policy_changed.last_observation = first
    changed = policy_changed.evaluate(
        total_logical_cpu_threads=10,
        requested_threads=2,
        job_id="job_changed",
    )

    assert duplicate.action_state == THREAD_BUDGET_STATE_SUPPRESSED
    assert duplicate.duplicate_suppressed is True
    assert (
        THREAD_REASON_ACTION_DUPLICATE_SUPPRESSED
        in duplicate.reason_codes
    )
    assert retry.action_state == THREAD_BUDGET_STATE_DEFERRED
    assert THREAD_REASON_ACTION_RETRY_EXHAUSTED in retry.reason_codes
    assert THREAD_REASON_ACTION_COOLDOWN not in changed.reason_codes


def test_cooldown_suppresses_different_plan_before_window_expires():

    clock = FakeClock()
    service = make_service(
        clock=clock
    )

    service.evaluate(
        total_logical_cpu_threads=8,
        requested_threads=2,
        job_id="job_cooldown",
    )
    changed = service.evaluate(
        total_logical_cpu_threads=8,
        requested_threads=1,
        job_id="job_cooldown",
    )

    assert changed.cooldown_active is True
    assert THREAD_REASON_ACTION_COOLDOWN in changed.reason_codes


def test_lease_process_and_runtime_guard_integration_defer_or_reconcile():

    policy = make_service().resolve_policy()
    service = make_service()

    result = service.evaluate(
        total_logical_cpu_threads=8,
        requested_threads=2,
        lease_observation={
            "lease_id": "lease_1",
            "would_reconcile": True,
            "policy_fingerprint": "old",
        },
        process_observation={
            "process_identity": {
                "process_id": "proc_1"
            },
            "identity_valid": False,
            "reason_codes": [
                "process_identity_unknown"
            ],
            "policy_fingerprint": policy.fingerprint,
        },
        runtime_guard_observation={
            "pressure_level": "critical"
        },
        job_id="job_integration",
    )

    assert result.action == THREAD_BUDGET_ACTION_RECONCILE
    assert result.reconciliation_required is True
    assert (
        THREAD_REASON_LEASE_RECONCILIATION_REQUIRED
        in result.reason_codes
    )
    assert (
        THREAD_REASON_PROCESS_RECONCILIATION_REQUIRED
        in result.reason_codes
    )
    assert THREAD_REASON_IDENTITY_UNKNOWN in result.reason_codes
    assert THREAD_REASON_POLICY_MISMATCH in result.reason_codes


def test_nested_parallelism_cases_are_detected():

    service = make_service()

    env_nested = service.evaluate(
        total_logical_cpu_threads=8,
        requested_threads=2,
        environment={
            "OMP_NUM_THREADS": "2",
            "MKL_NUM_THREADS": "2",
        },
        job_id="job_nested_env",
    )
    torch_nested = service.evaluate(
        total_logical_cpu_threads=8,
        requested_threads=2,
        runtime_settings={
            "num_threads": 2,
            "num_interop_threads": 2,
        },
        job_id="job_nested_torch",
    )

    assert env_nested.action == THREAD_BUDGET_ACTION_DISABLE_NESTED
    assert torch_nested.action == THREAD_BUDGET_ACTION_DISABLE_NESTED
    assert env_nested.nested_parallelism_detected is True
    assert torch_nested.nested_parallelism_detected is True


def test_injected_failure_does_not_retry_forever():

    clock = FakeClock()
    executor = SimulatedThreadBudgetExecutor(
        fail_actions=[
            THREAD_BUDGET_ACTION_DISABLE_NESTED
        ]
    )
    service = make_service(
        mode=FEATURE_MODE_ENFORCE,
        clock=clock,
        executor=executor,
        max_action_attempts=1,
    )

    failed = service.evaluate(
        total_logical_cpu_threads=8,
        requested_threads=2,
        environment={
            "OMP_NUM_THREADS": "8"
        },
        runtime_settings={
            "num_threads": 2,
            "num_interop_threads": 2,
        },
        job_id="job_fail",
    )
    clock.advance(
        31
    )
    retry = service.evaluate(
        total_logical_cpu_threads=8,
        requested_threads=2,
        environment={
            "OMP_NUM_THREADS": "8"
        },
        job_id="job_retry_exhausted",
        action_attempt=1,
    )

    assert failed.action == THREAD_BUDGET_ACTION_DISABLE_NESTED
    assert failed.action_state == THREAD_BUDGET_STATE_DEFERRED or (
        failed.action_state == "failed"
    )
    assert THREAD_REASON_ACTION_FAILED in failed.reason_codes
    assert retry.action_state == THREAD_BUDGET_STATE_DEFERRED
    assert THREAD_REASON_ACTION_RETRY_EXHAUSTED in retry.reason_codes


def test_reason_codes_are_stable_for_core_paths():

    service = make_service()

    constrained = service.evaluate(
        total_logical_cpu_threads=8,
        workload_class=WORKLOAD_CLASS_LIGHT,
        requested_threads=4,
        job_id="job_reason_1",
    )
    nested = service.evaluate(
        total_logical_cpu_threads=8,
        requested_threads=2,
        environment={
            "OMP_NUM_THREADS": "2",
            "OPENBLAS_NUM_THREADS": "2",
        },
        job_id="job_reason_2",
    )

    assert THREAD_REASON_CONSTRAINED in constrained.reason_codes
    assert THREAD_REASON_ENVIRONMENT_PLAN_REQUIRED in nested.reason_codes
    assert THREAD_REASON_NESTED_PARALLELISM in nested.reason_codes

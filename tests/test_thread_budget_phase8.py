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
    DEFAULT_RESOURCE_FEATURE_MODES,
    FEATURE_MODE_ENFORCE,
    FEATURE_MODE_MONITOR_ONLY,
    THREAD_BUDGET_STATE_APPLIED,
    THREAD_BUDGET_STATE_DEFERRED,
    THREAD_BUDGET_STATE_FAILED,
    THREAD_BUDGET_STATE_RESTORED,
    THREAD_REASON_ENFORCEMENT_APPLIED,
    THREAD_REASON_ENFORCEMENT_DEFERRED,
    THREAD_REASON_ENGINE_CAPABILITY_MISSING,
    THREAD_REASON_ENVIRONMENT_APPLIED,
    THREAD_REASON_PRIMARY_ERROR_PRESERVED,
    THREAD_REASON_ROLLBACK_COMPLETED,
    THREAD_REASON_RUNTIME_APPLY_FAILED,
    THREAD_REASON_RUNTIME_APPLIED,
    WORKLOAD_CLASS_CPU_HEAVY,
    ResourcePolicy,
    ResourceRequirement,
    ResolvedResourcePolicy,
    ThreadBudgetEngineCapability,
)
from services.job_handler_registry import JobHandlerRegistry
from services.job_log_service import JobLogService
from services.job_queue_service import JobQueueService
from services.job_repository import JobRepository
from services.job_runner import JobRunner
from services.job_worker import BaseJobWorker
from services.thread_budget_capability_registry import (
    ThreadBudgetCapabilityRegistry,
)
from services.thread_budget_runtime_adapter import (
    FakeThreadBudgetRuntimeAdapter,
)
from services.thread_budget_service import ThreadBudgetService


class FakePolicyService:

    def __init__(
        self,
        mode=FEATURE_MODE_MONITOR_ONLY,
    ):

        feature_modes = dict(
            DEFAULT_RESOURCE_FEATURE_MODES
        )
        feature_modes[
            "thread_budget_mode"
        ] = mode

        self.policy = ResourcePolicy(
            feature_modes=feature_modes,
            max_total_cpu_threads=8,
            max_threads_per_cpu_heavy_job=4,
            reserve_cpu_threads=1,
            thread_budget_cooldown_seconds=0,
        )

    def resolve(
        self,
        migrate=False,
    ):

        return ResolvedResourcePolicy.from_policy(
            self.policy
        )


def make_registry(
    adapter=None,
):

    registry = ThreadBudgetCapabilityRegistry()
    registry.register(
        ThreadBudgetEngineCapability(
            engine_id="engine_test",
            adapter_id="fake",
            supports_environment_threads=True,
            supports_runtime_threads=True,
            supports_restore=True,
            supports_intraop_threads=True,
            supports_interop_threads=True,
        ),
        adapter=adapter
        or FakeThreadBudgetRuntimeAdapter(
            {
                "num_threads": 8,
                "num_interop_threads": 4,
            }
        ),
    )
    return registry


def make_service(
    mode=FEATURE_MODE_MONITOR_ONLY,
    registry=None,
):

    return ThreadBudgetService(
        policy_service=FakePolicyService(
            mode
        ),
        capability_registry=registry,
    )


def test_monitor_only_prepare_does_not_mutate_environment():

    adapter = FakeThreadBudgetRuntimeAdapter(
        {
            "num_threads": 8
        }
    )
    service = make_service(
        registry=make_registry(
            adapter
        )
    )
    environment = {
        "OMP_NUM_THREADS": "8"
    }

    observation, state = service.prepare_enforcement(
        engine_id="engine_test",
        environment=environment,
        workload_class=WORKLOAD_CLASS_CPU_HEAVY,
        requested_threads=2,
        total_logical_cpu_threads=8,
        job_id="job_1",
        owner_id="owner_1",
    )

    assert observation.mode == FEATURE_MODE_MONITOR_ONLY
    assert state.status == THREAD_BUDGET_STATE_DEFERRED
    assert THREAD_REASON_ENFORCEMENT_DEFERRED in state.reason_codes
    assert state.environment_before == environment
    assert state.environment_after == environment
    assert environment[
        "OMP_NUM_THREADS"
    ] == "8"
    assert all(
        call[
            0
        ]
        != "apply"
        for call in adapter.calls
    )


def test_enforce_applies_scoped_environment_and_runtime_adapter():

    adapter = FakeThreadBudgetRuntimeAdapter(
        {
            "num_threads": 8,
            "num_interop_threads": 4,
        }
    )
    service = make_service(
        mode=FEATURE_MODE_ENFORCE,
        registry=make_registry(
            adapter
        ),
    )
    environment = {
        "OMP_NUM_THREADS": "8"
    }

    _, state = service.prepare_enforcement(
        engine_id="engine_test",
        environment=environment,
        workload_class=WORKLOAD_CLASS_CPU_HEAVY,
        requested_threads=2,
        total_logical_cpu_threads=8,
        job_id="job_1",
        owner_id="owner_1",
    )

    assert state.status == THREAD_BUDGET_STATE_APPLIED
    assert state.environment_before[
        "OMP_NUM_THREADS"
    ] == "8"
    assert state.environment_after[
        "OMP_NUM_THREADS"
    ] == "2"
    assert environment[
        "OMP_NUM_THREADS"
    ] == "8"
    assert adapter.settings[
        "num_threads"
    ] == 2
    assert THREAD_REASON_ENVIRONMENT_APPLIED in state.reason_codes
    assert THREAD_REASON_RUNTIME_APPLIED in state.reason_codes
    assert THREAD_REASON_ENFORCEMENT_APPLIED in state.reason_codes


def test_missing_capability_is_not_fail_open_in_enforce():

    service = make_service(
        mode=FEATURE_MODE_ENFORCE,
        registry=ThreadBudgetCapabilityRegistry(),
    )

    _, state = service.prepare_enforcement(
        engine_id="missing_engine",
        environment={},
        workload_class=WORKLOAD_CLASS_CPU_HEAVY,
        requested_threads=2,
        total_logical_cpu_threads=8,
        job_id="job_1",
        owner_id="owner_1",
    )

    assert state.status == THREAD_BUDGET_STATE_DEFERRED
    assert THREAD_REASON_ENGINE_CAPABILITY_MISSING in state.reason_codes


def test_runtime_apply_failure_rolls_back_scoped_state():

    adapter = FakeThreadBudgetRuntimeAdapter(
        {
            "num_threads": 8
        },
        fail_apply=True,
    )
    service = make_service(
        mode=FEATURE_MODE_ENFORCE,
        registry=make_registry(
            adapter
        ),
    )

    _, state = service.prepare_enforcement(
        engine_id="engine_test",
        environment={
            "OMP_NUM_THREADS": "8"
        },
        workload_class=WORKLOAD_CLASS_CPU_HEAVY,
        requested_threads=2,
        total_logical_cpu_threads=8,
        job_id="job_1",
        owner_id="owner_1",
    )

    assert state.status == THREAD_BUDGET_STATE_FAILED
    assert state.environment_after == state.environment_before
    assert THREAD_REASON_RUNTIME_APPLY_FAILED in state.reason_codes
    assert THREAD_REASON_ROLLBACK_COMPLETED in state.reason_codes


def test_restore_failure_preserves_primary_error():

    adapter = FakeThreadBudgetRuntimeAdapter(
        {
            "num_threads": 8
        }
    )
    service = make_service(
        mode=FEATURE_MODE_ENFORCE,
        registry=make_registry(
            adapter
        ),
    )
    _, state = service.prepare_enforcement(
        engine_id="engine_test",
        environment={},
        workload_class=WORKLOAD_CLASS_CPU_HEAVY,
        requested_threads=2,
        total_logical_cpu_threads=8,
        job_id="job_1",
        owner_id="owner_1",
    )

    adapter.fail_restore = True
    restored = service.restore_enforcement(
        state,
        engine_id="engine_test",
        primary_error=RuntimeError(
            "primary_failure"
        ),
    )

    assert restored.status == THREAD_BUDGET_STATE_FAILED
    assert THREAD_REASON_PRIMARY_ERROR_PRESERVED in restored.reason_codes


def make_job_stack(
    tmp_path,
    service,
    worker_cls,
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
    registry.register(
        "phase8_worker",
        worker_cls,
    )
    runner = JobRunner(
        repository=repository,
        queue_service=queue,
        handler_registry=registry,
        log_service=logs,
        thread_budget_service=service,
    )
    return repository, queue, runner


def test_job_runner_applies_before_workload_and_restores_after(tmp_path):

    class CapturingWorker(BaseJobWorker):

        resource_requirement = ResourceRequirement(
            cpu_threads=2,
            workload_class=WORKLOAD_CLASS_CPU_HEAVY,
        )

        def execute(
            self,
            job,
            context,
        ):

            assert context.thread_budget_state.status == (
                THREAD_BUDGET_STATE_APPLIED
            )
            assert context.environment[
                "OMP_NUM_THREADS"
            ] == "2"
            return {
                "environment": dict(
                    context.environment
                )
            }

    service = make_service(
        mode=FEATURE_MODE_ENFORCE,
        registry=make_registry(),
    )
    repository, queue, runner = make_job_stack(
        tmp_path,
        service,
        CapturingWorker,
    )
    queue.enqueue_new(
        "phase8_worker",
        payload={
            "thread_budget_engine_id": "engine_test",
            "environment": {
                "OMP_NUM_THREADS": "8"
            },
        },
    )

    result = runner.run_next()
    stored = repository.load(
        result.job_id
    )

    assert result.state == "completed"
    assert stored.recovery_state[
        "thread_budget_phase8"
    ][
        "state"
    ][
        "status"
    ] == THREAD_BUDGET_STATE_RESTORED


def test_job_runner_enforce_missing_capability_blocks_workload(tmp_path):

    class ShouldNotRunWorker(BaseJobWorker):

        resource_requirement = ResourceRequirement(
            cpu_threads=2,
            workload_class=WORKLOAD_CLASS_CPU_HEAVY,
        )

        def execute(
            self,
            job,
            context,
        ):

            raise AssertionError(
                "workload_should_not_run"
            )

    service = make_service(
        mode=FEATURE_MODE_ENFORCE,
        registry=ThreadBudgetCapabilityRegistry(),
    )
    repository, queue, runner = make_job_stack(
        tmp_path,
        service,
        ShouldNotRunWorker,
    )
    job = repository.save(
        JobModel(
            job_id="job_missing_capability",
            job_type="phase8_worker",
            state="queued",
            payload={
                "thread_budget_engine_id": "missing"
            },
        )
    )

    result = runner.run_job(
        job.job_id
    )

    assert result.state == "failed"
    assert result.error_message == "thread_budget_enforcement_not_applied"


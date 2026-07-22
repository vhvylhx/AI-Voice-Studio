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

from models.resource_model import (
    DEFAULT_RESOURCE_FEATURE_MODES,
    FEATURE_MODE_ENFORCE,
    FEATURE_MODE_MONITOR_ONLY,
    THREAD_BUDGET_STATE_APPLIED,
    THREAD_BUDGET_STATE_DEFERRED,
    THREAD_BUDGET_STATE_RESTORED,
    THREAD_REASON_CONTROLLED_ROLLOUT_DEFERRED,
    THREAD_REASON_ENGINE_CAPABILITY_NOT_PRODUCTION_READY,
    THREAD_REASON_ENGINE_DENIED,
    THREAD_REASON_ENGINE_NOT_ALLOWLISTED,
    THREAD_REASON_ENGINE_NOT_REGISTERED,
    THREAD_REASON_ENGINE_OPT_IN_REQUIRED,
    THREAD_REASON_ROLLOUT_NOT_SELECTED,
    THREAD_REASON_ROLLOUT_SELECTED,
    THREAD_REASON_SUBPROCESS_ENVIRONMENT_APPLIED,
    THREAD_REASON_UNKNOWN_ENGINE_DEFERRED,
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
    GPT_SOVITS_THREAD_ENVIRONMENT_VARIABLES,
    ThreadBudgetCapabilityRegistry,
    build_default_thread_budget_registry,
)
from services.thread_budget_runtime_adapter import (
    PyTorchThreadBudgetAdapter,
    SubprocessEnvironmentThreadAdapter,
)
from services.thread_budget_service import ThreadBudgetService


class FakePolicyService:

    def __init__(
        self,
        mode=FEATURE_MODE_MONITOR_ONLY,
        allowlist=None,
        denylist=None,
        rollout_percentage=0,
        require_opt_in=True,
        fail_open=False,
    ):

        feature_modes = dict(
            DEFAULT_RESOURCE_FEATURE_MODES
        )
        feature_modes[
            "thread_budget_mode"
        ] = mode
        self.policy = ResourcePolicy(
            feature_modes=feature_modes,
            thread_budget_engine_allowlist=list(
                allowlist
                or []
            ),
            thread_budget_engine_denylist=list(
                denylist
                or []
            ),
            thread_budget_rollout_percentage=rollout_percentage,
            thread_budget_require_explicit_engine_opt_in=require_opt_in,
            thread_budget_fail_open=fail_open,
            thread_budget_cooldown_seconds=0,
        )

    def resolve(
        self,
        migrate=False,
    ):

        return ResolvedResourcePolicy.from_policy(
            self.policy
        )


def make_service(
    mode=FEATURE_MODE_MONITOR_ONLY,
    registry=None,
    **policy,
):

    return ThreadBudgetService(
        policy_service=FakePolicyService(
            mode=mode,
            **policy,
        ),
        capability_registry=registry
        or build_default_thread_budget_registry(),
    )


def prepare(
    service,
    engine_id="gpt_sovits",
    environment=None,
    job_id="job_1",
    engine_opt_in=False,
):

    return service.prepare_enforcement(
        engine_id=engine_id,
        environment=environment
        or {
            "OMP_NUM_THREADS": "8",
            "TORCH_NUM_THREADS": "99",
        },
        workload_class=WORKLOAD_CLASS_CPU_HEAVY,
        requested_threads=2,
        total_logical_cpu_threads=8,
        job_id=job_id,
        owner_id="owner_1",
        engine_opt_in=engine_opt_in,
    )


def test_default_registry_uses_source_evidence_and_marks_unknowns_unavailable():

    manager = SimpleNamespace(
        engine_ids=lambda: [
            "mock",
            "gpt_sovits",
        ]
    )
    registry = build_default_thread_budget_registry(
        manager
    )
    gpt = registry.capability(
        "gpt_sovits"
    )
    mock = registry.capability(
        "mock"
    )
    vieneu = registry.capability(
        "vieneu"
    )

    assert gpt.engine_id == "gpt_sovits"
    assert gpt.execution_mode == "subprocess"
    assert gpt.runtime_framework == "pytorch_subprocess"
    assert gpt.supports_scoped_environment is True
    assert gpt.supports_runtime_threads is False
    assert gpt.production_ready is True
    assert "subprocess.run(env=env)" in gpt.provenance[
        "source"
    ]
    assert mock.production_ready is False
    assert vieneu.production_ready is False


def test_policy_rollout_defaults_are_safe_and_additive():

    policy = FakePolicyService().resolve()

    assert policy.feature_modes[
        "thread_budget_mode"
    ] == FEATURE_MODE_MONITOR_ONLY
    assert policy.thread_budget_engine_allowlist == []
    assert policy.thread_budget_engine_denylist == []
    assert policy.thread_budget_rollout_percentage == 0
    assert policy.thread_budget_require_explicit_engine_opt_in is True
    assert policy.thread_budget_fail_open is False


def test_enforce_requires_allowlist_or_explicit_opt_in_and_rollout():

    service = make_service(
        mode=FEATURE_MODE_ENFORCE,
        rollout_percentage=100,
    )

    _, state = prepare(
        service
    )

    assert state.status == THREAD_BUDGET_STATE_DEFERRED
    assert THREAD_REASON_ENGINE_OPT_IN_REQUIRED in state.reason_codes
    assert THREAD_REASON_CONTROLLED_ROLLOUT_DEFERRED in state.reason_codes

    service = make_service(
        mode=FEATURE_MODE_ENFORCE,
        rollout_percentage=100,
    )
    _, opted_in = prepare(
        service,
        engine_opt_in=True,
    )

    assert opted_in.status == THREAD_BUDGET_STATE_APPLIED
    assert THREAD_REASON_ROLLOUT_SELECTED in opted_in.reason_codes


def test_denylist_precedence_and_unknown_engine_do_not_fail_open():

    denied_service = make_service(
        mode=FEATURE_MODE_ENFORCE,
        allowlist=[
            "gpt_sovits"
        ],
        denylist=[
            "gpt_sovits"
        ],
        rollout_percentage=100,
    )
    _, denied = prepare(
        denied_service
    )

    assert denied.status == THREAD_BUDGET_STATE_DEFERRED
    assert THREAD_REASON_ENGINE_DENIED in denied.reason_codes

    unknown_service = make_service(
        mode=FEATURE_MODE_ENFORCE,
        allowlist=[
            "missing"
        ],
        rollout_percentage=100,
    )
    _, unknown = prepare(
        unknown_service,
        engine_id="missing",
    )

    assert unknown.status == THREAD_BUDGET_STATE_DEFERRED
    assert THREAD_REASON_ENGINE_NOT_REGISTERED in unknown.reason_codes
    assert THREAD_REASON_UNKNOWN_ENGINE_DEFERRED in unknown.reason_codes


def test_percentage_rollout_is_deterministic_and_can_defer():

    service = make_service(
        mode=FEATURE_MODE_ENFORCE,
        allowlist=[
            "gpt_sovits"
        ],
        rollout_percentage=0,
    )
    _, state_a = prepare(
        service,
        job_id="job_stable",
    )
    _, state_b = prepare(
        service,
        job_id="job_stable",
    )

    assert state_a.status == THREAD_BUDGET_STATE_DEFERRED
    assert state_b.metadata[
        "rollout"
    ][
        "selected"
    ] == state_a.metadata[
        "rollout"
    ][
        "selected"
    ]
    assert THREAD_REASON_ROLLOUT_NOT_SELECTED in state_a.reason_codes


def test_not_allowlisted_when_explicit_opt_in_not_required():

    service = make_service(
        mode=FEATURE_MODE_ENFORCE,
        rollout_percentage=100,
        require_opt_in=False,
    )
    _, state = prepare(
        service
    )

    assert state.status == THREAD_BUDGET_STATE_DEFERRED
    assert THREAD_REASON_ENGINE_NOT_ALLOWLISTED in state.reason_codes


def test_subprocess_environment_adapter_uses_scoped_supported_variables_only():

    service = make_service(
        mode=FEATURE_MODE_ENFORCE,
        allowlist=[
            "gpt_sovits"
        ],
        rollout_percentage=100,
    )
    original = {
        "OMP_NUM_THREADS": "8",
        "TORCH_NUM_THREADS": "99",
    }

    _, state = prepare(
        service,
        environment=original,
    )

    assert state.status == THREAD_BUDGET_STATE_APPLIED
    assert state.environment_before[
        "OMP_NUM_THREADS"
    ] == "8"
    assert state.environment_after[
        "OMP_NUM_THREADS"
    ] == "2"
    assert state.environment_after[
        "TOKENIZERS_PARALLELISM"
    ] == "false"
    assert state.environment_after[
        "TORCH_NUM_THREADS"
    ] == "99"
    assert original[
        "OMP_NUM_THREADS"
    ] == "8"
    assert set(
        GPT_SOVITS_THREAD_ENVIRONMENT_VARIABLES
    ).issuperset(
        {
            "OMP_NUM_THREADS",
            "RAYON_NUM_THREADS",
        }
    )
    assert THREAD_REASON_SUBPROCESS_ENVIRONMENT_APPLIED in (
        state.reason_codes
    )


def test_pytorch_adapter_is_lazy_and_intraop_only_with_fake_module():

    class FakeTorch:

        def __init__(
            self,
        ):

            self.threads = 8

        def get_num_threads(
            self,
        ):

            return self.threads

        def set_num_threads(
            self,
            value,
        ):

            self.threads = int(
                value
            )

    module_name = "fake_torch_phase9"
    fake = FakeTorch()
    sys.modules[
        module_name
    ] = fake

    try:

        adapter = PyTorchThreadBudgetAdapter(
            "engine_torch",
            module_name=module_name,
        )
        registry = ThreadBudgetCapabilityRegistry()
        registry.register(
            ThreadBudgetEngineCapability(
                engine_id="engine_torch",
                engine_name="Fake Torch",
                execution_mode="in_process",
                runtime_framework="pytorch",
                adapter_id="pytorch",
                adapter_name="PyTorchThreadBudgetAdapter",
                supports_environment_threads=False,
                supports_runtime_threads=True,
                supports_restore=True,
                supports_scoped_environment=False,
                supports_intraop_threads=True,
                supports_interop_threads=False,
                production_ready=True,
            ),
            adapter=adapter,
        )
        service = make_service(
            mode=FEATURE_MODE_ENFORCE,
            registry=registry,
            allowlist=[
                "engine_torch"
            ],
            rollout_percentage=100,
        )

        _, state = prepare(
            service,
            engine_id="engine_torch",
            environment={},
        )
        applied_status = state.status
        restored = service.restore_enforcement(
            state,
            engine_id="engine_torch",
        )

        assert applied_status == THREAD_BUDGET_STATE_APPLIED
        assert fake.threads == 8
        assert restored.status == THREAD_BUDGET_STATE_RESTORED

    finally:

        sys.modules.pop(
            module_name,
            None,
        )


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
        "phase9_worker",
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


def test_job_runner_enforce_registered_engine_apply_restore(tmp_path):

    class Worker(BaseJobWorker):

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
                "ok": True
            }

    service = make_service(
        mode=FEATURE_MODE_ENFORCE,
        allowlist=[
            "gpt_sovits"
        ],
        rollout_percentage=100,
    )
    repository, queue, runner = make_job_stack(
        tmp_path,
        service,
        Worker,
    )
    queue.enqueue_new(
        "phase9_worker",
        payload={
            "thread_budget_engine_id": "gpt_sovits",
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


def test_job_runner_no_service_keeps_legacy_flow(tmp_path):

    class Worker(BaseJobWorker):

        def execute(
            self,
            job,
            context,
        ):

            assert context.thread_budget_state is None
            return {
                "ok": True
            }

    repository, queue, runner = make_job_stack(
        tmp_path,
        None,
        Worker,
    )
    queue.enqueue_new(
        "phase9_worker"
    )

    result = runner.run_next()

    assert result.state == "completed"

from models.resource_model import ThreadBudgetEngineCapability
from models.resource_model import (
    THREAD_REASON_ADAPTER_REGISTERED,
    THREAD_REASON_ENGINE_CAPABILITY_AVAILABLE,
    THREAD_REASON_ENGINE_CAPABILITY_NOT_PRODUCTION_READY,
    THREAD_REASON_ENGINE_CAPABILITY_UNAVAILABLE,
    THREAD_REASON_ENGINE_NOT_REGISTERED,
    THREAD_REASON_ENGINE_REGISTERED,
    THREAD_REASON_UNKNOWN_ENGINE_DEFERRED,
)
from services.thread_budget_runtime_adapter import (
    SubprocessEnvironmentThreadAdapter,
    UnsupportedEngineThreadAdapter,
)


GPT_SOVITS_THREAD_ENVIRONMENT_VARIABLES = (
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "BLIS_NUM_THREADS",
    "TOKENIZERS_PARALLELISM",
    "RAYON_NUM_THREADS",
)


class ThreadBudgetCapabilityRegistry:

    def __init__(
        self,
    ):

        self.capabilities = {}

        self.adapters = {}

    def register(
        self,
        capability,
        adapter=None,
    ):

        capability = ThreadBudgetEngineCapability.from_dict(
            capability
        )

        self.capabilities[
            capability.engine_id
        ] = capability

        if adapter is not None:

            self.adapters[
                capability.engine_id
            ] = adapter

        return capability

    def register_unsupported(
        self,
        engine_id,
        engine_name="",
        unavailable_reason="thread_engine_capability_unavailable",
    ):

        return self.register(
            ThreadBudgetEngineCapability(
                engine_id=engine_id,
                engine_name=engine_name
                or engine_id,
                execution_mode="unknown",
                runtime_framework="unknown",
                adapter_id="unsupported",
                adapter_name="UnsupportedEngineThreadAdapter",
                adapter_version="phase9",
                supports_environment_threads=False,
                supports_runtime_threads=False,
                supports_restore=False,
                supports_scoped_environment=False,
                production_ready=False,
                unavailable_reason=unavailable_reason,
                capability_version="phase9",
                provenance={
                    "source": "source_inventory_phase9",
                },
            ),
            adapter=UnsupportedEngineThreadAdapter(
                engine_id,
                unavailable_reason,
            ),
        )

    def capability(
        self,
        engine_id,
    ):

        return self.capabilities.get(
            engine_id
        )

    def adapter(
        self,
        engine_id,
    ):

        return self.adapters.get(
            engine_id
        )

    def supports(
        self,
        engine_id,
    ):

        capability = self.capability(
            engine_id
        )

        if capability is None:

            return False

        return bool(
            capability.supports_environment_threads
            or capability.supports_runtime_threads
        )

    def reason_codes(
        self,
        engine_id,
    ):

        capability = self.capability(
            engine_id
        )

        if capability is None:

            return [
                THREAD_REASON_ENGINE_NOT_REGISTERED,
                THREAD_REASON_UNKNOWN_ENGINE_DEFERRED,
            ]

        reasons = [
            THREAD_REASON_ENGINE_REGISTERED
        ]

        if capability.production_ready:

            reasons.append(
                THREAD_REASON_ENGINE_CAPABILITY_AVAILABLE
            )

        else:

            reasons.extend(
                [
                    THREAD_REASON_ENGINE_CAPABILITY_UNAVAILABLE,
                    THREAD_REASON_ENGINE_CAPABILITY_NOT_PRODUCTION_READY,
                ]
            )

        if self.adapter(
            engine_id
        ) is not None:

            reasons.append(
                THREAD_REASON_ADAPTER_REGISTERED
            )

        return sorted(
            set(
                reasons
            )
        )


def build_default_thread_budget_registry(
    engine_manager=None,
):

    registry = ThreadBudgetCapabilityRegistry()

    engine_ids = set()

    if engine_manager is not None and hasattr(
        engine_manager,
        "engine_ids",
    ):

        engine_ids.update(
            engine_manager.engine_ids()
        )

    engine_ids.add(
        "gpt_sovits"
    )

    if "gpt_sovits" in engine_ids:

        registry.register(
            ThreadBudgetEngineCapability(
                engine_id="gpt_sovits",
                engine_name="GPT-SoVITS",
                execution_mode="subprocess",
                runtime_framework="pytorch_subprocess",
                adapter_id="subprocess_environment",
                adapter_name="SubprocessEnvironmentThreadAdapter",
                adapter_version="phase9",
                supports_environment_threads=True,
                supports_runtime_threads=False,
                supports_restore=True,
                supports_scoped_environment=True,
                supports_intraop_threads=False,
                supports_interop_threads=False,
                requires_restart_for_thread_change=True,
                max_safe_threads=0,
                capability_version="phase9",
                production_ready=True,
                unavailable_reason="",
                supported_environment_variables=list(
                    GPT_SOVITS_THREAD_ENVIRONMENT_VARIABLES
                ),
                provenance={
                    "source": (
                        "src/engines/gpt_sovits_adapter.py:"
                        "subprocess.run(env=env)"
                    ),
                    "engine_id_source": (
                        "src/engines/gpt_sovits_engine.py:info.id"
                    ),
                },
            ),
            adapter=SubprocessEnvironmentThreadAdapter(
                "gpt_sovits",
                supported_environment_variables=(
                    GPT_SOVITS_THREAD_ENVIRONMENT_VARIABLES
                ),
            ),
        )

    for engine_id in sorted(
        engine_ids - {
            "gpt_sovits"
        }
    ):

        registry.register_unsupported(
            engine_id,
            unavailable_reason=(
                "thread_engine_capability_not_production_ready"
            ),
        )

    registry.register_unsupported(
        "vieneu",
        engine_name="VieNeu",
        unavailable_reason="thread_engine_not_registered",
    )

    return registry

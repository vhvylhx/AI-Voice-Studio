from models.resource_model import (
    FEATURE_MODE_ENFORCE,
    THREAD_BUDGET_STATE_APPLIED,
    THREAD_BUDGET_ACTION_RESTORE,
    THREAD_BUDGET_STATE_DEFERRED,
    THREAD_BUDGET_STATE_FAILED,
    THREAD_BUDGET_STATE_RESTORED,
    THREAD_BUDGET_STATE_SIMULATED,
    THREAD_REASON_ADAPTER_UNAVAILABLE,
    THREAD_REASON_ADAPTER_UNSUPPORTED,
    THREAD_REASON_ADAPTER_APPLY_FAILED,
    THREAD_REASON_ADAPTER_CAPTURE_FAILED,
    THREAD_REASON_ADAPTER_PARTIAL_APPLY,
    THREAD_REASON_ADAPTER_ROLLBACK_COMPLETED,
    THREAD_REASON_ADAPTER_ROLLBACK_FAILED,
    THREAD_REASON_ACTION_FAILED,
    THREAD_REASON_ACTION_NOT_ALLOWED,
    THREAD_REASON_ACTION_SIMULATED,
    THREAD_REASON_ENFORCEMENT_APPLIED,
    THREAD_REASON_ENFORCEMENT_DEFERRED,
    THREAD_REASON_ENGINE_CAPABILITY_MISSING,
    THREAD_REASON_ENGINE_CAPABILITY_NOT_PRODUCTION_READY,
    THREAD_REASON_ENVIRONMENT_APPLIED,
    THREAD_REASON_ENVIRONMENT_RESTORED,
    THREAD_REASON_MODE_ENFORCE,
    THREAD_REASON_PARTIAL_APPLY,
    THREAD_REASON_PRIMARY_ERROR_PRESERVED,
    THREAD_REASON_RUNTIME_APPLIED,
    THREAD_REASON_RUNTIME_APPLY_FAILED,
    THREAD_REASON_RUNTIME_RESTORED,
    THREAD_REASON_RUNTIME_RESTORE_FAILED,
    THREAD_REASON_ROLLBACK_COMPLETED,
    THREAD_REASON_ROLLBACK_FAILED,
    THREAD_REASON_ROLLBACK_REQUIRED,
    THREAD_REASON_SUBPROCESS_ENVIRONMENT_APPLIED,
    THREAD_REASON_PRODUCTION_EXECUTOR_UNAVAILABLE,
    THREAD_REASON_RESTORE_REQUIRED,
    ThreadBudgetApplyState,
)
from models.resource_model import now_iso
from uuid import uuid4


class ThreadBudgetExecutor:

    def execute(
        self,
        observation,
        policy,
        mode,
        runtime_adapter=None,
    ):

        return {
            "state": THREAD_BUDGET_STATE_DEFERRED,
            "executed": False,
            "simulated": False,
            "reason_codes": [
                THREAD_REASON_PRODUCTION_EXECUTOR_UNAVAILABLE
            ],
            "audit": [],
        }


class SimulatedThreadBudgetExecutor(ThreadBudgetExecutor):

    def __init__(
        self,
        fail_actions=None,
    ):

        self.fail_actions = set(
            fail_actions
            or []
        )

        self.calls = []

        self.previous_values = {}

    def execute(
        self,
        observation,
        policy,
        mode,
        runtime_adapter=None,
    ):

        self.calls.append(
            (
                observation.action,
                observation.job_id,
                observation.lease_id,
                observation.process_id,
            )
        )

        if mode != FEATURE_MODE_ENFORCE:

            return {
                "state": THREAD_BUDGET_STATE_DEFERRED,
                "executed": False,
                "simulated": False,
                "reason_codes": [
                    THREAD_REASON_ACTION_NOT_ALLOWED
                ],
                "audit": [],
            }

        if observation.action in self.fail_actions:

            return {
                "state": THREAD_BUDGET_STATE_FAILED,
                "executed": False,
                "simulated": True,
                "reason_codes": [
                    THREAD_REASON_ACTION_FAILED
                ],
                "audit": [
                    {
                        "action": observation.action,
                        "simulated": True,
                        "result": "failed",
                    }
                ],
            }

        self.previous_values[
            observation.budget_id
        ] = {
            "environment": {
                name: data.get(
                    "current"
                )
                for name, data in observation.environment_plan.items()
            },
            "runtime": {
                name: data.get(
                    "current"
                )
                for name, data in observation.runtime_plan.items()
            },
        }

        if observation.action == THREAD_BUDGET_ACTION_RESTORE:

            return {
                "state": THREAD_BUDGET_STATE_RESTORED,
                "executed": False,
                "simulated": True,
                "reason_codes": [
                    THREAD_REASON_ACTION_SIMULATED,
                    THREAD_REASON_RESTORE_REQUIRED,
                ],
                "audit": [
                    {
                        "action": observation.action,
                        "simulated": True,
                        "result": "restored",
                    }
                ],
            }

        return {
            "state": THREAD_BUDGET_STATE_SIMULATED,
            "executed": False,
            "simulated": True,
            "reason_codes": [
                THREAD_REASON_ACTION_SIMULATED
            ],
            "audit": [
                {
                    "action": observation.action,
                    "simulated": True,
                    "result": "simulated",
                }
            ],
        }


class ScopedThreadBudgetExecutor(ThreadBudgetExecutor):

    def apply(
        self,
        observation,
        policy,
        mode,
        engine_id="",
        capability=None,
        runtime_adapter=None,
        environment=None,
    ):

        state = self.new_state(
            observation,
            mode,
            engine_id,
            environment,
        )

        if mode != FEATURE_MODE_ENFORCE:

            state.status = THREAD_BUDGET_STATE_DEFERRED
            state.reason_codes.append(
                THREAD_REASON_ENFORCEMENT_DEFERRED
            )
            return state

        if capability is None:

            state.status = THREAD_BUDGET_STATE_DEFERRED
            state.reason_codes.append(
                THREAD_REASON_ENGINE_CAPABILITY_MISSING
            )
            return state

        if not getattr(
            capability,
            "production_ready",
            False,
        ):

            state.status = THREAD_BUDGET_STATE_DEFERRED
            state.reason_codes.append(
                THREAD_REASON_ENGINE_CAPABILITY_NOT_PRODUCTION_READY
            )
            return state

        if runtime_adapter is None and capability.supports_runtime_threads:

            state.status = THREAD_BUDGET_STATE_DEFERRED
            state.reason_codes.append(
                THREAD_REASON_ADAPTER_UNAVAILABLE
            )
            return state

        if not (
            capability.supports_environment_threads
            or capability.supports_runtime_threads
        ):

            state.status = THREAD_BUDGET_STATE_DEFERRED
            state.reason_codes.append(
                THREAD_REASON_ADAPTER_UNSUPPORTED
            )
            return state

        if runtime_adapter is not None:

            try:

                valid = runtime_adapter.validate_thread_budget(
                    observation,
                    capability,
                )

            except Exception as exc:

                state.status = THREAD_BUDGET_STATE_DEFERRED
                state.reason_codes.append(
                    THREAD_REASON_ADAPTER_UNSUPPORTED
                )
                state.audit.append(
                    {
                        "action": "validate",
                        "result": "failed",
                        "error": str(
                            exc
                        ),
                    }
                )
                return state

            if not valid:

                state.status = THREAD_BUDGET_STATE_DEFERRED
                state.reason_codes.append(
                    THREAD_REASON_ADAPTER_UNSUPPORTED
                )
                return state

            try:

                state.runtime_before = (
                    runtime_adapter.capture_current_settings()
                )

            except Exception as exc:

                state.status = THREAD_BUDGET_STATE_DEFERRED
                state.reason_codes.append(
                    THREAD_REASON_ADAPTER_CAPTURE_FAILED
                )
                state.audit.append(
                    {
                        "action": "capture",
                        "result": "failed",
                        "error": str(
                            exc
                        ),
                    }
                )
                return state

        environment_applied = False

        if capability.supports_environment_threads:

            state.environment_after = self.apply_environment_plan(
                state.environment_before,
                observation.environment_plan,
                capability,
            )
            environment_applied = bool(
                observation.environment_plan
            )

            if environment_applied:

                state.reason_codes.append(
                    THREAD_REASON_ENVIRONMENT_APPLIED
                )

                if getattr(
                    capability,
                    "execution_mode",
                    "",
                ) == "subprocess":

                    state.reason_codes.append(
                        THREAD_REASON_SUBPROCESS_ENVIRONMENT_APPLIED
                    )

        try:

            if (
                capability.supports_runtime_threads
                and runtime_adapter is not None
            ):

                result = runtime_adapter.apply_thread_budget(
                    observation,
                    capability,
                )
                state.runtime_after = dict(
                    result.get(
                        "settings",
                        {},
                    )
                )
                state.reason_codes.append(
                    THREAD_REASON_RUNTIME_APPLIED
                )

        except Exception as exc:

            state.status = THREAD_BUDGET_STATE_FAILED
            state.reason_codes.extend(
                [
                    THREAD_REASON_RUNTIME_APPLY_FAILED,
                    THREAD_REASON_ADAPTER_APPLY_FAILED,
                    THREAD_REASON_ADAPTER_PARTIAL_APPLY,
                    THREAD_REASON_PARTIAL_APPLY,
                    THREAD_REASON_ROLLBACK_REQUIRED,
                ]
            )
            state.audit.append(
                {
                    "action": "apply_runtime",
                    "result": "failed",
                    "error": str(
                        exc
                    ),
                }
            )
            self.rollback_after_apply_failure(
                state,
                runtime_adapter,
                environment_applied,
            )
            return state

        state.status = THREAD_BUDGET_STATE_APPLIED
        state.applied_at = now_iso()
        state.reason_codes.extend(
            [
                THREAD_REASON_MODE_ENFORCE,
                THREAD_REASON_ENFORCEMENT_APPLIED,
            ]
        )
        state.reason_codes = sorted(
            set(
                state.reason_codes
            )
        )
        state.audit.append(
            {
                "action": "apply",
                "result": "applied",
                "engine_id": engine_id,
            }
        )

        return state

    def restore(
        self,
        state,
        runtime_adapter=None,
        primary_error=None,
    ):

        state = ThreadBudgetApplyState.from_dict(
            state
        )

        if state.status == THREAD_BUDGET_STATE_RESTORED:

            return state

        restore_errors = []

        state.environment_after = dict(
            state.environment_before
        )

        if state.environment_before:

            state.reason_codes.append(
                THREAD_REASON_ENVIRONMENT_RESTORED
            )

        if runtime_adapter is not None:

            try:

                runtime_adapter.restore_thread_budget(
                    state
                )
                state.runtime_after = dict(
                    state.runtime_before
                )
                state.reason_codes.append(
                    THREAD_REASON_RUNTIME_RESTORED
                )

            except Exception as exc:

                restore_errors.append(
                    exc
                )
                state.reason_codes.append(
                    THREAD_REASON_RUNTIME_RESTORE_FAILED
                )

        state.restored_at = now_iso()

        if restore_errors:

            state.status = THREAD_BUDGET_STATE_FAILED
            state.reason_codes.append(
                THREAD_REASON_ROLLBACK_FAILED
            )

            if primary_error is not None:

                state.reason_codes.append(
                    THREAD_REASON_PRIMARY_ERROR_PRESERVED
                )

            state.audit.append(
                {
                    "action": "restore",
                    "result": "failed",
                    "error": str(
                        restore_errors[0]
                    ),
                }
            )
            return state

        state.status = THREAD_BUDGET_STATE_RESTORED
        state.reason_codes = sorted(
            set(
                state.reason_codes
            )
        )
        state.audit.append(
            {
                "action": "restore",
                "result": "restored",
            }
        )

        return state

    def new_state(
        self,
        observation,
        mode,
        engine_id,
        environment,
    ):

        environment = dict(
            environment
            or {}
        )

        return ThreadBudgetApplyState(
            state_id=f"thread_apply_{uuid4().hex[:12]}",
            budget_id=observation.budget_id,
            observation_id=observation.observation_id,
            job_id=observation.job_id,
            lease_id=observation.lease_id,
            process_id=observation.process_id,
            owner_id=observation.owner_id,
            engine_id=engine_id,
            mode=mode,
            status=THREAD_BUDGET_STATE_DEFERRED,
            environment_before=environment,
            environment_after=dict(
                environment
            ),
            policy_fingerprint=observation.policy_fingerprint,
            reason_codes=list(
                observation.reason_codes
            ),
        )

    def apply_environment_plan(
        self,
        environment,
        environment_plan,
        capability=None,
    ):

        scoped = dict(
            environment
            or {}
        )

        supported = set(
            getattr(
                capability,
                "supported_environment_variables",
                [],
            )
            or []
        )

        for name, change in sorted(
            (
                environment_plan
                or {}
            ).items()
        ):

            if supported and name not in supported:

                continue

            scoped[
                name
            ] = str(
                change.get(
                    "desired",
                    "",
                )
            )

        return scoped

    def rollback_after_apply_failure(
        self,
        state,
        runtime_adapter,
        environment_applied,
    ):

        state.environment_after = dict(
            state.environment_before
        )

        try:

            if runtime_adapter is not None:

                runtime_adapter.restore_thread_budget(
                    state
                )

            state.reason_codes.append(
                THREAD_REASON_ROLLBACK_COMPLETED
            )
            state.reason_codes.append(
                THREAD_REASON_ADAPTER_ROLLBACK_COMPLETED
            )

        except Exception as exc:

            state.reason_codes.append(
                THREAD_REASON_ROLLBACK_FAILED
            )
            state.reason_codes.append(
                THREAD_REASON_ADAPTER_ROLLBACK_FAILED
            )
            state.audit.append(
                {
                    "action": "rollback",
                    "result": "failed",
                    "error": str(
                        exc
                    ),
                }
            )

        if environment_applied:

            state.reason_codes.append(
                THREAD_REASON_ENVIRONMENT_RESTORED
            )

        state.reason_codes = sorted(
            set(
                state.reason_codes
            )
        )

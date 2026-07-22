from models.resource_model import (
    FEATURE_MODE_ENFORCE,
    THREAD_BUDGET_ACTION_RESTORE,
    THREAD_BUDGET_STATE_DEFERRED,
    THREAD_BUDGET_STATE_FAILED,
    THREAD_BUDGET_STATE_RESTORED,
    THREAD_BUDGET_STATE_SIMULATED,
    THREAD_REASON_ACTION_FAILED,
    THREAD_REASON_ACTION_NOT_ALLOWED,
    THREAD_REASON_ACTION_SIMULATED,
    THREAD_REASON_PRODUCTION_EXECUTOR_UNAVAILABLE,
    THREAD_REASON_RESTORE_REQUIRED,
)


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

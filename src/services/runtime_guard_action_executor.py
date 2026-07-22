from models.resource_model import (
    RUNTIME_GUARD_ACTION_GRACEFUL_STOP,
    RUNTIME_GUARD_ACTION_KILL_TREE,
    RUNTIME_GUARD_ACTION_REQUEST_PAUSE,
    RUNTIME_GUARD_ACTION_TERMINATE,
    RUNTIME_GUARD_STATE_DEFERRED,
    RUNTIME_GUARD_STATE_FAILED,
    RUNTIME_GUARD_STATE_SIMULATED,
    RUNTIME_REASON_ACTION_FAILED,
    RUNTIME_REASON_ACTION_NOT_ALLOWED,
    RUNTIME_REASON_ACTION_SIMULATED,
    RUNTIME_REASON_DESTRUCTIVE_ACTION_UNAVAILABLE,
)


DESTRUCTIVE_ACTIONS = (
    RUNTIME_GUARD_ACTION_TERMINATE,
    RUNTIME_GUARD_ACTION_KILL_TREE,
)


class RuntimeGuardActionExecutor:

    def execute(
        self,
        observation,
        policy,
    ):

        return {
            "state": RUNTIME_GUARD_STATE_DEFERRED,
            "executed": False,
            "simulated": False,
            "reason_codes": [
                RUNTIME_REASON_ACTION_NOT_ALLOWED
            ],
            "audit": [],
        }


class SimulatedRuntimeGuardActionExecutor(RuntimeGuardActionExecutor):

    def __init__(
        self,
        fail_actions=None,
    ):

        self.fail_actions = set(
            fail_actions
            or []
        )

        self.calls = []

    def execute(
        self,
        observation,
        policy,
    ):

        action = observation.action

        self.calls.append(
            (
                action,
                observation.job_id,
                observation.lease_id,
                observation.process_id,
            )
        )

        if action in self.fail_actions:

            return {
                "state": RUNTIME_GUARD_STATE_FAILED,
                "executed": False,
                "simulated": True,
                "reason_codes": [
                    RUNTIME_REASON_ACTION_FAILED
                ],
                "audit": [
                    {
                        "action": action,
                        "simulated": True,
                        "result": "failed",
                    }
                ],
            }

        if action in DESTRUCTIVE_ACTIONS:

            return {
                "state": RUNTIME_GUARD_STATE_DEFERRED,
                "executed": False,
                "simulated": True,
                "reason_codes": [
                    RUNTIME_REASON_DESTRUCTIVE_ACTION_UNAVAILABLE
                ],
                "audit": [
                    {
                        "action": action,
                        "simulated": True,
                        "result": "destructive_unavailable",
                    }
                ],
            }

        if action == RUNTIME_GUARD_ACTION_REQUEST_PAUSE and not getattr(
            policy,
            "allow_simulated_pause",
            False,
        ):

            return {
                "state": RUNTIME_GUARD_STATE_DEFERRED,
                "executed": False,
                "simulated": True,
                "reason_codes": [
                    RUNTIME_REASON_ACTION_NOT_ALLOWED
                ],
                "audit": [],
            }

        if action == RUNTIME_GUARD_ACTION_GRACEFUL_STOP and not getattr(
            policy,
            "allow_simulated_graceful_stop",
            False,
        ):

            return {
                "state": RUNTIME_GUARD_STATE_DEFERRED,
                "executed": False,
                "simulated": True,
                "reason_codes": [
                    RUNTIME_REASON_ACTION_NOT_ALLOWED
                ],
                "audit": [],
            }

        return {
            "state": RUNTIME_GUARD_STATE_SIMULATED,
            "executed": False,
            "simulated": True,
            "reason_codes": [
                RUNTIME_REASON_ACTION_SIMULATED
            ],
            "audit": [
                {
                    "action": action,
                    "simulated": True,
                    "result": "simulated",
                }
            ],
        }

class ThreadBudgetRuntimeAdapter:

    adapter_id = "base"

    def capture_current_settings(
        self,
    ):

        return {}

    def validate_thread_budget(
        self,
        observation,
        capability,
    ):

        return True

    def apply_thread_budget(
        self,
        observation,
        capability,
    ):

        return {
            "applied": False,
            "settings": self.capture_current_settings(),
        }

    def restore_thread_budget(
        self,
        state,
    ):

        return {
            "restored": False,
            "settings": self.capture_current_settings(),
        }


class FakeThreadBudgetRuntimeAdapter(ThreadBudgetRuntimeAdapter):

    adapter_id = "fake"

    def __init__(
        self,
        settings=None,
        validate_ok=True,
        fail_apply=False,
        fail_restore=False,
    ):

        self.settings = dict(
            settings
            or {}
        )
        self.validate_ok = validate_ok
        self.fail_apply = fail_apply
        self.fail_restore = fail_restore
        self.calls = []

    def capture_current_settings(
        self,
    ):

        self.calls.append(
            (
                "capture",
                dict(
                    self.settings
                ),
            )
        )

        return dict(
            self.settings
        )

    def validate_thread_budget(
        self,
        observation,
        capability,
    ):

        self.calls.append(
            (
                "validate",
                observation.budget_id,
                capability.engine_id,
            )
        )

        return bool(
            self.validate_ok
        )

    def apply_thread_budget(
        self,
        observation,
        capability,
    ):

        self.calls.append(
            (
                "apply",
                observation.resolved_threads,
            )
        )

        if self.fail_apply:

            raise RuntimeError(
                "thread_runtime_apply_failed"
            )

        if capability.supports_intraop_threads:

            self.settings[
                "num_threads"
            ] = observation.resolved_threads

        if capability.supports_interop_threads:

            self.settings[
                "num_interop_threads"
            ] = min(
                2,
                max(
                    1,
                    observation.resolved_threads,
                ),
            )

        return {
            "applied": True,
            "settings": dict(
                self.settings
            ),
        }

    def restore_thread_budget(
        self,
        state,
    ):

        self.calls.append(
            (
                "restore",
                state.state_id,
            )
        )

        if self.fail_restore:

            raise RuntimeError(
                "thread_runtime_restore_failed"
            )

        self.settings = dict(
            state.runtime_before
        )

        return {
            "restored": True,
            "settings": dict(
                self.settings
            ),
        }


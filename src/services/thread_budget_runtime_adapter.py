import importlib

from models.resource_model import (
    THREAD_REASON_ADAPTER_CAPTURE_FAILED,
    THREAD_REASON_ADAPTER_HEALTH_CHECK_FAILED,
    THREAD_REASON_ADAPTER_LAZY_IMPORT_FAILED,
    THREAD_REASON_ADAPTER_PARTIAL_APPLY,
    THREAD_REASON_ADAPTER_RESTORE_FAILED,
    THREAD_REASON_PYTORCH_INTEROP_UNSUPPORTED,
    THREAD_REASON_PYTORCH_UNAVAILABLE,
)


class ThreadBudgetRuntimeAdapter:

    adapter_id = "base"
    adapter_name = "base"
    adapter_version = "phase9"

    def supports_engine(
        self,
        engine_id,
    ):

        return False

    def discover_capabilities(
        self,
    ):

        return []

    def capture_current_settings(
        self,
    ):

        return {}

    def health_check(
        self,
    ):

        return {
            "ready": False,
            "reason_codes": [
                THREAD_REASON_ADAPTER_HEALTH_CHECK_FAILED
            ],
        }

    def describe_unavailability(
        self,
    ):

        return "adapter_unavailable"

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
    adapter_name = "fake"

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

    def health_check(
        self,
    ):

        return {
            "ready": True,
            "reason_codes": [],
        }

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


class UnsupportedEngineThreadAdapter(ThreadBudgetRuntimeAdapter):

    adapter_id = "unsupported"
    adapter_name = "UnsupportedEngineThreadAdapter"

    def __init__(
        self,
        engine_id,
        reason,
    ):

        self.engine_id = engine_id
        self.reason = reason

    def supports_engine(
        self,
        engine_id,
    ):

        return engine_id == self.engine_id

    def health_check(
        self,
    ):

        return {
            "ready": False,
            "reason_codes": [
                self.reason
            ],
        }

    def describe_unavailability(
        self,
    ):

        return self.reason


class SubprocessEnvironmentThreadAdapter(ThreadBudgetRuntimeAdapter):

    adapter_id = "subprocess_environment"
    adapter_name = "SubprocessEnvironmentThreadAdapter"

    def __init__(
        self,
        engine_id,
        supported_environment_variables=None,
    ):

        self.engine_id = engine_id
        self.supported_environment_variables = tuple(
            supported_environment_variables
            or ()
        )
        self.calls = []

    def supports_engine(
        self,
        engine_id,
    ):

        return engine_id == self.engine_id

    def capture_current_settings(
        self,
    ):

        self.calls.append(
            (
                "capture",
                self.engine_id,
            )
        )
        return {
            "execution_mode": "subprocess",
            "supported_environment_variables": list(
                self.supported_environment_variables
            ),
        }

    def validate_thread_budget(
        self,
        observation,
        capability,
    ):

        self.calls.append(
            (
                "validate",
                observation.budget_id,
            )
        )
        return bool(
            capability.supports_scoped_environment
            and capability.supports_restore
            and observation.resolved_threads > 0
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
        return {
            "applied": bool(
                observation.environment_plan
            ),
            "settings": {
                "execution_mode": "subprocess",
                "resolved_threads": observation.resolved_threads,
            },
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
        return {
            "restored": True,
            "settings": dict(
                state.runtime_before
            ),
        }

    def health_check(
        self,
    ):

        return {
            "ready": True,
            "reason_codes": [],
        }


class PyTorchThreadBudgetAdapter(ThreadBudgetRuntimeAdapter):

    adapter_id = "pytorch"
    adapter_name = "PyTorchThreadBudgetAdapter"

    def __init__(
        self,
        engine_id,
        module_name="torch",
    ):

        self.engine_id = engine_id
        self.module_name = module_name
        self._torch = None

    def supports_engine(
        self,
        engine_id,
    ):

        return engine_id == self.engine_id

    def torch(
        self,
    ):

        if self._torch is None:

            self._torch = importlib.import_module(
                self.module_name
            )

        return self._torch

    def health_check(
        self,
    ):

        try:

            torch = self.torch()

        except Exception:

            return {
                "ready": False,
                "reason_codes": [
                    THREAD_REASON_PYTORCH_UNAVAILABLE,
                    THREAD_REASON_ADAPTER_LAZY_IMPORT_FAILED,
                ],
            }

        ready = all(
            hasattr(
                torch,
                name,
            )
            for name in (
                "get_num_threads",
                "set_num_threads",
            )
        )

        return {
            "ready": ready,
            "reason_codes": []
            if ready
            else [
                THREAD_REASON_PYTORCH_UNAVAILABLE
            ],
        }

    def capture_current_settings(
        self,
    ):

        try:

            torch = self.torch()
            settings = {
                "num_threads": int(
                    torch.get_num_threads()
                )
            }

            if hasattr(
                torch,
                "get_num_interop_threads",
            ):

                settings[
                    "num_interop_threads"
                ] = int(
                    torch.get_num_interop_threads()
                )

            return settings

        except Exception as exc:

            raise RuntimeError(
                THREAD_REASON_ADAPTER_CAPTURE_FAILED
            ) from exc

    def validate_thread_budget(
        self,
        observation,
        capability,
    ):

        if observation.resolved_threads <= 0:

            return False

        health = self.health_check()

        if not health.get(
            "ready"
        ):

            return False

        if capability.supports_interop_threads:

            return False

        return bool(
            capability.supports_intraop_threads
        )

    def apply_thread_budget(
        self,
        observation,
        capability,
    ):

        if capability.supports_interop_threads:

            raise RuntimeError(
                THREAD_REASON_PYTORCH_INTEROP_UNSUPPORTED
            )

        torch = self.torch()
        desired = int(
            observation.resolved_threads
        )
        before = self.capture_current_settings()

        try:

            torch.set_num_threads(
                desired
            )
            after = self.capture_current_settings()

        except Exception as exc:

            try:

                torch.set_num_threads(
                    before[
                        "num_threads"
                    ]
                )

            except Exception as rollback_exc:

                raise RuntimeError(
                    THREAD_REASON_ADAPTER_PARTIAL_APPLY
                ) from rollback_exc

            raise RuntimeError(
                "thread_adapter_apply_failed"
            ) from exc

        if int(
            after.get(
                "num_threads",
                0,
            )
        ) != desired:

            torch.set_num_threads(
                before[
                    "num_threads"
                ]
            )
            raise RuntimeError(
                THREAD_REASON_ADAPTER_PARTIAL_APPLY
            )

        return {
            "applied": True,
            "settings": after,
        }

    def restore_thread_budget(
        self,
        state,
    ):

        try:

            torch = self.torch()
            previous = int(
                state.runtime_before.get(
                    "num_threads",
                    0,
                )
            )

            if previous <= 0:

                raise RuntimeError(
                    THREAD_REASON_ADAPTER_RESTORE_FAILED
                )

            torch.set_num_threads(
                previous
            )
            return {
                "restored": True,
                "settings": self.capture_current_settings(),
            }

        except Exception as exc:

            raise RuntimeError(
                THREAD_REASON_ADAPTER_RESTORE_FAILED
            ) from exc

from models.resource_model import ThreadBudgetEngineCapability


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


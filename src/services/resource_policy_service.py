from core import App
from models.resource_model import ResourcePolicy


class ResourcePolicyService:

    CONFIG_KEY = "resource_policy"

    def __init__(
        self,
        config=None,
    ):

        self.config = config or App.config

    def load(
        self,
    ):

        try:

            data = self.config.get(
                self.CONFIG_KEY,
                {},
            )

        except Exception:

            data = {}

        return ResourcePolicy.from_dict(
            data
        )

    def save(
        self,
        policy,
    ):

        policy = ResourcePolicy.from_dict(
            policy
        )

        self.config.set(
            self.CONFIG_KEY,
            policy.to_dict(),
        )

        return policy

    def summary(
        self,
    ):

        return self.load().to_dict()

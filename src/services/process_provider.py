from dataclasses import asdict
from dataclasses import dataclass


@dataclass
class ProcessSnapshot:

    pid: int

    parent_pid: int = 0

    executable: str = ""

    command_fingerprint: str = ""

    process_start_time: str = ""

    alive: bool = True

    permission_denied: bool = False

    provider_unavailable: bool = False

    malformed: bool = False

    process_group_id: str = ""

    session_id: str = ""

    def to_dict(
        self,
    ):

        return asdict(
            self
        )

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        if isinstance(
            data,
            cls,
        ):

            return data

        data = data or {}

        return cls(
            **{
                key: value
                for key, value in data.items()
                if key in cls.__dataclass_fields__
            }
        )


class ProcessProvider:

    def get_process(
        self,
        pid,
    ):

        return None

    def list_processes(
        self,
    ):

        return []


class StaticProcessProvider(ProcessProvider):

    def __init__(
        self,
        snapshots=None,
        unavailable=False,
        permission_denied_pids=None,
    ):

        self.snapshots = {
            int(
                ProcessSnapshot.from_dict(
                    item
                ).pid
            ): ProcessSnapshot.from_dict(
                item
            )
            for item in snapshots
            or []
        }

        self.unavailable = unavailable

        self.permission_denied_pids = set(
            permission_denied_pids
            or []
        )

    def get_process(
        self,
        pid,
    ):

        if self.unavailable:

            return ProcessSnapshot(
                pid=int(
                    pid
                ),
                provider_unavailable=True,
                alive=False,
            )

        if int(
            pid
        ) in self.permission_denied_pids:

            return ProcessSnapshot(
                pid=int(
                    pid
                ),
                permission_denied=True,
                alive=False,
            )

        return self.snapshots.get(
            int(
                pid
            )
        )

    def list_processes(
        self,
    ):

        if self.unavailable:

            return [
                ProcessSnapshot(
                    pid=0,
                    provider_unavailable=True,
                    alive=False,
                )
            ]

        return [
            self.snapshots[key]
            for key in sorted(
                self.snapshots
            )
        ]


class SimulatedProcessCommandExecutor:

    def __init__(
        self,
    ):

        self.calls = []

    def request_graceful_stop(
        self,
        identity,
    ):

        self.calls.append(
            (
                "graceful_stop",
                identity.process_id,
                identity.pid,
            )
        )

        return {
            "simulated": True,
            "action": "graceful_stop",
        }

    def terminate(
        self,
        identity,
    ):

        self.calls.append(
            (
                "terminate",
                identity.process_id,
                identity.pid,
            )
        )

        return {
            "simulated": True,
            "action": "terminate",
        }

    def kill_tree(
        self,
        identity,
        process_tree,
    ):

        self.calls.append(
            (
                "kill_tree",
                identity.process_id,
                tuple(
                    process_tree.get(
                        "pids",
                        []
                    )
                ),
            )
        )

        return {
            "simulated": True,
            "action": "kill_tree",
        }

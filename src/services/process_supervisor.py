import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from models.resource_model import (
    FEATURE_MODE_DISABLED,
    FEATURE_MODE_ENFORCE,
    FEATURE_MODE_ENFORCED,
    FEATURE_MODE_MONITOR_ONLY,
    PROCESS_ACTION_WOULD_BLOCK_IDENTITY_MISMATCH,
    PROCESS_ACTION_WOULD_DEFER,
    PROCESS_ACTION_WOULD_KILL_TREE,
    PROCESS_ACTION_WOULD_MARK_EXITED,
    PROCESS_ACTION_WOULD_MARK_ORPHANED,
    PROCESS_ACTION_WOULD_OBSERVE,
    PROCESS_ACTION_WOULD_RECONCILE,
    PROCESS_ACTION_WOULD_REQUEST_GRACEFUL_STOP,
    PROCESS_ACTION_WOULD_SKIP,
    PROCESS_ACTION_WOULD_TERMINATE,
    PROCESS_REASON_COMMAND_MISMATCH,
    PROCESS_REASON_EXECUTABLE_MISMATCH,
    PROCESS_REASON_GRACEFUL_STOP_DUE,
    PROCESS_REASON_IDENTITY_MISMATCH,
    PROCESS_REASON_IDENTITY_UNKNOWN,
    PROCESS_REASON_JOB_MISSING,
    PROCESS_REASON_KILL_TREE_DUE,
    PROCESS_REASON_LEASE_EXPIRED,
    PROCESS_REASON_LEASE_MISSING,
    PROCESS_REASON_MODE_DISABLED,
    PROCESS_REASON_MODE_ENFORCE,
    PROCESS_REASON_MODE_MONITOR_ONLY,
    PROCESS_REASON_MISSING,
    PROCESS_REASON_ORPHANED,
    PROCESS_REASON_OWNER_MISMATCH,
    PROCESS_REASON_PARENT_MISMATCH,
    PROCESS_REASON_PERMISSION_DENIED,
    PROCESS_REASON_PID_REUSED,
    PROCESS_REASON_PROVIDER_UNAVAILABLE,
    PROCESS_REASON_RECONCILIATION_DEFERRED,
    PROCESS_REASON_RECONCILIATION_REQUIRED,
    PROCESS_REASON_REGISTRY_CORRUPT,
    PROCESS_REASON_REGISTRY_UNAVAILABLE,
    PROCESS_REASON_STALE,
    PROCESS_REASON_TERMINATE_DUE,
    PROCESS_REASON_TREE_INCOMPLETE,
    PROCESS_STATE_EXITED,
    PROCESS_STATE_IDENTITY_MISMATCH,
    PROCESS_STATE_MISSING,
    PROCESS_STATE_ORPHANED,
    PROCESS_STATE_REGISTERED,
    PROCESS_STATE_RUNNING,
    PROCESS_STATE_STALE,
    PROCESS_STATE_UNKNOWN,
    ProcessIdentity,
    ProcessSupervisorObservation,
    now_iso,
)
from services.process_provider import ProcessProvider
from services.process_provider import SimulatedProcessCommandExecutor
from services.process_provider import ProcessSnapshot
from services.resource_policy_service import ResourcePolicyService


PROCESS_REGISTRY_SCHEMA_VERSION = 1


def command_fingerprint(
    command,
):

    if isinstance(
        command,
        (list, tuple),
    ):

        command = "\x00".join(
            str(
                item
            )
            for item in command
        )

    payload = str(
        command
        or ""
    )

    return hashlib.sha256(
        payload.encode(
            "utf-8"
        )
    ).hexdigest()


class ProcessSupervisor:

    def __init__(
        self,
        root="workspace/jobs/processes",
        policy_service=None,
        provider=None,
        executor=None,
        clock=None,
    ):

        self.root = Path(
            root
        )

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.file = self.root / "process_registry.json"

        self.policy_service = (
            policy_service
            or ResourcePolicyService()
        )

        self.provider = provider or ProcessProvider()

        self.executor = (
            executor
            or SimulatedProcessCommandExecutor()
        )

        self.clock = clock or datetime.now

        self.last_reason_codes = []

        self.last_audit = []

    def now(
        self,
    ):

        value = self.clock()

        if isinstance(
            value,
            datetime,
        ):

            return value

        return datetime.fromtimestamp(
            float(
                value
            )
        )

    def resolve_policy(
        self,
    ):

        if hasattr(
            self.policy_service,
            "resolve",
        ):

            return self.policy_service.resolve(
                migrate=False
            )

        return self.policy_service.load()

    def supervisor_mode(
        self,
        policy=None,
    ):

        policy = policy or self.resolve_policy()

        mode = getattr(
            policy,
            "feature_modes",
            {},
        ).get(
            "process_supervisor_mode",
            FEATURE_MODE_MONITOR_ONLY,
        )

        if mode == FEATURE_MODE_ENFORCED:

            return FEATURE_MODE_ENFORCE

        return mode

    def mode_reason(
        self,
        mode,
    ):

        if mode == FEATURE_MODE_DISABLED:

            return PROCESS_REASON_MODE_DISABLED

        if mode == FEATURE_MODE_ENFORCE:

            return PROCESS_REASON_MODE_ENFORCE

        return PROCESS_REASON_MODE_MONITOR_ONLY

    def register(
        self,
        pid,
        parent_pid=0,
        job_id="",
        lease_id="",
        owner_id="",
        executable="",
        command=None,
        command_hash="",
        process_start_time="",
        workload_class="light",
        resource_kind="cpu",
        process_group_id="",
        session_id="",
        metadata=None,
        provenance=None,
    ):

        policy = self.resolve_policy()
        mode = self.supervisor_mode(
            policy
        )

        identity = ProcessIdentity(
            process_id=f"proc_{uuid4().hex[:12]}",
            pid=int(
                pid
            ),
            parent_pid=int(
                parent_pid
                or 0
            ),
            job_id=job_id,
            lease_id=lease_id,
            owner_id=owner_id,
            executable=executable,
            command_fingerprint=command_hash
            or command_fingerprint(
                command
            ),
            process_start_time=process_start_time,
            registered_at=self.now().isoformat(),
            last_observed_at=self.now().isoformat(),
            workload_class=workload_class,
            resource_kind=resource_kind,
            process_group_id=process_group_id,
            session_id=session_id,
            policy_fingerprint=getattr(
                policy,
                "fingerprint",
                "",
            ),
            metadata=metadata
            or {},
            provenance=provenance
            or {
                "source": "process_supervisor",
                "mode": mode,
            },
            schema_version=PROCESS_REGISTRY_SCHEMA_VERSION,
        )

        records, error = self.load_registry_checked()

        if error:

            self.last_reason_codes = [
                error,
                PROCESS_REASON_RECONCILIATION_DEFERRED,
            ]

            return None

        records.append(
            identity
        )

        self.save_registry(
            records
        )

        self.last_reason_codes = [
            self.mode_reason(
                mode
            )
        ]

        return identity

    def load_registry(
        self,
    ):

        records, error = self.load_registry_checked()

        if error:

            return []

        return records

    def load_registry_checked(
        self,
    ):

        if not self.file.exists():

            return [], ""

        try:

            data = json.loads(
                self.file.read_text(
                    encoding="utf-8"
                )
            )

        except PermissionError:

            return [], PROCESS_REASON_REGISTRY_UNAVAILABLE

        except Exception:

            return [], PROCESS_REASON_REGISTRY_CORRUPT

        if not isinstance(
            data,
            dict,
        ):

            return [], PROCESS_REASON_REGISTRY_CORRUPT

        try:

            records = [
                ProcessIdentity.from_dict(
                    item
                )
                for item in data.get(
                    "processes",
                    []
                )
            ]

        except Exception:

            return [], PROCESS_REASON_REGISTRY_CORRUPT

        return records, ""

    def save_registry(
        self,
        records,
    ):

        data = {
            "schema_version": PROCESS_REGISTRY_SCHEMA_VERSION,
            "updated_at": now_iso(),
            "processes": [
                ProcessIdentity.from_dict(
                    record
                ).to_dict()
                for record in records
            ],
        }

        temp = self.file.with_name(
            f"{self.file.name}.{uuid4().hex}.tmp"
        )

        try:

            temp.write_text(
                json.dumps(
                    data,
                    indent=4,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            os.replace(
                temp,
                self.file,
            )

        finally:

            if temp.exists():

                try:

                    temp.unlink()

                except Exception:

                    pass

    def observe_all(
        self,
        jobs_by_id=None,
        leases_by_id=None,
    ):

        records, error = self.load_registry_checked()

        if error:

            return [
                self.observation(
                    reason_codes=[
                        error,
                        PROCESS_REASON_RECONCILIATION_DEFERRED,
                    ],
                    shadow_action=PROCESS_ACTION_WOULD_DEFER,
                    actual_state=PROCESS_STATE_UNKNOWN,
                    shadow_state=PROCESS_STATE_UNKNOWN,
                    would_reconcile=True,
                ).to_dict()
            ]

        seen = set()
        observations = []

        for record in records:

            identity = ProcessIdentity.from_dict(
                record
            )

            duplicate = identity.process_id in seen

            seen.add(
                identity.process_id
            )

            observations.append(
                self.observe(
                    identity,
                    jobs_by_id=jobs_by_id,
                    leases_by_id=leases_by_id,
                    duplicate_record=duplicate,
                ).to_dict()
            )

        return observations

    def observe(
        self,
        identity,
        jobs_by_id=None,
        leases_by_id=None,
        duplicate_record=False,
    ):

        identity = ProcessIdentity.from_dict(
            identity
        )

        policy = self.resolve_policy()
        mode = self.supervisor_mode(
            policy
        )
        reason_codes = [
            self.mode_reason(
                mode
            )
        ]

        if mode == FEATURE_MODE_DISABLED:

            return self.observation(
                identity=identity,
                reason_codes=reason_codes,
                shadow_action=PROCESS_ACTION_WOULD_SKIP,
                actual_state=PROCESS_STATE_UNKNOWN,
                shadow_state=PROCESS_STATE_UNKNOWN,
                policy=policy,
            )

        snapshot = self.provider.get_process(
            identity.pid
        )

        tree = self.discover_tree(
            identity.pid
        )

        actual_state = PROCESS_STATE_RUNNING
        shadow_state = PROCESS_STATE_RUNNING
        shadow_action = PROCESS_ACTION_WOULD_OBSERVE
        identity_valid = True
        owner_valid = True
        is_alive = True
        is_orphan = False
        is_stale = False
        would_reconcile = False

        if snapshot is None:

            actual_state = PROCESS_STATE_MISSING
            shadow_state = PROCESS_STATE_MISSING
            shadow_action = PROCESS_ACTION_WOULD_MARK_EXITED
            is_alive = False
            identity_valid = False
            reason_codes.append(
                PROCESS_REASON_MISSING
            )

        else:

            snapshot = ProcessSnapshot.from_dict(
                snapshot
            )

            if snapshot.provider_unavailable:

                actual_state = PROCESS_STATE_UNKNOWN
                shadow_state = PROCESS_STATE_UNKNOWN
                shadow_action = PROCESS_ACTION_WOULD_DEFER
                is_alive = False
                identity_valid = False
                would_reconcile = True
                reason_codes.extend(
                    [
                        PROCESS_REASON_PROVIDER_UNAVAILABLE,
                        PROCESS_REASON_RECONCILIATION_DEFERRED,
                    ]
                )

            elif snapshot.permission_denied:

                actual_state = PROCESS_STATE_UNKNOWN
                shadow_state = PROCESS_STATE_UNKNOWN
                shadow_action = PROCESS_ACTION_WOULD_DEFER
                is_alive = False
                identity_valid = False
                would_reconcile = True
                reason_codes.extend(
                    [
                        PROCESS_REASON_PERMISSION_DENIED,
                        PROCESS_REASON_RECONCILIATION_DEFERRED,
                    ]
                )

            elif not snapshot.alive:

                actual_state = PROCESS_STATE_EXITED
                shadow_state = PROCESS_STATE_EXITED
                shadow_action = PROCESS_ACTION_WOULD_MARK_EXITED
                is_alive = False
                reason_codes.append(
                    PROCESS_REASON_EXITED
                )

            else:

                mismatch_codes = self.identity_mismatch_codes(
                    identity,
                    snapshot,
                )

                if mismatch_codes:

                    actual_state = PROCESS_STATE_IDENTITY_MISMATCH
                    shadow_state = PROCESS_STATE_IDENTITY_MISMATCH
                    shadow_action = (
                        PROCESS_ACTION_WOULD_BLOCK_IDENTITY_MISMATCH
                    )
                    identity_valid = False
                    would_reconcile = True
                    reason_codes.extend(
                        mismatch_codes
                    )

        if duplicate_record:

            reason_codes.append(
                PROCESS_REASON_RECONCILIATION_REQUIRED
            )

        jobs_by_id = jobs_by_id or {}
        leases_by_id = leases_by_id or {}

        if identity.job_id and identity.job_id not in jobs_by_id:

            is_orphan = True
            would_reconcile = True
            reason_codes.extend(
                [
                    PROCESS_REASON_JOB_MISSING,
                    PROCESS_REASON_ORPHANED,
                    PROCESS_REASON_RECONCILIATION_REQUIRED,
                ]
            )

            if shadow_action == PROCESS_ACTION_WOULD_OBSERVE:

                shadow_action = PROCESS_ACTION_WOULD_MARK_ORPHANED
                shadow_state = PROCESS_STATE_ORPHANED

        if identity.lease_id:

            lease = leases_by_id.get(
                identity.lease_id
            )

            if lease is None:

                reason_codes.extend(
                    [
                        PROCESS_REASON_LEASE_MISSING,
                        PROCESS_REASON_RECONCILIATION_REQUIRED,
                    ]
                )
                would_reconcile = True

            elif (
                getattr(
                    lease,
                    "owner",
                    "",
                )
                and identity.owner_id
                and getattr(
                    lease,
                    "owner",
                    "",
                )
                != identity.owner_id
            ):

                owner_valid = False
                reason_codes.extend(
                    [
                        PROCESS_REASON_OWNER_MISMATCH,
                        PROCESS_REASON_RECONCILIATION_REQUIRED,
                    ]
                )
                would_reconcile = True

            elif getattr(
                lease,
                "status",
                "",
            ) in (
                "expired",
                "stale",
                "released",
            ):

                reason_codes.extend(
                    [
                        PROCESS_REASON_LEASE_EXPIRED,
                        PROCESS_REASON_RECONCILIATION_REQUIRED,
                    ]
                )
                would_reconcile = True

        if not tree.get(
            "complete",
            False,
        ):

            reason_codes.append(
                PROCESS_REASON_TREE_INCOMPLETE
            )

        if self.is_stale(
            identity,
            policy,
        ):

            is_stale = True
            shadow_state = PROCESS_STATE_STALE
            if shadow_action == PROCESS_ACTION_WOULD_OBSERVE:

                shadow_action = PROCESS_ACTION_WOULD_RECONCILE

            reason_codes.extend(
                [
                    PROCESS_REASON_STALE,
                    PROCESS_REASON_RECONCILIATION_REQUIRED,
                ]
            )
            would_reconcile = True

        return self.observation(
            identity=identity,
            reason_codes=reason_codes,
            shadow_action=shadow_action,
            actual_state=actual_state,
            shadow_state=shadow_state,
            policy=policy,
            root_pid=identity.pid,
            descendant_pids=tree.get(
                "descendant_pids",
                []
            ),
            process_tree_complete=tree.get(
                "complete",
                False,
            ),
            identity_valid=identity_valid,
            owner_valid=owner_valid,
            is_alive=is_alive,
            is_orphan=is_orphan,
            is_stale=is_stale,
            would_reconcile=would_reconcile,
        )

    def identity_mismatch_codes(
        self,
        identity,
        snapshot,
    ):

        codes = []

        if not identity.process_start_time:

            codes.append(
                PROCESS_REASON_IDENTITY_UNKNOWN
            )

        elif (
            snapshot.process_start_time
            and identity.process_start_time
            != snapshot.process_start_time
        ):

            codes.extend(
                [
                    PROCESS_REASON_PID_REUSED,
                    PROCESS_REASON_IDENTITY_MISMATCH,
                ]
            )

        if (
            identity.parent_pid
            and snapshot.parent_pid
            and int(
                identity.parent_pid
            )
            != int(
                snapshot.parent_pid
            )
        ):

            codes.append(
                PROCESS_REASON_PARENT_MISMATCH
            )

        if (
            identity.executable
            and snapshot.executable
            and identity.executable != snapshot.executable
        ):

            codes.append(
                PROCESS_REASON_EXECUTABLE_MISMATCH
            )

        if (
            identity.command_fingerprint
            and snapshot.command_fingerprint
            and identity.command_fingerprint
            != snapshot.command_fingerprint
        ):

            codes.append(
                PROCESS_REASON_COMMAND_MISMATCH
            )

        if codes:

            codes.append(
                PROCESS_REASON_RECONCILIATION_REQUIRED
            )

        return sorted(
            set(
                codes
            )
        )

    def discover_tree(
        self,
        root_pid,
    ):

        snapshots = self.provider.list_processes()

        if (
            len(
                snapshots
            ) == 1
            and ProcessSnapshot.from_dict(
                snapshots[0]
            ).provider_unavailable
        ):

            return {
                "root_pid": int(
                    root_pid
                ),
                "descendant_pids": [],
                "pids": [
                    int(
                        root_pid
                    )
                ],
                "complete": False,
            }

        by_parent = {}
        by_pid = {}
        complete = True

        for item in snapshots:

            try:

                snapshot = ProcessSnapshot.from_dict(
                    item
                )

            except Exception:

                complete = False
                continue

            by_pid[snapshot.pid] = snapshot
            by_parent.setdefault(
                snapshot.parent_pid,
                [],
            ).append(
                snapshot.pid
            )

        if int(
            root_pid
        ) not in by_pid:

            complete = False

        descendants = []
        queue = sorted(
            by_parent.get(
                int(
                    root_pid
                ),
                [],
            )
        )
        visited = {
            int(
                root_pid
            )
        }

        while queue:

            pid = queue.pop(
                0
            )

            if pid in visited:

                complete = False
                continue

            visited.add(
                pid
            )
            descendants.append(
                pid
            )

            for child in sorted(
                by_parent.get(
                    pid,
                    [],
                )
            ):

                queue.append(
                    child
                )

        return {
            "root_pid": int(
                root_pid
            ),
            "descendant_pids": descendants,
            "pids": [
                int(
                    root_pid
                )
            ]
            + descendants,
            "complete": complete,
        }

    def is_stale(
        self,
        identity,
        policy,
    ):

        if not identity.last_observed_at:

            return False

        try:

            observed = datetime.fromisoformat(
                identity.last_observed_at
            )

        except Exception:

            return True

        ttl = float(
            getattr(
                policy,
                "process_observation_ttl_seconds",
                5.0,
            )
        )

        return (
            self.now()
            - observed
        ).total_seconds() > ttl

    def shutdown_plan(
        self,
        identity,
        stage="graceful",
        jobs_by_id=None,
        leases_by_id=None,
    ):

        observation = self.observe(
            identity,
            jobs_by_id=jobs_by_id,
            leases_by_id=leases_by_id,
        )

        reason_codes = list(
            observation.reason_codes
        )
        action = PROCESS_ACTION_WOULD_DEFER

        if not observation.identity_valid:

            reason_codes.append(
                PROCESS_REASON_RECONCILIATION_DEFERRED
            )

        elif stage == "graceful":

            action = PROCESS_ACTION_WOULD_REQUEST_GRACEFUL_STOP
            reason_codes.append(
                PROCESS_REASON_GRACEFUL_STOP_DUE
            )

        elif stage == "terminate":

            action = PROCESS_ACTION_WOULD_TERMINATE
            reason_codes.append(
                PROCESS_REASON_TERMINATE_DUE
            )

        elif stage == "kill_tree":

            if observation.process_tree_complete:

                action = PROCESS_ACTION_WOULD_KILL_TREE
                reason_codes.append(
                    PROCESS_REASON_KILL_TREE_DUE
                )

            else:

                reason_codes.extend(
                    [
                        PROCESS_REASON_TREE_INCOMPLETE,
                        PROCESS_REASON_RECONCILIATION_DEFERRED,
                    ]
                )

        return self.observation(
            identity=ProcessIdentity.from_dict(
                identity
            ),
            reason_codes=reason_codes,
            shadow_action=action,
            actual_state=observation.actual_process_state,
            shadow_state=observation.shadow_process_state,
            policy=self.resolve_policy(),
            root_pid=observation.root_pid,
            descendant_pids=observation.descendant_pids,
            process_tree_complete=observation.process_tree_complete,
            identity_valid=observation.identity_valid,
            owner_valid=observation.owner_valid,
            is_alive=observation.is_alive,
            is_orphan=observation.is_orphan,
            is_stale=observation.is_stale,
            would_request_graceful_stop=(
                action == PROCESS_ACTION_WOULD_REQUEST_GRACEFUL_STOP
            ),
            would_terminate=action == PROCESS_ACTION_WOULD_TERMINATE,
            would_kill_tree=action == PROCESS_ACTION_WOULD_KILL_TREE,
            would_reconcile=observation.would_reconcile
            or action == PROCESS_ACTION_WOULD_DEFER,
            audit=[
                {
                    "simulated": True,
                    "stage": stage,
                    "action": action,
                    "created_at": self.now().isoformat(),
                }
            ],
        )

    def observation(
        self,
        reason_codes,
        shadow_action,
        actual_state,
        shadow_state,
        identity=None,
        policy=None,
        root_pid=0,
        descendant_pids=None,
        process_tree_complete=False,
        identity_valid=False,
        owner_valid=False,
        is_alive=False,
        is_orphan=False,
        is_stale=False,
        would_request_graceful_stop=False,
        would_terminate=False,
        would_kill_tree=False,
        would_reconcile=False,
        audit=None,
    ):

        identity = ProcessIdentity.from_dict(
            identity
            or {}
        )
        policy = policy or self.resolve_policy()
        mode = self.supervisor_mode(
            policy
        )

        return ProcessSupervisorObservation(
            actual_process_state=actual_state,
            shadow_process_state=shadow_state,
            shadow_action=shadow_action,
            reason_codes=sorted(
                set(
                    reason_codes
                )
            ),
            process_identity=identity.to_dict(),
            job_id=identity.job_id,
            lease_id=identity.lease_id,
            root_pid=int(
                root_pid
                or identity.pid
                or 0
            ),
            descendant_pids=sorted(
                set(
                    descendant_pids
                    or []
                )
            ),
            process_tree_complete=process_tree_complete,
            identity_valid=identity_valid,
            owner_valid=owner_valid,
            is_alive=is_alive,
            is_orphan=is_orphan,
            is_stale=is_stale,
            would_request_graceful_stop=would_request_graceful_stop,
            would_terminate=would_terminate,
            would_kill_tree=would_kill_tree,
            would_reconcile=would_reconcile,
            policy_fingerprint=getattr(
                policy,
                "fingerprint",
                "",
            ),
            observed_at=self.now().isoformat(),
            monitor_only=mode != FEATURE_MODE_ENFORCE,
            audit=audit
            or [],
            schema_version=PROCESS_REGISTRY_SCHEMA_VERSION,
        )

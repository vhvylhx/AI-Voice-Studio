import json
import sys
from datetime import datetime
from datetime import timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(
    0,
    str(
        SRC
    ),
)

from models.resource_model import (
    DEFAULT_RESOURCE_FEATURE_MODES,
    FEATURE_MODE_DISABLED,
    FEATURE_MODE_ENFORCE,
    FEATURE_MODE_MONITOR_ONLY,
    PROCESS_ACTION_WOULD_BLOCK_IDENTITY_MISMATCH,
    PROCESS_ACTION_WOULD_DEFER,
    PROCESS_ACTION_WOULD_KILL_TREE,
    PROCESS_ACTION_WOULD_MARK_EXITED,
    PROCESS_ACTION_WOULD_MARK_ORPHANED,
    PROCESS_ACTION_WOULD_OBSERVE,
    PROCESS_ACTION_WOULD_REQUEST_GRACEFUL_STOP,
    PROCESS_ACTION_WOULD_SKIP,
    PROCESS_ACTION_WOULD_TERMINATE,
    PROCESS_REASON_COMMAND_MISMATCH,
    PROCESS_REASON_EXECUTABLE_MISMATCH,
    PROCESS_REASON_GRACEFUL_STOP_DUE,
    PROCESS_REASON_IDENTITY_UNKNOWN,
    PROCESS_REASON_JOB_MISSING,
    PROCESS_REASON_KILL_TREE_DUE,
    PROCESS_REASON_LEASE_EXPIRED,
    PROCESS_REASON_LEASE_MISSING,
    PROCESS_REASON_MODE_DISABLED,
    PROCESS_REASON_MODE_MONITOR_ONLY,
    PROCESS_REASON_ORPHANED,
    PROCESS_REASON_OWNER_MISMATCH,
    PROCESS_REASON_PARENT_MISMATCH,
    PROCESS_REASON_PERMISSION_DENIED,
    PROCESS_REASON_PID_REUSED,
    PROCESS_REASON_PROVIDER_UNAVAILABLE,
    PROCESS_REASON_RECONCILIATION_DEFERRED,
    PROCESS_REASON_REGISTRY_CORRUPT,
    PROCESS_REASON_STALE,
    PROCESS_REASON_TERMINATE_DUE,
    PROCESS_REASON_TREE_INCOMPLETE,
    PROCESS_STATE_IDENTITY_MISMATCH,
    PROCESS_STATE_ORPHANED,
    PROCESS_STATE_RUNNING,
    ProcessIdentity,
    ResourcePolicy,
    ResolvedResourcePolicy,
)
from services.process_provider import ProcessSnapshot
from services.process_provider import SimulatedProcessCommandExecutor
from services.process_provider import StaticProcessProvider
from services.process_supervisor import ProcessSupervisor
from services.process_supervisor import command_fingerprint


FIXED_NOW = datetime(
    2026,
    7,
    22,
    11,
    0,
    0,
)


class FakeClock:

    def __init__(
        self,
        now=FIXED_NOW,
    ):

        self.current = now

    def __call__(
        self,
    ):

        return self.current

    def advance(
        self,
        seconds,
    ):

        self.current = self.current + timedelta(
            seconds=seconds
        )


class FakePolicyService:

    def __init__(
        self,
        mode=FEATURE_MODE_MONITOR_ONLY,
    ):

        feature_modes = dict(
            DEFAULT_RESOURCE_FEATURE_MODES
        )
        feature_modes["process_supervisor_mode"] = mode

        self.policy = ResourcePolicy(
            schema_version=2,
            feature_modes=feature_modes,
            graceful_shutdown_timeout_seconds=20,
            terminate_timeout_seconds=5,
            kill_tree_timeout_seconds=5,
            process_identity_required=True,
            orphan_handling_mode="monitor_only",
            process_observation_ttl_seconds=5,
        )

    def load(
        self,
    ):

        return self.policy

    def resolve(
        self,
        migrate=False,
    ):

        return ResolvedResourcePolicy.from_policy(
            self.policy
        )


class FakeJob:

    def __init__(
        self,
        job_id,
        state="running",
    ):

        self.job_id = job_id
        self.state = state


class FakeLease:

    def __init__(
        self,
        lease_id,
        owner="runner_1",
        status="active",
    ):

        self.lease_id = lease_id
        self.owner = owner
        self.status = status


def snapshot(
    pid=100,
    parent_pid=10,
    executable="python.exe",
    command="demo --run",
    start_time="2026-07-22T10:59:00",
    alive=True,
):

    return ProcessSnapshot(
        pid=pid,
        parent_pid=parent_pid,
        executable=executable,
        command_fingerprint=command_fingerprint(
            command
        ),
        process_start_time=start_time,
        alive=alive,
    )


def make_supervisor(
    tmp_path,
    mode=FEATURE_MODE_MONITOR_ONLY,
    snapshots=None,
    provider=None,
    clock=None,
):

    return ProcessSupervisor(
        root=tmp_path / "processes",
        policy_service=FakePolicyService(
            mode=mode
        ),
        provider=provider
        or StaticProcessProvider(
            snapshots=[
                snapshot()
            ]
            if snapshots is None
            else snapshots
        ),
        executor=SimulatedProcessCommandExecutor(),
        clock=clock or FakeClock(),
    )


def make_identity(
    **overrides,
):

    data = {
        "process_id": "proc_1",
        "pid": 100,
        "parent_pid": 10,
        "job_id": "job_1",
        "lease_id": "lease_1",
        "owner_id": "runner_1",
        "executable": "python.exe",
        "command_fingerprint": command_fingerprint(
            "demo --run"
        ),
        "process_start_time": "2026-07-22T10:59:00",
        "registered_at": FIXED_NOW.isoformat(),
        "last_observed_at": FIXED_NOW.isoformat(),
        "workload_class": "gpu_inference",
        "resource_kind": "gpu",
    }

    data.update(
        overrides
    )

    return ProcessIdentity(
        **data
    )


def test_policy_defaults_are_monitor_only_and_additive():

    resolved = FakePolicyService().resolve()

    assert resolved.feature_modes["process_supervisor_mode"] == (
        FEATURE_MODE_MONITOR_ONLY
    )
    assert resolved.graceful_shutdown_timeout_seconds == 20
    assert resolved.terminate_timeout_seconds == 5
    assert resolved.kill_tree_timeout_seconds == 5
    assert resolved.process_identity_required is True
    assert resolved.orphan_handling_mode == "monitor_only"


def test_register_persists_identity_without_pid_only_identity(tmp_path):

    supervisor = make_supervisor(
        tmp_path
    )

    identity = supervisor.register(
        pid=100,
        parent_pid=10,
        job_id="job_1",
        lease_id="lease_1",
        owner_id="runner_1",
        executable="python.exe",
        command=[
            "demo",
            "--run",
        ],
        process_start_time="2026-07-22T10:59:00",
        workload_class="gpu_inference",
        resource_kind="gpu",
    )

    loaded = supervisor.load_registry()[0]

    assert identity.process_id == loaded.process_id
    assert loaded.pid == 100
    assert loaded.process_start_time
    assert loaded.command_fingerprint
    assert loaded.policy_fingerprint


def test_observe_valid_identity_running_and_tree_sorted(tmp_path):

    supervisor = make_supervisor(
        tmp_path,
        snapshots=[
            snapshot(),
            snapshot(
                pid=102,
                parent_pid=101,
            ),
            snapshot(
                pid=101,
                parent_pid=100,
            ),
        ],
    )

    observation = supervisor.observe(
        make_identity(),
        jobs_by_id={
            "job_1": FakeJob(
                "job_1"
            )
        },
        leases_by_id={
            "lease_1": FakeLease(
                "lease_1"
            )
        },
    )

    assert observation.actual_process_state == PROCESS_STATE_RUNNING
    assert observation.shadow_action == PROCESS_ACTION_WOULD_OBSERVE
    assert observation.identity_valid is True
    assert observation.descendant_pids == [
        101,
        102,
    ]


def test_pid_reuse_start_time_mismatch_blocks_identity(tmp_path):

    supervisor = make_supervisor(
        tmp_path,
        snapshots=[
            snapshot(
                start_time="2026-07-22T11:00:00"
            )
        ],
    )

    observation = supervisor.observe(
        make_identity(),
        jobs_by_id={
            "job_1": FakeJob(
                "job_1"
            )
        },
        leases_by_id={
            "lease_1": FakeLease(
                "lease_1"
            )
        },
    )

    assert observation.shadow_action == (
        PROCESS_ACTION_WOULD_BLOCK_IDENTITY_MISMATCH
    )
    assert observation.shadow_process_state == PROCESS_STATE_IDENTITY_MISMATCH
    assert PROCESS_REASON_PID_REUSED in observation.reason_codes


def test_command_executable_and_parent_mismatch_are_reported(tmp_path):

    supervisor = make_supervisor(
        tmp_path,
        snapshots=[
            snapshot(
                parent_pid=11,
                executable="other.exe",
                command="other --run",
            )
        ],
    )

    observation = supervisor.observe(
        make_identity(),
        jobs_by_id={
            "job_1": FakeJob(
                "job_1"
            )
        },
        leases_by_id={
            "lease_1": FakeLease(
                "lease_1"
            )
        },
    )

    assert PROCESS_REASON_PARENT_MISMATCH in observation.reason_codes
    assert PROCESS_REASON_EXECUTABLE_MISMATCH in observation.reason_codes
    assert PROCESS_REASON_COMMAND_MISMATCH in observation.reason_codes


def test_missing_process_permission_and_provider_unavailable_defer(tmp_path):

    missing = make_supervisor(
        tmp_path / "missing",
        snapshots=[],
    ).observe(
        make_identity(),
        jobs_by_id={
            "job_1": FakeJob(
                "job_1"
            )
        },
        leases_by_id={
            "lease_1": FakeLease(
                "lease_1"
            )
        },
    )

    permission = make_supervisor(
        tmp_path / "permission",
        provider=StaticProcessProvider(
            snapshots=[
                snapshot()
            ],
            permission_denied_pids=[
                100
            ],
        ),
    ).observe(
        make_identity(),
    )

    unavailable = make_supervisor(
        tmp_path / "unavailable",
        provider=StaticProcessProvider(
            unavailable=True
        ),
    ).observe(
        make_identity(),
    )

    assert missing.shadow_action == PROCESS_ACTION_WOULD_MARK_EXITED
    assert permission.shadow_action == PROCESS_ACTION_WOULD_DEFER
    assert PROCESS_REASON_PERMISSION_DENIED in permission.reason_codes
    assert unavailable.shadow_action == PROCESS_ACTION_WOULD_DEFER
    assert PROCESS_REASON_PROVIDER_UNAVAILABLE in unavailable.reason_codes


def test_unknown_identity_and_stale_observation_are_not_trusted(tmp_path):

    clock = FakeClock()
    clock.advance(
        10
    )
    supervisor = make_supervisor(
        tmp_path,
        clock=clock,
    )

    observation = supervisor.observe(
        make_identity(
            process_start_time="",
            last_observed_at=FIXED_NOW.isoformat(),
        ),
        jobs_by_id={
            "job_1": FakeJob(
                "job_1"
            )
        },
        leases_by_id={
            "lease_1": FakeLease(
                "lease_1"
            )
        },
    )

    assert PROCESS_REASON_IDENTITY_UNKNOWN in observation.reason_codes
    assert PROCESS_REASON_STALE in observation.reason_codes
    assert observation.is_stale is True


def test_orphan_and_lease_recovery_observations(tmp_path):

    supervisor = make_supervisor(
        tmp_path,
    )

    orphan = supervisor.observe(
        make_identity(),
        jobs_by_id={},
        leases_by_id={
            "lease_1": FakeLease(
                "lease_1"
            )
        },
    )

    lease_missing = supervisor.observe(
        make_identity(),
        jobs_by_id={
            "job_1": FakeJob(
                "job_1"
            )
        },
        leases_by_id={},
    )

    lease_expired = supervisor.observe(
        make_identity(),
        jobs_by_id={
            "job_1": FakeJob(
                "job_1"
            )
        },
        leases_by_id={
            "lease_1": FakeLease(
                "lease_1",
                status="expired",
            )
        },
    )

    assert orphan.shadow_action == PROCESS_ACTION_WOULD_MARK_ORPHANED
    assert orphan.shadow_process_state == PROCESS_STATE_ORPHANED
    assert PROCESS_REASON_JOB_MISSING in orphan.reason_codes
    assert PROCESS_REASON_ORPHANED in orphan.reason_codes
    assert PROCESS_REASON_LEASE_MISSING in lease_missing.reason_codes
    assert PROCESS_REASON_LEASE_EXPIRED in lease_expired.reason_codes


def test_owner_mismatch_from_lease_is_observed_not_destructive(tmp_path):

    supervisor = make_supervisor(
        tmp_path,
    )

    observation = supervisor.observe(
        make_identity(),
        jobs_by_id={
            "job_1": FakeJob(
                "job_1"
            )
        },
        leases_by_id={
            "lease_1": FakeLease(
                "lease_1",
                owner="runner_2",
            )
        },
    )

    assert PROCESS_REASON_OWNER_MISMATCH in observation.reason_codes
    assert observation.owner_valid is False


def test_process_tree_handles_incomplete_and_cycle_without_outside_pids(tmp_path):

    supervisor = make_supervisor(
        tmp_path,
        snapshots=[
            snapshot(
                pid=100,
                parent_pid=101,
            ),
            snapshot(
                pid=101,
                parent_pid=100,
            ),
            snapshot(
                pid=999,
                parent_pid=998,
            ),
        ],
    )

    tree = supervisor.discover_tree(
        100
    )

    assert tree["descendant_pids"] == [
        101
    ]
    assert 999 not in tree["pids"]
    assert tree["complete"] is False


def test_shutdown_plan_is_simulated_and_never_calls_executor_kill(tmp_path):

    executor = SimulatedProcessCommandExecutor()
    supervisor = ProcessSupervisor(
        root=tmp_path / "processes",
        policy_service=FakePolicyService(
            mode=FEATURE_MODE_ENFORCE
        ),
        provider=StaticProcessProvider(
            snapshots=[
                snapshot(),
                snapshot(
                    pid=101,
                    parent_pid=100,
                ),
            ]
        ),
        executor=executor,
        clock=FakeClock(),
    )

    graceful = supervisor.shutdown_plan(
        make_identity(),
        stage="graceful",
        jobs_by_id={
            "job_1": FakeJob(
                "job_1"
            )
        },
        leases_by_id={
            "lease_1": FakeLease(
                "lease_1"
            )
        },
    )

    terminate = supervisor.shutdown_plan(
        make_identity(),
        stage="terminate",
        jobs_by_id={
            "job_1": FakeJob(
                "job_1"
            )
        },
        leases_by_id={
            "lease_1": FakeLease(
                "lease_1"
            )
        },
    )

    kill_tree = supervisor.shutdown_plan(
        make_identity(),
        stage="kill_tree",
        jobs_by_id={
            "job_1": FakeJob(
                "job_1"
            )
        },
        leases_by_id={
            "lease_1": FakeLease(
                "lease_1"
            )
        },
    )

    assert graceful.shadow_action == (
        PROCESS_ACTION_WOULD_REQUEST_GRACEFUL_STOP
    )
    assert PROCESS_REASON_GRACEFUL_STOP_DUE in graceful.reason_codes
    assert terminate.shadow_action == PROCESS_ACTION_WOULD_TERMINATE
    assert PROCESS_REASON_TERMINATE_DUE in terminate.reason_codes
    assert kill_tree.shadow_action == PROCESS_ACTION_WOULD_KILL_TREE
    assert PROCESS_REASON_KILL_TREE_DUE in kill_tree.reason_codes
    assert executor.calls == []


def test_disabled_mode_skips_and_monitor_only_does_not_mutate_or_kill(tmp_path):

    disabled = make_supervisor(
        tmp_path / "disabled",
        mode=FEATURE_MODE_DISABLED,
    ).observe(
        make_identity()
    )

    monitor = make_supervisor(
        tmp_path / "monitor",
        mode=FEATURE_MODE_MONITOR_ONLY,
    )

    identity = monitor.register(
        pid=100,
        parent_pid=10,
        job_id="job_1",
        owner_id="runner_1",
        executable="python.exe",
        command="demo --run",
        process_start_time="2026-07-22T10:59:00",
    )
    before = monitor.file.read_text(
        encoding="utf-8"
    )
    observation = monitor.observe(
        identity,
        jobs_by_id={
            "job_1": FakeJob(
                "job_1"
            )
        },
    )
    after = monitor.file.read_text(
        encoding="utf-8"
    )

    assert disabled.shadow_action == PROCESS_ACTION_WOULD_SKIP
    assert PROCESS_REASON_MODE_DISABLED in disabled.reason_codes
    assert PROCESS_REASON_MODE_MONITOR_ONLY in observation.reason_codes
    assert before == after
    assert monitor.executor.calls == []


def test_corrupt_registry_is_preserved_and_reports_deferred(tmp_path):

    supervisor = make_supervisor(
        tmp_path,
    )
    corrupt = "{not-json"
    supervisor.file.write_text(
        corrupt,
        encoding="utf-8",
    )

    observations = supervisor.observe_all()

    assert PROCESS_REASON_REGISTRY_CORRUPT in observations[0][
        "reason_codes"
    ]
    assert PROCESS_REASON_RECONCILIATION_DEFERRED in observations[0][
        "reason_codes"
    ]
    assert supervisor.file.read_text(
        encoding="utf-8"
    ) == corrupt


def test_unknown_fields_legacy_record_and_atomic_temp_cleanup(tmp_path):

    supervisor = make_supervisor(
        tmp_path,
    )

    identity = make_identity().to_dict()
    identity.pop(
        "process_start_time"
    )
    identity["unknown_field"] = "ignored"

    supervisor.file.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "unknown_top": True,
                "processes": [
                    identity
                ],
            }
        ),
        encoding="utf-8",
    )

    loaded = supervisor.load_registry()[0]

    supervisor.save_registry(
        [
            loaded
        ]
    )

    assert loaded.process_id == "proc_1"
    assert loaded.process_start_time == ""
    assert list(
        supervisor.root.glob(
            "*.tmp"
        )
    ) == []


def test_atomic_write_interruption_leaves_no_temp(tmp_path, monkeypatch):

    supervisor = make_supervisor(
        tmp_path,
    )

    def fail_replace(
        source,
        destination,
    ):

        raise OSError(
            "simulated_replace_failure"
        )

    monkeypatch.setattr(
        "services.process_supervisor.os.replace",
        fail_replace,
    )

    try:

        supervisor.save_registry(
            [
                make_identity()
            ]
        )

    except OSError:

        pass

    assert list(
        supervisor.root.glob(
            "*.tmp"
        )
    ) == []

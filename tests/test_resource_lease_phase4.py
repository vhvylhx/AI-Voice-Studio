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

from models.job_model import JobModel
from models.resource_model import (
    DEFAULT_RESOURCE_FEATURE_MODES,
    FEATURE_MODE_DISABLED,
    FEATURE_MODE_ENFORCE,
    FEATURE_MODE_MONITOR_ONLY,
    LEASE_REASON_ACQUIRED,
    LEASE_REASON_ACQUIRE_DENIED,
    LEASE_REASON_DUPLICATE,
    LEASE_REASON_EXPIRED,
    LEASE_REASON_OWNER_MISMATCH,
    LEASE_REASON_POLICY_MISMATCH,
    LEASE_REASON_PROCESS_IDENTITY_MISMATCH,
    LEASE_REASON_RELEASED,
    LEASE_REASON_RELEASE_DENIED,
    LEASE_REASON_RENEWED,
    LEASE_REASON_RENEW_DENIED,
    LEASE_REASON_STORE_CORRUPT,
    LEASE_STATUS_ACTIVE,
    LEASE_STATUS_EXPIRED,
    LEASE_STATUS_RELEASED,
    LEASE_STATUS_STALE,
    ResourceLease,
    ResourcePolicy,
    ResourceRequirement,
    ResolvedResourcePolicy,
)
from services.resource_lease_manager import ResourceLeaseManager
from services.resource_policy_service import ResourcePolicyService


FIXED_NOW = datetime(
    2026,
    7,
    22,
    10,
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
        mode=FEATURE_MODE_ENFORCE,
        max_concurrent_jobs=1,
        max_gpu_jobs=1,
        lease_ttl_seconds=60,
    ):

        feature_modes = dict(
            DEFAULT_RESOURCE_FEATURE_MODES
        )

        feature_modes["resource_lease_v2_mode"] = mode

        self.policy = ResourcePolicy(
            schema_version=2,
            max_concurrent_jobs=max_concurrent_jobs,
            max_gpu_jobs=max_gpu_jobs,
            lease_ttl_seconds=lease_ttl_seconds,
            lease_renew_interval_seconds=20,
            stale_lease_handling_mode="monitor_only",
            feature_modes=feature_modes,
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


def make_manager(
    tmp_path,
    mode=FEATURE_MODE_ENFORCE,
    max_concurrent_jobs=1,
    clock=None,
):

    return ResourceLeaseManager(
        root=tmp_path / "leases",
        policy_service=FakePolicyService(
            mode=mode,
            max_concurrent_jobs=max_concurrent_jobs,
        ),
        clock=clock or FakeClock(),
    )


def make_job(
    job_id="job_1",
    state="queued",
):

    return JobModel(
        job_id=job_id,
        job_type="demo_progress",
        state=state,
    )


def make_requirement(
    requires_gpu=False,
):

    return ResourceRequirement(
        requires_gpu=requires_gpu,
        gpu_count=1
        if requires_gpu
        else 0,
    )


def make_legacy_lease(
    lease_id="lease_1",
    job_id="job_1",
    owner="runner_1",
    expires_at=None,
    status=LEASE_STATUS_ACTIVE,
):

    return ResourceLease(
        lease_id=lease_id,
        job_id=job_id,
        job_type="demo_progress",
        owner=owner,
        resource_type="cpu",
        requirement=ResourceRequirement().to_dict(),
        acquired_at=FIXED_NOW.isoformat(),
        renewed_at=FIXED_NOW.isoformat(),
        expires_at=expires_at
        or (
            FIXED_NOW
            + timedelta(
                seconds=60
            )
        ).isoformat(),
        status=status,
    )


def test_monitor_only_and_disabled_keep_legacy_acquire_boundary(tmp_path):

    for mode in (
        FEATURE_MODE_MONITOR_ONLY,
        FEATURE_MODE_DISABLED,
    ):

        manager = make_manager(
            tmp_path / mode,
            mode=mode,
        )

        first, first_reason = manager.acquire(
            make_job(
                job_id=f"{mode}_job_1"
            ),
            make_requirement(),
            owner="runner_1",
        )

        second, second_reason = manager.acquire(
            make_job(
                job_id=f"{mode}_job_2"
            ),
            make_requirement(),
            owner="runner_1",
        )

        assert first is not None
        assert first_reason == ""
        assert second is None
        assert second_reason == "max_concurrent_jobs"


def test_enforce_acquire_is_idempotent_for_same_job_owner(tmp_path):

    manager = make_manager(
        tmp_path,
        max_concurrent_jobs=2,
    )

    first, first_reason = manager.acquire(
        make_job(),
        make_requirement(),
        owner="runner_1",
    )

    second, second_reason = manager.acquire(
        make_job(),
        make_requirement(),
        owner="runner_1",
    )

    assert first.lease_id == second.lease_id
    assert first_reason == LEASE_REASON_ACQUIRED
    assert second_reason == LEASE_REASON_ACQUIRED
    assert len(
        manager.load_all()
    ) == 1


def test_enforce_acquire_denies_duplicate_owner_mismatch(tmp_path):

    manager = make_manager(
        tmp_path,
        max_concurrent_jobs=2,
    )

    manager.acquire(
        make_job(),
        make_requirement(),
        owner="runner_1",
    )

    duplicate, reason = manager.acquire(
        make_job(),
        make_requirement(),
        owner="runner_2",
    )

    assert duplicate is None
    assert reason == LEASE_REASON_OWNER_MISMATCH


def test_enforce_acquire_denies_concurrency_without_counting_expired(tmp_path):

    manager = make_manager(
        tmp_path,
        max_concurrent_jobs=1,
    )

    expired = make_legacy_lease(
        expires_at=(
            FIXED_NOW
            - timedelta(
                seconds=1
            )
        ).isoformat()
    )

    manager.save_all(
        [
            expired
        ]
    )

    lease, reason = manager.acquire(
        make_job(
            job_id="job_2"
        ),
        make_requirement(),
        owner="runner_1",
    )

    denied, denied_reason = manager.acquire(
        make_job(
            job_id="job_3"
        ),
        make_requirement(),
        owner="runner_1",
    )

    assert lease is not None
    assert reason == LEASE_REASON_ACQUIRED
    assert denied is None
    assert denied_reason == LEASE_REASON_ACQUIRE_DENIED


def test_enforce_renew_requires_matching_job_and_owner(tmp_path):

    clock = FakeClock()
    manager = make_manager(
        tmp_path,
        clock=clock,
    )

    lease, _ = manager.acquire(
        make_job(),
        make_requirement(),
        owner="runner_1",
    )

    clock.advance(
        10
    )

    denied = manager.renew(
        lease.lease_id,
        job_id="job_1",
        owner="runner_2",
    )

    denied_reason_codes = list(
        manager.last_reason_codes
    )

    renewed = manager.renew(
        lease.lease_id,
        job_id="job_1",
        owner="runner_1",
    )

    assert denied is None
    assert LEASE_REASON_RENEW_DENIED in denied_reason_codes
    assert renewed is not None
    assert manager.last_reason_codes == [
        LEASE_REASON_RENEWED
    ]
    assert renewed.expires_at == (
        clock.current
        + timedelta(
            seconds=60
        )
    ).isoformat()


def test_enforce_renew_expired_lease_goes_to_reconciliation(tmp_path):

    clock = FakeClock()
    manager = make_manager(
        tmp_path,
        clock=clock,
    )

    lease, _ = manager.acquire(
        make_job(),
        make_requirement(),
        owner="runner_1",
    )

    clock.advance(
        61
    )

    renewed = manager.renew(
        lease.lease_id,
        job_id="job_1",
        owner="runner_1",
    )

    loaded = manager.load_all()[0]

    assert renewed is None
    assert loaded.status == LEASE_STATUS_EXPIRED
    assert LEASE_REASON_EXPIRED in manager.last_reason_codes


def test_enforce_release_requires_matching_job_and_owner_and_is_idempotent(tmp_path):

    manager = make_manager(
        tmp_path,
    )

    lease, _ = manager.acquire(
        make_job(),
        make_requirement(),
        owner="runner_1",
    )

    denied = manager.release(
        lease.lease_id,
        job_id="job_1",
        owner="runner_2",
    )

    released = manager.release(
        lease.lease_id,
        job_id="job_1",
        owner="runner_1",
    )

    released_again = manager.release(
        lease.lease_id,
        job_id="job_1",
        owner="runner_1",
    )

    assert denied is False
    assert released is True
    assert released_again is True
    assert manager.load_all()[0].status == LEASE_STATUS_RELEASED
    assert manager.last_reason_codes == [
        LEASE_REASON_RELEASED
    ]


def test_enforce_corrupt_store_is_fail_safe_and_preserved(tmp_path):

    manager = make_manager(
        tmp_path,
    )

    corrupt = "{not-json"

    manager.file.write_text(
        corrupt,
        encoding="utf-8",
    )

    lease, reason = manager.acquire(
        make_job(),
        make_requirement(),
        owner="runner_1",
    )

    released = manager.release(
        "lease_missing",
        job_id="job_1",
        owner="runner_1",
    )

    assert lease is None
    assert reason == LEASE_REASON_STORE_CORRUPT
    assert released is False
    assert manager.file.read_text(
        encoding="utf-8"
    ) == corrupt


def test_enforce_reconcile_marks_expired_and_duplicate_non_destructively(tmp_path):

    manager = make_manager(
        tmp_path,
        max_concurrent_jobs=3,
    )

    expired = make_legacy_lease(
        lease_id="lease_expired",
        job_id="job_expired",
        expires_at=(
            FIXED_NOW
            - timedelta(
                seconds=1
            )
        ).isoformat(),
    )

    first = make_legacy_lease(
        lease_id="lease_dup_1",
        job_id="job_dup",
    )

    duplicate = make_legacy_lease(
        lease_id="lease_dup_2",
        job_id="job_dup",
    )

    manager.save_all(
        [
            expired,
            first,
            duplicate,
        ]
    )

    observations = manager.reconcile(
        jobs_by_id={
            "job_expired": make_job(
                job_id="job_expired",
                state="running",
            ),
            "job_dup": make_job(
                job_id="job_dup",
                state="running",
            ),
        },
        owner_id="runner_1",
    )

    by_id = {
        lease.lease_id: lease.status
        for lease in manager.load_all()
    }

    assert by_id["lease_expired"] == LEASE_STATUS_EXPIRED
    assert by_id["lease_dup_1"] == LEASE_STATUS_ACTIVE
    assert by_id["lease_dup_2"] == LEASE_STATUS_STALE
    assert any(
        LEASE_REASON_DUPLICATE in item["reason_codes"]
        for item in observations
    )


def test_enforce_reconcile_reports_policy_and_process_identity_mismatch(tmp_path):

    manager = make_manager(
        tmp_path,
    )

    lease = make_legacy_lease(
        lease_id="lease_v2",
        job_id="job_1",
    )

    lease.schema_version = 2
    lease.policy_fingerprint = "old_policy"
    lease.process_identity = {
        "pid": 123,
        "create_time": 10,
    }

    manager.save_all(
        [
            lease
        ]
    )

    observations = manager.reconcile(
        jobs_by_id={
            "job_1": make_job(
                state="running",
            )
        },
        process_identity_by_lease_id={
            "lease_v2": {
                "pid": 123,
                "create_time": 11,
            }
        },
        owner_id="runner_1",
    )

    reason_codes = observations[0]["reason_codes"]

    assert LEASE_REASON_POLICY_MISMATCH in reason_codes
    assert LEASE_REASON_PROCESS_IDENTITY_MISMATCH in reason_codes
    assert manager.load_all()[0].status == LEASE_STATUS_ACTIVE


def test_atomic_write_schema_and_temp_cleanup(tmp_path):

    manager = make_manager(
        tmp_path,
    )

    manager.acquire(
        make_job(),
        make_requirement(),
        owner="runner_1",
    )

    data = json.loads(
        manager.file.read_text(
            encoding="utf-8"
        )
    )

    assert data["schema_version"] == 2
    assert list(
        manager.root.glob(
            "*.tmp"
        )
    ) == []


def test_policy_fallback_disables_enforce_mode():

    policy = ResourcePolicy(
        feature_modes=dict(
            DEFAULT_RESOURCE_FEATURE_MODES
        )
        | {
            "resource_lease_v2_mode": FEATURE_MODE_ENFORCE
        }
    )

    fallback = ResourcePolicyService().fallback_policy(
        policy,
        source="test",
    )

    assert fallback.feature_modes["resource_lease_v2_mode"] == "disabled"


def test_release_missing_lease_is_denied_in_enforce(tmp_path):

    manager = make_manager(
        tmp_path,
    )

    assert manager.release(
        "missing",
        job_id="job_1",
        owner="runner_1",
    ) is False
    assert manager.last_reason_codes == [
        LEASE_REASON_RELEASE_DENIED
    ]

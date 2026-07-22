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
    LEASE_REASON_DUPLICATE,
    LEASE_REASON_EXPIRED,
    LEASE_REASON_JOB_MISSING,
    LEASE_REASON_MISSING,
    LEASE_REASON_OWNER_MISMATCH,
    LEASE_REASON_POLICY_MISMATCH,
    LEASE_REASON_PROCESS_IDENTITY_MISMATCH,
    LEASE_REASON_PROCESS_MISSING,
    LEASE_REASON_RECONCILIATION_REQUIRED,
    LEASE_REASON_RENEWAL_DUE,
    LEASE_REASON_SCHEMA_LEGACY,
    LEASE_REASON_STORE_CORRUPT,
    LEASE_SHADOW_ACTION_WOULD_ACQUIRE,
    LEASE_SHADOW_ACTION_WOULD_BLOCK_DUPLICATE,
    LEASE_SHADOW_ACTION_WOULD_EXPIRE,
    LEASE_SHADOW_ACTION_WOULD_MARK_STALE,
    LEASE_SHADOW_ACTION_WOULD_RECONCILE,
    LEASE_SHADOW_ACTION_WOULD_RELEASE,
    LEASE_SHADOW_ACTION_WOULD_RENEW,
    LEASE_SHADOW_ACTION_WOULD_SKIP,
    LEASE_STATUS_ACTIVE,
    ResourceLease,
    ResourceLeaseV2,
    ResourcePolicy,
    ResourceRequirement,
    ResolvedResourcePolicy,
)
from services.resource_lease_manager import ResourceLeaseManager
from services.resource_lease_shadow_evaluator import ResourceLeaseShadowEvaluator


FIXED_NOW = datetime(
    2026,
    7,
    22,
    9,
    30,
    0,
)


class FakePolicyService:

    def __init__(
        self,
        policy=None,
    ):

        self.policy = policy or ResourcePolicy(
            schema_version=2,
            max_concurrent_jobs=1,
            max_gpu_jobs=1,
            lease_ttl_seconds=300,
            lease_renew_interval_seconds=120,
            stale_lease_handling_mode="monitor_only",
            feature_modes=dict(
                DEFAULT_RESOURCE_FEATURE_MODES
            ),
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


def iso_after(
    seconds,
):

    return (
        FIXED_NOW
        + timedelta(
            seconds=seconds
        )
    ).isoformat()


def iso_before(
    seconds,
):

    return (
        FIXED_NOW
        - timedelta(
            seconds=seconds
        )
    ).isoformat()


def make_lease(
    lease_id="lease_1",
    job_id="job_1",
    owner="runner_1",
    resource_type="cpu",
    acquired_seconds_ago=60,
    renewed_seconds_ago=60,
    expires_seconds_from_now=240,
    status=LEASE_STATUS_ACTIVE,
    requirement=None,
):

    return ResourceLease(
        lease_id=lease_id,
        job_id=job_id,
        job_type="demo_progress",
        owner=owner,
        resource_type=resource_type,
        requirement=(
            requirement
            or ResourceRequirement().to_dict()
        ),
        acquired_at=iso_before(
            acquired_seconds_ago
        ),
        renewed_at=iso_before(
            renewed_seconds_ago
        ),
        expires_at=iso_after(
            expires_seconds_from_now
        ),
        status=status,
    )


def make_job(
    job_id="job_1",
    state="running",
):

    return JobModel(
        job_id=job_id,
        job_type="demo_progress",
        state=state,
    )


def make_evaluator():

    return ResourceLeaseShadowEvaluator(
        clock=lambda: FIXED_NOW
    )


def make_policy():

    return FakePolicyService().resolve(
        migrate=False
    )


def test_shadow_acquire_when_lease_missing():

    observation = make_evaluator().observe_missing(
        job_id="job_1",
        resource_kind="cpu",
        owner_id="runner_1",
        policy=make_policy(),
    )

    assert observation.shadow_action == LEASE_SHADOW_ACTION_WOULD_ACQUIRE
    assert observation.would_acquire is True
    assert LEASE_REASON_MISSING in observation.reason_codes


def test_shadow_skips_when_lease_active_and_renew_not_due():

    observation = make_evaluator().observe(
        make_lease(
            renewed_seconds_ago=30,
            expires_seconds_from_now=240,
        ),
        job=make_job(),
        owner_id="runner_1",
        policy=make_policy(),
    )

    assert observation.shadow_action == LEASE_SHADOW_ACTION_WOULD_SKIP
    assert observation.is_expired is False
    assert LEASE_REASON_SCHEMA_LEGACY in observation.reason_codes


def test_shadow_renew_when_interval_due():

    observation = make_evaluator().observe(
        make_lease(
            renewed_seconds_ago=121,
            expires_seconds_from_now=120,
        ),
        job=make_job(),
        owner_id="runner_1",
        policy=make_policy(),
    )

    assert observation.shadow_action == LEASE_SHADOW_ACTION_WOULD_RENEW
    assert observation.would_renew is True
    assert LEASE_REASON_RENEWAL_DUE in observation.reason_codes


def test_shadow_expire_when_ttl_elapsed_and_job_not_running():

    observation = make_evaluator().observe(
        make_lease(
            expires_seconds_from_now=-1,
        ),
        job=make_job(
            state="queued"
        ),
        owner_id="runner_1",
        policy=make_policy(),
    )

    assert observation.shadow_action == LEASE_SHADOW_ACTION_WOULD_EXPIRE
    assert observation.is_expired is True
    assert LEASE_REASON_EXPIRED in observation.reason_codes


def test_shadow_reconcile_when_expired_but_job_running():

    observation = make_evaluator().observe(
        make_lease(
            expires_seconds_from_now=-1,
        ),
        job=make_job(
            state="running"
        ),
        owner_id="runner_1",
        policy=make_policy(),
    )

    assert observation.shadow_action == LEASE_SHADOW_ACTION_WOULD_RECONCILE
    assert observation.would_reconcile is True
    assert LEASE_REASON_RECONCILIATION_REQUIRED in observation.reason_codes


def test_shadow_release_when_job_missing():

    observation = make_evaluator().observe(
        make_lease(),
        job=None,
        owner_id="runner_1",
        policy=make_policy(),
    )

    assert observation.shadow_action == LEASE_SHADOW_ACTION_WOULD_RELEASE
    assert observation.would_release is True
    assert observation.orphan_detected is True
    assert LEASE_REASON_JOB_MISSING in observation.reason_codes


def test_shadow_marks_stale_when_process_missing():

    observation = make_evaluator().observe(
        make_lease(),
        job=make_job(),
        owner_id="runner_1",
        process_alive=False,
        policy=make_policy(),
    )

    assert observation.shadow_action == LEASE_SHADOW_ACTION_WOULD_MARK_STALE
    assert observation.is_stale is True
    assert observation.would_release is True
    assert LEASE_REASON_PROCESS_MISSING in observation.reason_codes


def test_shadow_blocks_duplicate_same_job_and_resource():

    first = make_lease(
        lease_id="lease_1"
    )
    second = make_lease(
        lease_id="lease_2"
    )

    observation = make_evaluator().observe(
        first,
        all_leases=[
            first,
            second,
        ],
        job=make_job(),
        owner_id="runner_1",
        policy=make_policy(),
    )

    assert observation.shadow_action == (
        LEASE_SHADOW_ACTION_WOULD_BLOCK_DUPLICATE
    )
    assert observation.duplicate_detected is True
    assert LEASE_REASON_DUPLICATE in observation.reason_codes


def test_shadow_owner_mismatch_is_observation_only():

    observation = make_evaluator().observe(
        make_lease(
            owner="runner_a"
        ),
        job=make_job(),
        owner_id="runner_b",
        policy=make_policy(),
    )

    assert observation.shadow_action == LEASE_SHADOW_ACTION_WOULD_SKIP
    assert LEASE_REASON_OWNER_MISMATCH in observation.reason_codes


def test_shadow_process_identity_mismatch_reconciles():

    policy = make_policy()
    lease = ResourceLeaseV2(
        lease_id="lease_v2",
        job_id="job_1",
        resource_kind="cpu",
        owner_id="runner_1",
        runner_id="runner_1",
        acquired_at=iso_before(
            60
        ),
        last_renewed_at=iso_before(
            60
        ),
        expires_at=iso_after(
            240
        ),
        ttl_seconds=policy.lease_ttl_seconds,
        policy_fingerprint=policy.fingerprint,
        process_identity={
            "pid": 123,
            "create_time": 10,
        },
    )

    observation = make_evaluator().observe(
        lease,
        all_leases=[
            lease
        ],
        job=make_job(),
        owner_id="runner_1",
        actual_process_identity={
            "pid": 123,
            "create_time": 11,
        },
        policy=policy,
    )

    assert observation.shadow_action == LEASE_SHADOW_ACTION_WOULD_RECONCILE
    assert LEASE_REASON_PROCESS_IDENTITY_MISMATCH in observation.reason_codes


def test_shadow_policy_fingerprint_mismatch_is_reported():

    old_policy = make_policy()
    new_policy = FakePolicyService(
        ResourcePolicy(
            schema_version=2,
            reserve_ram_mb=12288,
            lease_ttl_seconds=300,
            lease_renew_interval_seconds=120,
        )
    ).resolve(
        migrate=False
    )
    lease = ResourceLeaseV2(
        lease_id="lease_v2",
        job_id="job_1",
        resource_kind="cpu",
        owner_id="runner_1",
        acquired_at=iso_before(
            60
        ),
        last_renewed_at=iso_before(
            60
        ),
        expires_at=iso_after(
            240
        ),
        policy_fingerprint=old_policy.fingerprint,
    )

    observation = make_evaluator().observe(
        lease,
        job=make_job(),
        owner_id="runner_1",
        policy=new_policy,
    )

    assert LEASE_REASON_POLICY_MISMATCH in observation.reason_codes


def test_manager_shadow_observation_for_job_does_not_mutate_actual_lease(tmp_path):

    manager = ResourceLeaseManager(
        root=tmp_path / "leases",
        policy_service=FakePolicyService(),
    )
    manager.shadow_evaluator = make_evaluator()

    original = make_lease(
        renewed_seconds_ago=121,
        expires_seconds_from_now=120,
    )

    manager.save_all(
        [
            original
        ]
    )

    before = manager.file.read_text(
        encoding="utf-8"
    )

    observation = manager.shadow_observation_for_job(
        make_job(),
        ResourceRequirement(),
        owner_id="runner_1",
    )

    after = manager.file.read_text(
        encoding="utf-8"
    )

    assert observation["shadow_action"] == LEASE_SHADOW_ACTION_WOULD_RENEW
    assert before == after


def test_manager_shadow_observations_do_not_cleanup_expired_legacy(tmp_path):

    manager = ResourceLeaseManager(
        root=tmp_path / "leases",
        policy_service=FakePolicyService(),
    )
    manager.shadow_evaluator = make_evaluator()

    expired = make_lease(
        expires_seconds_from_now=-1,
    )

    manager.save_all(
        [
            expired
        ]
    )

    observation = manager.shadow_observations(
        jobs_by_id={
            "job_1": make_job(
                state="queued"
            )
        },
        owner_id="runner_1",
    )[0]

    loaded = manager.load_all()[0]

    assert observation["shadow_action"] == LEASE_SHADOW_ACTION_WOULD_EXPIRE
    assert loaded.status == LEASE_STATUS_ACTIVE


def test_corrupt_lease_store_observation_does_not_overwrite_file(tmp_path):

    manager = ResourceLeaseManager(
        root=tmp_path / "leases",
        policy_service=FakePolicyService(),
    )
    manager.shadow_evaluator = make_evaluator()

    corrupt = "{not-json"

    manager.file.write_text(
        corrupt,
        encoding="utf-8",
    )

    observations = manager.shadow_observations()

    assert observations[0]["shadow_action"] == (
        LEASE_SHADOW_ACTION_WOULD_RECONCILE
    )
    assert LEASE_REASON_STORE_CORRUPT in observations[0]["reason_codes"]
    assert manager.file.read_text(
        encoding="utf-8"
    ) == corrupt


def test_unknown_fields_and_legacy_schema_load_without_crash(tmp_path):

    manager = ResourceLeaseManager(
        root=tmp_path / "leases",
        policy_service=FakePolicyService(),
    )
    manager.shadow_evaluator = make_evaluator()

    data = {
        "schema_version": 1,
        "unknown_top_level": True,
        "leases": [
            make_lease().to_dict()
            | {
                "unknown_field": "ignored"
            }
        ],
    }

    manager.file.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    observations = manager.shadow_observations(
        jobs_by_id={
            "job_1": make_job()
        },
        owner_id="runner_1",
    )

    assert observations[0]["lease_id"] == "lease_1"
    assert LEASE_REASON_SCHEMA_LEGACY in observations[0]["reason_codes"]


def test_monitor_only_reason_codes_are_deterministic():

    observation = make_evaluator().observe(
        make_lease(
            owner="runner_a",
            expires_seconds_from_now=-1,
        ),
        job=None,
        owner_id="runner_b",
        process_alive=False,
        policy=make_policy(),
    )

    assert observation.reason_codes == sorted(
        observation.reason_codes
    )
    assert observation.monitor_only is True


test_shadow_acquire_when_lease_missing()
test_shadow_skips_when_lease_active_and_renew_not_due()
test_shadow_renew_when_interval_due()

print("RESOURCE_LEASE_PHASE3_IMPORT_TEST_OK")

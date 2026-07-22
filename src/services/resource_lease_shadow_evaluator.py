from datetime import datetime

from models.resource_model import (
    FEATURE_MODE_ENFORCED,
    LEASE_REASON_DUPLICATE,
    LEASE_REASON_EXPIRED,
    LEASE_REASON_JOB_MISSING,
    LEASE_REASON_MISSING,
    LEASE_REASON_ORPHANED,
    LEASE_REASON_OWNER_MISMATCH,
    LEASE_REASON_POLICY_MISMATCH,
    LEASE_REASON_PROCESS_IDENTITY_MISMATCH,
    LEASE_REASON_PROCESS_MISSING,
    LEASE_REASON_RECONCILIATION_REQUIRED,
    LEASE_REASON_RELEASE_DUE,
    LEASE_REASON_RENEWAL_DUE,
    LEASE_REASON_SCHEMA_LEGACY,
    LEASE_REASON_STALE,
    LEASE_SHADOW_ACTION_WOULD_ACQUIRE,
    LEASE_SHADOW_ACTION_WOULD_BLOCK_DUPLICATE,
    LEASE_SHADOW_ACTION_WOULD_EXPIRE,
    LEASE_SHADOW_ACTION_WOULD_MARK_STALE,
    LEASE_SHADOW_ACTION_WOULD_RECONCILE,
    LEASE_SHADOW_ACTION_WOULD_RELEASE,
    LEASE_SHADOW_ACTION_WOULD_RENEW,
    LEASE_SHADOW_ACTION_WOULD_SKIP,
    LEASE_STATUS_ACTIVE,
    LEASE_STATUS_EXPIRED,
    LEASE_STATUS_ORPHANED,
    LEASE_STATUS_RELEASED,
    LEASE_STATUS_STALE,
    LEASE_STATUS_UNKNOWN,
    ResourceLeaseObservation,
    ResourceLeaseV2,
    ResourceRequirement,
)


class ResourceLeaseShadowEvaluator:

    def __init__(
        self,
        clock=None,
    ):

        self.clock = clock or datetime.now

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

    def observe_missing(
        self,
        job_id,
        resource_kind="cpu",
        owner_id="",
        policy=None,
    ):

        return self.observation(
            actual_lease_state=LEASE_STATUS_UNKNOWN,
            shadow_lease_state=LEASE_STATUS_ACTIVE,
            shadow_action=LEASE_SHADOW_ACTION_WOULD_ACQUIRE,
            reason_codes=[
                LEASE_REASON_MISSING
            ],
            job_id=job_id,
            resource_kind=resource_kind,
            owner_id=owner_id,
            policy=policy,
            would_acquire=True,
        )

    def observe_store_error(
        self,
        reason_code,
        policy=None,
    ):

        return self.observation(
            actual_lease_state=LEASE_STATUS_UNKNOWN,
            shadow_lease_state=LEASE_STATUS_UNKNOWN,
            shadow_action=LEASE_SHADOW_ACTION_WOULD_RECONCILE,
            reason_codes=[
                reason_code,
                LEASE_REASON_RECONCILIATION_REQUIRED,
            ],
            policy=policy,
            would_reconcile=True,
        )

    def observe(
        self,
        lease,
        all_leases=None,
        job=None,
        owner_id="",
        process_alive=None,
        actual_process_identity=None,
        policy=None,
    ):

        policy = policy or object()
        lease_v2 = self.to_v2(
            lease,
            policy,
        )

        all_v2 = [
            self.to_v2(
                item,
                policy,
            )
            for item in all_leases
            or [
                lease
            ]
        ]

        now = self.now()
        expires_at = self.parse_time(
            lease_v2.expires_at
        )
        renewed_at = self.parse_time(
            lease_v2.last_renewed_at
        )

        reason_codes = []
        action = LEASE_SHADOW_ACTION_WOULD_SKIP
        shadow_state = lease_v2.status
        is_expired = False
        is_stale = False
        duplicate_detected = False
        orphan_detected = False

        if lease_v2.provenance.get(
            "schema_version"
        ) == 1:

            reason_codes.append(
                LEASE_REASON_SCHEMA_LEGACY
            )

        if (
            lease_v2.policy_fingerprint
            and getattr(
                policy,
                "fingerprint",
                "",
            )
            and lease_v2.policy_fingerprint
            != policy.fingerprint
        ):

            reason_codes.append(
                LEASE_REASON_POLICY_MISMATCH
            )

        if owner_id and lease_v2.owner_id and lease_v2.owner_id != owner_id:

            reason_codes.append(
                LEASE_REASON_OWNER_MISMATCH
            )

        duplicates = [
            item
            for item in all_v2
            if item.status == LEASE_STATUS_ACTIVE
            and item.job_id == lease_v2.job_id
            and item.resource_kind == lease_v2.resource_kind
        ]

        if len(
            duplicates
        ) > 1:

            duplicate_detected = True
            reason_codes.append(
                LEASE_REASON_DUPLICATE
            )
            action = LEASE_SHADOW_ACTION_WOULD_BLOCK_DUPLICATE

        job_exists = job is not None
        job_running = bool(
            getattr(
                job,
                "state",
                "",
            )
            == "running"
        )

        if not job_exists:

            orphan_detected = True
            reason_codes.extend(
                [
                    LEASE_REASON_JOB_MISSING,
                    LEASE_REASON_RELEASE_DUE,
                    LEASE_REASON_ORPHANED,
                ]
            )

            if action == LEASE_SHADOW_ACTION_WOULD_SKIP:

                action = LEASE_SHADOW_ACTION_WOULD_RELEASE
                shadow_state = LEASE_STATUS_ORPHANED

        if expires_at is None or expires_at <= now:

            is_expired = True
            shadow_state = LEASE_STATUS_EXPIRED
            reason_codes.append(
                LEASE_REASON_EXPIRED
            )

            if job_running:

                reason_codes.append(
                    LEASE_REASON_RECONCILIATION_REQUIRED
                )

                if action == LEASE_SHADOW_ACTION_WOULD_SKIP:

                    action = LEASE_SHADOW_ACTION_WOULD_RECONCILE

            elif action == LEASE_SHADOW_ACTION_WOULD_SKIP:

                action = LEASE_SHADOW_ACTION_WOULD_EXPIRE

        renew_due = self.renew_due(
            renewed_at,
            now,
            policy,
        )

        if (
            not is_expired
            and job_exists
            and renew_due
            and action == LEASE_SHADOW_ACTION_WOULD_SKIP
        ):

            reason_codes.append(
                LEASE_REASON_RENEWAL_DUE
            )
            action = LEASE_SHADOW_ACTION_WOULD_RENEW

        if process_alive is False:

            reason_codes.extend(
                [
                    LEASE_REASON_PROCESS_MISSING,
                    LEASE_REASON_RECONCILIATION_REQUIRED,
                ]
            )

            is_stale = True
            shadow_state = LEASE_STATUS_STALE

            if action in (
                LEASE_SHADOW_ACTION_WOULD_SKIP,
                LEASE_SHADOW_ACTION_WOULD_RELEASE,
            ):

                action = LEASE_SHADOW_ACTION_WOULD_MARK_STALE

        if (
            actual_process_identity is not None
            and lease_v2.process_identity
            and lease_v2.process_identity != actual_process_identity
        ):

            reason_codes.extend(
                [
                    LEASE_REASON_PROCESS_IDENTITY_MISMATCH,
                    LEASE_REASON_RECONCILIATION_REQUIRED,
                ]
            )

            if action == LEASE_SHADOW_ACTION_WOULD_SKIP:

                action = LEASE_SHADOW_ACTION_WOULD_RECONCILE

        if is_stale:

            reason_codes.append(
                LEASE_REASON_STALE
            )

        reason_codes = sorted(
            set(
                reason_codes
            )
        )

        return self.observation(
            actual_lease_state=lease_v2.status,
            shadow_lease_state=shadow_state,
            shadow_action=action,
            reason_codes=reason_codes,
            lease_id=lease_v2.lease_id,
            job_id=lease_v2.job_id,
            resource_kind=lease_v2.resource_kind,
            owner_id=lease_v2.owner_id,
            expires_at=lease_v2.expires_at,
            is_expired=is_expired,
            is_stale=is_stale,
            duplicate_detected=duplicate_detected,
            orphan_detected=orphan_detected,
            policy=policy,
            would_acquire=action == LEASE_SHADOW_ACTION_WOULD_ACQUIRE,
            would_renew=action == LEASE_SHADOW_ACTION_WOULD_RENEW,
            would_release=action
            in (
                LEASE_SHADOW_ACTION_WOULD_RELEASE,
                LEASE_SHADOW_ACTION_WOULD_MARK_STALE,
            ),
            would_reconcile=action == LEASE_SHADOW_ACTION_WOULD_RECONCILE,
        )

    def observation(
        self,
        actual_lease_state,
        shadow_lease_state,
        shadow_action,
        reason_codes,
        policy=None,
        lease_id="",
        job_id="",
        resource_kind="cpu",
        owner_id="",
        expires_at="",
        is_expired=False,
        is_stale=False,
        duplicate_detected=False,
        orphan_detected=False,
        would_acquire=False,
        would_renew=False,
        would_release=False,
        would_reconcile=False,
    ):

        feature_modes = getattr(
            policy,
            "feature_modes",
            {},
        )

        return ResourceLeaseObservation(
            actual_lease_state=actual_lease_state,
            shadow_lease_state=shadow_lease_state,
            shadow_action=shadow_action,
            reason_codes=sorted(
                set(
                    reason_codes
                )
            ),
            lease_id=lease_id,
            job_id=job_id,
            resource_kind=resource_kind,
            owner_id=owner_id,
            expires_at=expires_at,
            is_expired=is_expired,
            is_stale=is_stale,
            duplicate_detected=duplicate_detected,
            orphan_detected=orphan_detected,
            would_acquire=would_acquire,
            would_renew=would_renew,
            would_release=would_release,
            would_reconcile=would_reconcile,
            policy_fingerprint=getattr(
                policy,
                "fingerprint",
                "",
            ),
            observed_at=self.now().isoformat(),
            monitor_only=feature_modes.get(
                "resource_lease_v2_mode"
            )
            != FEATURE_MODE_ENFORCED,
        )

    def renew_due(
        self,
        renewed_at,
        now,
        policy,
    ):

        if renewed_at is None:

            return True

        interval = float(
            getattr(
                policy,
                "lease_renew_interval_seconds",
                120.0,
            )
        )

        return (
            now
            - renewed_at
        ).total_seconds() >= interval

    def parse_time(
        self,
        value,
    ):

        if not value:

            return None

        try:

            return datetime.fromisoformat(
                value
            )

        except Exception:

            return None

    def to_v2(
        self,
        lease,
        policy,
    ):

        if isinstance(
            lease,
            ResourceLeaseV2,
        ):

            return lease

        return ResourceLeaseV2.from_legacy(
            lease,
            policy=policy,
        )

import json
import os
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from uuid import uuid4

from models.resource_model import (
    FEATURE_MODE_ENFORCE,
    FEATURE_MODE_ENFORCED,
    LEASE_REASON_ACQUIRED,
    LEASE_REASON_ACQUIRE_CONFLICT,
    LEASE_REASON_ACQUIRE_DENIED,
    LEASE_REASON_DUPLICATE,
    LEASE_REASON_EXPIRED,
    LEASE_REASON_JOB_MISSING,
    LEASE_REASON_MODE_ENFORCE,
    LEASE_REASON_OWNER_MISMATCH,
    LEASE_REASON_POLICY_MISMATCH,
    LEASE_REASON_PROCESS_IDENTITY_MISMATCH,
    LEASE_REASON_PROCESS_MISSING,
    LEASE_REASON_RECONCILIATION_COMPLETED,
    LEASE_REASON_RECONCILIATION_DEFERRED,
    LEASE_REASON_RECONCILIATION_REQUIRED,
    LEASE_REASON_RELEASED,
    LEASE_REASON_RELEASE_DENIED,
    LEASE_REASON_RENEWED,
    LEASE_REASON_RENEW_DENIED,
    LEASE_REASON_SCHEMA_LEGACY,
    LEASE_REASON_STALE,
    LEASE_REASON_STORE_CORRUPT,
    LEASE_REASON_STORE_UNAVAILABLE,
    LEASE_STATUS_ACTIVE,
    LEASE_STATUS_EXPIRED,
    LEASE_STATUS_RELEASED,
    LEASE_STATUS_STALE,
    ResourceLease,
    ResourceRequirement,
    now_iso,
)
from services.resource_lease_shadow_evaluator import ResourceLeaseShadowEvaluator
from services.resource_policy_service import ResourcePolicyService


class ResourceLeaseManager:

    def __init__(
        self,
        root="workspace/jobs/resources",
        policy_service=None,
        clock=None,
    ):

        self.root = Path(
            root
        )

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.file = self.root / "resource_leases.json"

        self.policy_service = (
            policy_service
            or ResourcePolicyService()
        )

        self.shadow_evaluator = ResourceLeaseShadowEvaluator()

        self.clock = clock or datetime.now

        self.last_reason_codes = []

        self.last_reconciliation = []

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

    def lease_mode(
        self,
        policy=None,
    ):

        policy = policy or self.resolve_policy_for_observation()

        feature_modes = getattr(
            policy,
            "feature_modes",
            {},
        )

        mode = feature_modes.get(
            "resource_lease_v2_mode",
            "monitor_only",
        )

        if mode == FEATURE_MODE_ENFORCED:

            return FEATURE_MODE_ENFORCE

        return mode

    def is_enforce_mode(
        self,
        policy=None,
    ):

        return self.lease_mode(
            policy
        ) == FEATURE_MODE_ENFORCE

    def active_leases(
        self,
    ):

        self.cleanup_stale()

        return [
            lease
            for lease in self.load_all()
            if lease.status == "active"
        ]

    def can_acquire(
        self,
        requirement,
        selected_gpu_device_id="",
    ):

        requirement = ResourceRequirement.from_dict(
            requirement
        )

        active = self.active_leases()

        policy = self.policy_service.load()

        if len(
            active
        ) >= policy.max_concurrent_jobs:

            return False, "max_concurrent_jobs"

        if requirement.requires_gpu:

            gpu_active = [
                lease
                for lease in active
                if lease.resource_type == "gpu"
            ]

            if len(
                gpu_active
            ) >= policy.max_gpu_jobs:

                return False, "max_gpu_jobs"

            if requirement.exclusive_gpu:

                for lease in gpu_active:

                    if (
                        lease.gpu_device_id
                        == selected_gpu_device_id
                    ):

                        return False, "gpu_exclusive_busy"

        return True, ""

    def acquire(
        self,
        job,
        requirement,
        selected_gpu_device_id="",
        owner="",
    ):

        policy = self.resolve_policy_for_observation()

        if self.is_enforce_mode(
            policy
        ):

            return self.acquire_enforced(
                job,
                requirement,
                selected_gpu_device_id=selected_gpu_device_id,
                owner=owner,
                policy=policy,
            )

        allowed, reason = self.can_acquire(
            requirement,
            selected_gpu_device_id,
        )

        if not allowed:

            return None, reason

        requirement = ResourceRequirement.from_dict(
            requirement
        )

        policy = self.policy_service.load()

        expires_at = (
            self.now()
            + timedelta(
                seconds=policy.lease_ttl_seconds
            )
        ).isoformat()

        lease = ResourceLease(
            lease_id=f"lease_{uuid4().hex[:12]}",
            job_id=job.job_id,
            job_type=job.job_type,
            owner=owner,
            resource_type="gpu"
            if requirement.requires_gpu
            and selected_gpu_device_id
            else "cpu",
            gpu_device_id=selected_gpu_device_id,
            requirement=requirement.to_dict(),
            expires_at=expires_at,
        )

        leases = [
            item
            for item in self.load_all()
            if item.status == "active"
        ]

        leases.append(
            lease
        )

        self.save_all(
            leases
        )

        return lease, ""

    def renew(
        self,
        lease_id,
        job_id="",
        owner="",
    ):

        policy = self.resolve_policy_for_observation()

        if self.is_enforce_mode(
            policy
        ):

            return self.renew_enforced(
                lease_id,
                job_id=job_id,
                owner=owner,
                policy=policy,
            )

        policy = self.policy_service.load()

        leases = self.load_all()

        renewed = None

        for lease in leases:

            if lease.lease_id == lease_id:

                lease.renewed_at = self.now().isoformat()

                lease.expires_at = (
                    self.now()
                    + timedelta(
                        seconds=policy.lease_ttl_seconds
                    )
                ).isoformat()

                renewed = lease

        self.save_all(
            leases
        )

        return renewed

    def release(
        self,
        lease_id,
        job_id="",
        owner="",
    ):

        policy = self.resolve_policy_for_observation()

        if self.is_enforce_mode(
            policy
        ):

            return self.release_enforced(
                lease_id,
                job_id=job_id,
                owner=owner,
            )

        if not lease_id:

            return False

        changed = False

        leases = self.load_all()

        for lease in leases:

            if (
                lease.lease_id == lease_id
                and lease.status == "active"
            ):

                lease.status = "released"

                changed = True

        self.save_all(
            leases
        )

        return changed

    def release_job(
        self,
        job_id,
        owner="",
    ):

        policy = self.resolve_policy_for_observation()

        if self.is_enforce_mode(
            policy
        ):

            changed = False

            leases, error = self.load_all_checked()

            if error:

                self.last_reason_codes = [
                    error,
                    LEASE_REASON_RELEASE_DENIED,
                ]

                return False

            for lease in leases:

                if (
                    lease.job_id == job_id
                    and lease.status == LEASE_STATUS_ACTIVE
                ):

                    if owner and lease.owner != owner:

                        self.last_reason_codes = [
                            LEASE_REASON_OWNER_MISMATCH,
                            LEASE_REASON_RELEASE_DENIED,
                        ]

                        return False

                    lease.status = LEASE_STATUS_RELEASED

                    changed = True

            if changed:

                self.save_all(
                    leases
                )

                self.last_reason_codes = [
                    LEASE_REASON_RELEASED
                ]

            return changed

        changed = False

        leases = self.load_all()

        for lease in leases:

            if (
                lease.job_id == job_id
                and lease.status == "active"
            ):

                lease.status = "released"

                changed = True

        self.save_all(
            leases
        )

        return changed

    def cleanup_stale(
        self,
    ):

        now = self.now()

        changed = False

        leases = self.load_all()

        for lease in leases:

            if lease.status != "active":

                continue

            try:

                expires = datetime.fromisoformat(
                    lease.expires_at
                )

            except Exception:

                expires = now

            if expires < now:

                lease.status = "stale"

                changed = True

        if changed:

            self.save_all(
                leases
            )

        return changed

    def load_all(
        self,
    ):

        if not self.file.exists():

            return []

        try:

            data = json.loads(
                self.file.read_text(
                    encoding="utf-8"
                )
            )

        except Exception:

            return []

        return [
            ResourceLease.from_dict(
                item
            )
            for item in data.get(
                "leases",
                []
            )
        ]

    def load_all_checked(
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

            return [], LEASE_REASON_STORE_UNAVAILABLE

        except Exception:

            return [], LEASE_REASON_STORE_CORRUPT

        if not isinstance(
            data,
            dict,
        ):

            return [], LEASE_REASON_STORE_CORRUPT

        try:

            leases = [
                ResourceLease.from_dict(
                    item
                )
                for item in data.get(
                    "leases",
                    []
                )
            ]

        except Exception:

            return [], LEASE_REASON_STORE_CORRUPT

        return leases, ""

    def acquire_enforced(
        self,
        job,
        requirement,
        selected_gpu_device_id="",
        owner="",
        policy=None,
    ):

        self.last_reason_codes = [
            LEASE_REASON_MODE_ENFORCE
        ]

        leases, error = self.load_all_checked()

        if error:

            self.last_reason_codes = [
                error,
                LEASE_REASON_ACQUIRE_DENIED,
            ]

            return None, error

        requirement = ResourceRequirement.from_dict(
            requirement
        )

        resource_type = (
            "gpu"
            if requirement.requires_gpu
            and selected_gpu_device_id
            else "cpu"
        )

        now = self.now()
        active = self.valid_active_leases(
            leases,
            now,
        )

        matching = [
            lease
            for lease in active
            if lease.job_id == job.job_id
            and lease.resource_type == resource_type
        ]

        if matching:

            if len(
                matching
            ) > 1:

                self.last_reason_codes = [
                    LEASE_REASON_DUPLICATE,
                    LEASE_REASON_ACQUIRE_CONFLICT,
                ]

                return None, LEASE_REASON_DUPLICATE

            lease = matching[0]

            if owner and lease.owner and lease.owner != owner:

                self.last_reason_codes = [
                    LEASE_REASON_OWNER_MISMATCH,
                    LEASE_REASON_ACQUIRE_CONFLICT,
                ]

                return None, LEASE_REASON_OWNER_MISMATCH

            self.last_reason_codes = [
                LEASE_REASON_ACQUIRED
            ]

            return lease, LEASE_REASON_ACQUIRED

        if len(
            active
        ) >= int(
            policy.max_concurrent_jobs
        ):

            self.last_reason_codes = [
                LEASE_REASON_ACQUIRE_DENIED
            ]

            return None, LEASE_REASON_ACQUIRE_DENIED

        if requirement.requires_gpu:

            gpu_active = [
                lease
                for lease in active
                if lease.resource_type == "gpu"
            ]

            if len(
                gpu_active
            ) >= int(
                policy.max_gpu_jobs
            ):

                self.last_reason_codes = [
                    LEASE_REASON_ACQUIRE_DENIED
                ]

                return None, LEASE_REASON_ACQUIRE_DENIED

            if requirement.exclusive_gpu:

                for lease in gpu_active:

                    if (
                        lease.gpu_device_id
                        == selected_gpu_device_id
                    ):

                        self.last_reason_codes = [
                            LEASE_REASON_ACQUIRE_CONFLICT
                        ]

                        return None, LEASE_REASON_ACQUIRE_CONFLICT

        expires_at = (
            now
            + timedelta(
                seconds=policy.lease_ttl_seconds
            )
        ).isoformat()

        lease = ResourceLease(
            lease_id=f"lease_{uuid4().hex[:12]}",
            job_id=job.job_id,
            job_type=job.job_type,
            owner=owner,
            resource_type=resource_type,
            gpu_device_id=selected_gpu_device_id,
            requirement=requirement.to_dict(),
            acquired_at=now.isoformat(),
            renewed_at=now.isoformat(),
            expires_at=expires_at,
            status=LEASE_STATUS_ACTIVE,
            policy_fingerprint=getattr(
                policy,
                "fingerprint",
                "",
            ),
            schema_version=2,
        )

        leases.append(
            lease
        )

        self.save_all(
            leases
        )

        self.last_reason_codes = [
            LEASE_REASON_ACQUIRED
        ]

        return lease, LEASE_REASON_ACQUIRED

    def renew_enforced(
        self,
        lease_id,
        job_id="",
        owner="",
        policy=None,
    ):

        leases, error = self.load_all_checked()

        if error:

            self.last_reason_codes = [
                error,
                LEASE_REASON_RENEW_DENIED,
            ]

            return None

        now = self.now()

        renewed = None

        for lease in leases:

            if lease.lease_id != lease_id:

                continue

            if (
                job_id
                and lease.job_id != job_id
            ) or (
                owner
                and lease.owner != owner
            ):

                self.last_reason_codes = [
                    LEASE_REASON_OWNER_MISMATCH,
                    LEASE_REASON_RENEW_DENIED,
                ]

                return None

            if not self.lease_is_valid_active(
                lease,
                now,
            ):

                lease.status = LEASE_STATUS_EXPIRED

                self.last_reason_codes = [
                    LEASE_REASON_EXPIRED,
                    LEASE_REASON_RECONCILIATION_REQUIRED,
                    LEASE_REASON_RENEW_DENIED,
                ]

                self.save_all(
                    leases
                )

                return None

            lease.renewed_at = now.isoformat()

            lease.expires_at = (
                now
                + timedelta(
                    seconds=policy.lease_ttl_seconds
                )
            ).isoformat()

            renewed = lease

        if renewed is None:

            self.last_reason_codes = [
                LEASE_REASON_RENEW_DENIED
            ]

            return None

        self.save_all(
            leases
        )

        self.last_reason_codes = [
            LEASE_REASON_RENEWED
        ]

        return renewed

    def release_enforced(
        self,
        lease_id,
        job_id="",
        owner="",
    ):

        if not lease_id:

            self.last_reason_codes = [
                LEASE_REASON_RELEASE_DENIED
            ]

            return False

        leases, error = self.load_all_checked()

        if error:

            self.last_reason_codes = [
                error,
                LEASE_REASON_RELEASE_DENIED,
            ]

            return False

        changed = False

        for lease in leases:

            if lease.lease_id != lease_id:

                continue

            if (
                job_id
                and lease.job_id != job_id
            ) or (
                owner
                and lease.owner != owner
            ):

                self.last_reason_codes = [
                    LEASE_REASON_OWNER_MISMATCH,
                    LEASE_REASON_RELEASE_DENIED,
                ]

                return False

            if lease.status == LEASE_STATUS_RELEASED:

                self.last_reason_codes = [
                    LEASE_REASON_RELEASED
                ]

                return True

            if lease.status == LEASE_STATUS_ACTIVE:

                lease.status = LEASE_STATUS_RELEASED

                changed = True

        if changed:

            self.save_all(
                leases
            )

            self.last_reason_codes = [
                LEASE_REASON_RELEASED
            ]

            return True

        self.last_reason_codes = [
            LEASE_REASON_RELEASE_DENIED
        ]

        return False

    def reconcile(
        self,
        jobs_by_id=None,
        process_alive_by_lease_id=None,
        process_identity_by_lease_id=None,
        owner_id="",
    ):

        policy = self.resolve_policy_for_observation()

        if not self.is_enforce_mode(
            policy
        ):

            return []

        leases, error = self.load_all_checked()

        if error:

            self.last_reconciliation = [
                {
                    "reason_codes": [
                        error,
                        LEASE_REASON_RECONCILIATION_DEFERRED,
                    ],
                }
            ]

            return self.last_reconciliation

        jobs_by_id = jobs_by_id or {}
        process_alive_by_lease_id = process_alive_by_lease_id or {}
        process_identity_by_lease_id = process_identity_by_lease_id or {}
        observations = []
        changed = False
        now = self.now()

        seen = set()

        for lease in leases:

            codes = []
            key = (
                lease.job_id,
                lease.resource_type,
            )

            if (
                lease.status == LEASE_STATUS_ACTIVE
                and key in seen
            ):

                lease.status = LEASE_STATUS_STALE
                codes.extend(
                    [
                        LEASE_REASON_DUPLICATE,
                        LEASE_REASON_STALE,
                    ]
                )
                changed = True

            if lease.status == LEASE_STATUS_ACTIVE:

                seen.add(
                    key
                )

            if (
                lease.status == LEASE_STATUS_ACTIVE
                and not self.lease_is_valid_active(
                    lease,
                    now,
                )
            ):

                lease.status = LEASE_STATUS_EXPIRED
                codes.extend(
                    [
                        LEASE_REASON_EXPIRED,
                        LEASE_REASON_RECONCILIATION_REQUIRED,
                    ]
                )
                changed = True

            job = jobs_by_id.get(
                lease.job_id
            )

            if (
                lease.status == LEASE_STATUS_ACTIVE
                and job is None
            ):

                lease.status = LEASE_STATUS_STALE
                codes.extend(
                    [
                        LEASE_REASON_JOB_MISSING,
                        LEASE_REASON_STALE,
                    ]
                )
                changed = True

            if (
                lease.status == LEASE_STATUS_ACTIVE
                and owner_id
                and lease.owner
                and lease.owner != owner_id
            ):

                codes.append(
                    LEASE_REASON_OWNER_MISMATCH
                )

            process_alive = process_alive_by_lease_id.get(
                lease.lease_id
            )

            if (
                lease.status == LEASE_STATUS_ACTIVE
                and process_alive is False
            ):

                lease.status = LEASE_STATUS_STALE
                codes.extend(
                    [
                        LEASE_REASON_PROCESS_MISSING,
                        LEASE_REASON_STALE,
                    ]
                )
                changed = True

            actual_identity = process_identity_by_lease_id.get(
                lease.lease_id
            )

            if (
                lease.status == LEASE_STATUS_ACTIVE
                and actual_identity is not None
                and lease.process_identity
                and actual_identity != lease.process_identity
            ):

                codes.extend(
                    [
                        LEASE_REASON_PROCESS_IDENTITY_MISMATCH,
                        LEASE_REASON_RECONCILIATION_REQUIRED,
                    ]
                )

            if (
                lease.status == LEASE_STATUS_ACTIVE
                and lease.policy_fingerprint
                and getattr(
                    policy,
                    "fingerprint",
                    "",
                )
                and lease.policy_fingerprint != policy.fingerprint
            ):

                codes.extend(
                    [
                        LEASE_REASON_POLICY_MISMATCH,
                        LEASE_REASON_RECONCILIATION_REQUIRED,
                    ]
                )

            if int(
                getattr(
                    lease,
                    "schema_version",
                    1,
                )
            ) < 2:

                codes.append(
                    LEASE_REASON_SCHEMA_LEGACY
                )

            if codes:

                observations.append(
                    {
                        "lease_id": lease.lease_id,
                        "job_id": lease.job_id,
                        "status": lease.status,
                        "reason_codes": sorted(
                            set(
                                codes
                                + [
                                    LEASE_REASON_RECONCILIATION_COMPLETED
                                ]
                            )
                        ),
                    }
                )

        if changed:

            self.save_all(
                leases
            )

        self.last_reconciliation = observations

        return observations

    def valid_active_leases(
        self,
        leases,
        now,
    ):

        return [
            lease
            for lease in leases
            if self.lease_is_valid_active(
                lease,
                now,
            )
        ]

    def lease_is_valid_active(
        self,
        lease,
        now,
    ):

        if lease.status != LEASE_STATUS_ACTIVE:

            return False

        try:

            expires = datetime.fromisoformat(
                lease.expires_at
            )

        except Exception:

            return False

        return expires > now

    def load_all_for_observation(
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

            return [], LEASE_REASON_STORE_UNAVAILABLE

        except Exception:

            return [], LEASE_REASON_STORE_CORRUPT

        try:

            leases = [
                ResourceLease.from_dict(
                    item
                )
                for item in data.get(
                    "leases",
                    []
                )
            ]

        except Exception:

            return [], LEASE_REASON_STORE_CORRUPT

        return leases, ""

    def shadow_observations(
        self,
        jobs_by_id=None,
        owner_id="",
        process_alive_by_lease_id=None,
        process_identity_by_lease_id=None,
    ):

        policy = self.resolve_policy_for_observation()

        leases, store_error = self.load_all_for_observation()

        if store_error:

            return [
                self.shadow_evaluator.observe_store_error(
                    store_error,
                    policy=policy,
                ).to_dict()
            ]

        jobs_by_id = jobs_by_id or {}
        process_alive_by_lease_id = process_alive_by_lease_id or {}
        process_identity_by_lease_id = process_identity_by_lease_id or {}

        return [
            self.shadow_evaluator.observe(
                lease,
                all_leases=leases,
                job=jobs_by_id.get(
                    lease.job_id
                ),
                owner_id=owner_id,
                process_alive=process_alive_by_lease_id.get(
                    lease.lease_id
                ),
                actual_process_identity=process_identity_by_lease_id.get(
                    lease.lease_id
                ),
                policy=policy,
            ).to_dict()
            for lease in leases
        ]

    def shadow_observation_for_job(
        self,
        job,
        requirement,
        selected_gpu_device_id="",
        owner_id="",
    ):

        policy = self.resolve_policy_for_observation()

        leases, store_error = self.load_all_for_observation()

        if store_error:

            return self.shadow_evaluator.observe_store_error(
                store_error,
                policy=policy,
            ).to_dict()

        requirement = ResourceRequirement.from_dict(
            requirement
        )

        resource_kind = (
            "gpu"
            if requirement.requires_gpu
            and selected_gpu_device_id
            else "cpu"
        )

        for lease in leases:

            if (
                lease.job_id == job.job_id
                and lease.resource_type == resource_kind
            ):

                return self.shadow_evaluator.observe(
                    lease,
                    all_leases=leases,
                    job=job,
                    owner_id=owner_id,
                    policy=policy,
                ).to_dict()

        return self.shadow_evaluator.observe_missing(
            job_id=job.job_id,
            resource_kind=resource_kind,
            owner_id=owner_id,
            policy=policy,
        ).to_dict()

    def resolve_policy_for_observation(
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

    def save_all(
        self,
        leases,
    ):

        data = {
            "schema_version": 2,
            "updated_at": now_iso(),
            "leases": [
                lease.to_dict()
                for lease in leases
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

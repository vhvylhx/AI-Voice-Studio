import json
import os
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from uuid import uuid4

from models.resource_model import (
    ResourceLease,
    ResourceRequirement,
    now_iso,
)
from services.resource_policy_service import ResourcePolicyService


class ResourceLeaseManager:

    def __init__(
        self,
        root="workspace/jobs/resources",
        policy_service=None,
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
            datetime.now()
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
    ):

        policy = self.policy_service.load()

        leases = self.load_all()

        renewed = None

        for lease in leases:

            if lease.lease_id == lease_id:

                lease.renewed_at = now_iso()

                lease.expires_at = (
                    datetime.now()
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
    ):

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
    ):

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

        now = datetime.now()

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

    def save_all(
        self,
        leases,
    ):

        data = {
            "schema_version": 1,
            "updated_at": now_iso(),
            "leases": [
                lease.to_dict()
                for lease in leases
            ],
        }

        temp = self.file.with_suffix(
            ".json.tmp"
        )

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

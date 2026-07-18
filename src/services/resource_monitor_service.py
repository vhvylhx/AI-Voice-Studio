from services.hardware_detection_service import HardwareDetectionService
from services.resource_policy_service import ResourcePolicyService
from services.resource_snapshot_service import ResourceSnapshotService


class ResourceMonitorService:

    def __init__(
        self,
        hardware_detection=None,
        snapshot_service=None,
        policy_service=None,
        lease_manager=None,
        job_queue_service=None,
    ):

        self.hardware_detection = (
            hardware_detection
            or HardwareDetectionService()
        )

        self.snapshot_service = (
            snapshot_service
            or ResourceSnapshotService(
                hardware_detection=self.hardware_detection
            )
        )

        self.policy_service = (
            policy_service
            or ResourcePolicyService()
        )

        self.lease_manager = lease_manager

        self.job_queue_service = job_queue_service

    def hardware(
        self,
    ):

        return self.hardware_detection.detect().to_dict()

    def snapshot(
        self,
    ):

        return self.snapshot_service.snapshot().to_dict()

    def policy(
        self,
    ):

        return self.policy_service.summary()

    def leases(
        self,
    ):

        if self.lease_manager is None:

            return []

        return [
            lease.to_dict()
            for lease in self.lease_manager.active_leases()
        ]

    def waiting_jobs(
        self,
    ):

        if self.job_queue_service is None:

            return []

        return [
            job.safe_summary()
            for job in self.job_queue_service.list_jobs(
                state="waiting_resource"
            )
        ]

    def summary(
        self,
    ):

        snapshot = self.snapshot()

        return {
            "hardware": self.hardware(),
            "snapshot": snapshot,
            "policy": self.policy(),
            "leases": self.leases(),
            "waiting_jobs": self.waiting_jobs(),
            "pressure_state": snapshot.get(
                "pressure_state",
                "unknown",
            ),
        }

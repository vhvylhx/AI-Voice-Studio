import shutil
import time
from datetime import datetime
from pathlib import Path

from models.resource_model import (
    RESOURCE_REASON_DISK_SNAPSHOT_INVALID,
    RESOURCE_REASON_DISK_SNAPSHOT_UNKNOWN,
    RESOURCE_REASON_GPU_SNAPSHOT_INVALID,
    RESOURCE_REASON_GPU_SNAPSHOT_UNKNOWN,
    RESOURCE_REASON_RAM_SNAPSHOT_INVALID,
    RESOURCE_REASON_RAM_SNAPSHOT_UNKNOWN,
    RESOURCE_REASON_SNAPSHOT_STALE,
    SNAPSHOT_STATUS_INVALID,
    SNAPSHOT_STATUS_STALE,
    SNAPSHOT_STATUS_UNKNOWN,
    SNAPSHOT_STATUS_VALID,
    ResourceSnapshot,
    ResourceSnapshotValidation,
    now_iso,
)
from services.hardware_detection_service import HardwareDetectionService
from services.resource_policy_service import ResourcePolicyService


class ResourceSnapshotService:

    def __init__(
        self,
        hardware_detection=None,
        policy_service=None,
        disk_path=None,
        clock=None,
    ):

        self.hardware_detection = (
            hardware_detection
            or HardwareDetectionService()
        )

        self.policy_service = (
            policy_service
            or ResourcePolicyService()
        )

        self.disk_path = Path(
            disk_path or Path.cwd()
        )

        self.clock = clock or time.time

        self._cached_snapshot = None

        self._cached_at = 0.0

    def snapshot(
        self,
        force=False,
    ):

        policy = self.policy_service.load()

        now = self.clock()

        if (
            not force
            and self._cached_snapshot is not None
            and now - self._cached_at
            < policy.snapshot_ttl_seconds
        ):

            return self._cached_snapshot

        hardware = self.hardware_detection.detect()

        ram = self.ram_status()

        disk = shutil.disk_usage(
            self.disk_path
        )

        disk_total_mb = int(
            disk.total / 1024 / 1024
        )

        disk_free_mb = int(
            disk.free / 1024 / 1024
        )

        disk_used_percent = (
            100.0
            - (
                disk.free * 100.0 / disk.total
            )
            if disk.total
            else 0.0
        )

        snapshot = ResourceSnapshot(
            cpu_percent=self.cpu_percent(),
            ram_total_mb=ram[
                "total_mb"
            ]
            or hardware.ram_total_mb,
            ram_available_mb=ram[
                "available_mb"
            ],
            ram_used_percent=ram[
                "used_percent"
            ],
            disk_path=str(
                self.disk_path
            ),
            disk_total_mb=disk_total_mb,
            disk_free_mb=disk_free_mb,
            disk_used_percent=disk_used_percent,
            gpu_devices=hardware.gpu_devices,
        )

        snapshot.pressure_state = self.pressure_state(
            snapshot,
            policy,
        )

        validation = self.validate_snapshot(
            snapshot,
            policy=policy,
            now_seconds=now,
        )

        snapshot.validation_status = validation.status
        snapshot.validation_reason_codes = list(
            validation.reason_codes
        )
        snapshot.freshness_age_seconds = validation.age_seconds

        self._cached_snapshot = snapshot

        self._cached_at = now

        return snapshot

    def cpu_percent(
        self,
    ):

        try:

            import psutil

            return float(
                psutil.cpu_percent(
                    interval=None
                )
            )

        except Exception:

            return 0.0

    def ram_status(
        self,
    ):

        try:

            import psutil

            memory = psutil.virtual_memory()

            return {
                "total_mb": int(
                    memory.total / 1024 / 1024
                ),
                "available_mb": int(
                    memory.available / 1024 / 1024
                ),
                "used_percent": float(
                    memory.percent
                ),
            }

        except Exception:

            total = self.hardware_detection.detect_ram_total_mb()

            return {
                "total_mb": total,
                "available_mb": 0,
                "used_percent": 0.0,
            }

    def validate_snapshot(
        self,
        snapshot,
        policy=None,
        now_seconds=None,
    ):

        snapshot = ResourceSnapshot.from_dict(
            snapshot
        )

        policy = policy or self.policy_service.resolve(
            migrate=False
        )

        now_seconds = (
            self.clock()
            if now_seconds is None
            else now_seconds
        )

        reason_codes = []

        ram_status = SNAPSHOT_STATUS_VALID
        gpu_status = SNAPSHOT_STATUS_VALID
        disk_status = SNAPSHOT_STATUS_VALID

        age_seconds = self.snapshot_age_seconds(
            snapshot,
            now_seconds,
        )

        if age_seconds > float(
            policy.snapshot_ttl_seconds
        ):

            reason_codes.append(
                RESOURCE_REASON_SNAPSHOT_STALE
            )

            ram_status = SNAPSHOT_STATUS_STALE
            gpu_status = SNAPSHOT_STATUS_STALE
            disk_status = SNAPSHOT_STATUS_STALE

        provider_status = snapshot.provider_status or {}

        ram_provider_status = provider_status.get(
            "ram",
            "valid",
        )

        if ram_provider_status in (
            "exception",
            "timeout",
            "unknown",
            "missing",
        ):

            ram_status = SNAPSHOT_STATUS_UNKNOWN
            reason_codes.append(
                RESOURCE_REASON_RAM_SNAPSHOT_UNKNOWN
            )

        if snapshot.ram_total_mb < 0 or snapshot.ram_available_mb < 0:

            ram_status = SNAPSHOT_STATUS_INVALID
            reason_codes.append(
                RESOURCE_REASON_RAM_SNAPSHOT_INVALID
            )

        elif snapshot.ram_total_mb == 0:

            ram_status = SNAPSHOT_STATUS_UNKNOWN
            reason_codes.append(
                RESOURCE_REASON_RAM_SNAPSHOT_UNKNOWN
            )

        elif snapshot.ram_available_mb > snapshot.ram_total_mb:

            ram_status = SNAPSHOT_STATUS_INVALID
            reason_codes.append(
                RESOURCE_REASON_RAM_SNAPSHOT_INVALID
            )

        gpu_provider_status = provider_status.get(
            "gpu",
            "valid",
        )

        if gpu_provider_status in (
            "exception",
            "timeout",
            "unknown",
            "malformed",
            "driver_unknown",
        ):

            gpu_status = SNAPSHOT_STATUS_UNKNOWN
            reason_codes.append(
                RESOURCE_REASON_GPU_SNAPSHOT_UNKNOWN
            )

        for gpu in snapshot.gpu_devices:

            gpu = getattr(
                gpu,
                "to_dict",
                lambda: gpu,
            )()

            total = int(
                gpu.get(
                    "vram_total_mb",
                    0,
                )
            )

            free = int(
                gpu.get(
                    "vram_free_mb",
                    0,
                )
            )

            if total < 0 or free < 0 or free > total:

                gpu_status = SNAPSHOT_STATUS_INVALID
                reason_codes.append(
                    RESOURCE_REASON_GPU_SNAPSHOT_INVALID
                )

        disk_provider_status = provider_status.get(
            "disk",
            "valid",
        )

        if disk_provider_status in (
            "exception",
            "timeout",
            "missing",
            "permission_error",
            "unknown",
        ):

            disk_status = SNAPSHOT_STATUS_UNKNOWN
            reason_codes.append(
                RESOURCE_REASON_DISK_SNAPSHOT_UNKNOWN
            )

        if snapshot.disk_free_mb < 0 or snapshot.disk_total_mb < 0:

            disk_status = SNAPSHOT_STATUS_INVALID
            reason_codes.append(
                RESOURCE_REASON_DISK_SNAPSHOT_INVALID
            )

        elif snapshot.disk_total_mb and snapshot.disk_free_mb > snapshot.disk_total_mb:

            disk_status = SNAPSHOT_STATUS_INVALID
            reason_codes.append(
                RESOURCE_REASON_DISK_SNAPSHOT_INVALID
            )

        status = SNAPSHOT_STATUS_VALID

        if SNAPSHOT_STATUS_INVALID in (
            ram_status,
            gpu_status,
            disk_status,
        ):

            status = SNAPSHOT_STATUS_INVALID

        elif SNAPSHOT_STATUS_UNKNOWN in (
            ram_status,
            gpu_status,
            disk_status,
        ):

            status = SNAPSHOT_STATUS_UNKNOWN

        elif SNAPSHOT_STATUS_STALE in (
            ram_status,
            gpu_status,
            disk_status,
        ):

            status = SNAPSHOT_STATUS_STALE

        return ResourceSnapshotValidation(
            status=status,
            reason_codes=sorted(
                set(
                    reason_codes
                )
            ),
            ram_status=ram_status,
            gpu_status=gpu_status,
            disk_status=disk_status,
            age_seconds=age_seconds,
            validated_at=now_iso(),
        )

    def snapshot_age_seconds(
        self,
        snapshot,
        now_seconds,
    ):

        try:

            captured = datetime.fromisoformat(
                snapshot.captured_at
            )

            now = datetime.fromtimestamp(
                now_seconds
            )

            return max(
                0.0,
                float(
                    (
                        now
                        - captured
                    ).total_seconds()
                ),
            )

        except Exception:

            return 0.0

    def pressure_state(
        self,
        snapshot,
        policy,
    ):

        if (
            snapshot.disk_used_percent
            >= policy.pressure_disk_warning_percent
        ):

            return "critical"

        if (
            snapshot.ram_used_percent
            >= policy.pressure_ram_warning_percent
        ):

            return "high"

        if (
            snapshot.cpu_percent
            >= policy.pressure_cpu_warning_percent
        ):

            return "elevated"

        for gpu in snapshot.gpu_devices:

            if not gpu.vram_total_mb:

                continue

            used = (
                gpu.vram_used_mb
                * 100.0
                / gpu.vram_total_mb
            )

            if used >= policy.pressure_vram_warning_percent:

                return "high"

        return "normal"

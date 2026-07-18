import shutil
import time
from pathlib import Path

from models.resource_model import ResourceSnapshot
from services.hardware_detection_service import HardwareDetectionService
from services.resource_policy_service import ResourcePolicyService


class ResourceSnapshotService:

    def __init__(
        self,
        hardware_detection=None,
        policy_service=None,
        disk_path=None,
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

        self._cached_snapshot = None

        self._cached_at = 0.0

    def snapshot(
        self,
        force=False,
    ):

        policy = self.policy_service.load()

        now = time.time()

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

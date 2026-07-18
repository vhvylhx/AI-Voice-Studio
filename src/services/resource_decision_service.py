from models.resource_model import (
    ResourceDecision,
    ResourceRequirement,
)
from services.resource_policy_service import ResourcePolicyService
from services.resource_snapshot_service import ResourceSnapshotService


class ResourceDecisionService:

    def __init__(
        self,
        snapshot_service=None,
        policy_service=None,
    ):

        self.snapshot_service = (
            snapshot_service
            or ResourceSnapshotService()
        )

        self.policy_service = (
            policy_service
            or ResourcePolicyService()
        )

    def evaluate(
        self,
        requirement,
    ):

        requirement = ResourceRequirement.from_dict(
            requirement
        )

        policy = self.policy_service.load()

        snapshot = self.snapshot_service.snapshot()

        remediation = []

        if (
            snapshot.disk_free_mb
            and snapshot.disk_free_mb
            < requirement.disk_free_mb
            + policy.reserve_disk_mb
        ):

            remediation.append(
                "Giải phóng dung lượng ổ đĩa hoặc chọn output/cache khác."
            )

            return self.decision(
                "waiting_resource",
                "disk_free_low",
                "Đang chờ đủ dung lượng ổ đĩa.",
                requirement,
                snapshot,
                policy,
                remediation=remediation,
            )

        if (
            snapshot.ram_available_mb
            and snapshot.ram_available_mb
            < requirement.ram_mb
            + policy.reserve_ram_mb
        ):

            remediation.append(
                "Đóng bớt ứng dụng đang dùng RAM hoặc chờ job khác hoàn thành."
            )

            return self.decision(
                "waiting_resource",
                "ram_low",
                "Đang chờ đủ RAM trống.",
                requirement,
                snapshot,
                policy,
                remediation=remediation,
            )

        if requirement.requires_gpu:

            gpu = self.select_gpu(
                snapshot,
                requirement,
                policy,
            )

            if gpu is None:

                if (
                    requirement.allow_cpu_fallback
                    and policy.allow_cpu_fallback
                ):

                    return self.decision(
                        "ready",
                        "cpu_fallback",
                        "GPU chưa sẵn sàng, job được phép chạy bằng CPU fallback.",
                        requirement,
                        snapshot,
                        policy,
                        selected_gpu_device_id="",
                    )

                remediation.append(
                    "Kiểm tra NVIDIA driver bằng nvidia-smi hoặc chọn job không yêu cầu GPU."
                )

                return self.decision(
                    "unsupported",
                    "gpu_unavailable",
                    "Không tìm thấy GPU phù hợp cho job này.",
                    requirement,
                    snapshot,
                    policy,
                    remediation=remediation,
                )

            return self.decision(
                "ready",
                "gpu_ready",
                "GPU đủ điều kiện.",
                requirement,
                snapshot,
                policy,
                selected_gpu_device_id=gpu.device_id,
            )

        return self.decision(
            "ready",
            "cpu_ready",
            "CPU/RAM/Disk đủ điều kiện.",
            requirement,
            snapshot,
            policy,
        )

    def select_gpu(
        self,
        snapshot,
        requirement,
        policy,
    ):

        for gpu in snapshot.gpu_devices:

            if not gpu.cuda_available:

                continue

            if (
                gpu.vram_free_mb
                >= requirement.vram_mb
                + policy.reserve_vram_mb
            ):

                return gpu

        return None

    def decision(
        self,
        status,
        reason_code,
        message_vi,
        requirement,
        snapshot,
        policy,
        selected_gpu_device_id="",
        remediation=None,
    ):

        return ResourceDecision(
            status=status,
            reason_code=reason_code,
            message_vi=message_vi,
            requirement=requirement.to_dict(),
            snapshot=snapshot.to_dict(),
            policy=policy.to_dict(),
            selected_gpu_device_id=selected_gpu_device_id,
            pressure_state=snapshot.pressure_state,
            remediation=remediation
            or [],
        )

from models.resource_model import (
    FEATURE_MODE_MONITOR_ONLY,
    RESOURCE_REASON_CPU_FALLBACK_CONFIRMATION_REQUIRED,
    RESOURCE_REASON_DISK_BELOW_RESERVE,
    RESOURCE_REASON_DISK_SNAPSHOT_INVALID,
    RESOURCE_REASON_DISK_SNAPSHOT_UNKNOWN,
    RESOURCE_REASON_GPU_SNAPSHOT_INVALID,
    RESOURCE_REASON_GPU_SNAPSHOT_UNKNOWN,
    RESOURCE_REASON_GPU_UNAVAILABLE,
    RESOURCE_REASON_HEAVY_JOB_ALREADY_ACTIVE,
    RESOURCE_REASON_RAM_BELOW_RESERVE,
    RESOURCE_REASON_RAM_SNAPSHOT_INVALID,
    RESOURCE_REASON_RAM_SNAPSHOT_UNKNOWN,
    RESOURCE_REASON_SNAPSHOT_STALE,
    RESOURCE_REASON_VRAM_BELOW_RESERVE,
    SHADOW_DECISION_CONFIRMATION_REQUIRED,
    SHADOW_DECISION_WOULD_BLOCK,
    SHADOW_DECISION_WOULD_READY,
    SHADOW_DECISION_WOULD_WAIT,
    SNAPSHOT_STATUS_INVALID,
    SNAPSHOT_STATUS_STALE,
    SNAPSHOT_STATUS_UNKNOWN,
    WORKLOAD_CLASS_LIGHT,
    ResourceDecision,
    ResourceDecisionObservation,
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

            return self.with_shadow_observation(
                self.decision(
                    "waiting_resource",
                    "disk_free_low",
                    "Đang chờ đủ dung lượng ổ đĩa.",
                    requirement,
                    snapshot,
                    policy,
                    remediation=remediation,
                ),
                requirement,
                snapshot,
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

            return self.with_shadow_observation(
                self.decision(
                    "waiting_resource",
                    "ram_low",
                    "Đang chờ đủ RAM trống.",
                    requirement,
                    snapshot,
                    policy,
                    remediation=remediation,
                ),
                requirement,
                snapshot,
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

                    return self.with_shadow_observation(
                        self.decision(
                            "ready",
                            "cpu_fallback",
                            "GPU chưa sẵn sàng, job được phép chạy bằng CPU fallback.",
                            requirement,
                            snapshot,
                            policy,
                            selected_gpu_device_id="",
                        ),
                        requirement,
                        snapshot,
                    )

                remediation.append(
                    "Kiểm tra NVIDIA driver bằng nvidia-smi hoặc chọn job không yêu cầu GPU."
                )

                return self.with_shadow_observation(
                    self.decision(
                        "unsupported",
                        "gpu_unavailable",
                        "Không tìm thấy GPU phù hợp cho job này.",
                        requirement,
                        snapshot,
                        policy,
                        remediation=remediation,
                    ),
                    requirement,
                    snapshot,
                )

            return self.with_shadow_observation(
                self.decision(
                    "ready",
                    "gpu_ready",
                    "GPU đủ điều kiện.",
                    requirement,
                    snapshot,
                    policy,
                    selected_gpu_device_id=gpu.device_id,
                ),
                requirement,
                snapshot,
            )

        return self.with_shadow_observation(
            self.decision(
                "ready",
                "cpu_ready",
                "CPU/RAM/Disk đủ điều kiện.",
                requirement,
                snapshot,
                policy,
            ),
            requirement,
            snapshot,
        )

    def with_shadow_observation(
        self,
        decision,
        requirement,
        snapshot,
        active_heavy_jobs=0,
    ):

        observation = self.evaluate_shadow(
            requirement,
            actual_decision=decision,
            snapshot=snapshot,
            active_heavy_jobs=active_heavy_jobs,
        )

        decision.shadow_observation = observation.to_dict()

        return decision

    def evaluate_shadow(
        self,
        requirement,
        actual_decision=None,
        snapshot=None,
        active_heavy_jobs=0,
    ):

        requirement = ResourceRequirement.from_dict(
            requirement
        )

        if hasattr(
            self.policy_service,
            "resolve",
        ):

            resolved_policy = self.policy_service.resolve(
                migrate=False
            )

        else:

            resolved_policy = self.policy_service.load()

        snapshot = (
            self.snapshot_service.snapshot()
            if snapshot is None
            else snapshot
        )

        if hasattr(
            self.snapshot_service,
            "validate_snapshot",
        ):

            validation = self.snapshot_service.validate_snapshot(
                snapshot,
                policy=resolved_policy,
            )

        else:

            validation = ResourceSnapshotService(
                policy_service=self.policy_service
            ).validate_snapshot(
                snapshot,
                policy=resolved_policy,
            )

        reason_codes = list(
            validation.reason_codes
        )

        ram_invalid = validation.ram_status == SNAPSHOT_STATUS_INVALID
        ram_unknown = validation.ram_status == SNAPSHOT_STATUS_UNKNOWN
        ram_stale = validation.ram_status == SNAPSHOT_STATUS_STALE
        disk_invalid = validation.disk_status == SNAPSHOT_STATUS_INVALID
        disk_unknown = validation.disk_status == SNAPSHOT_STATUS_UNKNOWN
        disk_stale = validation.disk_status == SNAPSHOT_STATUS_STALE
        gpu_invalid = validation.gpu_status == SNAPSHOT_STATUS_INVALID
        gpu_unknown = validation.gpu_status == SNAPSHOT_STATUS_UNKNOWN
        gpu_stale = validation.gpu_status == SNAPSHOT_STATUS_STALE

        if ram_invalid:

            reason_codes.append(
                RESOURCE_REASON_RAM_SNAPSHOT_INVALID
            )

        elif ram_unknown:

            reason_codes.append(
                RESOURCE_REASON_RAM_SNAPSHOT_UNKNOWN
            )

        if disk_invalid:

            reason_codes.append(
                RESOURCE_REASON_DISK_SNAPSHOT_INVALID
            )

        elif disk_unknown:

            reason_codes.append(
                RESOURCE_REASON_DISK_SNAPSHOT_UNKNOWN
            )

        if gpu_invalid:

            reason_codes.append(
                RESOURCE_REASON_GPU_SNAPSHOT_INVALID
            )

        elif gpu_unknown:

            reason_codes.append(
                RESOURCE_REASON_GPU_SNAPSHOT_UNKNOWN
            )

        if any(
            (
                ram_stale,
                disk_stale,
                gpu_stale,
            )
        ):

            reason_codes.append(
                RESOURCE_REASON_SNAPSHOT_STALE
            )

        if (
            not ram_invalid
            and not ram_unknown
            and snapshot.ram_available_mb
            < requirement.estimated_peak_ram_mb
            + resolved_policy.reserve_ram_mb
        ):

            reason_codes.append(
                RESOURCE_REASON_RAM_BELOW_RESERVE
            )

        if (
            not disk_invalid
            and not disk_unknown
            and snapshot.disk_free_mb
            < requirement.estimated_disk_mb
            + resolved_policy.reserve_disk_mb
        ):

            reason_codes.append(
                RESOURCE_REASON_DISK_BELOW_RESERVE
            )

        selected_gpu = None

        if requirement.requires_gpu:

            selected_gpu = self.select_gpu(
                snapshot,
                requirement,
                resolved_policy,
            )

            if selected_gpu is None:

                if gpu_invalid:

                    reason_codes.append(
                        RESOURCE_REASON_GPU_SNAPSHOT_INVALID
                    )

                elif gpu_unknown or gpu_stale:

                    reason_codes.append(
                        RESOURCE_REASON_GPU_SNAPSHOT_UNKNOWN
                    )

                elif any(
                    gpu.cuda_available
                    for gpu in snapshot.gpu_devices
                ):

                    reason_codes.append(
                        RESOURCE_REASON_VRAM_BELOW_RESERVE
                    )

                else:

                    reason_codes.append(
                        RESOURCE_REASON_GPU_UNAVAILABLE
                    )

        if selected_gpu is not None and (
            selected_gpu.vram_free_mb
            < requirement.estimated_peak_vram_mb
            + resolved_policy.reserve_vram_mb
        ):

            reason_codes.append(
                RESOURCE_REASON_VRAM_BELOW_RESERVE
            )

        confirmation_required = False

        if (
            requirement.requires_gpu
            and requirement.cpu_fallback_supported
            and not requirement.cpu_fallback_confirmed
            and resolved_policy.cpu_fallback_requires_job_confirmation
        ):

            confirmation_required = True

            reason_codes.append(
                RESOURCE_REASON_CPU_FALLBACK_CONFIRMATION_REQUIRED
            )

        if requirement.heavy_job and active_heavy_jobs > 0:

            reason_codes.append(
                RESOURCE_REASON_HEAVY_JOB_ALREADY_ACTIVE
            )

        reason_codes = sorted(
            set(
                reason_codes
            )
        )

        shadow_decision = self.shadow_decision_for_reasons(
            requirement,
            reason_codes,
            confirmation_required,
        )

        feature_mode = resolved_policy.feature_modes.get(
            "resource_decision_v2_mode",
            FEATURE_MODE_MONITOR_ONLY,
        )

        return ResourceDecisionObservation(
            actual_decision=actual_decision.status
            if actual_decision
            else "",
            shadow_decision=shadow_decision,
            reason_codes=reason_codes,
            snapshot_status=validation.status,
            workload_class=requirement.workload_class,
            policy_fingerprint=getattr(
                resolved_policy,
                "fingerprint",
                "",
            ),
            would_block=shadow_decision == SHADOW_DECISION_WOULD_BLOCK,
            would_wait=shadow_decision == SHADOW_DECISION_WOULD_WAIT,
            confirmation_required=(
                shadow_decision
                == SHADOW_DECISION_CONFIRMATION_REQUIRED
            ),
            monitor_only=feature_mode != "enforced",
        )

    def shadow_decision_for_reasons(
        self,
        requirement,
        reason_codes,
        confirmation_required,
    ):

        if confirmation_required:

            return SHADOW_DECISION_CONFIRMATION_REQUIRED

        block_reasons = {
            RESOURCE_REASON_RAM_SNAPSHOT_INVALID,
            RESOURCE_REASON_DISK_SNAPSHOT_INVALID,
            RESOURCE_REASON_GPU_SNAPSHOT_INVALID,
            RESOURCE_REASON_RAM_BELOW_RESERVE,
            RESOURCE_REASON_GPU_UNAVAILABLE,
            RESOURCE_REASON_VRAM_BELOW_RESERVE,
        }

        wait_reasons = {
            RESOURCE_REASON_SNAPSHOT_STALE,
            RESOURCE_REASON_DISK_BELOW_RESERVE,
            RESOURCE_REASON_HEAVY_JOB_ALREADY_ACTIVE,
        }

        if requirement.heavy_job:

            block_reasons = block_reasons | {
                RESOURCE_REASON_RAM_SNAPSHOT_UNKNOWN,
                RESOURCE_REASON_DISK_SNAPSHOT_UNKNOWN,
                RESOURCE_REASON_GPU_SNAPSHOT_UNKNOWN,
            }

        elif requirement.workload_class == WORKLOAD_CLASS_LIGHT:

            block_reasons = block_reasons - {
                RESOURCE_REASON_GPU_SNAPSHOT_INVALID,
                RESOURCE_REASON_GPU_UNAVAILABLE,
                RESOURCE_REASON_VRAM_BELOW_RESERVE,
            }

        if any(
            reason in block_reasons
            for reason in reason_codes
        ):

            return SHADOW_DECISION_WOULD_BLOCK

        if any(
            reason in wait_reasons
            for reason in reason_codes
        ):

            return SHADOW_DECISION_WOULD_WAIT

        return SHADOW_DECISION_WOULD_READY

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

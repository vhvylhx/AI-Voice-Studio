from datetime import datetime
from uuid import uuid4

from models.resource_model import (
    FEATURE_MODE_DISABLED,
    FEATURE_MODE_ENFORCE,
    FEATURE_MODE_ENFORCED,
    FEATURE_MODE_MONITOR_ONLY,
    RUNTIME_GUARD_ACTION_DEESCALATE,
    RUNTIME_GUARD_ACTION_DEFER,
    RUNTIME_GUARD_ACTION_DEFER_HEAVY,
    RUNTIME_GUARD_ACTION_GRACEFUL_STOP,
    RUNTIME_GUARD_ACTION_KILL_TREE,
    RUNTIME_GUARD_ACTION_MARK_UNAVAILABLE,
    RUNTIME_GUARD_ACTION_NONE,
    RUNTIME_GUARD_ACTION_OBSERVE,
    RUNTIME_GUARD_ACTION_RECONCILE_LEASE,
    RUNTIME_GUARD_ACTION_RECONCILE_PROCESS,
    RUNTIME_GUARD_ACTION_REDUCE_BATCH,
    RUNTIME_GUARD_ACTION_REDUCE_CONCURRENCY,
    RUNTIME_GUARD_ACTION_REQUEST_PAUSE,
    RUNTIME_GUARD_ACTION_SKIP,
    RUNTIME_GUARD_ACTION_TERMINATE,
    RUNTIME_GUARD_STATE_DEFERRED,
    RUNTIME_GUARD_STATE_PROPOSED,
    RUNTIME_GUARD_STATE_SUPPRESSED,
    RUNTIME_PRESSURE_CRITICAL,
    RUNTIME_PRESSURE_EMERGENCY,
    RUNTIME_PRESSURE_HIGH,
    RUNTIME_PRESSURE_INVALID,
    RUNTIME_PRESSURE_NORMAL,
    RUNTIME_PRESSURE_STALE,
    RUNTIME_PRESSURE_UNKNOWN,
    RUNTIME_PRESSURE_WARNING,
    RUNTIME_REASON_ACTION_COOLDOWN,
    RUNTIME_REASON_ACTION_DEESCALATED,
    RUNTIME_REASON_ACTION_DUPLICATE_SUPPRESSED,
    RUNTIME_REASON_ACTION_ESCALATED,
    RUNTIME_REASON_ACTION_NOT_ALLOWED,
    RUNTIME_REASON_ACTION_RETRY_EXHAUSTED,
    RUNTIME_REASON_DESTRUCTIVE_ACTION_UNAVAILABLE,
    RUNTIME_REASON_DISK_BELOW_RESERVE,
    RUNTIME_REASON_HEAVY_JOB_ACTIVE,
    RUNTIME_REASON_IDENTITY_UNKNOWN,
    RUNTIME_REASON_LEASE_RECONCILIATION_REQUIRED,
    RUNTIME_REASON_MODE_DISABLED,
    RUNTIME_REASON_MODE_ENFORCE,
    RUNTIME_REASON_MODE_MONITOR_ONLY,
    RUNTIME_REASON_PRESSURE_CRITICAL,
    RUNTIME_REASON_PRESSURE_EMERGENCY,
    RUNTIME_REASON_PRESSURE_HIGH,
    RUNTIME_REASON_PRESSURE_NORMAL,
    RUNTIME_REASON_PRESSURE_UNKNOWN,
    RUNTIME_REASON_PRESSURE_WARNING,
    RUNTIME_REASON_PROCESS_RECONCILIATION_REQUIRED,
    RUNTIME_REASON_RAM_BELOW_CRITICAL,
    RUNTIME_REASON_RAM_BELOW_EMERGENCY,
    RUNTIME_REASON_RAM_BELOW_HIGH,
    RUNTIME_REASON_RAM_BELOW_WARNING,
    RUNTIME_REASON_SNAPSHOT_INVALID,
    RUNTIME_REASON_SNAPSHOT_STALE,
    RUNTIME_REASON_VRAM_BELOW_RESERVE,
    SNAPSHOT_STATUS_INVALID,
    SNAPSHOT_STATUS_STALE,
    SNAPSHOT_STATUS_UNKNOWN,
    WORKLOAD_CLASS_CPU_HEAVY,
    WORKLOAD_CLASS_GPU_INFERENCE,
    WORKLOAD_CLASS_GPU_TRAINING,
    WORKLOAD_CLASS_IO_HEAVY,
    ResourceSnapshot,
    RuntimeGuardObservation,
)
from services.resource_policy_service import ResourcePolicyService
from services.runtime_guard_action_executor import (
    SimulatedRuntimeGuardActionExecutor,
)


PRESSURE_ORDER = {
    RUNTIME_PRESSURE_UNKNOWN: -1,
    RUNTIME_PRESSURE_INVALID: -1,
    RUNTIME_PRESSURE_STALE: -1,
    RUNTIME_PRESSURE_NORMAL: 0,
    RUNTIME_PRESSURE_WARNING: 1,
    RUNTIME_PRESSURE_HIGH: 2,
    RUNTIME_PRESSURE_CRITICAL: 3,
    RUNTIME_PRESSURE_EMERGENCY: 4,
}


PRESSURE_REASON = {
    RUNTIME_PRESSURE_NORMAL: RUNTIME_REASON_PRESSURE_NORMAL,
    RUNTIME_PRESSURE_WARNING: RUNTIME_REASON_PRESSURE_WARNING,
    RUNTIME_PRESSURE_HIGH: RUNTIME_REASON_PRESSURE_HIGH,
    RUNTIME_PRESSURE_CRITICAL: RUNTIME_REASON_PRESSURE_CRITICAL,
    RUNTIME_PRESSURE_EMERGENCY: RUNTIME_REASON_PRESSURE_EMERGENCY,
    RUNTIME_PRESSURE_UNKNOWN: RUNTIME_REASON_PRESSURE_UNKNOWN,
    RUNTIME_PRESSURE_STALE: RUNTIME_REASON_SNAPSHOT_STALE,
    RUNTIME_PRESSURE_INVALID: RUNTIME_REASON_SNAPSHOT_INVALID,
}


class RuntimeGuard:

    def __init__(
        self,
        policy_service=None,
        executor=None,
        clock=None,
    ):

        self.policy_service = (
            policy_service
            or ResourcePolicyService()
        )

        self.executor = (
            executor
            or SimulatedRuntimeGuardActionExecutor()
        )

        self.clock = clock or datetime.now

        self.last_observation = None

        self.action_attempts = {}

        self.failed_at = {}

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

    def resolve_policy(
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

    def guard_mode(
        self,
        policy=None,
    ):

        policy = policy or self.resolve_policy()

        modes = getattr(
            policy,
            "feature_modes",
            {},
        )

        mode = modes.get(
            "runtime_guard_mode",
            modes.get(
                "runtime_pressure_guard_mode",
                FEATURE_MODE_MONITOR_ONLY,
            ),
        )

        if mode == FEATURE_MODE_ENFORCED:

            return FEATURE_MODE_ENFORCE

        return mode

    def mode_reason(
        self,
        mode,
    ):

        if mode == FEATURE_MODE_DISABLED:

            return RUNTIME_REASON_MODE_DISABLED

        if mode == FEATURE_MODE_ENFORCE:

            return RUNTIME_REASON_MODE_ENFORCE

        return RUNTIME_REASON_MODE_MONITOR_ONLY

    def evaluate(
        self,
        snapshot,
        workload_class="light",
        job_id="",
        lease_observation=None,
        process_observation=None,
        owner_id="",
        active_heavy_jobs=0,
        action_attempt=0,
    ):

        policy = self.resolve_policy()
        mode = self.guard_mode(
            policy
        )

        pressure_level, reason_codes = self.classify_pressure(
            snapshot,
            policy,
            workload_class=workload_class,
            active_heavy_jobs=active_heavy_jobs,
        )

        previous_level = (
            self.last_observation.pressure_level
            if self.last_observation is not None
            else RUNTIME_PRESSURE_UNKNOWN
        )

        reason_codes.append(
            self.mode_reason(
                mode
            )
        )

        lease_id = self.extract_id(
            lease_observation,
            "lease_id",
        )
        process_id = self.extract_id(
            process_observation,
            "process_id",
        ) or self.extract_nested_process_id(
            process_observation
        )

        reconciliation_required = False

        if self.needs_lease_reconciliation(
            lease_observation,
        ):

            reason_codes.append(
                RUNTIME_REASON_LEASE_RECONCILIATION_REQUIRED
            )
            reconciliation_required = True

        if self.needs_process_reconciliation(
            process_observation,
        ):

            reason_codes.append(
                RUNTIME_REASON_PROCESS_RECONCILIATION_REQUIRED
            )
            reconciliation_required = True

        if self.process_identity_unknown(
            process_observation,
        ):

            reason_codes.append(
                RUNTIME_REASON_IDENTITY_UNKNOWN
            )

        action = self.recommend_action(
            pressure_level,
            workload_class,
            reconciliation_required,
            process_observation,
            policy,
        )

        observation = RuntimeGuardObservation(
            observation_id=f"guard_{uuid4().hex[:12]}",
            observed_at=self.now().isoformat(),
            pressure_level=pressure_level,
            previous_pressure_level=previous_level,
            action=action,
            action_state=RUNTIME_GUARD_STATE_PROPOSED,
            reason_codes=sorted(
                set(
                    reason_codes
                )
            ),
            snapshot_status=getattr(
                ResourceSnapshot.from_dict(
                    snapshot
                ),
                "validation_status",
                SNAPSHOT_STATUS_UNKNOWN,
            ),
            workload_class=workload_class,
            job_id=job_id,
            lease_id=lease_id,
            process_id=process_id,
            owner_id=owner_id,
            policy_fingerprint=getattr(
                policy,
                "fingerprint",
                "",
            ),
            action_attempt=action_attempt,
            reconciliation_required=reconciliation_required,
            action_allowed=False,
            metadata={
                "active_heavy_jobs": active_heavy_jobs,
            },
            provenance={
                "source": "runtime_guard_phase6",
                "mode": mode,
            },
        )

        self.apply_state_machine(
            observation,
            policy,
            mode,
        )

        self.last_observation = observation

        return observation

    def classify_pressure(
        self,
        snapshot,
        policy,
        workload_class="light",
        active_heavy_jobs=0,
    ):

        snapshot = ResourceSnapshot.from_dict(
            snapshot
        )

        reason_codes = []

        if snapshot.validation_status == SNAPSHOT_STATUS_INVALID:

            return RUNTIME_PRESSURE_INVALID, [
                RUNTIME_REASON_SNAPSHOT_INVALID
            ]

        if snapshot.validation_status == SNAPSHOT_STATUS_STALE:

            return RUNTIME_PRESSURE_STALE, [
                RUNTIME_REASON_SNAPSHOT_STALE
            ]

        if snapshot.validation_status == SNAPSHOT_STATUS_UNKNOWN:

            return RUNTIME_PRESSURE_UNKNOWN, [
                RUNTIME_REASON_PRESSURE_UNKNOWN
            ]

        level = RUNTIME_PRESSURE_NORMAL

        ram_available = int(
            snapshot.ram_available_mb
        )
        thresholds = getattr(
            policy,
            "ram_pressure_thresholds",
            {},
        )

        checks = [
            (
                "emergency_available_ram_mb",
                RUNTIME_PRESSURE_EMERGENCY,
                RUNTIME_REASON_RAM_BELOW_EMERGENCY,
            ),
            (
                "critical_available_ram_mb",
                RUNTIME_PRESSURE_CRITICAL,
                RUNTIME_REASON_RAM_BELOW_CRITICAL,
            ),
            (
                "high_available_ram_mb",
                RUNTIME_PRESSURE_HIGH,
                RUNTIME_REASON_RAM_BELOW_HIGH,
            ),
            (
                "warning_available_ram_mb",
                RUNTIME_PRESSURE_WARNING,
                RUNTIME_REASON_RAM_BELOW_WARNING,
            ),
        ]

        for key, candidate, reason in checks:

            if ram_available <= int(
                thresholds.get(
                    key,
                    0,
                )
            ):

                level = self.max_level(
                    level,
                    candidate,
                )
                reason_codes.append(
                    reason
                )
                break

        if int(
            snapshot.disk_free_mb
        ) < int(
            policy.reserve_disk_mb
        ):

            level = self.max_level(
                level,
                RUNTIME_PRESSURE_CRITICAL,
            )
            reason_codes.append(
                RUNTIME_REASON_DISK_BELOW_RESERVE
            )

        for gpu in snapshot.gpu_devices:

            gpu = getattr(
                gpu,
                "to_dict",
                lambda: gpu,
            )()

            if int(
                gpu.get(
                    "vram_free_mb",
                    0,
                )
            ) < int(
                policy.reserve_vram_mb
            ):

                level = self.max_level(
                    level,
                    RUNTIME_PRESSURE_CRITICAL,
                )
                reason_codes.append(
                    RUNTIME_REASON_VRAM_BELOW_RESERVE
                )
                break

        if active_heavy_jobs:

            reason_codes.append(
                RUNTIME_REASON_HEAVY_JOB_ACTIVE
            )

            if workload_class in (
                WORKLOAD_CLASS_CPU_HEAVY,
                WORKLOAD_CLASS_GPU_INFERENCE,
                WORKLOAD_CLASS_GPU_TRAINING,
                WORKLOAD_CLASS_IO_HEAVY,
            ):

                level = self.max_level(
                    level,
                    RUNTIME_PRESSURE_HIGH,
                )

        reason_codes.append(
            PRESSURE_REASON.get(
                level,
                RUNTIME_REASON_PRESSURE_UNKNOWN,
            )
        )

        return level, sorted(
            set(
                reason_codes
            )
        )

    def recommend_action(
        self,
        pressure_level,
        workload_class,
        reconciliation_required,
        process_observation,
        policy,
    ):

        if pressure_level in (
            RUNTIME_PRESSURE_UNKNOWN,
            RUNTIME_PRESSURE_INVALID,
            RUNTIME_PRESSURE_STALE,
        ):

            return RUNTIME_GUARD_ACTION_DEFER

        if reconciliation_required:

            if self.needs_process_reconciliation(
                process_observation,
            ):

                return RUNTIME_GUARD_ACTION_RECONCILE_PROCESS

            return RUNTIME_GUARD_ACTION_RECONCILE_LEASE

        if pressure_level == RUNTIME_PRESSURE_NORMAL:

            return RUNTIME_GUARD_ACTION_OBSERVE

        if pressure_level == RUNTIME_PRESSURE_WARNING:

            if workload_class in (
                WORKLOAD_CLASS_CPU_HEAVY,
                WORKLOAD_CLASS_GPU_INFERENCE,
                WORKLOAD_CLASS_GPU_TRAINING,
                WORKLOAD_CLASS_IO_HEAVY,
            ):

                return RUNTIME_GUARD_ACTION_DEFER_HEAVY

            return RUNTIME_GUARD_ACTION_REDUCE_BATCH

        if pressure_level == RUNTIME_PRESSURE_HIGH:

            if getattr(
                policy,
                "allow_simulated_pause",
                False,
            ):

                return RUNTIME_GUARD_ACTION_REQUEST_PAUSE

            return RUNTIME_GUARD_ACTION_REDUCE_CONCURRENCY

        if pressure_level == RUNTIME_PRESSURE_CRITICAL:

            return RUNTIME_GUARD_ACTION_GRACEFUL_STOP

        if pressure_level == RUNTIME_PRESSURE_EMERGENCY:

            return RUNTIME_GUARD_ACTION_KILL_TREE

        return RUNTIME_GUARD_ACTION_NONE

    def apply_state_machine(
        self,
        observation,
        policy,
        mode,
    ):

        if mode == FEATURE_MODE_DISABLED:

            observation.action = RUNTIME_GUARD_ACTION_SKIP
            observation.action_state = RUNTIME_GUARD_STATE_DEFERRED
            observation.action_allowed = False
            return observation

        if self.deescalation_needed(
            observation,
            policy,
        ):

            observation.action = RUNTIME_GUARD_ACTION_DEESCALATE
            observation.reason_codes = sorted(
                set(
                    observation.reason_codes
                    + [
                        RUNTIME_REASON_ACTION_DEESCALATED
                    ]
                )
            )

        elif self.is_escalation(
            observation,
        ):

            observation.escalation_count = (
                self.last_observation.escalation_count + 1
                if self.last_observation is not None
                else 1
            )
            observation.reason_codes = sorted(
                set(
                    observation.reason_codes
                    + [
                        RUNTIME_REASON_ACTION_ESCALATED
                    ]
                )
            )

        if self.is_duplicate(
            observation,
        ):

            observation.duplicate_suppressed = True
            observation.action_state = RUNTIME_GUARD_STATE_SUPPRESSED
            observation.reason_codes = sorted(
                set(
                    observation.reason_codes
                    + [
                        RUNTIME_REASON_ACTION_DUPLICATE_SUPPRESSED
                    ]
                )
            )
            return observation

        if self.cooldown_active(
            observation,
            policy,
        ):

            observation.cooldown_active = True
            observation.action_state = RUNTIME_GUARD_STATE_SUPPRESSED
            observation.reason_codes = sorted(
                set(
                    observation.reason_codes
                    + [
                        RUNTIME_REASON_ACTION_COOLDOWN
                    ]
                )
            )
            return observation

        if self.retry_exhausted(
            observation,
            policy,
        ):

            observation.action_state = RUNTIME_GUARD_STATE_DEFERRED
            observation.reason_codes = sorted(
                set(
                    observation.reason_codes
                    + [
                        RUNTIME_REASON_ACTION_RETRY_EXHAUSTED
                    ]
                )
            )
            return observation

        if mode != FEATURE_MODE_ENFORCE:

            return observation

        observation.action_allowed = self.action_allowed(
            observation,
            policy,
            mode,
        )

        if not observation.action_allowed:

            observation.action_state = RUNTIME_GUARD_STATE_DEFERRED
            observation.reason_codes = sorted(
                set(
                    observation.reason_codes
                    + [
                        RUNTIME_REASON_ACTION_NOT_ALLOWED
                    ]
                )
            )
            return observation

        if mode == FEATURE_MODE_ENFORCE:

            result = self.executor.execute(
                observation,
                policy,
            )
            observation.action_state = result.get(
                "state",
                RUNTIME_GUARD_STATE_DEFERRED,
            )
            observation.action_executed = bool(
                result.get(
                    "executed",
                    False,
                )
            )
            observation.action_simulated = bool(
                result.get(
                    "simulated",
                    False,
                )
            )
            observation.reason_codes = sorted(
                set(
                    observation.reason_codes
                    + list(
                        result.get(
                            "reason_codes",
                            [],
                        )
                    )
                )
            )
            observation.metadata["audit"] = result.get(
                "audit",
                [],
            )

        return observation

    def action_allowed(
        self,
        observation,
        policy,
        mode,
    ):

        if observation.action in (
            RUNTIME_GUARD_ACTION_OBSERVE,
            RUNTIME_GUARD_ACTION_DEFER_HEAVY,
            RUNTIME_GUARD_ACTION_REDUCE_BATCH,
            RUNTIME_GUARD_ACTION_REDUCE_CONCURRENCY,
            RUNTIME_GUARD_ACTION_DEESCALATE,
            RUNTIME_GUARD_ACTION_RECONCILE_LEASE,
            RUNTIME_GUARD_ACTION_RECONCILE_PROCESS,
            RUNTIME_GUARD_ACTION_MARK_UNAVAILABLE,
            RUNTIME_GUARD_ACTION_DEFER,
        ):

            return True

        if observation.action == RUNTIME_GUARD_ACTION_REQUEST_PAUSE:

            return bool(
                policy.allow_simulated_pause
            )

        if observation.action == RUNTIME_GUARD_ACTION_GRACEFUL_STOP:

            return bool(
                policy.allow_simulated_graceful_stop
            )

        if observation.action in (
            RUNTIME_GUARD_ACTION_TERMINATE,
            RUNTIME_GUARD_ACTION_KILL_TREE,
        ):

            observation.reason_codes = sorted(
                set(
                    observation.reason_codes
                    + [
                        RUNTIME_REASON_DESTRUCTIVE_ACTION_UNAVAILABLE
                    ]
                )
            )
            return False

        return mode != FEATURE_MODE_DISABLED

    def max_level(
        self,
        left,
        right,
    ):

        if PRESSURE_ORDER[right] > PRESSURE_ORDER[left]:

            return right

        return left

    def is_escalation(
        self,
        observation,
    ):

        return (
            self.last_observation is not None
            and PRESSURE_ORDER.get(
                observation.pressure_level,
                -1,
            )
            > PRESSURE_ORDER.get(
                self.last_observation.pressure_level,
                -1,
            )
        )

    def deescalation_needed(
        self,
        observation,
        policy,
    ):

        if self.last_observation is None:

            return False

        if observation.pressure_level in (
            RUNTIME_PRESSURE_UNKNOWN,
            RUNTIME_PRESSURE_INVALID,
            RUNTIME_PRESSURE_STALE,
        ):

            return False

        if PRESSURE_ORDER.get(
            observation.pressure_level,
            -1,
        ) >= PRESSURE_ORDER.get(
            self.last_observation.pressure_level,
            -1,
        ):

            return False

        try:

            previous = datetime.fromisoformat(
                self.last_observation.observed_at
            )

        except Exception:

            return False

        stable = (
            self.now()
            - previous
        ).total_seconds() >= float(
            policy.deescalation_stable_seconds
        )

        observation.hysteresis_active = not stable

        return stable

    def is_duplicate(
        self,
        observation,
    ):

        if self.last_observation is None:

            return False

        return (
            observation.action == self.last_observation.action
            and observation.pressure_level
            == self.last_observation.pressure_level
            and observation.job_id == self.last_observation.job_id
            and observation.lease_id == self.last_observation.lease_id
            and observation.process_id == self.last_observation.process_id
        )

    def cooldown_active(
        self,
        observation,
        policy,
    ):

        if self.last_observation is None:

            return False

        if self.is_escalation(
            observation,
        ):

            return False

        try:

            previous = datetime.fromisoformat(
                self.last_observation.observed_at
            )

        except Exception:

            return False

        return (
            self.now()
            - previous
        ).total_seconds() < float(
            policy.action_cooldown_seconds
        )

    def retry_exhausted(
        self,
        observation,
        policy,
    ):

        key = (
            observation.action,
            observation.job_id,
            observation.lease_id,
            observation.process_id,
        )
        attempts = self.action_attempts.get(
            key,
            observation.action_attempt,
        )

        if attempts >= int(
            policy.max_action_attempts
        ):

            return True

        self.action_attempts[key] = attempts + 1
        observation.action_attempt = attempts + 1

        return False

    def extract_id(
        self,
        value,
        name,
    ):

        if value is None:

            return ""

        if isinstance(
            value,
            dict,
        ):

            return value.get(
                name,
                "",
            )

        return getattr(
            value,
            name,
            "",
        )

    def extract_nested_process_id(
        self,
        value,
    ):

        if isinstance(
            value,
            dict,
        ):

            identity = value.get(
                "process_identity",
                {},
            )
            if isinstance(
                identity,
                dict,
            ):

                return identity.get(
                    "process_id",
                    "",
                )

        identity = getattr(
            value,
            "process_identity",
            {},
        )

        if isinstance(
            identity,
            dict,
        ):

            return identity.get(
                "process_id",
                "",
            )

        return ""

    def needs_lease_reconciliation(
        self,
        lease_observation,
    ):

        if lease_observation is None:

            return False

        if isinstance(
            lease_observation,
            dict,
        ):

            return bool(
                lease_observation.get(
                    "would_reconcile",
                    False,
                )
                or lease_observation.get(
                    "is_expired",
                    False,
                )
                or lease_observation.get(
                    "is_stale",
                    False,
                )
            )

        return bool(
            getattr(
                lease_observation,
                "would_reconcile",
                False,
            )
            or getattr(
                lease_observation,
                "is_expired",
                False,
            )
            or getattr(
                lease_observation,
                "is_stale",
                False,
            )
        )

    def needs_process_reconciliation(
        self,
        process_observation,
    ):

        if process_observation is None:

            return False

        if isinstance(
            process_observation,
            dict,
        ):

            return bool(
                process_observation.get(
                    "would_reconcile",
                    False,
                )
                or process_observation.get(
                    "is_orphan",
                    False,
                )
                or not process_observation.get(
                    "identity_valid",
                    True,
                )
            )

        return bool(
            getattr(
                process_observation,
                "would_reconcile",
                False,
            )
            or getattr(
                process_observation,
                "is_orphan",
                False,
            )
            or not getattr(
                process_observation,
                "identity_valid",
                True,
            )
        )

    def process_identity_unknown(
        self,
        process_observation,
    ):

        if process_observation is None:

            return False

        reason_codes = (
            process_observation.get(
                "reason_codes",
                [],
            )
            if isinstance(
                process_observation,
                dict,
            )
            else getattr(
                process_observation,
                "reason_codes",
                [],
            )
        )

        return "process_identity_unknown" in reason_codes

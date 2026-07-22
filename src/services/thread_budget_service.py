from datetime import datetime
from uuid import uuid4

from models.resource_model import (
    FEATURE_MODE_DISABLED,
    FEATURE_MODE_ENFORCE,
    FEATURE_MODE_ENFORCED,
    FEATURE_MODE_MONITOR_ONLY,
    RUNTIME_PRESSURE_CRITICAL,
    RUNTIME_PRESSURE_EMERGENCY,
    THREAD_BUDGET_ACTION_APPLY_ENVIRONMENT,
    THREAD_BUDGET_ACTION_APPLY_RUNTIME,
    THREAD_BUDGET_ACTION_ASSIGN,
    THREAD_BUDGET_ACTION_DEFER,
    THREAD_BUDGET_ACTION_DEFER_JOB,
    THREAD_BUDGET_ACTION_DISABLE_NESTED,
    THREAD_BUDGET_ACTION_RECONCILE,
    THREAD_BUDGET_ACTION_REDUCE,
    THREAD_BUDGET_ACTION_RESTORE,
    THREAD_BUDGET_ACTION_SKIP,
    THREAD_BUDGET_STATE_DEFERRED,
    THREAD_BUDGET_STATE_PROPOSED,
    THREAD_BUDGET_STATE_SUPPRESSED,
    THREAD_BUDGET_STATUS_CONSTRAINED,
    THREAD_BUDGET_STATUS_DEFERRED,
    THREAD_BUDGET_STATUS_INVALID,
    THREAD_BUDGET_STATUS_OVERSUBSCRIBED,
    THREAD_BUDGET_STATUS_STALE,
    THREAD_BUDGET_STATUS_UNKNOWN,
    THREAD_BUDGET_STATUS_VALID,
    THREAD_REASON_ACTION_COOLDOWN,
    THREAD_REASON_ACTION_DUPLICATE_SUPPRESSED,
    THREAD_REASON_ACTION_NOT_ALLOWED,
    THREAD_REASON_ACTION_RETRY_EXHAUSTED,
    THREAD_REASON_AVAILABLE,
    THREAD_REASON_CONSTRAINED,
    THREAD_REASON_ENVIRONMENT_PLAN_REQUIRED,
    THREAD_REASON_HEAVY_JOB_LIMIT_REACHED,
    THREAD_REASON_IDENTITY_UNKNOWN,
    THREAD_REASON_INVALID,
    THREAD_REASON_LEASE_RECONCILIATION_REQUIRED,
    THREAD_REASON_MODE_DISABLED,
    THREAD_REASON_MODE_ENFORCE,
    THREAD_REASON_MODE_MONITOR_ONLY,
    THREAD_REASON_NESTED_PARALLELISM,
    THREAD_REASON_OVERSUBSCRIBED,
    THREAD_REASON_POLICY_MISMATCH,
    THREAD_REASON_PROCESS_RECONCILIATION_REQUIRED,
    THREAD_REASON_PROCESS_THREAD_COUNT_UNKNOWN,
    THREAD_REASON_REQUEST_ABOVE_WORKLOAD_LIMIT,
    THREAD_REASON_RESERVE_VIOLATION,
    THREAD_REASON_RESTORE_REQUIRED,
    THREAD_REASON_RUNTIME_PLAN_REQUIRED,
    THREAD_REASON_STALE,
    THREAD_REASON_TOTAL_ABOVE_POLICY_LIMIT,
    THREAD_REASON_UNKNOWN,
    WORKLOAD_CLASS_CPU_HEAVY,
    WORKLOAD_CLASS_GPU_INFERENCE,
    WORKLOAD_CLASS_GPU_TRAINING,
    WORKLOAD_CLASS_IO_HEAVY,
    WORKLOAD_CLASS_LIGHT,
    WORKLOAD_CLASSES,
    ThreadBudgetObservation,
)
from services.resource_policy_service import ResourcePolicyService
from services.thread_budget_executor import SimulatedThreadBudgetExecutor


HEAVY_WORKLOADS = (
    WORKLOAD_CLASS_CPU_HEAVY,
    WORKLOAD_CLASS_GPU_INFERENCE,
    WORKLOAD_CLASS_GPU_TRAINING,
    WORKLOAD_CLASS_IO_HEAVY,
)

ENVIRONMENT_VARIABLES = (
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "BLIS_NUM_THREADS",
    "TOKENIZERS_PARALLELISM",
    "RAYON_NUM_THREADS",
    "TORCH_NUM_THREADS",
    "TORCH_NUM_INTEROP_THREADS",
)

NUMERIC_ENVIRONMENT_VARIABLES = tuple(
    name
    for name in ENVIRONMENT_VARIABLES
    if name != "TOKENIZERS_PARALLELISM"
)


class ThreadBudgetService:

    def __init__(
        self,
        policy_service=None,
        executor=None,
        clock=None,
        supported_environment_variables=None,
    ):

        self.policy_service = policy_service or ResourcePolicyService()
        self.executor = executor or SimulatedThreadBudgetExecutor()
        self.clock = clock or datetime.now
        self.supported_environment_variables = tuple(
            supported_environment_variables
            or ENVIRONMENT_VARIABLES
        )
        self.last_observation = None
        self.action_attempts = {}

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

    def mode(
        self,
        policy,
    ):

        mode = getattr(
            policy,
            "feature_modes",
            {},
        ).get(
            "thread_budget_mode",
            FEATURE_MODE_MONITOR_ONLY,
        )

        if mode == FEATURE_MODE_ENFORCED:

            return FEATURE_MODE_ENFORCE

        return mode

    def mode_reason(
        self,
        mode,
    ):

        if mode == FEATURE_MODE_DISABLED:

            return THREAD_REASON_MODE_DISABLED

        if mode == FEATURE_MODE_ENFORCE:

            return THREAD_REASON_MODE_ENFORCE

        return THREAD_REASON_MODE_MONITOR_ONLY

    def evaluate(
        self,
        total_logical_cpu_threads,
        workload_class=WORKLOAD_CLASS_LIGHT,
        requested_threads=1,
        active_budgets=None,
        active_job_count=0,
        active_heavy_job_count=0,
        job_id="",
        lease_id="",
        process_id="",
        owner_id="",
        environment=None,
        runtime_settings=None,
        outer_worker_threads=1,
        process_thread_count=None,
        lease_observation=None,
        process_observation=None,
        runtime_guard_observation=None,
        release=False,
        previous_environment_plan=None,
        previous_runtime_plan=None,
        snapshot_status="valid",
        action_attempt=0,
    ):

        policy = self.resolve_policy()
        mode = self.mode(
            policy
        )
        reason_codes = [
            self.mode_reason(
                mode
            )
        ]

        if mode == FEATURE_MODE_DISABLED:

            observation = self.build_observation(
                policy=policy,
                mode=mode,
                status=THREAD_BUDGET_STATUS_DEFERRED,
                workload_class=workload_class,
                requested_threads=requested_threads,
                resolved_threads=0,
                total_logical_cpu_threads=total_logical_cpu_threads,
                reserve_cpu_threads=getattr(
                    policy,
                    "reserve_cpu_threads",
                    0,
                ),
                available_budget_threads=0,
                active_total_threads=0,
                projected_total_threads=0,
                action=THREAD_BUDGET_ACTION_SKIP,
                action_state=THREAD_BUDGET_STATE_DEFERRED,
                reason_codes=reason_codes,
                job_id=job_id,
                lease_id=lease_id,
                process_id=process_id,
                owner_id=owner_id,
            )
            self.last_observation = observation
            return observation

        active_budgets = [
            ThreadBudgetObservation.from_dict(
                item
            )
            for item in (
                active_budgets
                or []
            )
        ]

        workload_class = self.normalize_workload(
            workload_class
        )
        total_logical_cpu_threads = self.safe_int(
            total_logical_cpu_threads
        )
        requested_threads = self.safe_int(
            requested_threads
        )

        status = THREAD_BUDGET_STATUS_VALID

        if snapshot_status == "stale":

            status = THREAD_BUDGET_STATUS_STALE
            reason_codes.append(
                THREAD_REASON_STALE
            )

        elif snapshot_status == "invalid" or requested_threads <= 0:

            status = THREAD_BUDGET_STATUS_INVALID
            reason_codes.append(
                THREAD_REASON_INVALID
            )

        elif total_logical_cpu_threads <= 0:

            status = THREAD_BUDGET_STATUS_UNKNOWN
            reason_codes.append(
                THREAD_REASON_UNKNOWN
            )

        max_total = int(
            getattr(
                policy,
                "max_total_cpu_threads",
                1,
            )
        )
        reserve = int(
            getattr(
                policy,
                "reserve_cpu_threads",
                0,
            )
        )
        total_cap = min(
            max_total,
            total_logical_cpu_threads,
        )
        available = max(
            0,
            total_cap - reserve,
        )
        active_total = sum(
            max(
                0,
                int(
                    item.resolved_threads
                ),
            )
            for item in active_budgets
        )
        remaining = max(
            0,
            available - active_total,
        )
        workload_limit = self.workload_limit(
            policy,
            workload_class,
        )

        resolved_threads = min(
            max(
                requested_threads,
                0,
            ),
            workload_limit,
            remaining,
        )

        if status in (
            THREAD_BUDGET_STATUS_UNKNOWN,
            THREAD_BUDGET_STATUS_STALE,
            THREAD_BUDGET_STATUS_INVALID,
        ):

            resolved_threads = 0

        projected_total = active_total + resolved_threads
        oversubscribed = False

        if requested_threads > workload_limit:

            status = THREAD_BUDGET_STATUS_CONSTRAINED
            reason_codes.extend(
                [
                    THREAD_REASON_CONSTRAINED,
                    THREAD_REASON_REQUEST_ABOVE_WORKLOAD_LIMIT,
                ]
            )

        if requested_threads > resolved_threads and status == (
            THREAD_BUDGET_STATUS_VALID
        ):

            status = THREAD_BUDGET_STATUS_CONSTRAINED
            reason_codes.append(
                THREAD_REASON_CONSTRAINED
            )

        budget_known = status not in (
            THREAD_BUDGET_STATUS_UNKNOWN,
            THREAD_BUDGET_STATUS_STALE,
            THREAD_BUDGET_STATUS_INVALID,
        )

        if budget_known and active_total + requested_threads > available:

            oversubscribed = True
            status = THREAD_BUDGET_STATUS_OVERSUBSCRIBED
            reason_codes.extend(
                [
                    THREAD_REASON_OVERSUBSCRIBED,
                    THREAD_REASON_TOTAL_ABOVE_POLICY_LIMIT,
                ]
            )

        if budget_known and available <= 0:

            oversubscribed = True
            status = THREAD_BUDGET_STATUS_OVERSUBSCRIBED
            reason_codes.append(
                THREAD_REASON_RESERVE_VIOLATION
            )

        if (
            budget_known
            and
            workload_class in HEAVY_WORKLOADS
            and active_heavy_job_count >= int(
                policy.max_parallel_heavy_jobs
            )
        ):

            oversubscribed = True
            status = THREAD_BUDGET_STATUS_OVERSUBSCRIBED
            reason_codes.append(
                THREAD_REASON_HEAVY_JOB_LIMIT_REACHED
            )

        nested = self.detect_nested_parallelism(
            environment
            or {},
            runtime_settings
            or {},
            outer_worker_threads,
        )

        if nested and not getattr(
            policy,
            "allow_nested_parallelism",
            False,
        ):

            reason_codes.append(
                THREAD_REASON_NESTED_PARALLELISM
            )

        if process_thread_count is None:

            reason_codes.append(
                THREAD_REASON_PROCESS_THREAD_COUNT_UNKNOWN
            )

        elif budget_known and resolved_threads and int(
            process_thread_count
        ) > resolved_threads:

            oversubscribed = True
            status = THREAD_BUDGET_STATUS_OVERSUBSCRIBED
            reason_codes.append(
                THREAD_REASON_OVERSUBSCRIBED
            )

        reconciliation_required = False

        if self.needs_lease_reconciliation(
            lease_observation,
        ):

            reconciliation_required = True
            reason_codes.append(
                THREAD_REASON_LEASE_RECONCILIATION_REQUIRED
            )

        if self.needs_process_reconciliation(
            process_observation,
        ):

            reconciliation_required = True
            reason_codes.append(
                THREAD_REASON_PROCESS_RECONCILIATION_REQUIRED
            )

        if self.process_identity_unknown(
            process_observation,
        ):

            reconciliation_required = True
            reason_codes.append(
                THREAD_REASON_IDENTITY_UNKNOWN
            )

        if self.policy_mismatch(
            policy,
            lease_observation,
            process_observation,
        ):

            reconciliation_required = True
            reason_codes.append(
                THREAD_REASON_POLICY_MISMATCH
            )

        if self.runtime_pressure_reduces_budget(
            runtime_guard_observation,
        ):

            oversubscribed = True
            status = THREAD_BUDGET_STATUS_OVERSUBSCRIBED
            reason_codes.append(
                THREAD_REASON_OVERSUBSCRIBED
            )

        environment_plan = self.environment_plan(
            resolved_threads,
            environment
            or {},
            supported_variables=self.supported_environment_variables,
        )
        runtime_plan = self.runtime_plan(
            resolved_threads,
            runtime_settings
            or {},
        )

        if environment_plan:

            reason_codes.append(
                THREAD_REASON_ENVIRONMENT_PLAN_REQUIRED
            )

        if runtime_plan:

            reason_codes.append(
                THREAD_REASON_RUNTIME_PLAN_REQUIRED
            )

        restore_required = bool(
            release
            and getattr(
                policy,
                "thread_budget_restore_on_release",
                True,
            )
            and (
                previous_environment_plan
                or previous_runtime_plan
            )
        )

        if restore_required:

            reason_codes.append(
                THREAD_REASON_RESTORE_REQUIRED
            )

        if status == THREAD_BUDGET_STATUS_VALID:

            reason_codes.append(
                THREAD_REASON_AVAILABLE
            )

        action = self.recommend_action(
            status=status,
            oversubscribed=oversubscribed,
            nested=nested,
            environment_plan=environment_plan,
            runtime_plan=runtime_plan,
            reconciliation_required=reconciliation_required,
            restore_required=restore_required,
        )

        observation = self.build_observation(
            policy=policy,
            mode=mode,
            status=status,
            workload_class=workload_class,
            requested_threads=requested_threads,
            resolved_threads=resolved_threads,
            total_logical_cpu_threads=total_logical_cpu_threads,
            reserve_cpu_threads=reserve,
            available_budget_threads=available,
            active_total_threads=active_total,
            projected_total_threads=projected_total,
            action=action,
            action_state=THREAD_BUDGET_STATE_PROPOSED,
            reason_codes=reason_codes,
            job_id=job_id,
            lease_id=lease_id
            or self.extract_id(
                lease_observation,
                "lease_id",
            ),
            process_id=process_id
            or self.extract_process_id(
                process_observation,
            ),
            owner_id=owner_id,
            active_job_count=active_job_count,
            active_heavy_job_count=active_heavy_job_count,
            oversubscribed=oversubscribed,
            nested_parallelism_detected=nested,
            environment_plan=environment_plan,
            runtime_plan=runtime_plan,
            reconciliation_required=reconciliation_required,
            restore_required=restore_required,
            action_attempt=action_attempt,
            metadata={
                "workload_limit": workload_limit,
                "remaining_budget_threads": remaining,
                "outer_worker_threads": outer_worker_threads,
                "process_thread_count": process_thread_count,
            },
        )

        self.apply_state_machine(
            observation,
            policy,
            mode,
        )

        self.last_observation = observation

        return observation

    def build_observation(
        self,
        policy,
        mode,
        status,
        workload_class,
        requested_threads,
        resolved_threads,
        total_logical_cpu_threads,
        reserve_cpu_threads,
        available_budget_threads,
        active_total_threads,
        projected_total_threads,
        action,
        action_state,
        reason_codes,
        job_id="",
        lease_id="",
        process_id="",
        owner_id="",
        active_job_count=0,
        active_heavy_job_count=0,
        oversubscribed=False,
        nested_parallelism_detected=False,
        environment_plan=None,
        runtime_plan=None,
        reconciliation_required=False,
        restore_required=False,
        action_attempt=0,
        metadata=None,
    ):

        return ThreadBudgetObservation(
            observation_id=f"thread_obs_{uuid4().hex[:12]}",
            budget_id=f"thread_budget_{uuid4().hex[:12]}",
            job_id=job_id,
            lease_id=lease_id,
            process_id=process_id,
            owner_id=owner_id,
            observed_at=self.now().isoformat(),
            mode=mode,
            status=status,
            workload_class=workload_class,
            requested_threads=int(
                requested_threads
            ),
            resolved_threads=int(
                resolved_threads
            ),
            active_job_count=int(
                active_job_count
            ),
            active_heavy_job_count=int(
                active_heavy_job_count
            ),
            total_logical_cpu_threads=int(
                total_logical_cpu_threads
            ),
            reserve_cpu_threads=int(
                reserve_cpu_threads
            ),
            available_budget_threads=int(
                available_budget_threads
            ),
            active_total_threads=int(
                active_total_threads
            ),
            projected_total_threads=int(
                projected_total_threads
            ),
            oversubscribed=bool(
                oversubscribed
            ),
            nested_parallelism_detected=bool(
                nested_parallelism_detected
            ),
            environment_plan=environment_plan
            or {},
            runtime_plan=runtime_plan
            or {},
            action=action,
            action_state=action_state,
            reason_codes=sorted(
                set(
                    reason_codes
                )
            ),
            action_attempt=int(
                action_attempt
            ),
            reconciliation_required=bool(
                reconciliation_required
            ),
            restore_required=bool(
                restore_required
            ),
            policy_fingerprint=getattr(
                policy,
                "fingerprint",
                "",
            ),
            metadata=metadata
            or {},
            provenance={
                "source": "thread_budget_phase7",
            },
        )

    def recommend_action(
        self,
        status,
        oversubscribed,
        nested,
        environment_plan,
        runtime_plan,
        reconciliation_required,
        restore_required,
    ):

        if restore_required:

            return THREAD_BUDGET_ACTION_RESTORE

        if reconciliation_required:

            return THREAD_BUDGET_ACTION_RECONCILE

        if status in (
            THREAD_BUDGET_STATUS_UNKNOWN,
            THREAD_BUDGET_STATUS_STALE,
            THREAD_BUDGET_STATUS_INVALID,
        ):

            return THREAD_BUDGET_ACTION_DEFER

        if oversubscribed:

            return THREAD_BUDGET_ACTION_DEFER_JOB

        if nested:

            return THREAD_BUDGET_ACTION_DISABLE_NESTED

        if status == THREAD_BUDGET_STATUS_CONSTRAINED:

            return THREAD_BUDGET_ACTION_REDUCE

        if runtime_plan:

            return THREAD_BUDGET_ACTION_APPLY_RUNTIME

        if environment_plan:

            return THREAD_BUDGET_ACTION_APPLY_ENVIRONMENT

        return THREAD_BUDGET_ACTION_ASSIGN

    def apply_state_machine(
        self,
        observation,
        policy,
        mode,
    ):

        if self.is_duplicate(
            observation,
        ):

            observation.duplicate_suppressed = True
            observation.action_state = THREAD_BUDGET_STATE_SUPPRESSED
            observation.reason_codes = sorted(
                set(
                    observation.reason_codes
                    + [
                        THREAD_REASON_ACTION_DUPLICATE_SUPPRESSED
                    ]
                )
            )
            return observation

        if self.cooldown_active(
            observation,
            policy,
        ):

            observation.cooldown_active = True
            observation.action_state = THREAD_BUDGET_STATE_SUPPRESSED
            observation.reason_codes = sorted(
                set(
                    observation.reason_codes
                    + [
                        THREAD_REASON_ACTION_COOLDOWN
                    ]
                )
            )
            return observation

        if self.retry_exhausted(
            observation,
            policy,
        ):

            observation.action_state = THREAD_BUDGET_STATE_DEFERRED
            observation.reason_codes = sorted(
                set(
                    observation.reason_codes
                    + [
                        THREAD_REASON_ACTION_RETRY_EXHAUSTED
                    ]
                )
            )
            return observation

        if mode != FEATURE_MODE_ENFORCE:

            return observation

        observation.action_allowed = self.action_allowed(
            observation,
            policy,
        )

        if not observation.action_allowed:

            observation.action_state = THREAD_BUDGET_STATE_DEFERRED
            observation.reason_codes = sorted(
                set(
                    observation.reason_codes
                    + [
                        THREAD_REASON_ACTION_NOT_ALLOWED
                    ]
                )
            )
            return observation

        result = self.executor.execute(
            observation,
            policy,
            mode,
        )
        observation.action_state = result.get(
            "state",
            THREAD_BUDGET_STATE_DEFERRED,
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
    ):

        if observation.status in (
            THREAD_BUDGET_STATUS_UNKNOWN,
            THREAD_BUDGET_STATUS_STALE,
            THREAD_BUDGET_STATUS_INVALID,
        ):

            return False

        if observation.reconciliation_required and observation.action != (
            THREAD_BUDGET_ACTION_RECONCILE
        ):

            return False

        return True

    def workload_limit(
        self,
        policy,
        workload_class,
    ):

        mapping = {
            WORKLOAD_CLASS_LIGHT: "max_threads_per_light_job",
            WORKLOAD_CLASS_CPU_HEAVY: "max_threads_per_cpu_heavy_job",
            WORKLOAD_CLASS_GPU_INFERENCE: (
                "max_threads_per_gpu_inference_job"
            ),
            WORKLOAD_CLASS_GPU_TRAINING: (
                "max_threads_per_gpu_training_job"
            ),
            WORKLOAD_CLASS_IO_HEAVY: "max_threads_per_io_heavy_job",
        }

        return max(
            1,
            int(
                getattr(
                    policy,
                    mapping[
                        self.normalize_workload(
                            workload_class
                        )
                    ],
                    1,
                )
            ),
        )

    def normalize_workload(
        self,
        workload_class,
    ):

        if workload_class in WORKLOAD_CLASSES:

            return workload_class

        return WORKLOAD_CLASS_LIGHT

    def environment_plan(
        self,
        resolved_threads,
        environment,
        supported_variables=None,
    ):

        if resolved_threads <= 0:

            return {}

        supported = set(
            supported_variables
            or ENVIRONMENT_VARIABLES
        )
        plan = {}

        for name in ENVIRONMENT_VARIABLES:

            if name not in supported:

                continue

            current = environment.get(
                name
            )

            desired = (
                "false"
                if name == "TOKENIZERS_PARALLELISM"
                else str(
                    max(
                        1,
                        int(
                            resolved_threads
                        ),
                    )
                )
            )

            if current == desired:

                continue

            plan[name] = {
                "name": name,
                "current": current,
                "desired": desired,
                "restore_value": current,
                "supported": True,
                "would_set": True,
            }

        return dict(
            sorted(
                plan.items()
            )
        )

    def runtime_plan(
        self,
        resolved_threads,
        runtime_settings,
    ):

        if resolved_threads <= 0:

            return {}

        plan = {}
        current_threads = runtime_settings.get(
            "num_threads"
        )
        current_interop = runtime_settings.get(
            "num_interop_threads"
        )

        if current_threads != resolved_threads:

            plan["set_num_threads"] = {
                "current": current_threads,
                "desired": resolved_threads,
                "restore_value": current_threads,
                "supported": bool(
                    runtime_settings.get(
                        "supports_set_num_threads",
                        False,
                    )
                ),
            }

        desired_interop = min(
            2,
            max(
                1,
                resolved_threads,
            ),
        )

        if current_interop != desired_interop:

            plan["set_num_interop_threads"] = {
                "current": current_interop,
                "desired": desired_interop,
                "restore_value": current_interop,
                "supported": bool(
                    runtime_settings.get(
                        "supports_set_num_interop_threads",
                        False,
                    )
                ),
            }

        return dict(
            sorted(
                plan.items()
            )
        )

    def detect_nested_parallelism(
        self,
        environment,
        runtime_settings,
        outer_worker_threads,
    ):

        enabled_libs = []

        for name in NUMERIC_ENVIRONMENT_VARIABLES:

            if self.safe_int(
                environment.get(
                    name,
                    0,
                )
            ) > 1:

                enabled_libs.append(
                    name
                )

        tokenizer_enabled = str(
            environment.get(
                "TOKENIZERS_PARALLELISM",
                "",
            )
        ).lower() in (
            "1",
            "true",
            "yes",
        )

        torch_nested = (
            self.safe_int(
                runtime_settings.get(
                    "num_threads",
                    0,
                )
            )
            > 1
            and self.safe_int(
                runtime_settings.get(
                    "num_interop_threads",
                    0,
                )
            )
            > 1
        )

        return bool(
            len(
                enabled_libs
            )
            > 1
            or (
                self.safe_int(
                    outer_worker_threads
                )
                > 1
                and enabled_libs
            )
            or tokenizer_enabled
            or torch_nested
        )

    def is_duplicate(
        self,
        observation,
    ):

        if self.last_observation is None:

            return False

        return (
            observation.action == self.last_observation.action
            and observation.job_id == self.last_observation.job_id
            and observation.lease_id == self.last_observation.lease_id
            and observation.process_id == self.last_observation.process_id
            and observation.resolved_threads
            == self.last_observation.resolved_threads
            and observation.policy_fingerprint
            == self.last_observation.policy_fingerprint
        )

    def cooldown_active(
        self,
        observation,
        policy,
    ):

        if self.last_observation is None:

            return False

        if (
            observation.policy_fingerprint
            != self.last_observation.policy_fingerprint
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
            policy.thread_budget_cooldown_seconds
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
                    "owner_valid",
                    True,
                )
                is False
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
                "owner_valid",
                True,
            )
            is False
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

    def policy_mismatch(
        self,
        policy,
        *observations,
    ):

        for observation in observations:

            if observation is None:

                continue

            fingerprint = self.extract_id(
                observation,
                "policy_fingerprint",
            )

            if fingerprint and fingerprint != policy.fingerprint:

                return True

        return False

    def runtime_pressure_reduces_budget(
        self,
        runtime_guard_observation,
    ):

        if runtime_guard_observation is None:

            return False

        pressure = self.extract_id(
            runtime_guard_observation,
            "pressure_level",
        )

        return pressure in (
            RUNTIME_PRESSURE_CRITICAL,
            RUNTIME_PRESSURE_EMERGENCY,
        )

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

    def extract_process_id(
        self,
        value,
    ):

        direct = self.extract_id(
            value,
            "process_id",
        )

        if direct:

            return direct

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

    def safe_int(
        self,
        value,
        default=0,
    ):

        try:

            return int(
                value
            )

        except Exception:

            return default

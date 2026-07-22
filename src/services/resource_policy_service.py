import json
import shutil
from pathlib import Path

from core import App
from models.resource_model import (
    DEFAULT_RAM_PRESSURE_THRESHOLDS_MB,
    DEFAULT_RESOURCE_FEATURE_MODES,
    DEFAULT_THREAD_LIMITS,
    FALLBACK_RESOURCE_FEATURE_MODES,
    FEATURE_MODE_ENFORCE,
    FEATURE_MODE_ENFORCED,
    RESOURCE_FEATURE_MODE_KEYS,
    RESOURCE_FEATURE_MODES,
    RESOURCE_POLICY_SCHEMA_VERSION,
    ResolvedResourcePolicy,
    ResourcePolicy,
    now_iso,
)


class ResourcePolicyValidationError(ValueError):

    pass


class ResourcePolicyService:

    CONFIG_KEY = "resource_policy"

    BACKUP_KEY = "resource_policy_backups"

    BACKUP_SUFFIX = ".resource_policy.backup.json"

    def __init__(
        self,
        config=None,
    ):

        self.config = config or App.config

        self.last_load_source = "primary"

        self.last_notices = []

    def load(
        self,
    ):

        resolved = self.resolve()

        return self.compat_policy(
            resolved
        )

    def resolve(
        self,
        runtime_override=None,
        migrate=True,
    ):

        self.last_notices = []

        data = self.primary_data()

        try:

            policy, migrated = self.normalize(
                data
            )

            self.validate(
                policy
            )

            if migrated and migrate:

                self.backup_before_migration(
                    data
                )

                self.persist_policy(
                    policy
                )

                self.last_notices.append(
                    "resource_policy_migrated_to_v2"
                )

            resolved = ResolvedResourcePolicy.from_policy(
                policy,
                source="primary",
                notices=self.last_notices,
            )

            if runtime_override:

                resolved = self.apply_runtime_override(
                    resolved,
                    runtime_override,
                )

            self.last_load_source = "primary"

            return resolved

        except Exception as exc:

            self.last_notices.append(
                f"primary_policy_invalid:{exc}"
            )

            backup = self.load_latest_valid_backup()

            if backup is not None:

                policy = self.fallback_policy(
                    backup,
                    source="backup",
                )

                self.last_load_source = "backup"

                return ResolvedResourcePolicy.from_policy(
                    policy,
                    source="backup",
                    notices=self.last_notices
                    + [
                        "loaded_valid_backup",
                        "enforcement_disabled_after_fallback",
                    ],
                )

            policy = self.fallback_policy(
                ResourcePolicy(),
                source="built_in_fallback",
            )

            self.last_load_source = "built_in_fallback"

            return ResolvedResourcePolicy.from_policy(
                policy,
                source="built_in_fallback",
                notices=self.last_notices
                + [
                    "using_built_in_safe_policy",
                    "enforcement_disabled_after_fallback",
                ],
            )

    def save(
        self,
        policy,
    ):

        policy, _ = self.normalize(
            policy
        )

        self.validate(
            policy
        )

        self.persist_policy(
            policy
        )

        return policy

    def summary(
        self,
    ):

        resolved = self.resolve(
            migrate=False
        )

        data = resolved.to_dict()

        data["policy"] = self.compat_policy(
            resolved
        ).to_dict()

        return data

    def primary_data(
        self,
    ):

        try:

            return self.config.get(
                self.CONFIG_KEY,
                {},
            )

        except Exception:

            return {}

    def normalize(
        self,
        data,
    ):

        if isinstance(
            data,
            ResourcePolicy,
        ):

            data = data.to_dict()

        if data in (
            None,
            "",
        ):

            data = {}

        if not isinstance(
            data,
            dict,
        ):

            raise ResourcePolicyValidationError(
                "policy_must_be_object"
            )

        migrated = False

        normalized = dict(
            data
        )

        version = normalized.get(
            "schema_version",
            1,
        )

        try:

            version = int(
                version
            )

        except Exception as exc:

            raise ResourcePolicyValidationError(
                "invalid_schema_version"
            ) from exc

        if version < RESOURCE_POLICY_SCHEMA_VERSION:

            migrated = True

            normalized["schema_version"] = (
                RESOURCE_POLICY_SCHEMA_VERSION
            )

        elif version != RESOURCE_POLICY_SCHEMA_VERSION:

            raise ResourcePolicyValidationError(
                "unsupported_schema_version"
            )

        normalized.setdefault(
            "policy_id",
            "balanced",
        )

        normalized.setdefault(
            "display_name",
            "Balanced",
        )

        normalized.setdefault(
            "reserve_ram_mb",
            8192,
        )

        normalized.setdefault(
            "reserve_vram_mb",
            512,
        )

        normalized.setdefault(
            "reserve_disk_mb",
            1024,
        )

        normalized.setdefault(
            "max_concurrent_jobs",
            1,
        )

        normalized.setdefault(
            "max_gpu_jobs",
            1,
        )

        normalized.setdefault(
            "batch_size",
            1,
        )

        normalized.setdefault(
            "allow_cpu_fallback",
            False,
        )

        normalized.setdefault(
            "cpu_fallback_requires_job_confirmation",
            True,
        )

        normalized.setdefault(
            "cooperative_stop_grace_seconds",
            20,
        )

        normalized.setdefault(
            "kill_escalation_wait_seconds",
            5,
        )

        normalized.setdefault(
            "snapshot_ttl_seconds",
            2.0,
        )

        normalized.setdefault(
            "resource_wait_recheck_seconds",
            5.0,
        )

        normalized.setdefault(
            "lease_ttl_seconds",
            300.0,
        )

        normalized.setdefault(
            "lease_renew_interval_seconds",
            120.0,
        )

        normalized.setdefault(
            "stale_lease_handling_mode",
            "monitor_only",
        )

        normalized.setdefault(
            "graceful_shutdown_timeout_seconds",
            20.0,
        )

        normalized.setdefault(
            "terminate_timeout_seconds",
            5.0,
        )

        normalized.setdefault(
            "kill_tree_timeout_seconds",
            5.0,
        )

        normalized.setdefault(
            "process_identity_required",
            True,
        )

        normalized.setdefault(
            "orphan_handling_mode",
            "monitor_only",
        )

        normalized.setdefault(
            "process_observation_ttl_seconds",
            5.0,
        )

        normalized.setdefault(
            "action_cooldown_seconds",
            30.0,
        )

        normalized.setdefault(
            "deescalation_stable_seconds",
            60.0,
        )

        normalized.setdefault(
            "observation_ttl_seconds",
            5.0,
        )

        normalized.setdefault(
            "max_action_attempts",
            3,
        )

        normalized.setdefault(
            "action_retry_backoff_seconds",
            10.0,
        )

        normalized.setdefault(
            "allow_simulated_throttle",
            True,
        )

        normalized.setdefault(
            "allow_simulated_pause",
            False,
        )

        normalized.setdefault(
            "allow_simulated_graceful_stop",
            False,
        )

        normalized.setdefault(
            "allow_simulated_terminate",
            False,
        )

        normalized.setdefault(
            "allow_simulated_kill_tree",
            False,
        )

        normalized.setdefault(
            "max_total_cpu_threads",
            8,
        )

        normalized.setdefault(
            "max_threads_per_light_job",
            2,
        )

        normalized.setdefault(
            "max_threads_per_cpu_heavy_job",
            4,
        )

        normalized.setdefault(
            "max_threads_per_gpu_inference_job",
            2,
        )

        normalized.setdefault(
            "max_threads_per_gpu_training_job",
            2,
        )

        normalized.setdefault(
            "max_threads_per_io_heavy_job",
            2,
        )

        normalized.setdefault(
            "max_parallel_heavy_jobs",
            1,
        )

        normalized.setdefault(
            "reserve_cpu_threads",
            1,
        )

        normalized.setdefault(
            "allow_nested_parallelism",
            False,
        )

        normalized.setdefault(
            "thread_budget_cooldown_seconds",
            30.0,
        )

        normalized.setdefault(
            "thread_budget_observation_ttl_seconds",
            5.0,
        )

        normalized.setdefault(
            "thread_budget_restore_on_release",
            True,
        )

        normalized.setdefault(
            "snapshot_unknown_state_policy",
            "monitor_only",
        )

        normalized.setdefault(
            "scope",
            "global_application",
        )

        feature_modes = normalized.get(
            "feature_modes",
            {},
        )

        if not isinstance(
            feature_modes,
            dict,
        ):

            raise ResourcePolicyValidationError(
                "feature_modes_must_be_object"
            )

        flattened_modes = {
            key: normalized.pop(
                key
            )
            for key in list(
                normalized.keys()
            )
            if key in RESOURCE_FEATURE_MODE_KEYS
        }

        normalized["feature_modes"] = (
            dict(
                DEFAULT_RESOURCE_FEATURE_MODES
            )
            | feature_modes
            | flattened_modes
        )

        thresholds = normalized.get(
            "ram_pressure_thresholds",
            {},
        )

        if not isinstance(
            thresholds,
            dict,
        ):

            raise ResourcePolicyValidationError(
                "ram_pressure_thresholds_must_be_object"
            )

        normalized["ram_pressure_thresholds"] = (
            dict(
                DEFAULT_RAM_PRESSURE_THRESHOLDS_MB
            )
            | thresholds
        )

        thread_limits = normalized.get(
            "thread_limits",
            {},
        )

        if not isinstance(
            thread_limits,
            dict,
        ):

            raise ResourcePolicyValidationError(
                "thread_limits_must_be_object"
            )

        normalized["thread_limits"] = (
            dict(
                DEFAULT_THREAD_LIMITS
            )
            | thread_limits
        )

        return ResourcePolicy.from_dict(
            normalized
        ), migrated

    def validate(
        self,
        policy,
        total_ram_mb=0,
    ):

        policy = ResourcePolicy.from_dict(
            policy
        )

        errors = []

        if policy.schema_version != RESOURCE_POLICY_SCHEMA_VERSION:

            errors.append(
                "invalid_schema_version"
            )

        if policy.scope != "global_application":

            errors.append(
                "global_only_scope_required"
            )

        unknown_modes = set(
            policy.feature_modes.keys()
        ) - set(
            RESOURCE_FEATURE_MODE_KEYS
        )

        if unknown_modes:

            errors.append(
                "unknown_feature_flag"
            )

        for mode in policy.feature_modes.values():

            if mode not in RESOURCE_FEATURE_MODES:

                errors.append(
                    "invalid_feature_mode"
                )

        for name in (
            "reserve_ram_mb",
            "reserve_vram_mb",
            "reserve_disk_mb",
        ):

            if int(
                getattr(
                    policy,
                    name,
                )
            ) < 0:

                errors.append(
                    "negative_reserve"
                )

        if total_ram_mb and policy.reserve_ram_mb > total_ram_mb:

            errors.append(
                "reserve_ram_exceeds_total"
            )

        if policy.max_concurrent_jobs <= 0:

            errors.append(
                "invalid_concurrency"
            )

        if policy.max_gpu_jobs <= 0:

            errors.append(
                "invalid_concurrency"
            )

        if policy.batch_size <= 0:

            errors.append(
                "invalid_batch_size"
            )

        for name in (
            "snapshot_ttl_seconds",
            "resource_wait_recheck_seconds",
            "lease_ttl_seconds",
            "lease_renew_interval_seconds",
            "graceful_shutdown_timeout_seconds",
            "terminate_timeout_seconds",
            "kill_tree_timeout_seconds",
            "process_observation_ttl_seconds",
            "action_cooldown_seconds",
            "deescalation_stable_seconds",
            "observation_ttl_seconds",
            "action_retry_backoff_seconds",
            "thread_budget_cooldown_seconds",
            "thread_budget_observation_ttl_seconds",
            "cooperative_stop_grace_seconds",
            "kill_escalation_wait_seconds",
        ):

            if float(
                getattr(
                    policy,
                    name,
                )
            ) <= 0:

                errors.append(
                    "invalid_timeout"
                )

        if int(
            policy.max_action_attempts
        ) <= 0:

            errors.append(
                "invalid_action_attempts"
            )

        for name in (
            "max_total_cpu_threads",
            "max_threads_per_light_job",
            "max_threads_per_cpu_heavy_job",
            "max_threads_per_gpu_inference_job",
            "max_threads_per_gpu_training_job",
            "max_threads_per_io_heavy_job",
            "max_parallel_heavy_jobs",
        ):

            if int(
                getattr(
                    policy,
                    name,
                )
            ) <= 0:

                errors.append(
                    "invalid_thread_budget"
                )

        if int(
            policy.reserve_cpu_threads
        ) < 0:

            errors.append(
                "invalid_thread_budget"
            )

        if (
            int(
                policy.reserve_cpu_threads
            )
            >= int(
                policy.max_total_cpu_threads
            )
        ):

            errors.append(
                "invalid_thread_budget"
            )

        for value in policy.thread_limits.values():

            if int(
                value
            ) < 0 or int(
                value
            ) > 64:

                errors.append(
                    "invalid_thread_limit"
                )

        thresholds = policy.ram_pressure_thresholds

        ordered = [
            int(
                thresholds.get(
                    "warning_available_ram_mb",
                    0,
                )
            ),
            int(
                thresholds.get(
                    "high_available_ram_mb",
                    0,
                )
            ),
            int(
                thresholds.get(
                    "critical_available_ram_mb",
                    0,
                )
            ),
            int(
                thresholds.get(
                    "emergency_available_ram_mb",
                    0,
                )
            ),
        ]

        if not (
            ordered[0]
            > ordered[1]
            > ordered[2]
            > ordered[3]
        ):

            errors.append(
                "invalid_threshold_order"
            )

        if errors:

            raise ResourcePolicyValidationError(
                ",".join(
                    sorted(
                        set(
                            errors
                        )
                    )
                )
            )

        return True

    def apply_runtime_override(
        self,
        resolved,
        runtime_override,
    ):

        if not isinstance(
            runtime_override,
            dict,
        ):

            raise ResourcePolicyValidationError(
                "runtime_override_must_be_object"
            )

        allowed = {
            "feature_modes",
            "allow_cpu_fallback",
            "cpu_fallback_requires_job_confirmation",
        }

        unknown = set(
            runtime_override.keys()
        ) - allowed

        if unknown:

            raise ResourcePolicyValidationError(
                "unsupported_runtime_override"
            )

        policy_data = resolved.effective_dict()

        if "feature_modes" in runtime_override:

            policy_data["feature_modes"] = dict(
                policy_data["feature_modes"]
            ) | dict(
                runtime_override["feature_modes"]
            )

        for key in (
            "allow_cpu_fallback",
            "cpu_fallback_requires_job_confirmation",
        ):

            if key in runtime_override:

                policy_data[key] = runtime_override[
                    key
                ]

        policy = ResourcePolicy.from_dict(
            policy_data
        )

        self.validate(
            policy
        )

        overridden = ResolvedResourcePolicy.from_policy(
            policy,
            source=resolved.source,
            notices=resolved.notices
            + [
                "runtime_override_applied_not_persisted"
            ],
            provenance=dict(
                resolved.provenance
            )
            | {
                "runtime_override": "validated"
            },
        )

        return overridden

    def compat_policy(
        self,
        resolved,
    ):

        policy = ResourcePolicy()

        data = policy.to_dict()

        data["schema_version"] = resolved.schema_version

        data["feature_modes"] = dict(
            resolved.feature_modes
        )

        data["ram_pressure_thresholds"] = dict(
            resolved.ram_pressure_thresholds
        )

        data["thread_limits"] = dict(
            resolved.thread_limits
        )

        data["batch_size"] = resolved.batch_size

        data["cooperative_stop_grace_seconds"] = (
            resolved.cooperative_stop_grace_seconds
        )

        data["kill_escalation_wait_seconds"] = (
            resolved.kill_escalation_wait_seconds
        )

        data["lease_renew_interval_seconds"] = (
            resolved.lease_renew_interval_seconds
        )

        data["stale_lease_handling_mode"] = (
            resolved.stale_lease_handling_mode
        )

        data["graceful_shutdown_timeout_seconds"] = (
            resolved.graceful_shutdown_timeout_seconds
        )

        data["terminate_timeout_seconds"] = (
            resolved.terminate_timeout_seconds
        )

        data["kill_tree_timeout_seconds"] = (
            resolved.kill_tree_timeout_seconds
        )

        data["process_identity_required"] = (
            resolved.process_identity_required
        )

        data["orphan_handling_mode"] = (
            resolved.orphan_handling_mode
        )

        data["process_observation_ttl_seconds"] = (
            resolved.process_observation_ttl_seconds
        )

        data["action_cooldown_seconds"] = (
            resolved.action_cooldown_seconds
        )

        data["deescalation_stable_seconds"] = (
            resolved.deescalation_stable_seconds
        )

        data["observation_ttl_seconds"] = (
            resolved.observation_ttl_seconds
        )

        data["max_action_attempts"] = (
            resolved.max_action_attempts
        )

        data["action_retry_backoff_seconds"] = (
            resolved.action_retry_backoff_seconds
        )

        data["allow_simulated_throttle"] = (
            resolved.allow_simulated_throttle
        )

        data["allow_simulated_pause"] = (
            resolved.allow_simulated_pause
        )

        data["allow_simulated_graceful_stop"] = (
            resolved.allow_simulated_graceful_stop
        )

        data["allow_simulated_terminate"] = (
            resolved.allow_simulated_terminate
        )

        data["allow_simulated_kill_tree"] = (
            resolved.allow_simulated_kill_tree
        )

        data["max_total_cpu_threads"] = resolved.max_total_cpu_threads

        data["max_threads_per_light_job"] = (
            resolved.max_threads_per_light_job
        )

        data["max_threads_per_cpu_heavy_job"] = (
            resolved.max_threads_per_cpu_heavy_job
        )

        data["max_threads_per_gpu_inference_job"] = (
            resolved.max_threads_per_gpu_inference_job
        )

        data["max_threads_per_gpu_training_job"] = (
            resolved.max_threads_per_gpu_training_job
        )

        data["max_threads_per_io_heavy_job"] = (
            resolved.max_threads_per_io_heavy_job
        )

        data["max_parallel_heavy_jobs"] = (
            resolved.max_parallel_heavy_jobs
        )

        data["reserve_cpu_threads"] = resolved.reserve_cpu_threads

        data["allow_nested_parallelism"] = (
            resolved.allow_nested_parallelism
        )

        data["thread_budget_cooldown_seconds"] = (
            resolved.thread_budget_cooldown_seconds
        )

        data["thread_budget_observation_ttl_seconds"] = (
            resolved.thread_budget_observation_ttl_seconds
        )

        data["thread_budget_restore_on_release"] = (
            resolved.thread_budget_restore_on_release
        )

        data["cpu_fallback_requires_job_confirmation"] = (
            resolved.cpu_fallback_requires_job_confirmation
        )

        data["snapshot_unknown_state_policy"] = (
            resolved.snapshot_unknown_state_policy
        )

        data["scope"] = resolved.scope

        data["policy_id"] = "balanced"

        data["display_name"] = "Balanced"

        return ResourcePolicy.from_dict(
            data
        )

    def fallback_policy(
        self,
        policy,
        source,
    ):

        policy = ResourcePolicy.from_dict(
            policy
        )

        policy.feature_modes = dict(
            FALLBACK_RESOURCE_FEATURE_MODES
        )

        for key, mode in list(
            policy.feature_modes.items()
        ):

            if mode in (
                FEATURE_MODE_ENFORCE,
                FEATURE_MODE_ENFORCED,
            ):

                policy.feature_modes[key] = "disabled"

        policy.allow_cpu_fallback = False

        policy.cpu_fallback_requires_job_confirmation = True

        policy.schema_version = RESOURCE_POLICY_SCHEMA_VERSION

        policy.scope = "global_application"

        policy.reserve_ram_mb = 8192

        policy.reserve_vram_mb = 512

        return policy

    def persist_policy(
        self,
        policy,
    ):

        self.config.set(
            self.CONFIG_KEY,
            ResourcePolicy.from_dict(
                policy
            ).to_dict(),
        )

    def backup_before_migration(
        self,
        data,
    ):

        backup = {
            "created_at": now_iso(),
            "reason": "before_resource_policy_v2_migration",
            "resource_policy": data
            if isinstance(
                data,
                dict,
            )
            else {
                "invalid_policy": repr(
                    data
                )
            },
        }

        path = self.backup_path()

        if path is not None:

            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            path.write_text(
                json.dumps(
                    backup,
                    indent=4,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

        backups = list(
            self.config.get(
                self.BACKUP_KEY,
                [],
            )
            or []
        )

        backups.append(
            backup
        )

        self.config.set(
            self.BACKUP_KEY,
            backups,
        )

    def backup_path(
        self,
    ):

        file_path = getattr(
            self.config,
            "file",
            None,
        )

        if not file_path:

            return None

        file_path = Path(
            file_path
        )

        return file_path.with_name(
            file_path.name
            + self.BACKUP_SUFFIX
        )

    def load_latest_valid_backup(
        self,
    ):

        candidates = []

        try:

            candidates.extend(
                self.config.get(
                    self.BACKUP_KEY,
                    [],
                )
                or []
            )

        except Exception:

            pass

        path = self.backup_path()

        if path is not None and path.exists():

            try:

                candidates.append(
                    json.loads(
                        path.read_text(
                            encoding="utf-8"
                        )
                    )
                )

            except Exception:

                pass

        for item in reversed(
            candidates
        ):

            data = item.get(
                "resource_policy",
                item,
            )

            try:

                policy, _ = self.normalize(
                    data
                )

                self.validate(
                    policy
                )

                return policy

            except Exception:

                continue

        return None

    def preserve_corrupt_primary(
        self,
        destination,
    ):

        file_path = getattr(
            self.config,
            "file",
            None,
        )

        if not file_path:

            return False

        file_path = Path(
            file_path
        )

        if not file_path.exists():

            return False

        shutil.copy2(
            file_path,
            destination,
        )

        return True

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(
    0,
    str(
        SRC
    ),
)

from models.resource_model import (
    DEFAULT_RESOURCE_FEATURE_MODES,
    RESOURCE_POLICY_SCHEMA_VERSION,
    ResourcePolicy,
)
from services.resource_policy_service import (
    ResourcePolicyService,
    ResourcePolicyValidationError,
)


class MemoryConfig:

    def __init__(
        self,
        data=None,
        file=None,
    ):

        self.data = dict(
            data
            or {}
        )

        self.file = file

        self.set_calls = []

    def get(
        self,
        key,
        default=None,
    ):

        return self.data.get(
            key,
            default,
        )

    def set(
        self,
        key,
        value,
    ):

        self.data[key] = value

        self.set_calls.append(
            (
                key,
                value,
            )
        )

        if self.file:

            Path(
                self.file
            ).write_text(
                json.dumps(
                    self.data,
                    indent=4,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )


def service_with_policy(
    policy,
    tmp_path=None,
):

    file = None

    if tmp_path is not None:

        file = tmp_path / "settings.json"

        file.write_text(
            json.dumps(
                {
                    "resource_policy": policy
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    return ResourcePolicyService(
        MemoryConfig(
            {
                "resource_policy": policy
            },
            file=file,
        )
    )


def assert_validation_error(
    policy,
    code,
):

    service = service_with_policy(
        policy
    )

    try:

        service.resolve(
            migrate=False
        )

    except ResourcePolicyValidationError as exc:

        assert code in str(
            exc
        )

        return

    assert False, f"Expected validation error {code}"


def test_load_policy_v1_and_migrate_to_v2_with_backup(tmp_path):

    v1 = {
        "policy_id": "legacy",
        "display_name": "Legacy",
        "max_concurrent_jobs": 1,
        "max_gpu_jobs": 1,
        "reserve_ram_mb": 2048,
        "reserve_vram_mb": 256,
    }

    service = service_with_policy(
        v1,
        tmp_path=tmp_path,
    )

    resolved = service.resolve()

    assert resolved.schema_version == RESOURCE_POLICY_SCHEMA_VERSION
    assert resolved.reserve_ram_mb == 2048
    assert resolved.feature_modes == DEFAULT_RESOURCE_FEATURE_MODES
    assert service.config.data["resource_policy"]["schema_version"] == 2
    assert service.config.data["resource_policy_backups"][0][
        "resource_policy"
    ] == v1
    assert (
        tmp_path
        / "settings.json.resource_policy.backup.json"
    ).exists()


def test_migration_is_idempotent(tmp_path):

    service = service_with_policy(
        {
            "schema_version": 1,
            "max_concurrent_jobs": 1,
            "max_gpu_jobs": 1,
        },
        tmp_path=tmp_path,
    )

    first = service.resolve()

    set_count = len(
        service.config.set_calls
    )

    second = service.resolve()

    assert first.fingerprint == second.fingerprint
    assert len(
        service.config.set_calls
    ) == set_count


def test_load_valid_v2_and_missing_fields_use_safe_defaults():

    service = service_with_policy(
        {
            "schema_version": 2,
            "feature_modes": {},
            "unknown_top_level": "kept_out_of_model",
        }
    )

    resolved = service.resolve(
        migrate=False
    )

    assert resolved.reserve_ram_mb == 8192
    assert resolved.reserve_vram_mb == 512
    assert resolved.batch_size == 1
    assert resolved.thread_limits["ui_light_threads"] == 2
    assert resolved.allow_cpu_fallback is False


def test_unknown_top_level_field_does_not_crash():

    resolved = service_with_policy(
        {
            "schema_version": 2,
            "not_a_policy_field": "ignored",
        }
    ).resolve(
        migrate=False
    )

    assert resolved.source == "primary"


def test_invalid_feature_mode():

    resolved = service_with_policy(
        {
            "schema_version": 2,
            "feature_modes": {
                "resource_policy_v2_mode": "enabled"
            },
        }
    ).resolve(
        migrate=False
    )

    assert resolved.source == "built_in_fallback"
    assert any(
        "invalid_feature_mode" in notice
        for notice in resolved.notices
    )


def test_unknown_feature_flag():

    resolved = service_with_policy(
        {
            "schema_version": 2,
            "feature_modes": {
                "unknown_resource_mode": "monitor_only"
            },
        }
    ).resolve(
        migrate=False
    )

    assert resolved.source == "built_in_fallback"
    assert any(
        "unknown_feature_flag" in notice
        for notice in resolved.notices
    )


def test_negative_reserve_invalid():

    resolved = service_with_policy(
        {
            "schema_version": 2,
            "reserve_ram_mb": -1,
        }
    ).resolve(
        migrate=False
    )

    assert resolved.source == "built_in_fallback"
    assert any(
        "negative_reserve" in notice
        for notice in resolved.notices
    )


def test_invalid_threshold_ordering():

    resolved = service_with_policy(
        {
            "schema_version": 2,
            "ram_pressure_thresholds": {
                "warning_available_ram_mb": 4096,
                "high_available_ram_mb": 8192,
                "critical_available_ram_mb": 6144,
                "emergency_available_ram_mb": 1024,
            },
        }
    ).resolve(
        migrate=False
    )

    assert resolved.source == "built_in_fallback"
    assert any(
        "invalid_threshold_order" in notice
        for notice in resolved.notices
    )


def test_invalid_thread_limits():

    resolved = service_with_policy(
        {
            "schema_version": 2,
            "thread_limits": {
                "cpu_heavy_preprocessing_threads": 100
            },
        }
    ).resolve(
        migrate=False
    )

    assert resolved.source == "built_in_fallback"
    assert any(
        "invalid_thread_limit" in notice
        for notice in resolved.notices
    )


def test_invalid_batch_and_concurrency():

    resolved = service_with_policy(
        {
            "schema_version": 2,
            "batch_size": 0,
            "max_concurrent_jobs": 0,
        }
    ).resolve(
        migrate=False
    )

    assert resolved.source == "built_in_fallback"
    assert any(
        "invalid_batch_size" in notice
        for notice in resolved.notices
    )
    assert any(
        "invalid_concurrency" in notice
        for notice in resolved.notices
    )


def test_policy_fingerprint_deterministic_and_key_order_independent():

    left = {
        "schema_version": 2,
        "reserve_ram_mb": 8192,
        "reserve_vram_mb": 512,
    }

    right = {
        "reserve_vram_mb": 512,
        "reserve_ram_mb": 8192,
        "schema_version": 2,
    }

    first = service_with_policy(
        left
    ).resolve(
        migrate=False
    )

    second = service_with_policy(
        right
    ).resolve(
        migrate=False
    )

    assert first.fingerprint == second.fingerprint


def test_effective_policy_change_changes_fingerprint():

    first = service_with_policy(
        {
            "schema_version": 2,
            "reserve_ram_mb": 8192,
        }
    ).resolve(
        migrate=False
    )

    second = service_with_policy(
        {
            "schema_version": 2,
            "reserve_ram_mb": 12288,
        }
    ).resolve(
        migrate=False
    )

    assert first.fingerprint != second.fingerprint


def test_corrupted_primary_loads_valid_backup_and_disables_enforcement():

    service = ResourcePolicyService(
        MemoryConfig(
            {
                "resource_policy": "corrupt",
                "resource_policy_backups": [
                    {
                        "resource_policy": {
                            "schema_version": 2,
                            "feature_modes": {
                                "resource_policy_v2_mode": "enforced"
                            },
                        }
                    }
                ],
            }
        )
    )

    resolved = service.resolve(
        migrate=False
    )

    assert resolved.source == "backup"
    assert all(
        mode != "enforced"
        for mode in resolved.feature_modes.values()
    )


def test_corrupted_primary_without_backup_uses_built_in_fallback():

    service = service_with_policy(
        [
            "corrupt"
        ]
    )

    resolved = service.resolve(
        migrate=False
    )

    assert resolved.source == "built_in_fallback"
    assert resolved.reserve_ram_mb == 8192
    assert all(
        mode != "enforced"
        for mode in resolved.feature_modes.values()
    )


def test_corrupt_file_not_overwritten(tmp_path):

    file = tmp_path / "settings.json"

    original = "{not json, but preserved"

    file.write_text(
        original,
        encoding="utf-8",
    )

    config = MemoryConfig(
        {
            "resource_policy": "corrupt"
        },
        file=file,
    )

    service = ResourcePolicyService(
        config
    )

    service.resolve(
        migrate=False
    )

    assert file.read_text(
        encoding="utf-8"
    ) == original

    assert config.set_calls == []


def test_global_only_scope_rejects_project_or_voice_override():

    resolved = service_with_policy(
        {
            "schema_version": 2,
            "scope": "project",
        }
    ).resolve(
        migrate=False
    )

    assert resolved.source == "built_in_fallback"
    assert any(
        "global_only_scope_required" in notice
        for notice in resolved.notices
    )


def test_runtime_override_affects_resolved_only_and_does_not_persist():

    service = service_with_policy(
        {
            "schema_version": 2,
            "allow_cpu_fallback": False,
        }
    )

    resolved = service.resolve(
        runtime_override={
            "allow_cpu_fallback": True,
            "cpu_fallback_requires_job_confirmation": True,
        },
        migrate=False,
    )

    assert resolved.allow_cpu_fallback is True
    assert service.config.data["resource_policy"]["allow_cpu_fallback"] is False
    assert service.config.set_calls == []


def test_monitor_only_initial_modes_and_no_runtime_behavior_change():

    policy = service_with_policy(
        {
            "schema_version": 2
        }
    ).load()

    assert policy.feature_modes["resource_policy_v2_mode"] == "monitor_only"
    assert policy.feature_modes[
        "job_runner_safety_integration_mode"
    ] == "disabled"
    assert policy.max_concurrent_jobs == 1
    assert policy.max_gpu_jobs == 1
    assert policy.reserve_ram_mb == 1024
    assert policy.allow_cpu_fallback is True
    assert policy.batch_size == 1

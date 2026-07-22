from __future__ import annotations

import importlib.util
import json
import py_compile
from pathlib import Path
from typing import Any

import pytest


def _load_runner_module():
    path = Path("cache/avs01424_calibration_runner.py")
    spec = importlib.util.spec_from_file_location("avs01424_calibration_runner", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REFERENCE_VARIANTS = ["R0_RAW", "R1_TRIM", "R2_DC_TRIM", "R3_DC_TRIM_HP"]


def _create_variant_reviews() -> list[dict[str, object]]:
    return [
        {
            "reference_variant": variant,
            "similarity": 4,
            "naturalness": 4,
            "pronunciation": 4,
            "stability": 4,
            "overall": 5 if variant == "R3_DC_TRIM_HP" else 4,
        }
        for variant in REFERENCE_VARIANTS
    ]


def _write_completed_selection_artifact(
    module,
    path: Path,
    winner: str,
) -> Path:
    artifact = module.complete_reference_selection_artifact(
        module.create_reference_selection_artifact(REFERENCE_VARIANTS),
        winner_reference_variant=winner,
        variant_reviews=_create_variant_reviews(),
        review_date="2026-07-20",
        reviewer="reviewer-test",
        notes="Đã nghe và đối chiếu toàn bộ variants.",
    )
    path.write_text(json.dumps(artifact, ensure_ascii=False), encoding="utf-8")
    return path


def test_generated_runner_defines_twenty_candidate_calibration_pairs(tmp_path):
    module = _load_runner_module()
    run_root = tmp_path / "vieneu_similarity_calibration_test"
    (run_root / "logs").mkdir(parents=True)

    runner_path = module.create_generation_runner(
        run_root,
        "Nội dung transcript khớp audio gốc.",
        "Nội dung transcript mới.",
        "R2_DC_TRIM",
    )
    generated = runner_path.read_text(encoding="utf-8")

    py_compile.compile(str(runner_path), doraise=True)

    assert 'if len(candidates) != 20:' in generated
    assert '"id": f"A{index:02d}"' in generated
    assert 'for side, text in (("original", ORIGINAL_TEXT), ("new", NEW_TEXT)):' in generated
    assert 'output = RUN / "calibration" / f"{candidate_id}_{side}.wav"' in generated
    assert 'expected_review_ids = [f"A{index:02d}" for index in range(1, 21)]' in generated
    assert 'and len(list(set_a.glob("*.wav"))) == 40' in generated
    assert '"candidate_count": 20' in generated
    assert '"pair_file_count": 40' in generated
    assert 'WINNER_REFERENCE_VARIANT = \'R2_DC_TRIM\'' in generated
    assert 'winner_reference_path = RUN / "references" / WINNER_REFERENCE_VARIANT / "reference.wav"' in generated


def test_generated_runner_validates_only_text_differs_between_pair_sides(tmp_path):
    module = _load_runner_module()
    run_root = tmp_path / "vieneu_similarity_calibration_test"
    (run_root / "logs").mkdir(parents=True)

    runner_path = module.create_generation_runner(
        run_root,
        "Transcript gốc.",
        "Transcript mới.",
        "R3_DC_TRIM_HP",
    )
    generated = runner_path.read_text(encoding="utf-8")

    assert 'if ORIGINAL_TEXT == NEW_TEXT:' in generated
    assert 'raise RuntimeError("CALIBRATION_PAIR_TEXT_MUST_DIFFER")' in generated
    assert '"reference_variant": WINNER_REFERENCE_VARIANT' in generated
    assert '"reference_audio_sha256": sha256(winner_reference_path)' in generated
    assert '"preprocessing_manifest_sha256": sha256(' in generated
    assert '"inference": candidate.copy()' in generated
    assert '"engine": {' in generated
    assert 'original["non_text_contract"] != new["non_text_contract"]' in generated
    assert 'original["input_text_sha256"] == new["input_text_sha256"]' in generated
    assert 'raise RuntimeError("CALIBRATION_PAIR_NON_TEXT_CONTRACT_INVALID")' in generated


def test_generated_runner_limits_stale_cleanup_to_current_managed_pair_files(tmp_path):
    module = _load_runner_module()
    run_root = tmp_path / "vieneu_similarity_calibration_test"
    (run_root / "logs").mkdir(parents=True)

    runner_path = module.create_generation_runner(
        run_root,
        "Transcript gốc.",
        "Transcript mới.",
        "R1_TRIM",
    )
    generated = runner_path.read_text(encoding="utf-8")

    assert 'for stale_path in sorted(set_a.glob("A??_*.wav")):' in generated
    assert '"policy": "REMOVE_ONLY_MANAGED_Axx_PAIR_WAV_IN_CURRENT_RUN"' in generated


def test_reference_selection_artifact_defaults_to_manual_review_pending(tmp_path):
    module = _load_runner_module()
    run_root = tmp_path / "reference_preprocessing_ab"
    variants = ["R0_RAW", "R1_TRIM", "R2_DC_TRIM", "R3_DC_TRIM_HP"]

    artifact_path = module.write_reference_selection_artifact(run_root, variants)
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == module.REFERENCE_PREPROCESSING_SCHEMA_VERSION
    assert artifact["experiment_type"] == "REFERENCE_PREPROCESSING_AB"
    assert artifact["status"] == "MANUAL_REVIEW_PENDING"
    assert artifact["review_status"] == "MANUAL_REVIEW_PENDING"
    assert artifact["review_completed"] is False
    assert artifact["winner_reference_variant"] is None
    assert artifact["available_reference_variants"] == variants
    assert artifact["review_rubric"] == module.REVIEW_RUBRIC
    assert artifact["variant_reviews"] == []


def test_winner_loader_blocks_candidate_calibration_before_manual_review(tmp_path):
    module = _load_runner_module()
    artifact_path = module.write_reference_selection_artifact(
        tmp_path / "reference_preprocessing_ab",
        ["R0_RAW", "R1_TRIM", "R2_DC_TRIM", "R3_DC_TRIM_HP"],
    )

    with pytest.raises(
        module.ReferenceSelectionPendingError,
        match="REFERENCE_SELECTION_MANUAL_REVIEW_PENDING",
    ):
        module.load_winner_reference_variant(artifact_path)


def test_winner_loader_returns_only_completed_manual_review_winner(tmp_path):
    module = _load_runner_module()
    artifact_path = _write_completed_selection_artifact(
        module,
        tmp_path / "reference_selection.json",
        "R3_DC_TRIM_HP",
    )

    assert module.load_winner_reference_variant(artifact_path) == "R3_DC_TRIM_HP"


def test_completed_review_artifact_persists_winner_and_review_metadata(tmp_path):
    module = _load_runner_module()
    artifact_path = _write_completed_selection_artifact(
        module,
        tmp_path / "reference_selection.json",
        "R3_DC_TRIM_HP",
    )
    artifact = module.load_reference_selection_artifact(artifact_path)

    assert artifact["review_completed"] is True
    assert artifact["review_status"] == "REVIEW_COMPLETED"
    assert artifact["review_status"] == module.REVIEW_COMPLETED
    assert artifact["winner_reference_variant"] == "R3_DC_TRIM_HP"
    assert artifact["review_date"] == "2026-07-20"
    assert artifact["reviewer"] == "reviewer-test"
    assert artifact["notes"] == "Đã nghe và đối chiếu toàn bộ variants."
    assert [review["reference_variant"] for review in artifact["variant_reviews"]] == REFERENCE_VARIANTS


@pytest.mark.parametrize(
    ("mutation", "expected_error"),
    [
        (
            lambda artifact: artifact.update(
                {
                    "winner_reference_variant": "R9_UNKNOWN",
                }
            ),
            "REFERENCE_SELECTION_ARTIFACT_WINNER_INVALID",
        ),
        (
            lambda artifact: artifact.update(
                {
                    "winner_reference_variant": None,
                }
            ),
            "REFERENCE_SELECTION_ARTIFACT_WINNER_INVALID",
        ),
        (
            lambda artifact: artifact.update(
                {
                    "winner_reference_variant": [
                        "R2_DC_TRIM",
                        "R3_DC_TRIM_HP",
                    ],
                }
            ),
            "REFERENCE_SELECTION_ARTIFACT_WINNER_INVALID",
        ),
        (
            lambda artifact: artifact.update(
                {
                    "review_date": "",
                }
            ),
            "REFERENCE_SELECTION_ARTIFACT_REVIEW_DATE_INVALID",
        ),
        (
            lambda artifact: artifact.update(
                {
                    "reviewer": "",
                }
            ),
            "REFERENCE_SELECTION_ARTIFACT_REVIEWER_INVALID",
        ),
        (
            lambda artifact: artifact.update(
                {
                    "review_status": "MANUAL_REVIEW_PENDING",
                }
            ),
            "REFERENCE_SELECTION_ARTIFACT_REVIEW_STATUS_INCONSISTENT",
        ),
        (
            lambda artifact: artifact.update(
                {
                    "variant_reviews": _create_variant_reviews()[:-1]
                    + [_create_variant_reviews()[0]],
                }
            ),
            "REFERENCE_SELECTION_ARTIFACT_VARIANT_REVIEWS_INCOMPLETE",
        ),
    ],
)
def test_winner_loader_rejects_invalid_completed_review(
    tmp_path,
    mutation,
    expected_error,
):
    module = _load_runner_module()
    artifact_path = _write_completed_selection_artifact(
        module,
        tmp_path / "reference_selection.json",
        "R3_DC_TRIM_HP",
    )
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    mutation(artifact)
    artifact_path.write_text(json.dumps(artifact), encoding="utf-8")

    with pytest.raises(
        module.ReferenceSelectionPendingError,
        match="REFERENCE_SELECTION_MANUAL_REVIEW_PENDING",
    ):
        module.load_winner_reference_variant(artifact_path)

    with pytest.raises(ValueError, match=expected_error):
        module.load_reference_selection_artifact(artifact_path)


def _create_generalization_categories() -> list[dict[str, Any]]:
    return [
        {
            "category": "narration",
            "sample_count": 2,
            "samples": [
                {
                    "sample_id": "narration-001",
                    "input_text_sha256": "a" * 64,
                },
                {
                    "sample_id": "narration-002",
                    "input_text_sha256": "b" * 64,
                },
            ],
        },
        {
            "category": "difficult-pronunciation",
            "sample_count": 1,
            "samples": [
                {
                    "sample_id": "pronunciation-001",
                    "input_text_sha256": "c" * 64,
                },
            ],
        },
    ]


def _create_generalization_manifest(module) -> tuple[dict[str, Any], dict[str, Any]]:
    selection = module.complete_reference_selection_artifact(
        module.create_reference_selection_artifact(REFERENCE_VARIANTS),
        winner_reference_variant="R3_DC_TRIM_HP",
        variant_reviews=_create_variant_reviews(),
        review_date="2026-07-20",
        reviewer="reviewer-test",
        notes="Winner đã được review hoàn tất.",
    )
    manifest = module.create_generalization_experiment_manifest(
        experiment_id="avs01424-c3-generalization-001",
        winner_reference_variant="R3_DC_TRIM_HP",
        dataset_version="dataset-2026-07-20",
        categories=_create_generalization_categories(),
        generation_metadata={
            "scope": "DIAGNOSTIC_ONLY",
            "production_binding_changed": False,
            "inference_executed": False,
        },
        reference_selection_artifact=selection,
    )
    return manifest, selection


def test_generalization_manifest_accepts_multiple_caller_defined_categories():
    module = _load_runner_module()
    manifest, selection = _create_generalization_manifest(module)

    assert manifest["experiment_type"] == "REFERENCE_GENERALIZATION"
    assert manifest["winner_reference_variant"] == selection["winner_reference_variant"]
    assert [category["category"] for category in manifest["categories"]] == [
        "narration",
        "difficult-pronunciation",
    ]
    assert [category["sample_count"] for category in manifest["categories"]] == [2, 1]
    assert manifest["generation_metadata"]["scope"] == "DIAGNOSTIC_ONLY"


@pytest.mark.parametrize(
    ("mutation", "expected_error"),
    [
        (
            lambda manifest: manifest["categories"].append(
                {"sample_count": 1, "samples": [{"sample_id": "x", "input_text_sha256": "d" * 64}]}
            ),
            "GENERALIZATION_EXPERIMENT_CATEGORY_MISSING",
        ),
        (
            lambda manifest: manifest["categories"].append(
                {
                    "category": "empty",
                    "sample_count": 0,
                    "samples": [],
                }
            ),
            "GENERALIZATION_EXPERIMENT_CATEGORY_SAMPLES_MISSING",
        ),
        (
            lambda manifest: manifest["categories"][0]["samples"][0].pop(
                "input_text_sha256"
            ),
            "GENERALIZATION_EXPERIMENT_SAMPLE_MAPPING_INCOMPLETE",
        ),
        (
            lambda manifest: manifest.update(
                {"winner_reference_variant": "R2_DC_TRIM"}
            ),
            "GENERALIZATION_EXPERIMENT_WINNER_MISMATCH",
        ),
    ],
)
def test_generalization_manifest_rejects_invalid_categories_mappings_and_winner(
    mutation,
    expected_error,
):
    module = _load_runner_module()
    manifest, selection = _create_generalization_manifest(module)

    mutation(manifest)

    with pytest.raises(ValueError, match=expected_error):
        module.validate_generalization_experiment_manifest(manifest, selection)


def _create_ready_production_artifact(module) -> dict[str, object]:
    return module.create_production_readiness_artifact(
        winner_reference_variant="R3_DC_TRIM_HP",
        reference_selection_status=module.REVIEW_COMPLETED,
        generalization_status=module.GENERALIZATION_COMPLETED,
        validation_status=module.VALIDATION_PASS,
        blocker_list=[],
        generated_at="2026-07-20T12:00:00+07:00",
    )


def test_production_readiness_loader_returns_only_valid_ready_artifact(tmp_path):
    module = _load_runner_module()
    artifact = _create_ready_production_artifact(module)
    artifact_path = tmp_path / "production_readiness.json"
    artifact_path.write_text(json.dumps(artifact), encoding="utf-8")

    loaded = module.load_production_ready_artifact(artifact_path)

    assert loaded == artifact
    assert loaded["readiness_status"] == module.PRODUCTION_READINESS_READY
    assert loaded["blocker_list"] == []


def test_production_readiness_creator_marks_incomplete_gate_not_ready():
    module = _load_runner_module()

    artifact = module.create_production_readiness_artifact(
        winner_reference_variant="R3_DC_TRIM_HP",
        reference_selection_status=module.REVIEW_COMPLETED,
        generalization_status="PENDING",
        validation_status=module.VALIDATION_PASS,
        blocker_list=["GENERALIZATION_PENDING"],
        generated_at="2026-07-20T12:00:00+07:00",
    )

    assert artifact["readiness_status"] == module.PRODUCTION_READINESS_NOT_READY
    assert artifact["blocker_list"] == ["GENERALIZATION_PENDING"]


@pytest.mark.parametrize(
    ("artifact_path_factory", "expected_error"),
    [
        (
            lambda tmp_path, module: tmp_path / "missing_production_readiness.json",
            "PRODUCTION_READINESS_NOT_READY",
        ),
        (
            lambda tmp_path, module: (
                tmp_path / "malformed_production_readiness.json"
            ),
            "PRODUCTION_READINESS_NOT_READY",
        ),
    ],
)
def test_production_readiness_loader_fails_closed_for_missing_or_invalid_artifact(
    tmp_path,
    artifact_path_factory,
    expected_error,
):
    module = _load_runner_module()
    artifact_path = artifact_path_factory(tmp_path, module)
    if artifact_path.name.startswith("malformed"):
        artifact_path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(module.ProductionReadinessNotReadyError, match=expected_error):
        module.load_production_ready_artifact(artifact_path)


@pytest.mark.parametrize(
    ("mutation", "expected_error"),
    [
        (
            lambda artifact: artifact.update({"blocker_list": ["UNRESOLVED_BLOCKER"]}),
            "PRODUCTION_READINESS_ARTIFACT_READY_WITH_BLOCKERS",
        ),
        (
            lambda artifact: artifact.update({"generalization_status": "PENDING"}),
            "PRODUCTION_READINESS_ARTIFACT_READY_GATES_INCOMPLETE",
        ),
        (
            lambda artifact: artifact.update(
                {"reference_selection_status": "MANUAL_REVIEW_PENDING"}
            ),
            "PRODUCTION_READINESS_ARTIFACT_READY_GATES_INCOMPLETE",
        ),
        (
            lambda artifact: artifact.update({"validation_status": "FAIL"}),
            "PRODUCTION_READINESS_ARTIFACT_READY_GATES_INCOMPLETE",
        ),
    ],
)
def test_production_readiness_validator_rejects_ready_state_contradictions(
    mutation,
    expected_error,
):
    module = _load_runner_module()
    artifact = _create_ready_production_artifact(module)
    mutation(artifact)

    with pytest.raises(ValueError, match=expected_error):
        module.validate_production_readiness_artifact(artifact)


def test_production_readiness_loader_rejects_not_ready_artifact_with_blocker(tmp_path):
    module = _load_runner_module()
    artifact = module.create_production_readiness_artifact(
        winner_reference_variant="R3_DC_TRIM_HP",
        reference_selection_status=module.REVIEW_COMPLETED,
        generalization_status=module.GENERALIZATION_COMPLETED,
        validation_status=module.VALIDATION_PASS,
        blocker_list=["PRODUCTION_BINDING_NOT_APPROVED"],
        generated_at="2026-07-20T12:00:00+07:00",
    )
    artifact_path = tmp_path / "blocked_production_readiness.json"
    artifact_path.write_text(json.dumps(artifact), encoding="utf-8")

    with pytest.raises(
        module.ProductionReadinessNotReadyError,
        match="PRODUCTION_READINESS_NOT_READY",
    ):
        module.load_production_ready_artifact(artifact_path)

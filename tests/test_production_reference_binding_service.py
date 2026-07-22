from __future__ import annotations

from types import MappingProxyType
from typing import cast

import pytest

from src.services.production_reference_binding_service import (
    ProductionReferenceBindingError,
    ProductionReferenceBindingService,
)


WINNER = "R3_DC_TRIM_HP"


def _artifacts() -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    selection = {
        "status": "REVIEW_COMPLETED",
        "review_status": "REVIEW_COMPLETED",
        "review_completed": True,
        "available_reference_variants": ["R1_RAW", WINNER],
        "winner_reference_variant": WINNER,
    }
    generalization = {
        "experiment_type": "REFERENCE_GENERALIZATION",
        "winner_reference_variant": WINNER,
        "categories": [{"category": "narration", "samples": [{"sample_id": "s1"}]}],
        "generation_metadata": {"runtime": "diagnostic-only"},
    }
    readiness = {
        "winner_reference_variant": WINNER,
        "readiness_status": "READY",
        "reference_selection_status": "REVIEW_COMPLETED",
        "generalization_status": "COMPLETED",
        "validation_status": "PASS",
        "blocker_list": [],
    }
    return selection, generalization, readiness


def _bind(
    selection: object | None = None,
    generalization: object | None = None,
    readiness: object | None = None,
):
    valid_selection, valid_generalization, valid_readiness = _artifacts()
    return ProductionReferenceBindingService().bind_winner(
        reference_selection=valid_selection if selection is None else selection,
        generalization=valid_generalization if generalization is None else generalization,
        production_readiness=valid_readiness if readiness is None else readiness,
    )


def test_bind_winner_returns_only_consistent_ready_winner():
    binding = _bind()

    assert binding.winner_reference_variant == WINNER
    assert isinstance(binding.reference_selection, MappingProxyType)
    assert isinstance(binding.generalization, MappingProxyType)
    assert isinstance(binding.production_readiness, MappingProxyType)
    with pytest.raises(TypeError):
        cast(dict[str, object], binding.reference_selection)[
            "winner_reference_variant"
        ] = "R1_RAW"


@pytest.mark.parametrize(
    ("field", "value", "expected_error"),
    [
        ("review_completed", False, "SELECTION_NOT_READY"),
        ("status", "MANUAL_REVIEW_PENDING", "SELECTION_NOT_READY"),
        ("review_status", "MANUAL_REVIEW_PENDING", "SELECTION_NOT_READY"),
        ("available_reference_variants", ["R1_RAW"], "SELECTION_NOT_READY"),
        ("winner_reference_variant", None, "WINNER_INVALID"),
    ],
)
def test_bind_winner_fails_closed_when_reference_selection_is_not_ready(
    field,
    value,
    expected_error,
):
    selection, _, _ = _artifacts()
    selection[field] = value

    with pytest.raises(ProductionReferenceBindingError, match=expected_error):
        _bind(selection=selection)


@pytest.mark.parametrize(
    ("field", "value", "expected_error"),
    [
        ("winner_reference_variant", "R1_RAW", "GENERALIZATION_NOT_READY"),
        ("experiment_type", "OTHER", "GENERALIZATION_NOT_READY"),
        ("categories", [], "GENERALIZATION_NOT_READY"),
        ("generation_metadata", {}, "GENERALIZATION_NOT_READY"),
        ("winner_reference_variant", None, "GENERALIZATION_WINNER_INVALID"),
    ],
)
def test_bind_winner_fails_closed_when_generalization_is_not_ready(
    field,
    value,
    expected_error,
):
    _, generalization, _ = _artifacts()
    generalization[field] = value

    with pytest.raises(ProductionReferenceBindingError, match=expected_error):
        _bind(generalization=generalization)


@pytest.mark.parametrize(
    ("field", "value", "expected_error"),
    [
        ("winner_reference_variant", "R1_RAW", "ARTIFACT_INCONSISTENT"),
        ("readiness_status", "NOT_READY", "READINESS_NOT_READY"),
        ("reference_selection_status", "MANUAL_REVIEW_PENDING", "READINESS_NOT_READY"),
        ("generalization_status", "PENDING", "READINESS_NOT_READY"),
        ("validation_status", "FAIL", "READINESS_NOT_READY"),
        ("blocker_list", ["UNRESOLVED_BLOCKER"], "READINESS_NOT_READY"),
        ("winner_reference_variant", None, "READINESS_WINNER_INVALID"),
    ],
)
def test_bind_winner_fails_closed_when_production_readiness_is_not_ready(
    field,
    value,
    expected_error,
):
    _, _, readiness = _artifacts()
    readiness[field] = value

    with pytest.raises(ProductionReferenceBindingError, match=expected_error):
        _bind(readiness=readiness)


@pytest.mark.parametrize(
    ("selection", "generalization", "readiness", "expected_error"),
    [
        ([], None, None, "SELECTION_INVALID"),
        (None, [], None, "GENERALIZATION_INVALID"),
        (None, None, [], "READINESS_INVALID"),
    ],
)
def test_bind_winner_rejects_non_mapping_artifacts(
    selection,
    generalization,
    readiness,
    expected_error,
):
    with pytest.raises(ProductionReferenceBindingError, match=expected_error):
        _bind(selection=selection, generalization=generalization, readiness=readiness)


def test_consumer_must_receive_winner_from_binding_service():
    service = ProductionReferenceBindingService()
    selection, generalization, readiness = _artifacts()

    binding = service.bind_winner(
        reference_selection=selection,
        generalization=generalization,
        production_readiness=readiness,
    )

    assert binding.winner_reference_variant == WINNER
    assert not hasattr(service, "load_winner_reference_variant")
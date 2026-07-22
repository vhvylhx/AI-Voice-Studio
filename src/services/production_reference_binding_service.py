"""Fail-closed binding của winner reference đã được phê duyệt cho production."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


REFERENCE_SELECTION_READY = "REVIEW_COMPLETED"
GENERALIZATION_READY = "COMPLETED"
PRODUCTION_READINESS_READY = "READY"
VALIDATION_PASS = "PASS"


class ProductionReferenceBindingError(RuntimeError):
    """Báo lỗi khi winner reference chưa đủ điều kiện bind cho production."""


@dataclass(frozen=True)
class ProductionReferenceBinding:
    """Snapshot bất biến của winner đã qua toàn bộ gate C5."""

    winner_reference_variant: str
    reference_selection: Mapping[str, object]
    generalization: Mapping[str, object]
    production_readiness: Mapping[str, object]


class ProductionReferenceBindingService:
    """Chỉ là cổng bind; không chạy inference, generate hoặc thay đổi artifact."""

    def bind_winner(
        self,
        *,
        reference_selection: object,
        generalization: object,
        production_readiness: object,
    ) -> ProductionReferenceBinding:
        """Trả winner duy nhất khi selection, generalization và readiness đều READY."""
        selection = self._require_mapping(
            reference_selection,
            "PRODUCTION_REFERENCE_BINDING_SELECTION_INVALID",
        )
        generalization_artifact = self._require_mapping(
            generalization,
            "PRODUCTION_REFERENCE_BINDING_GENERALIZATION_INVALID",
        )
        readiness = self._require_mapping(
            production_readiness,
            "PRODUCTION_REFERENCE_BINDING_READINESS_INVALID",
        )

        winner = self._require_nonempty_string(
            selection.get("winner_reference_variant"),
            "PRODUCTION_REFERENCE_BINDING_WINNER_INVALID",
        )
        variants = selection.get("available_reference_variants")
        if (
            selection.get("review_completed") is not True
            or selection.get("status") != REFERENCE_SELECTION_READY
            or selection.get("review_status") != REFERENCE_SELECTION_READY
            or not isinstance(variants, list)
            or winner not in variants
        ):
            raise ProductionReferenceBindingError(
                "PRODUCTION_REFERENCE_BINDING_SELECTION_NOT_READY"
            )

        if (
            self._require_nonempty_string(
                generalization_artifact.get("winner_reference_variant"),
                "PRODUCTION_REFERENCE_BINDING_GENERALIZATION_WINNER_INVALID",
            )
            != winner
            or generalization_artifact.get("experiment_type")
            != "REFERENCE_GENERALIZATION"
            or not isinstance(generalization_artifact.get("categories"), list)
            or not generalization_artifact["categories"]
            or not isinstance(generalization_artifact.get("generation_metadata"), dict)
            or not generalization_artifact["generation_metadata"]
        ):
            raise ProductionReferenceBindingError(
                "PRODUCTION_REFERENCE_BINDING_GENERALIZATION_NOT_READY"
            )

        if (
            self._require_nonempty_string(
                readiness.get("winner_reference_variant"),
                "PRODUCTION_REFERENCE_BINDING_READINESS_WINNER_INVALID",
            )
            != winner
        ):
            raise ProductionReferenceBindingError(
                "PRODUCTION_REFERENCE_BINDING_ARTIFACT_INCONSISTENT"
            )
        if (
            readiness.get("readiness_status") != PRODUCTION_READINESS_READY
            or readiness.get("reference_selection_status") != REFERENCE_SELECTION_READY
            or readiness.get("generalization_status") != GENERALIZATION_READY
            or readiness.get("validation_status") != VALIDATION_PASS
            or readiness.get("blocker_list") != []
        ):
            raise ProductionReferenceBindingError(
                "PRODUCTION_REFERENCE_BINDING_READINESS_NOT_READY"
            )

        return ProductionReferenceBinding(
            winner_reference_variant=winner,
            reference_selection=MappingProxyType(dict(selection)),
            generalization=MappingProxyType(dict(generalization_artifact)),
            production_readiness=MappingProxyType(dict(readiness)),
        )

    @staticmethod
    def _require_mapping(value: object, error_code: str) -> Mapping[str, object]:
        if not isinstance(value, Mapping):
            raise ProductionReferenceBindingError(error_code)
        return value

    @staticmethod
    def _require_nonempty_string(value: object, error_code: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ProductionReferenceBindingError(error_code)
        return value
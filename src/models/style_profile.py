from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields


STYLE_PROFILE_SCHEMA_VERSION = 1


STYLE_STATUS_DRAFT = "draft"
STYLE_STATUS_SOURCE_READY = "source_ready"
STYLE_STATUS_EXTRACTION_PENDING = "extraction_pending"
STYLE_STATUS_EXTRACTING = "extracting"
STYLE_STATUS_PARTIAL = "partial"
STYLE_STATUS_READY = "ready"
STYLE_STATUS_DEGRADED = "degraded"
STYLE_STATUS_INVALID = "invalid"
STYLE_STATUS_ARCHIVED = "archived"


STYLE_SOURCE_DATASET = "dataset"
STYLE_SOURCE_ALIGNED_DATASET = "aligned_dataset"
STYLE_SOURCE_IMPORTED_PACKAGE = "imported_package"
STYLE_SOURCE_MANUAL_REFERENCE_LIBRARY = "manual_reference_library"


STYLE_MODE_INHERIT = "inherit_voice_default"
STYLE_MODE_EXPLICIT = "explicit"
STYLE_MODE_DISABLED = "disabled"


DEFAULT_STYLE_CAPABILITIES = {
    "pause_profile": False,
    "rhythm_profile": False,
    "punctuation_profile": False,
    "intonation_profile": False,
    "emphasis_profile": False,
    "breathing_profile": False,
    "dialogue_profile": False,
    "narrator_profile": False,
    "emotion_clusters": False,
    "reading_fingerprint": False,
}


@dataclass
class StyleProfile:

    schema_version: int = STYLE_PROFILE_SCHEMA_VERSION

    style_profile_id: str = ""

    display_name: str = ""

    description: str = ""

    language: str = "vi"

    source_type: str = STYLE_SOURCE_ALIGNED_DATASET

    status: str = STYLE_STATUS_DRAFT

    created_at: str = ""

    updated_at: str = ""

    source_summary: dict = field(
        default_factory=lambda: {
            "total_files": 0,
            "total_duration_seconds": 0.0,
            "aligned_segments": 0,
            "transcript_coverage": 0.0,
            "language": "vi",
            "last_scanned_at": "",
        }
    )

    dataset_reference: dict = field(
        default_factory=dict
    )

    source_assets: dict = field(
        default_factory=lambda: {
            "audio_asset_ids": [],
            "text_asset_ids": [],
            "manifest_asset_id": "",
            "validation_report_asset_id": "",
        }
    )

    extraction_summary: dict = field(
        default_factory=lambda: {
            "processed_segments": 0,
            "failed_segments": 0,
            "warnings": [],
            "extraction_version": "",
            "completed_at": "",
        }
    )

    capabilities: dict = field(
        default_factory=lambda: dict(
            DEFAULT_STYLE_CAPABILITIES
        )
    )

    default_tags: list[str] = field(
        default_factory=list
    )

    integrity: dict = field(
        default_factory=lambda: {
            "manifest_hash": "",
            "missing_files": [],
            "invalid_files": [],
            "last_verified_at": "",
        }
    )

    portability: dict = field(
        default_factory=lambda: {
            "package_version": 1,
            "relative_paths_only": True,
            "can_export": True,
            "can_import": True,
        }
    )

    metadata: dict = field(
        default_factory=dict
    )

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        data = data or {}

        names = {
            item.name
            for item in fields(cls)
        }

        migrated = {
            name: data[name]
            for name in names
            if name in data
        }

        profile = cls(
            **migrated
        )

        profile.schema_version = int(
            data.get(
                "schema_version",
                STYLE_PROFILE_SCHEMA_VERSION,
            )
            or STYLE_PROFILE_SCHEMA_VERSION
        )

        profile.capabilities = {
            **DEFAULT_STYLE_CAPABILITIES,
            **dict(
                profile.capabilities or {}
            ),
        }

        return profile

    def to_dict(
        self,
    ):

        return asdict(
            self
        )

    def validate(
        self,
    ):

        errors = []

        if not self.style_profile_id:

            errors.append(
                "style_profile_id_required"
            )

        if not str(
            self.style_profile_id
        ).startswith(
            "style_"
        ):

            errors.append(
                "style_profile_id_invalid"
            )

        if not self.display_name:

            errors.append(
                "display_name_required"
            )

        if self.status not in {
            STYLE_STATUS_DRAFT,
            STYLE_STATUS_SOURCE_READY,
            STYLE_STATUS_EXTRACTION_PENDING,
            STYLE_STATUS_EXTRACTING,
            STYLE_STATUS_PARTIAL,
            STYLE_STATUS_READY,
            STYLE_STATUS_DEGRADED,
            STYLE_STATUS_INVALID,
            STYLE_STATUS_ARCHIVED,
        }:

            errors.append(
                "status_invalid"
            )

        return errors

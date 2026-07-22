from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field as dc_field
from datetime import datetime
from uuid import uuid4


GENERATE_FOUNDATION_SCHEMA_VERSION = 1

GENERATE_STATE_CREATED = "created"
GENERATE_STATE_VALIDATED = "validated"
GENERATE_STATE_PLANNED = "planned"
GENERATE_STATE_READY = "ready"
GENERATE_STATE_RUNNING = "running"
GENERATE_STATE_PAUSED = "paused"
GENERATE_STATE_COMPLETED = "completed"
GENERATE_STATE_FAILED = "failed"
GENERATE_STATE_CANCELLED = "cancelled"
GENERATE_STATE_BLOCKED = "blocked"


def now_iso():

    return datetime.now().isoformat()


def new_id(
    prefix,
):

    return f"{prefix}_{uuid4().hex[:12]}"


def clean_dict(
    value,
):

    if hasattr(
        value,
        "to_dict",
    ):

        return value.to_dict()

    if isinstance(
        value,
        list,
    ):

        return [
            clean_dict(
                item
            )
            for item in value
        ]

    if isinstance(
        value,
        dict,
    ):

        return {
            key: clean_dict(
                item
            )
            for key, item in value.items()
        }

    return value


def dataclass_from_dict(
    cls,
    data,
):

    if isinstance(
        data,
        cls,
    ):

        return data

    data = data or {}

    return cls(
        **{
            key: value
            for key, value in data.items()
            if key in cls.__dataclass_fields__
        }
    )


@dataclass
class GenerateIssue:

    code: str = ""

    message_vi: str = ""

    field: str = ""

    severity: str = "error"

    suggestion: str = ""

    details: dict = dc_field(
        default_factory=dict
    )

    def to_dict(
        self,
    ):

        return asdict(
            self
        )

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        return dataclass_from_dict(
            cls,
            data,
        )


@dataclass
class GenerateValidationReport:

    ok: bool = False

    issues: list[GenerateIssue] = dc_field(
        default_factory=list
    )

    warnings: list[GenerateIssue] = dc_field(
        default_factory=list
    )

    checked_at: str = dc_field(
        default_factory=now_iso
    )

    def to_dict(
        self,
    ):

        return {
            "ok": self.ok,
            "issues": [
                item.to_dict()
                for item in self.issues
            ],
            "warnings": [
                item.to_dict()
                for item in self.warnings
            ],
            "checked_at": self.checked_at,
        }

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        data = data or {}

        return cls(
            ok=bool(
                data.get(
                    "ok",
                    False,
                )
            ),
            issues=[
                GenerateIssue.from_dict(
                    item
                )
                for item in data.get(
                    "issues",
                    []
                )
            ],
            warnings=[
                GenerateIssue.from_dict(
                    item
                )
                for item in data.get(
                    "warnings",
                    []
                )
            ],
            checked_at=data.get(
                "checked_at",
                now_iso(),
            ),
        )


@dataclass
class GenerateReconstructionReport:

    ok: bool = False

    policy_version: str = "reconstruct_v1"

    separator_policy: str = "unit.separator_after"

    source_checksum_sha256: str = ""

    normalized_checksum_sha256: str = ""

    reconstructed_checksum_sha256: str = ""

    mismatch_index: int = -1

    message_vi: str = ""

    checked_at: str = dc_field(
        default_factory=now_iso
    )

    def to_dict(
        self,
    ):

        return asdict(
            self
        )

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        return dataclass_from_dict(
            cls,
            data,
        )


@dataclass
class GenerateSelectionSnapshot:

    voice_id: str = ""

    variant_id: str = ""

    style_id: str = ""

    mode: str = "standard"

    speed: float = 1.0

    language: str = "vi"

    allowed_variant_ids: list[str] = dc_field(
        default_factory=list
    )

    allowed_style_ids: list[str] = dc_field(
        default_factory=list
    )

    allow_all_variants: bool = False

    allow_all_styles: bool = False

    extra: dict = dc_field(
        default_factory=dict
    )

    def to_dict(
        self,
    ):

        return asdict(
            self
        )

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        return dataclass_from_dict(
            cls,
            data,
        )


@dataclass
class GenerateOutputSpec:

    output_folder: str = ""

    output_name: str = ""

    output_format: str = "wav"

    mp3_bitrate_kbps: int = 192

    overwrite: bool = False

    final_output_path: str = ""

    report_path: str = ""

    temp_output_path: str = ""

    reserved: bool = False

    collision_policy: str = "fail_if_exists"

    def to_dict(
        self,
    ):

        return asdict(
            self
        )

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        return dataclass_from_dict(
            cls,
            data,
        )


@dataclass
class GenerateSourceSnapshot:

    source_id: str = dc_field(
        default_factory=lambda: new_id(
            "source"
        )
    )

    source_type: str = "pasted_text"

    original_path: str = ""

    snapshot_path: str = ""

    checksum_sha256: str = ""

    character_count: int = 0

    line_count: int = 0

    language: str = "vi"

    created_at: str = dc_field(
        default_factory=now_iso
    )

    def to_dict(
        self,
    ):

        return asdict(
            self
        )

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        return dataclass_from_dict(
            cls,
            data,
        )


@dataclass
class GenerateRequestRecord:

    request_id: str = dc_field(
        default_factory=lambda: new_id(
            "greq"
        )
    )

    revision: int = 1

    materialized_at: str = ""

    request_checksum_sha256: str = ""

    project_id: str = ""

    voice_id: str = ""

    source: GenerateSourceSnapshot = dc_field(
        default_factory=GenerateSourceSnapshot
    )

    selection: GenerateSelectionSnapshot = dc_field(
        default_factory=GenerateSelectionSnapshot
    )

    output: GenerateOutputSpec = dc_field(
        default_factory=GenerateOutputSpec
    )

    validation: GenerateValidationReport = dc_field(
        default_factory=GenerateValidationReport
    )

    status: str = GENERATE_STATE_CREATED

    created_at: str = dc_field(
        default_factory=now_iso
    )

    schema_version: int = GENERATE_FOUNDATION_SCHEMA_VERSION

    def to_dict(
        self,
    ):

        data = asdict(
            self
        )

        return clean_dict(
            data
        )

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        data = dict(
            data or {}
        )

        data["source"] = GenerateSourceSnapshot.from_dict(
            data.get(
                "source",
                {},
            )
        )

        data["selection"] = GenerateSelectionSnapshot.from_dict(
            data.get(
                "selection",
                {},
            )
        )

        data["output"] = GenerateOutputSpec.from_dict(
            data.get(
                "output",
                {},
            )
        )

        data["validation"] = GenerateValidationReport.from_dict(
            data.get(
                "validation",
                {},
            )
        )

        return dataclass_from_dict(
            cls,
            data,
        )


@dataclass
class GenerateSessionRecord:

    session_id: str = dc_field(
        default_factory=lambda: new_id(
            "gses"
        )
    )

    request_id: str = ""

    project_id: str = ""

    voice_id: str = ""

    status: str = GENERATE_STATE_CREATED

    current_unit_id: str = ""

    progress_percent: float = 0.0

    health: str = "unknown"

    allowed_actions: dict = dc_field(
        default_factory=dict
    )

    created_at: str = dc_field(
        default_factory=now_iso
    )

    updated_at: str = dc_field(
        default_factory=now_iso
    )

    schema_version: int = GENERATE_FOUNDATION_SCHEMA_VERSION

    def to_dict(
        self,
    ):

        return asdict(
            self
        )

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        return dataclass_from_dict(
            cls,
            data,
        )


@dataclass
class GenerateDocumentRecord:

    document_id: str = dc_field(
        default_factory=lambda: new_id(
            "gdoc"
        )
    )

    session_id: str = ""

    title: str = ""

    normalized_text_path: str = ""

    chapter_ids: list[str] = dc_field(
        default_factory=list
    )

    unit_count: int = 0

    character_count: int = 0

    language: str = "vi"

    def to_dict(
        self,
    ):

        return asdict(
            self
        )

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        return dataclass_from_dict(
            cls,
            data,
        )


@dataclass
class GenerateChapterRecord:

    chapter_id: str = dc_field(
        default_factory=lambda: new_id(
            "gchap"
        )
    )

    document_id: str = ""

    title: str = ""

    order: int = 0

    start_index: int = 0

    end_index: int = 0

    unit_ids: list[str] = dc_field(
        default_factory=list
    )

    def to_dict(
        self,
    ):

        return asdict(
            self
        )

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        return dataclass_from_dict(
            cls,
            data,
        )


@dataclass
class GenerateUnitRecord:

    unit_id: str = dc_field(
        default_factory=lambda: new_id(
            "gunit"
        )
    )

    chapter_id: str = ""

    order: int = 0

    text: str = ""

    normalized_text: str = ""

    boundary: str = "sentence"

    separator_after: str = ""

    language_code: str = ""

    engine_id: str = ""

    route_status: str = ""

    route_fingerprint: str = ""

    route_blockers: list[str] = dc_field(
        default_factory=list
    )

    status: str = "pending"

    attempt_ids: list[str] = dc_field(
        default_factory=list
    )

    estimated_characters: int = 0

    def to_dict(
        self,
    ):

        return asdict(
            self
        )

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        return dataclass_from_dict(
            cls,
            data,
        )


@dataclass
class GenerateAttemptRecord:

    attempt_id: str = dc_field(
        default_factory=lambda: new_id(
            "gatt"
        )
    )

    unit_id: str = ""

    attempt_index: int = 0

    status: str = "pending"

    job_id: str = ""

    artifact_id: str = ""

    reservation_id: str = ""

    error_code: str = ""

    error_message: str = ""

    artifact_path: str = ""

    started_at: str = ""

    finished_at: str = ""

    def to_dict(
        self,
    ):

        return asdict(
            self
        )

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        return dataclass_from_dict(
            cls,
            data,
        )


@dataclass
class GeneratePlanRecord:

    plan_id: str = dc_field(
        default_factory=lambda: new_id(
            "gplan"
        )
    )

    session_id: str = ""

    document_id: str = ""

    chapters: list[GenerateChapterRecord] = dc_field(
        default_factory=list
    )

    units: list[GenerateUnitRecord] = dc_field(
        default_factory=list
    )

    attempts: list[GenerateAttemptRecord] = dc_field(
        default_factory=list
    )

    status: str = GENERATE_STATE_PLANNED

    created_at: str = dc_field(
        default_factory=now_iso
    )

    frozen: bool = True

    settings_snapshot: dict = dc_field(
        default_factory=dict
    )

    selection_snapshot: dict = dc_field(
        default_factory=dict
    )

    output_snapshot: dict = dc_field(
        default_factory=dict
    )

    plan_checksum_sha256: str = ""

    immutable_checksum_sha256: str = ""

    freeze_version: int = 1

    frozen_at: str = ""

    reconstruction_report: GenerateReconstructionReport = dc_field(
        default_factory=GenerateReconstructionReport
    )

    def immutable_payload(
        self,
    ):

        return {
            "plan_id": self.plan_id,
            "session_id": self.session_id,
            "document_id": self.document_id,
            "chapters": [
                chapter.to_dict()
                for chapter in self.chapters
            ],
            "units": [
                {
                    "unit_id": unit.unit_id,
                    "chapter_id": unit.chapter_id,
                    "order": unit.order,
                    "text": unit.text,
                    "normalized_text": unit.normalized_text,
                    "boundary": unit.boundary,
                    "separator_after": unit.separator_after,
                    "language_code": unit.language_code,
                    "engine_id": unit.engine_id,
                    "route_status": unit.route_status,
                    "route_fingerprint": unit.route_fingerprint,
                    "route_blockers": unit.route_blockers,
                    "estimated_characters": unit.estimated_characters,
                }
                for unit in self.units
            ],
            "settings_snapshot": clean_dict(
                self.settings_snapshot
            ),
            "selection_snapshot": clean_dict(
                self.selection_snapshot
            ),
            "output_snapshot": clean_dict(
                self.output_snapshot
            ),
            "freeze_version": self.freeze_version,
            "reconstruction_report": self.reconstruction_report.to_dict(),
        }

    def to_dict(
        self,
    ):

        return {
            "plan_id": self.plan_id,
            "session_id": self.session_id,
            "document_id": self.document_id,
            "chapters": [
                item.to_dict()
                for item in self.chapters
            ],
            "units": [
                item.to_dict()
                for item in self.units
            ],
            "attempts": [
                item.to_dict()
                for item in self.attempts
            ],
            "status": self.status,
            "created_at": self.created_at,
            "frozen": self.frozen,
            "settings_snapshot": clean_dict(
                self.settings_snapshot
            ),
            "selection_snapshot": clean_dict(
                self.selection_snapshot
            ),
            "output_snapshot": clean_dict(
                self.output_snapshot
            ),
            "plan_checksum_sha256": self.plan_checksum_sha256,
            "immutable_checksum_sha256": self.immutable_checksum_sha256,
            "freeze_version": self.freeze_version,
            "frozen_at": self.frozen_at,
            "reconstruction_report": self.reconstruction_report.to_dict(),
        }

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        data = data or {}

        return cls(
            plan_id=data.get(
                "plan_id",
                new_id(
                    "gplan"
                ),
            ),
            session_id=data.get(
                "session_id",
                "",
            ),
            document_id=data.get(
                "document_id",
                "",
            ),
            chapters=[
                GenerateChapterRecord.from_dict(
                    item
                )
                for item in data.get(
                    "chapters",
                    []
                )
            ],
            units=[
                GenerateUnitRecord.from_dict(
                    item
                )
                for item in data.get(
                    "units",
                    []
                )
            ],
            attempts=[
                GenerateAttemptRecord.from_dict(
                    item
                )
                for item in data.get(
                    "attempts",
                    []
                )
            ],
            status=data.get(
                "status",
                GENERATE_STATE_PLANNED,
            ),
            created_at=data.get(
                "created_at",
                now_iso(),
            ),
            frozen=bool(
                data.get(
                    "frozen",
                    True,
                )
            ),
            settings_snapshot=dict(
                data.get(
                    "settings_snapshot",
                    {},
                )
                or {}
            ),
            selection_snapshot=dict(
                data.get(
                    "selection_snapshot",
                    {},
                )
                or {}
            ),
            output_snapshot=dict(
                data.get(
                    "output_snapshot",
                    {},
                )
                or {}
            ),
            plan_checksum_sha256=data.get(
                "plan_checksum_sha256",
                "",
            ),
            immutable_checksum_sha256=data.get(
                "immutable_checksum_sha256",
                "",
            ),
            freeze_version=int(
                data.get(
                    "freeze_version",
                    1,
                )
                or 1
            ),
            frozen_at=data.get(
                "frozen_at",
                "",
            ),
            reconstruction_report=GenerateReconstructionReport.from_dict(
                data.get(
                    "reconstruction_report",
                    {},
                )
            ),
        )


@dataclass
class GenerateArtifactRecord:

    artifact_id: str = dc_field(
        default_factory=lambda: new_id(
            "gart"
        )
    )

    session_id: str = ""

    unit_id: str = ""

    attempt_id: str = ""

    kind: str = "planned_audio"

    role: str = "unit_audio"

    project_id: str = ""

    plan_id: str = ""

    plan_checksum_sha256: str = ""

    input_fingerprint: str = ""

    output_format: str = "wav"

    reservation_id: str = ""

    reserved_at: str = ""

    planned_path: str = ""

    temp_path: str = ""

    final_path: str = ""

    status: str = "planned"

    checksum_sha256: str = ""

    validation_status: str = "not_validated"

    validation_errors: list[str] = dc_field(
        default_factory=list
    )

    duration_seconds: float = 0.0

    sample_rate: int = 0

    channels: int = 0

    created_at: str = dc_field(
        default_factory=now_iso
    )

    updated_at: str = dc_field(
        default_factory=now_iso
    )

    def to_dict(
        self,
    ):

        return asdict(
            self
        )

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        return dataclass_from_dict(
            cls,
            data,
        )


@dataclass
class GenerateManifestRecord:

    manifest_id: str = dc_field(
        default_factory=lambda: new_id(
            "gmanifest"
        )
    )

    session_id: str = ""

    request_id: str = ""

    plan_id: str = ""

    status: str = GENERATE_STATE_READY

    source: dict = dc_field(
        default_factory=dict
    )

    output: dict = dc_field(
        default_factory=dict
    )

    artifacts: list[dict] = dc_field(
        default_factory=list
    )

    artifact_records: list[GenerateArtifactRecord] = dc_field(
        default_factory=list
    )

    units_total: int = 0

    units_completed: int = 0

    units_failed: int = 0

    warnings: list[str] = dc_field(
        default_factory=list
    )

    errors: list[str] = dc_field(
        default_factory=list
    )

    created_at: str = dc_field(
        default_factory=now_iso
    )

    schema_version: int = GENERATE_FOUNDATION_SCHEMA_VERSION

    def to_dict(
        self,
    ):

        data = asdict(
            self
        )

        data[
            "artifact_records"
        ] = [
            GenerateArtifactRecord.from_dict(
                item
            ).to_dict()
            for item in self.artifact_records
        ]

        return data

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        data = dict(
            data or {}
        )

        data[
            "artifact_records"
        ] = [
            GenerateArtifactRecord.from_dict(
                item
            )
            for item in data.get(
                "artifact_records",
                []
            )
        ]

        return dataclass_from_dict(
            cls,
            data,
        )


@dataclass
class GenerateRegistryEntry:

    session_id: str = ""

    request_id: str = ""

    project_id: str = ""

    voice_id: str = ""

    status: str = GENERATE_STATE_CREATED

    created_at: str = dc_field(
        default_factory=now_iso
    )

    updated_at: str = dc_field(
        default_factory=now_iso
    )

    manifest_path: str = ""

    output_path: str = ""

    def to_dict(
        self,
    ):

        return asdict(
            self
        )

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        return dataclass_from_dict(
            cls,
            data,
        )


@dataclass
class GenerateSettings:

    default_language: str = "vi"

    max_unit_characters: int = 700

    min_unit_characters: int = 20

    supported_source_types: list[str] = dc_field(
        default_factory=lambda: [
            "pasted_text",
            "txt",
            "docx",
        ]
    )

    supported_output_formats: list[str] = dc_field(
        default_factory=lambda: [
            "wav",
            "mp3",
        ]
    )

    default_output_format: str = "wav"

    default_mp3_bitrate_kbps: int = 192

    temp_policy: dict = dc_field(
        default_factory=lambda: {
            "success": "cleanup",
            "pause": "keep",
            "cancel": "ask",
            "error": "keep",
            "resume": "reuse_existing",
        }
    )

    def to_dict(
        self,
    ):

        return asdict(
            self
        )

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        return dataclass_from_dict(
            cls,
            data,
        )


class GenerateStateMachine:

    transitions = {
        GENERATE_STATE_CREATED: {
            GENERATE_STATE_VALIDATED,
            GENERATE_STATE_BLOCKED,
            GENERATE_STATE_CANCELLED,
        },
        GENERATE_STATE_VALIDATED: {
            GENERATE_STATE_PLANNED,
            GENERATE_STATE_BLOCKED,
        },
        GENERATE_STATE_PLANNED: {
            GENERATE_STATE_READY,
            GENERATE_STATE_BLOCKED,
        },
        GENERATE_STATE_READY: {
            GENERATE_STATE_RUNNING,
            GENERATE_STATE_CANCELLED,
        },
        GENERATE_STATE_RUNNING: {
            GENERATE_STATE_PAUSED,
            GENERATE_STATE_COMPLETED,
            GENERATE_STATE_FAILED,
            GENERATE_STATE_CANCELLED,
        },
        GENERATE_STATE_PAUSED: {
            GENERATE_STATE_RUNNING,
            GENERATE_STATE_CANCELLED,
        },
        GENERATE_STATE_FAILED: {
            GENERATE_STATE_READY,
            GENERATE_STATE_CANCELLED,
        },
        GENERATE_STATE_BLOCKED: {
            GENERATE_STATE_VALIDATED,
            GENERATE_STATE_CANCELLED,
        },
    }

    def can_transition(
        self,
        current,
        target,
    ):

        if current == target:

            return True

        return target in self.transitions.get(
            current,
            set(),
        )

import hashlib
import json
import os
import secrets
import shutil
import unicodedata
import wave
from pathlib import Path

from models.generate_pipeline_foundation import (
    GENERATE_STATE_BLOCKED,
    GENERATE_STATE_READY,
    GENERATE_STATE_VALIDATED,
    GenerateAttemptRecord,
    GenerateArtifactRecord,
    GenerateIssue,
    GenerateManifestRecord,
    GenerateOutputSpec,
    GeneratePlanRecord,
    GenerateRegistryEntry,
    GenerateRequestRecord,
    GenerateReconstructionReport,
    GenerateSelectionSnapshot,
    GenerateSessionRecord,
    GenerateSettings,
    GenerateValidationReport,
    now_iso,
)
from services.generate_repository import GenerateRepository
from services.generate_text_structure_service import (
    GenerateTextStructureService,
)


class GenerateSessionService:

    windows_reserved_names = {
        "con",
        "prn",
        "aux",
        "nul",
        "com1",
        "com2",
        "com3",
        "com4",
        "com5",
        "com6",
        "com7",
        "com8",
        "com9",
        "lpt1",
        "lpt2",
        "lpt3",
        "lpt4",
        "lpt5",
        "lpt6",
        "lpt7",
        "lpt8",
        "lpt9",
    }

    def __init__(
        self,
        repository=None,
        text_structure=None,
        settings=None,
    ):

        self.repository = (
            repository
            or GenerateRepository()
        )

        self.text_structure = (
            text_structure
            or GenerateTextStructureService()
        )

        self.settings = (
            settings
            or GenerateSettings()
        )

    def stable_checksum(
        self,
        data,
    ):

        payload = json.dumps(
            data,
            ensure_ascii=False,
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
        )

        return hashlib.sha256(
            payload.encode(
                "utf-8"
            )
        ).hexdigest()

    def validate_request(
        self,
        data,
    ):

        data = data or {}

        issues = []

        warnings = []

        text = data.get(
            "text",
            "",
        )

        text_file = data.get(
            "text_file",
            "",
        )

        if not text and not text_file:

            issues.append(
                GenerateIssue(
                    code="generate_text_missing",
                    field="text",
                    message_vi="Thiếu văn bản hoặc file nguồn để lập kế hoạch Generate.",
                    suggestion="Nhập text hoặc chọn file TXT/DOCX.",
                )
            )

        if text_file:

            path = Path(
                text_file
            )

            if not path.exists():

                issues.append(
                    GenerateIssue(
                        code="generate_text_file_missing",
                        field="text_file",
                        message_vi="File văn bản nguồn không tồn tại.",
                        suggestion="Kiểm tra lại đường dẫn file TXT/DOCX.",
                    )
                )

            elif path.suffix.lower() not in {
                ".txt",
                ".docx",
            }:

                issues.append(
                    GenerateIssue(
                        code="generate_text_file_unsupported",
                        field="text_file",
                        message_vi="Generate foundation chỉ hỗ trợ TXT/DOCX ở bước này.",
                        suggestion="Dùng file TXT/DOCX hoặc dán nội dung trực tiếp.",
                    )
                )

        voice_id = data.get(
            "voice_id",
            "",
        ) or data.get(
            "selection",
            {},
        ).get(
            "voice_id",
            "",
        )

        if not voice_id:

            issues.append(
                GenerateIssue(
                    code="generate_voice_missing",
                    field="voice_id",
                    message_vi="Thiếu Voice ID cho Generate Request.",
                    suggestion="Chọn Voice trước khi lập kế hoạch.",
                )
            )

        output_format = (
            data.get(
                "output_format",
                "",
            )
            or data.get(
                "output",
                {},
            ).get(
                "output_format",
                self.settings.default_output_format,
            )
        ).lower()

        if output_format not in self.settings.supported_output_formats:

            issues.append(
                GenerateIssue(
                    code="generate_output_format_unsupported",
                    field="output_format",
                    message_vi="Định dạng output không được hỗ trợ.",
                    suggestion="Chọn WAV hoặc MP3.",
                )
            )

        if data.get(
            "start_inference",
            False,
        ):

            warnings.append(
                GenerateIssue(
                    code="generate_inference_not_in_scope",
                    message_vi="AVS-014.16 chỉ lập foundation, không chạy Generate thật.",
                    severity="warning",
                )
            )

        return GenerateValidationReport(
            ok=not issues,
            issues=issues,
            warnings=warnings,
        )

    def validate_output_spec(
        self,
        output,
    ):

        issues = []

        output_folder_raw = Path(
            output.output_folder
        )

        final_output_raw = Path(
            output.final_output_path
        )

        output_folder = output_folder_raw.resolve()

        final_output = final_output_raw.resolve()

        normalized_name = unicodedata.normalize(
            "NFC",
            final_output.name,
        )

        if normalized_name != final_output.name:

            issues.append(
                GenerateIssue(
                    code="generate_output_unicode_not_normalized",
                    field="output.output_name",
                    message_vi="Tên output chưa được chuẩn hóa Unicode NFC.",
                    suggestion="Đổi tên output rồi thử lại.",
                )
            )

        stem = final_output.stem.rstrip(
            " ."
        ).lower()

        if stem in self.windows_reserved_names:

            issues.append(
                GenerateIssue(
                    code="generate_output_windows_reserved_name",
                    field="output.output_name",
                    message_vi="Tên output trùng tên đặc biệt của Windows.",
                    suggestion="Đổi tên output khác CON/PRN/AUX/NUL/COM/LPT.",
                )
            )

        if len(
            str(
                final_output
            )
        ) > 240:

            issues.append(
                GenerateIssue(
                    code="generate_output_path_too_long",
                    field="output.final_output_path",
                    message_vi="Đường dẫn output quá dài.",
                    suggestion="Chọn thư mục hoặc tên file ngắn hơn.",
                )
            )

        try:

            final_output.relative_to(
                output_folder
            )

        except Exception:

            issues.append(
                GenerateIssue(
                    code="generate_output_path_escape",
                    field="output.final_output_path",
                    message_vi="Đường dẫn output vượt ra ngoài output folder.",
                    suggestion="Chọn output name/folder hợp lệ.",
                )
            )

        if final_output.exists() and not output.overwrite:

            issues.append(
                GenerateIssue(
                    code="generate_output_collision",
                    field="output.final_output_path",
                    message_vi="File output đã tồn tại và overwrite đang tắt.",
                    suggestion="Đổi tên output hoặc bật overwrite.",
                )
            )

        if output_folder.exists():

            for child in output_folder.iterdir():

                if (
                    child.name.lower()
                    == final_output.name.lower()
                    and child.name != final_output.name
                    and not output.overwrite
                ):

                    issues.append(
                        GenerateIssue(
                            code="generate_output_case_collision",
                            field="output.final_output_path",
                            message_vi="Tên output bị trùng khi so sánh không phân biệt hoa/thường.",
                            suggestion="Đổi tên output để tránh collision trên Windows.",
                        )
                    )

                    break

        return issues

    def create_session(
        self,
        data,
    ):

        self.repository.ensure_root()

        validation = self.validate_request(
            data
        )

        session = GenerateSessionRecord(
            project_id=data.get(
                "project_id",
                "",
            ),
            voice_id=data.get(
                "voice_id",
                "",
            )
            or data.get(
                "selection",
                {},
            ).get(
                "voice_id",
                "",
            ),
            status=GENERATE_STATE_VALIDATED
            if validation.ok
            else GENERATE_STATE_BLOCKED,
        )

        session_dir = self.repository.session_dir(
            session.session_id
        )

        source_text = ""

        source_type = "pasted_text"

        original_path = ""

        if validation.ok:

            source_text, source_type, original_path = (
                self.text_structure.read_source(
                    text=data.get(
                        "text",
                        "",
                    ),
                    text_file=data.get(
                        "text_file",
                        "",
                    ),
                )
            )

        source_dir = session_dir / "source"

        source_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        snapshot_file = source_dir / "source_snapshot.txt"

        snapshot_file.write_text(
            source_text,
            encoding="utf-8",
        )

        source = self.text_structure.make_snapshot(
            source_text,
            source_type,
            original_path,
            snapshot_file,
            language=data.get(
                "language",
                self.settings.default_language,
            ),
        )

        selection = self.build_selection(
            data
        )

        output = self.build_output(
            data,
            session.session_id,
        )

        for issue in self.validate_output_spec(
            output
        ):

            validation.issues.append(
                issue
            )

        validation.ok = not validation.issues

        request = GenerateRequestRecord(
            project_id=session.project_id,
            voice_id=session.voice_id,
            source=source,
            selection=selection,
            output=output,
            validation=validation,
            status=session.status,
        )

        request.request_checksum_sha256 = self.stable_checksum(
            {
                "project_id": request.project_id,
                "voice_id": request.voice_id,
                "source": request.source.to_dict(),
                "selection": request.selection.to_dict(),
                "output": request.output.to_dict(),
                "revision": request.revision,
            }
        )

        if validation.ok:

            request.materialized_at = now_iso()

            request.status = GENERATE_STATE_VALIDATED

            session.status = GENERATE_STATE_VALIDATED

            session.health = "ready"

            session.allowed_actions = {
                "plan": False,
                "resume_inspect": True,
                "resume_execute": False,
                "retry_inspect": True,
                "retry_execute": False,
                "generate_execute": False,
            }

        else:

            request.status = GENERATE_STATE_BLOCKED

            session.status = GENERATE_STATE_BLOCKED

            session.health = "blocked"

            session.allowed_actions = {
                "plan": False,
                "resume_inspect": False,
                "resume_execute": False,
                "retry_inspect": False,
                "retry_execute": False,
                "generate_execute": False,
            }

        session.request_id = request.request_id

        self.repository.save_session(
            session
        )

        self.repository.save_request(
            session.session_id,
            request,
        )

        if validation.ok:

            plan, document = self.build_plan(
                session,
                source_text,
            )

            normalized_text = Path(
                document.normalized_text_path
            ).read_text(
                encoding="utf-8"
            )

            reconstruction = (
                self.text_structure.verify_reconstruction(
                    source_text,
                    normalized_text,
                    plan.units,
                )
            )

            plan.reconstruction_report = reconstruction

            if not reconstruction.ok:

                validation.issues.append(
                    GenerateIssue(
                        code="generate_reconstruction_failed",
                        field="plan.units",
                        message_vi="Không thể reconstruct text chính xác từ Generate Plan.",
                        suggestion="Kiểm tra splitter/normalizer trước khi freeze plan.",
                        details=reconstruction.to_dict(),
                    )
                )

                validation.ok = False

                request.validation = validation

                request.status = GENERATE_STATE_BLOCKED

                session.status = GENERATE_STATE_BLOCKED

                session.health = "blocked"

                plan.frozen = False

            self.repository.atomic_write_json(
                session_dir / "document.json",
                document.to_dict(),
            )

            normalized_path = (
                session_dir
                / "source"
                / "normalized.txt"
            )

            normalized_path.write_text(
                Path(
                    document.normalized_text_path
                ).read_text(
                    encoding="utf-8"
                )
                if document.normalized_text_path
                else "",
                encoding="utf-8",
            )

            if validation.ok:

                manifest = self.build_manifest(
                    session,
                    request,
                    plan,
                    self.repository.session_dir(
                        session.session_id
                    )
                    / "plan.json",
                )

                self.repository.save_plan(
                    plan
                )

                self.repository.save_artifacts(
                    session.session_id,
                    manifest.artifact_records,
                )

                self.repository.save_manifest(
                    manifest
                )

                session.status = GENERATE_STATE_READY

                session.progress_percent = 0.0

                session.updated_at = now_iso()

                self.repository.save_session(
                    session
                )

            else:

                self.repository.save_plan(
                    plan
                )

                self.repository.save_request(
                    session.session_id,
                    request,
                )

                self.repository.save_session(
                    session
                )

        self.repository.upsert_registry(
            GenerateRegistryEntry(
                session_id=session.session_id,
                request_id=request.request_id,
                project_id=session.project_id,
                voice_id=session.voice_id,
                status=session.status,
                manifest_path=str(
                    session_dir / "manifest.json"
                ),
                output_path=output.final_output_path,
            )
        )

        return {
            "session": session.to_dict(),
            "request": request.to_dict(),
            "validation": validation.to_dict(),
            "plan": self.repository.load_plan(
                session.session_id
            ).to_dict()
            if self.repository.load_plan(
                session.session_id
            )
            else None,
            "manifest": self.repository.load_manifest(
                session.session_id
            ).to_dict()
            if validation.ok
            else None,
        }

    def build_selection(
        self,
        data,
    ):

        raw = data.get(
            "selection",
            {},
        )

        return GenerateSelectionSnapshot(
            voice_id=data.get(
                "voice_id",
                "",
            )
            or raw.get(
                "voice_id",
                "",
            ),
            variant_id=data.get(
                "variant_id",
                "",
            )
            or raw.get(
                "variant_id",
                raw.get(
                    "selected_variant_id",
                    "default",
                ),
            ),
            style_id=data.get(
                "style_id",
                "",
            )
            or raw.get(
                "style_id",
                raw.get(
                    "default_style_id",
                    "",
                ),
            ),
            mode=data.get(
                "mode",
                raw.get(
                    "mode",
                    "standard",
                ),
            ),
            speed=float(
                data.get(
                    "speed",
                    raw.get(
                        "speed",
                        1.0,
                    ),
                )
                or 1.0
            ),
            language=data.get(
                "language",
                raw.get(
                    "language",
                    self.settings.default_language,
                ),
            ),
            allowed_variant_ids=list(
                raw.get(
                    "allowed_variant_ids",
                    [],
                )
            ),
            allowed_style_ids=list(
                raw.get(
                    "allowed_style_ids",
                    [],
                )
            ),
            allow_all_variants=bool(
                raw.get(
                    "allow_all_variants",
                    False,
                )
            ),
            allow_all_styles=bool(
                raw.get(
                    "allow_all_styles",
                    False,
                )
            ),
        )

    def build_output(
        self,
        data,
        session_id,
    ):

        raw = data.get(
            "output",
            {},
        )

        output_folder = (
            data.get(
                "output_folder",
                "",
            )
            or raw.get(
                "output_folder",
                "",
            )
            or str(
                self.repository.session_dir(
                    session_id
                )
                / "output"
            )
        )

        output_name = (
            data.get(
                "output_name",
                "",
            )
            or raw.get(
                "output_name",
                ""
            )
            or session_id
        )

        output_format = (
            data.get(
                "output_format",
                "",
            )
            or raw.get(
                "output_format",
                self.settings.default_output_format,
            )
        ).lower()

        final_output = Path(
            output_folder
        ) / f"{output_name}.{output_format}"

        report_path = Path(
            output_folder
        ) / f"{output_name}.generate_report.json"

        temp_output = (
            self.repository.session_dir(
                session_id
            )
            / "temp"
            / f"{output_name}.{output_format}"
        )

        return GenerateOutputSpec(
            output_folder=str(
                output_folder
            ),
            output_name=output_name,
            output_format=output_format,
            mp3_bitrate_kbps=int(
                data.get(
                    "mp3_bitrate_kbps",
                    raw.get(
                        "mp3_bitrate_kbps",
                        self.settings.default_mp3_bitrate_kbps,
                    ),
                )
            ),
            overwrite=bool(
                data.get(
                    "overwrite",
                    raw.get(
                        "overwrite",
                        False,
                    ),
                )
            ),
            final_output_path=str(
                final_output
            ),
            report_path=str(
                report_path
            ),
            temp_output_path=str(
                temp_output
            ),
        )

    def build_plan(
        self,
        session,
        text,
    ):

        document, chapters, units, normalized = (
            self.text_structure.build_structure(
                text,
                session.session_id,
                max_unit_characters=self.settings.max_unit_characters,
                language=self.settings.default_language,
            )
        )

        normalized_path = (
            self.repository.session_dir(
                session.session_id
            )
            / "source"
            / "normalized.txt"
        )

        normalized_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        normalized_path.write_text(
            normalized,
            encoding="utf-8",
        )

        document.normalized_text_path = str(
            normalized_path
        )

        plan = GeneratePlanRecord(
            session_id=session.session_id,
            document_id=document.document_id,
            chapters=chapters,
            units=units,
            attempts=[],
            settings_snapshot=self.settings.to_dict(),
        )

        return plan, document

    def build_manifest(
        self,
        session,
        request,
        plan,
        plan_path,
    ):

        plan.selection_snapshot = request.selection.to_dict()

        plan.output_snapshot = request.output.to_dict()

        plan.frozen = True

        plan.frozen_at = now_iso()

        plan.immutable_checksum_sha256 = self.stable_checksum(
            plan.immutable_payload()
        )

        plan.plan_checksum_sha256 = self.stable_checksum(
            plan.to_dict()
        )

        artifacts = self.build_planned_artifacts(
            session,
            plan,
        )

        return GenerateManifestRecord(
            session_id=session.session_id,
            request_id=request.request_id,
            plan_id=plan.plan_id,
            status=GENERATE_STATE_READY,
            source=request.source.to_dict(),
            output=request.output.to_dict(),
            artifacts=[
                {
                    "kind": "request",
                    "path": str(
                        self.repository.session_dir(
                            session.session_id
                        )
                        / "request.json"
                    ),
                },
                {
                    "kind": "plan",
                    "path": str(
                        plan_path
                    ),
                },
                {
                    "kind": "source_snapshot",
                    "path": request.source.snapshot_path,
                },
            ],
            artifact_records=artifacts,
            units_total=len(
                plan.units
            ),
        )

    def build_planned_artifacts(
        self,
        session,
        plan,
    ):

        records = []

        for unit in plan.units:

            attempt_id = unit.attempt_ids[
                0
            ] if unit.attempt_ids else ""

            filename = f"{unit.order:06d}_{unit.unit_id}.wav"

            temp_path = (
                self.repository.session_dir(
                    session.session_id
                )
                / "temp"
                / "units"
                / filename
            )

            final_path = (
                self.repository.session_dir(
                    session.session_id
                )
                / "artifacts"
                / filename
            )

            records.append(
                GenerateArtifactRecord(
                    project_id=session.project_id,
                    session_id=session.session_id,
                    plan_id=plan.plan_id,
                    plan_checksum_sha256=plan.plan_checksum_sha256,
                    unit_id=unit.unit_id,
                    attempt_id=attempt_id,
                    output_format="wav",
                    input_fingerprint=self.stable_checksum(
                        {
                            "unit_id": unit.unit_id,
                            "text": unit.text,
                            "selection": plan.selection_snapshot,
                        }
                    ),
                    planned_path=str(
                        final_path
                    ),
                    temp_path=str(
                        temp_path
                    ),
                    final_path=str(
                        final_path
                    ),
                    status="planned",
                )
            )

        return records

    def plan_integrity(
        self,
        session_id,
    ):

        plan = self.repository.load_plan(
            session_id
        )

        if not plan:

            return {
                "ok": False,
                "code": "generate_plan_missing",
            }

        immutable = self.stable_checksum(
            plan.immutable_payload()
        )

        if (
            plan.immutable_checksum_sha256
            and immutable != plan.immutable_checksum_sha256
        ):

            return {
                "ok": False,
                "code": "generate_plan_corrupted",
                "expected": plan.immutable_checksum_sha256,
                "actual": immutable,
            }

        return {
            "ok": True,
            "code": "generate_plan_ok",
            "checksum": plan.immutable_checksum_sha256,
        }

    def validate_wav_artifact(
        self,
        artifact,
    ):

        artifact = GenerateArtifactRecord.from_dict(
            artifact
        )

        path = Path(
            artifact.final_path
            or artifact.temp_path
        )

        artifact.validation_errors = []

        if not path.exists():

            artifact.validation_status = "missing"

            artifact.validation_errors.append(
                "artifact_missing"
            )

            return artifact

        try:

            with wave.open(
                str(
                    path
                ),
                "rb",
            ) as wav:

                artifact.channels = wav.getnchannels()

                artifact.sample_rate = wav.getframerate()

                frames = wav.getnframes()

                artifact.duration_seconds = (
                    frames / artifact.sample_rate
                    if artifact.sample_rate
                    else 0.0
                )

        except Exception:

            artifact.validation_status = "invalid"

            artifact.validation_errors.append(
                "wav_read_failed"
            )

            return artifact

        if artifact.channels != 1:

            artifact.validation_errors.append(
                "wav_not_mono"
            )

        if artifact.sample_rate <= 0:

            artifact.validation_errors.append(
                "wav_sample_rate_invalid"
            )

        artifact.validation_status = (
            "valid"
            if not artifact.validation_errors
            else "invalid"
        )

        return artifact

    def list_artifacts(
        self,
        session_id,
    ):

        return {
            "items": [
                item.to_dict()
                for item in self.repository.load_artifacts(
                    session_id
                )
            ]
        }

    def get_artifact(
        self,
        session_id,
        artifact_id,
    ):

        for artifact in self.repository.load_artifacts(
            session_id
        ):

            if artifact.artifact_id == artifact_id:

                return artifact

        return None

    def reservation_file(
        self,
        artifact,
    ):

        return (
            self.repository.session_dir(
                artifact.session_id
            )
            / "reservations"
            / f"{artifact.artifact_id}.json"
        )

    def reserve_artifact(
        self,
        artifact,
    ):

        artifact = GenerateArtifactRecord.from_dict(
            artifact
        )

        issues = self.validate_output_spec(
            GenerateOutputSpec(
                output_folder=str(
                    Path(
                        artifact.final_path
                    ).parent
                ),
                output_name=Path(
                    artifact.final_path
                ).stem,
                output_format=artifact.output_format,
                final_output_path=artifact.final_path,
            )
        )

        if issues:

            artifact.status = "blocked"

            artifact.validation_status = "invalid"

            artifact.validation_errors = [
                issue.code
                for issue in issues
            ]

            self.repository.upsert_artifact(
                artifact
            )

            return {
                "ok": False,
                "artifact": artifact.to_dict(),
                "issues": [
                    issue.to_dict()
                    for issue in issues
                ],
            }

        reservation_id = (
            artifact.reservation_id
            or f"gres_{secrets.token_hex(8)}"
        )

        reservation_file = self.reservation_file(
            artifact
        )

        reservation_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = {
            "reservation_id": reservation_id,
            "artifact_id": artifact.artifact_id,
            "session_id": artifact.session_id,
            "final_path": artifact.final_path,
            "created_at": now_iso(),
        }

        try:

            with open(
                reservation_file,
                "x",
                encoding="utf-8",
            ) as handle:

                handle.write(
                    json.dumps(
                        payload,
                        ensure_ascii=False,
                        indent=2,
                    )
                )

        except FileExistsError:

            data = json.loads(
                reservation_file.read_text(
                    encoding="utf-8"
                )
            )

            if data.get(
                "reservation_id"
            ) != artifact.reservation_id or not artifact.reservation_id:

                return {
                    "ok": False,
                    "code": "generate_artifact_reserved_by_other_writer",
                    "artifact": artifact.to_dict(),
                }

        artifact.reservation_id = reservation_id

        artifact.reserved_at = now_iso()

        artifact.status = "reserved"

        artifact.updated_at = now_iso()

        self.repository.upsert_artifact(
            artifact
        )

        return {
            "ok": True,
            "reservation_id": reservation_id,
            "artifact": artifact.to_dict(),
        }

    def promote_artifact(
        self,
        artifact,
        reservation_id,
    ):

        artifact = GenerateArtifactRecord.from_dict(
            artifact
        )

        if artifact.reservation_id != reservation_id:

            return {
                "ok": False,
                "code": "generate_artifact_reservation_mismatch",
                "artifact": artifact.to_dict(),
            }

        temp_path = Path(
            artifact.temp_path
        )

        final_path = Path(
            artifact.final_path
        )

        if not temp_path.exists():

            artifact.status = "failed"

            artifact.validation_status = "missing"

            artifact.validation_errors = [
                "temp_output_missing",
            ]

            self.repository.upsert_artifact(
                artifact
            )

            return {
                "ok": False,
                "code": "temp_output_missing",
                "artifact": artifact.to_dict(),
            }

        temp_validation = self.validate_wav_artifact(
            {
                **artifact.to_dict(),
                "final_path": str(
                    temp_path
                ),
            }
        )

        if temp_validation.validation_status != "valid":

            artifact.status = "invalid"

            artifact.validation_status = (
                temp_validation.validation_status
            )

            artifact.validation_errors = (
                temp_validation.validation_errors
            )

            self.repository.upsert_artifact(
                artifact
            )

            return {
                "ok": False,
                "code": "artifact_validation_failed",
                "artifact": artifact.to_dict(),
            }

        if final_path.exists():

            artifact.status = "blocked"

            artifact.validation_status = "invalid"

            artifact.validation_errors = [
                "final_collision_on_promote",
            ]

            self.repository.upsert_artifact(
                artifact
            )

            return {
                "ok": False,
                "code": "final_collision_on_promote",
                "artifact": artifact.to_dict(),
            }

        final_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.move(
            str(
                temp_path
            ),
            str(
                final_path
            ),
        )

        artifact = self.validate_wav_artifact(
            artifact
        )

        if artifact.validation_status != "valid":

            artifact.status = "invalid"

            self.repository.upsert_artifact(
                artifact
            )

            return {
                "ok": False,
                "code": "artifact_validation_failed",
                "artifact": artifact.to_dict(),
            }

        artifact.status = "valid"

        artifact.updated_at = now_iso()

        self.repository.upsert_artifact(
            artifact
        )

        return {
            "ok": True,
            "artifact": artifact.to_dict(),
        }

    def create_attempt(
        self,
        session_id,
        unit_id,
        job_id="",
        retry_limit=3,
    ):

        plan = self.repository.load_plan(
            session_id
        )

        if not plan:

            return {
                "ok": False,
                "code": "generate_plan_missing",
            }

        unit = None

        for item in plan.units:

            if item.unit_id == unit_id:

                unit = item

                break

        if unit is None:

            return {
                "ok": False,
                "code": "generate_unit_not_found",
            }

        if unit.status == "completed":

            return {
                "ok": False,
                "code": "generate_unit_already_valid",
            }

        active = [
            attempt
            for attempt in plan.attempts
            if attempt.unit_id == unit_id
            and attempt.status
            in {
                "pending",
                "running",
                "reserved",
            }
        ]

        if active:

            return {
                "ok": False,
                "code": "generate_unit_active_attempt_exists",
                "attempt": active[
                    0
                ].to_dict(),
            }

        attempts = [
            attempt
            for attempt in plan.attempts
            if attempt.unit_id == unit_id
        ]

        if len(
            attempts
        ) >= retry_limit:

            return {
                "ok": False,
                "code": "generate_retry_limit_reached",
            }

        attempt = GenerateAttemptRecord(
            unit_id=unit_id,
            attempt_index=len(
                attempts
            )
            + 1,
            status="pending",
            job_id=job_id,
        )

        plan.attempts.append(
            attempt
        )

        unit.attempt_ids.append(
            attempt.attempt_id
        )

        unit.status = "running"

        self.repository.save_plan(
            plan
        )

        return {
            "ok": True,
            "attempt": attempt.to_dict(),
        }

    def complete_attempt_with_artifact(
        self,
        session_id,
        unit_id,
        attempt_id,
        artifact,
    ):

        artifact = GenerateArtifactRecord.from_dict(
            artifact
        )

        if artifact.status != "valid" or artifact.validation_status != "valid":

            return {
                "ok": False,
                "code": "artifact_not_valid",
            }

        plan = self.repository.load_plan(
            session_id
        )

        if not plan:

            return {
                "ok": False,
                "code": "generate_plan_missing",
            }

        for attempt in plan.attempts:

            if attempt.attempt_id == attempt_id:

                attempt.status = "completed"

                attempt.artifact_id = artifact.artifact_id

                attempt.artifact_path = artifact.final_path

                attempt.finished_at = now_iso()

        for unit in plan.units:

            if unit.unit_id == unit_id:

                unit.status = "completed"

        self.repository.save_plan(
            plan
        )

        return {
            "ok": True,
        }

    def execute_unit_with_provider(
        self,
        session_id,
        unit_id,
        provider=None,
    ):

        if provider is None:

            return {
                "ok": False,
                "code": "generate_execution_unavailable",
                "status": "UNAVAILABLE",
            }

        attempt_result = self.create_attempt(
            session_id,
            unit_id,
        )

        if not attempt_result.get(
            "ok"
        ):

            return attempt_result

        attempt = GenerateAttemptRecord.from_dict(
            attempt_result[
                "attempt"
            ]
        )

        artifacts = self.repository.load_artifacts(
            session_id
        )

        artifact = None

        for item in artifacts:

            if item.unit_id == unit_id and item.status in {
                "planned",
                "reserved",
                "failed",
                "invalid",
            }:

                artifact = item

                break

        if artifact is None:

            return {
                "ok": False,
                "code": "generate_artifact_missing",
            }

        artifact.attempt_id = attempt.attempt_id

        reserve = self.reserve_artifact(
            artifact
        )

        if not reserve.get(
            "ok"
        ):

            return reserve

        artifact = GenerateArtifactRecord.from_dict(
            reserve[
                "artifact"
            ]
        )

        Path(
            artifact.temp_path
        ).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        provider(
            artifact,
            Path(
                artifact.temp_path
            ),
        )

        promoted = self.promote_artifact(
            artifact,
            artifact.reservation_id,
        )

        if not promoted.get(
            "ok"
        ):

            return promoted

        self.complete_attempt_with_artifact(
            session_id,
            unit_id,
            attempt.attempt_id,
            promoted[
                "artifact"
            ],
        )

        return promoted

    def list_sessions(
        self,
        project_id="",
    ):

        return {
            "items": [
                item.to_dict()
                for item in self.repository.list_sessions(
                    project_id=project_id
                )
            ]
        }

    def get_session(
        self,
        session_id,
    ):

        session = self.repository.load_session(
            session_id
        )

        if not session:

            return None

        return {
            "session": session.to_dict(),
            "request": (
                self.repository.load_request(
                    session_id
                ).to_dict()
            ),
            "manifest": (
                self.repository.load_manifest(
                    session_id
                ).to_dict()
                if self.repository.load_manifest(
                    session_id
                )
                else None
            ),
        }

    def get_plan(
        self,
        session_id,
    ):

        plan = self.repository.load_plan(
            session_id
        )

        return plan.to_dict() if plan else None

    def get_manifest(
        self,
        session_id,
    ):

        manifest = self.repository.load_manifest(
            session_id
        )

        return manifest.to_dict() if manifest else None

    def inspect_resume(
        self,
        session_id,
    ):

        plan = self.repository.load_plan(
            session_id
        )

        session = self.repository.load_session(
            session_id
        )

        if not plan or not session:

            return None

        completed = [
            unit.unit_id
            for unit in plan.units
            if unit.status == "completed"
        ]

        failed = [
            unit.unit_id
            for unit in plan.units
            if unit.status == "failed"
        ]

        pending = [
            unit.unit_id
            for unit in plan.units
            if unit.status
            not in {
                "completed",
                "failed",
            }
        ]

        return {
            "session_id": session_id,
            "status": session.status,
            "fingerprint": self.stable_checksum(
                {
                    "session_id": session_id,
                    "plan_checksum": plan.plan_checksum_sha256,
                    "completed": completed,
                    "failed": failed,
                    "pending": pending,
                }
            ),
            "can_resume": bool(
                pending or failed
            ),
            "completed_units": completed,
            "failed_units": failed,
            "pending_units": pending,
            "message_vi": "Có thể resume từ state hiện tại; foundation không generate lại unit đã completed.",
        }

    def execute_resume(
        self,
        session_id,
        expected_fingerprint="",
        provider=None,
    ):

        inspection = self.inspect_resume(
            session_id
        )

        if not inspection:

            return {
                "ok": False,
                "code": "generate_session_not_found",
            }

        if (
            expected_fingerprint
            and expected_fingerprint
            != inspection.get(
                "fingerprint",
                "",
            )
        ):

            return {
                "ok": False,
                "code": "generate_stale_inspection",
            }

        if provider is None:

            return {
                "ok": False,
                "code": "generate_execution_unavailable",
                "status": "UNAVAILABLE",
            }

        results = []

        for unit_id in inspection.get(
            "pending_units",
            [],
        ) + inspection.get(
            "failed_units",
            [],
        ):

            results.append(
                self.execute_unit_with_provider(
                    session_id,
                    unit_id,
                    provider=provider,
                )
            )

        return {
            "ok": all(
                item.get(
                    "ok",
                    False,
                )
                for item in results
            ),
            "results": results,
        }

    def inspect_retry(
        self,
        session_id,
        unit_id,
    ):

        plan = self.repository.load_plan(
            session_id
        )

        if not plan:

            return None

        for unit in plan.units:

            if unit.unit_id != unit_id:

                continue

            return {
                "session_id": session_id,
                "unit_id": unit_id,
                "status": unit.status,
                "fingerprint": self.stable_checksum(
                    {
                        "session_id": session_id,
                        "unit_id": unit_id,
                        "status": unit.status,
                        "attempt_ids": unit.attempt_ids,
                        "plan_checksum": plan.plan_checksum_sha256,
                    }
                ),
                "can_retry": unit.status
                in {
                    "failed",
                    "error",
                },
                "message_vi": "Retry chỉ được phép cho unit lỗi; AVS-014.16 chưa chạy Generate thật.",
            }

        return None

    def retry_unit(
        self,
        session_id,
        unit_id,
        expected_fingerprint="",
        provider=None,
    ):

        inspection = self.inspect_retry(
            session_id,
            unit_id,
        )

        if not inspection:

            return {
                "ok": False,
                "code": "generate_unit_not_found",
            }

        if (
            expected_fingerprint
            and expected_fingerprint
            != inspection.get(
                "fingerprint",
                "",
            )
        ):

            return {
                "ok": False,
                "code": "generate_stale_inspection",
            }

        if not inspection.get(
            "can_retry",
            False,
        ):

            return {
                "ok": False,
                "code": "generate_unit_not_retryable",
            }

        if provider is None:

            return {
                "ok": False,
                "code": "generate_execution_unavailable",
                "status": "UNAVAILABLE",
            }

        return self.execute_unit_with_provider(
            session_id,
            unit_id,
            provider=provider,
        )

    def retry_chapter(
        self,
        session_id,
        chapter_id,
        provider=None,
    ):

        plan = self.repository.load_plan(
            session_id
        )

        if not plan:

            return {
                "ok": False,
                "code": "generate_plan_missing",
            }

        chapter = None

        for item in plan.chapters:

            if item.chapter_id == chapter_id:

                chapter = item

                break

        if chapter is None:

            return {
                "ok": False,
                "code": "generate_chapter_not_found",
            }

        results = []

        for unit_id in chapter.unit_ids:

            retry = self.inspect_retry(
                session_id,
                unit_id,
            )

            if retry and retry.get(
                "can_retry",
                False,
            ):

                results.append(
                    self.retry_unit(
                        session_id,
                        unit_id,
                        expected_fingerprint=retry.get(
                            "fingerprint",
                            "",
                        ),
                        provider=provider,
                    )
                )

        return {
            "ok": all(
                item.get(
                    "ok",
                    False,
                )
                for item in results
            )
            if results
            else False,
            "results": results,
        }

    def inspect_recovery(
        self,
    ):

        self.repository.ensure_root()

        sessions = []

        for path in self.repository.sessions_root.glob(
            "*"
        ):

            if not path.is_dir():

                continue

            session_id = path.name

            issues = []

            if not (
                path / "manifest.json"
            ).exists():

                issues.append(
                    "manifest_missing"
                )

            if not (
                path / "plan.json"
            ).exists():

                issues.append(
                    "plan_missing"
                )

            integrity = self.plan_integrity(
                session_id
            )

            if not integrity.get(
                "ok",
                False,
            ):

                issues.append(
                    integrity.get(
                        "code",
                        "plan_integrity_failed",
                    )
                )

            temp_files = [
                str(
                    item
                )
                for item in (
                    path / "temp"
                ).glob(
                    "**/*"
                )
                if item.is_file()
            ] if (
                path / "temp"
            ).exists() else []

            if temp_files:

                issues.append(
                    "temp_output_present"
                )

            sessions.append(
                {
                    "session_id": session_id,
                    "issues": issues,
                    "safe_actions": [
                        "rebuild_manifest"
                    ]
                    if "manifest_missing" in issues
                    else [],
                    "manual_actions": [
                        "review_temp_or_orphan"
                    ]
                    if temp_files
                    else [],
                    "temp_files": temp_files,
                }
            )

        return {
            "ok": True,
            "engine_loaded": False,
            "sessions": sessions,
        }

    def rebuild_manifest(
        self,
        session_id,
    ):

        session = self.repository.load_session(
            session_id
        )

        request = self.repository.load_request(
            session_id
        )

        plan = self.repository.load_plan(
            session_id
        )

        if not session or not request or not plan:

            return {
                "ok": False,
                "code": "generate_rebuild_missing_state",
            }

        manifest = self.build_manifest(
            session,
            request,
            plan,
            self.repository.session_dir(
                session_id
            )
            / "plan.json",
        )

        self.repository.save_manifest(
            manifest
        )

        self.repository.save_artifacts(
            session_id,
            manifest.artifact_records,
        )

        return {
            "ok": True,
            "manifest": manifest.to_dict(),
        }

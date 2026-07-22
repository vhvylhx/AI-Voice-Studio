import json
import time
from pathlib import Path
from uuid import uuid4

from models.generate_config import (
    GENERATE_MODE_STANDARD,
    TEMP_STATUS_ERROR,
    TEMP_STATUS_SUCCESS,
    GenerateResult,
)
from services.app_events import AppEvents
from services.audio_merge_service import AudioMergeService
from services.context_analysis_service import ContextAnalysisService
from services.generate_planning_service import GeneratePlanningService
from services.temp_workspace_service import TempWorkspaceService
from services.engine_language_router import EngineLanguageRouter


class GeneratePipelineService:

    def __init__(
        self,
        engine_manager=None,
        temp_service=None,
        planning_service=None,
        context_service=None,
        merge_service=None,
    ):

        self.engine_manager = engine_manager

        self.temp_service = (
            temp_service
            or TempWorkspaceService()
        )

        self.planning = (
            planning_service
            or GeneratePlanningService()
        )

        self.context = (
            context_service
            or ContextAnalysisService()
        )

        self.merge = (
            merge_service
            or AudioMergeService()
        )

        self.engine_router = EngineLanguageRouter()

        self.progress_events = []

    def run(
        self,
        request,
        voice,
        project=None,
        adapter=None,
    ):

        started = time.time()

        resume = bool(
            request.job_id
        )

        job_id = (
            request.job_id
            or uuid4().hex
        )

        request.job_id = job_id

        workspace = self.temp_service.create(
            kind="generate",
            job_id=job_id,
            resume=resume,
        )

        result = GenerateResult(
            ok=False,
            mode=request.selection.mode,
            temp_workspace=workspace,
        )

        try:

            validation_errors = self.validate_request(
                request,
                voice,
            )

            if validation_errors:

                result.errors = validation_errors

                result.report = self.build_report(
                    request=request,
                    voice=voice,
                    status="failed",
                    errors=validation_errors,
                    started=started,
                )

                self.write_report(
                    result,
                    workspace,
                )

                return result

            self.emit_progress(
                "planning",
                0,
                1,
                "Đang lập kế hoạch Generate",
            )

            plan = self.create_plan(
                request,
                voice,
                workspace,
            )

            result.variant_timeline = (
                plan.variant_timeline
            )

            result.style_timeline = (
                plan.style_timeline
            )

            chunk_files = self.generate_chunks(
                request=request,
                voice=voice,
                plan=plan,
                adapter=adapter,
            )

            output_file = self.output_path(
                request
            )

            self.emit_progress(
                "merge",
                len(plan.chunks),
                len(plan.chunks),
                "Đang ghép audio",
            )

            self.merge.merge(
                chunk_files=chunk_files,
                output_file=output_file,
                work_dir=Path(
                    workspace.work_dir
                )
                / "merge",
                profile=request.audio_profile,
            )

            result.ok = True

            result.output_file = str(
                output_file
            )

            result.report = self.build_report(
                request=request,
                voice=voice,
                status="success",
                plan=plan,
                output_path=output_file,
                started=started,
            )

            self.write_report(
                result,
                workspace,
            )

            self.temp_service.finish(
                workspace,
                TEMP_STATUS_SUCCESS,
            )

            self.emit_progress(
                "done",
                len(plan.chunks),
                len(plan.chunks),
                "Generate hoàn tất",
                level="success",
            )

            return result

        except Exception as exc:

            result.errors = [
                str(exc)
            ]

            result.report = self.build_report(
                request=request,
                voice=voice,
                status="failed",
                errors=result.errors,
                started=started,
            )

            self.write_report(
                result,
                workspace,
            )

            self.temp_service.finish(
                workspace,
                TEMP_STATUS_ERROR,
            )

            self.emit_progress(
                "error",
                0,
                0,
                str(exc),
                level="error",
            )

            return result

    def validate_request(
        self,
        request,
        voice,
    ):

        errors = []

        if voice is None:

            errors.append(
                "voice_missing"
            )

            return errors

        if not getattr(
            voice,
            "id",
            "",
        ):

            errors.append(
                "voice_id_invalid"
            )

        config = voice.config

        routed_engine = self.engine_router.resolve_engine(
            getattr(
                config,
                "language",
                "",
            ),
            getattr(
                config,
                "engine",
                "",
            ),
        )

        if self.engine_router.validate_binding(
            getattr(
                config,
                "language",
                "",
            ),
            routed_engine,
        ):

            errors.append(
                "vietnamese_requires_vieneu_tts"
            )

        if (
            routed_engine == "vieneu"
            and self.engine_manager is not None
            and hasattr(
                self.engine_manager,
                "get",
            )
        ):

            engine = self.engine_manager.get(
                "vieneu"
            )

            if engine is None or not engine.is_available():

                errors.append(
                    "vieneu_tts_unavailable"
                )

        if (
            not str(
                config.gpt_model
            ).strip()
            or not str(
                config.sovits_model
            ).strip()
            or not Path(
                str(config.gpt_model)
            ).exists()
            or not Path(
                str(config.sovits_model)
            ).exists()
        ):

            errors.append(
                "voice_model_missing"
            )

        if (
            not str(
                config.reference_audio
            ).strip()
            or not Path(
                str(config.reference_audio)
            ).exists()
        ):

            errors.append(
                "reference_audio_missing"
            )

        if not str(
            config.reference_text
        ).strip():

            errors.append(
                "reference_text_missing"
            )

        text = self.request_text(
            request
        )

        if not text.strip():

            errors.append(
                "text_empty"
            )

        if not str(
            request.selection.output_folder
        ).strip():

            errors.append(
                "output_folder_missing"
            )

            output_folder = Path()

        else:

            output_folder = Path(
                request.selection.output_folder
            )

        if output_folder and not output_folder.exists():

            errors.append(
                "output_folder_missing"
            )

        if (
            self.output_path(
                request
            ).exists()
            and not request.overwrite
        ):

            errors.append(
                "output_exists"
            )

        selection = request.selection

        selection.voice_id = (
            selection.voice_id
            or voice.id
        )

        selection.default_variant_id = (
            selection.default_variant_id
            or config.default_variant_id
        )

        selection.default_style_id = (
            selection.default_style_id
            or config.default_style_id
        )

        style_ids = self.style_ids(
            voice
        )

        validation = self.planning.validate_selection(
            selection,
            voice.variants,
            style_ids,
        )

        errors.extend(
            validation.errors
        )

        fmt = request.audio_profile.output_format

        if fmt not in request.audio_profile.supported_output_formats:

            errors.append(
                "output_format_invalid"
            )

        if (
            request.audio_profile.mp3_bitrate_kbps
            not in request.audio_profile.supported_mp3_bitrates
        ):

            errors.append(
                "mp3_bitrate_invalid"
            )

        return errors

    def create_plan(
        self,
        request,
        voice,
        workspace,
    ):

        text = self.request_text(
            request
        )

        segments = self.context.split_text(
            text
        )

        style_ids = self.style_ids(
            voice
        )

        selection = request.selection

        validation = self.planning.validate_selection(
            selection,
            voice.variants,
            style_ids,
        )

        if not validation.ok:

            raise RuntimeError(
                ",".join(
                    validation.errors
                )
            )

        if selection.mode == GENERATE_MODE_STANDARD:

            segments = [
                {
                    **segment,
                    "variant_id": selection.selected_variant_id,
                    "style_id": selection.reference_style_id,
                    "confidence": 1.0,
                }
                for segment in segments
            ]

        else:

            segments = self.context.analyze(
                segments,
                validation.allowed_variant_ids,
                validation.allowed_style_ids,
            )

        return self.planning.build_plan(
            job_id=request.job_id,
            segments=segments,
            config=selection,
            allowed_variant_ids=validation.allowed_variant_ids,
            allowed_style_ids=validation.allowed_style_ids,
            temp_dir=workspace.work_dir,
        )

    def generate_chunks(
        self,
        request,
        voice,
        plan,
        adapter=None,
    ):

        chunk_files = []

        total = len(
            plan.chunks
        )

        for index, chunk in enumerate(
            plan.chunks,
            start=1,
        ):

            self.emit_progress(
                "generate",
                index,
                total,
                f"Đang sinh chunk {index}/{total}",
            )

            output = Path(
                chunk.output_temp_path
            )

            output.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            if output.exists():

                chunk.status = "finished"

                chunk_files.append(
                    output
                )

                continue

            text_file = (
                output.parent
                / f"{chunk.chunk_id}.txt"
            )

            text_file.write_text(
                chunk.text,
                encoding="utf-8",
            )

            attempts = (
                request.audio_profile.retry_count
                + 1
            )

            last_error = ""

            for attempt in range(
                attempts
            ):

                try:

                    if adapter is not None:

                        adapter(
                            chunk,
                            text_file,
                            output,
                        )

                    else:

                        self.select_routed_engine(
                            voice
                        )

                        self.engine_manager.generate(
                            text_file=text_file,
                            output_file=output,
                            voice=voice,
                            variant=chunk.variant_id,
                            speed=chunk.speed,
                            style=chunk.style_id,
                        )

                    chunk.status = "finished"

                    chunk.retry_count = attempt

                    chunk_files.append(
                        output
                    )

                    break

                except Exception as exc:

                    last_error = str(
                        exc
                    )

                    chunk.error = last_error

                    chunk.retry_count = attempt

            if chunk.status != "finished":

                raise RuntimeError(
                    json.dumps(
                        {
                            "code": "chunk_failed",
                            "chunk_id": chunk.chunk_id,
                            "text": chunk.text,
                            "error": last_error,
                            "retry_count": chunk.retry_count,
                        },
                        ensure_ascii=False,
                    )
                )

        return chunk_files

    def select_routed_engine(
        self,
        voice,
    ):

        if self.engine_manager is None or not hasattr(
            self.engine_manager,
            "select",
        ):

            return ""

        config = voice.config
        engine_id = self.engine_router.resolve_engine(
            getattr(
                config,
                "language",
                "",
            ),
            getattr(
                config,
                "engine",
                "",
            ),
        )

        if engine_id:

            self.engine_manager.select(
                engine_id
            )

        return engine_id

    def request_text(
        self,
        request,
    ):

        if request.text:

            return request.text

        if request.text_file:

            return Path(
                request.text_file
            ).read_text(
                encoding="utf-8",
                errors="ignore",
            )

        return ""

    def output_path(
        self,
        request,
    ):

        selection = request.selection

        output_folder = Path(
            selection.output_folder
            or "."
        )

        output_name = (
            selection.output_name
            or "output"
        )

        suffix = self.merge.output_suffix(
            request.audio_profile.output_format
        )

        if not output_name.endswith(
            suffix
        ):

            output_name = (
                output_name
                + suffix
            )

        return output_folder / output_name

    def style_ids(
        self,
        voice,
    ):

        style_id = getattr(
            voice.config,
            "default_style_id",
            "",
        )

        result = []

        if style_id:

            result.append(
                style_id
            )

        result.extend([
            "natural",
            "story",
            "dramatic",
            "soft",
        ])

        return list(
            dict.fromkeys(
                result
            )
        )

    def build_report(
        self,
        request,
        voice,
        status,
        plan=None,
        output_path="",
        errors=None,
        started=None,
    ):

        elapsed = (
            time.time()
            - started
            if started
            else 0
        )

        chunks = (
            plan.chunks
            if plan
            else []
        )

        return {
            "job_id": request.job_id,
            "project_id": request.project_id,
            "voice_id": getattr(
                voice,
                "id",
                "",
            ),
            "mode": request.selection.mode,
            "variant_scope": request.selection.allowed_variant_ids,
            "style_scope": request.selection.allowed_style_ids,
            "engine": getattr(
                voice.config,
                "engine",
                "",
            )
            if voice
            else "",
            "model": {
                "gpt": getattr(
                    voice.config,
                    "gpt_model",
                    "",
                )
                if voice
                else "",
                "sovits": getattr(
                    voice.config,
                    "sovits_model",
                    "",
                )
                if voice
                else "",
            },
            "input": request.text_file
            or "direct_text",
            "chunk_count": len(
                chunks
            ),
            "successful_chunks": len([
                chunk
                for chunk in chunks
                if chunk.status == "finished"
            ]),
            "failed_chunks": len([
                chunk
                for chunk in chunks
                if chunk.status == "failed"
            ]),
            "retry_count": sum(
                chunk.retry_count
                for chunk in chunks
            ),
            "speed": request.selection.speed.speed,
            "output_format": request.audio_profile.output_format,
            "duration": 0,
            "elapsed": elapsed,
            "output_path": str(
                output_path
            ),
            "status": status,
            "warnings": [],
            "errors": errors or [],
        }

    def write_report(
        self,
        result,
        workspace,
    ):

        report_path = (
            Path(workspace.work_dir)
            / "generate_report.json"
        )

        report_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        report_path.write_text(
            json.dumps(
                result.report,
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        result.report_path = str(
            report_path
        )

    def emit_progress(
        self,
        stage,
        current_item,
        total_items,
        message,
        level="info",
    ):

        percent = 0

        if total_items:

            percent = int(
                current_item
                * 100
                / total_items
            )

        payload = {
            "job": "generate",
            "stage": stage,
            "chunk": current_item,
            "current_item": current_item,
            "total_items": total_items,
            "percent": percent,
            "elapsed": 0,
            "ETA": 0,
            "output": "",
            "retry": 0,
            "warnings": [],
            "errors": [],
            "message": message,
            "level": level,
        }

        self.progress_events.append(
            payload
        )

        AppEvents.job_progress(
            payload
        )

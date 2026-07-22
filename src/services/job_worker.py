import time
from dataclasses import dataclass
from types import SimpleNamespace

from models.job_model import now_iso
from models.generate_config import GenerateAudioProfile
from models.generate_config import GenerateRequest
from models.generate_config import GenerateSelectionConfig
from models.generate_config import SpeedProfile
from models.resource_model import ResourceRequirement
from models.voice_config import VoiceConfig


class JobCancelled(Exception):

    pass


class JobPaused(Exception):

    pass


@dataclass
class JobExecutionContext:

    repository: object

    log_service: object

    queue_service: object | None = None

    app_context: object | None = None

    environment: dict | None = None

    thread_budget_observation: object | None = None

    thread_budget_state: object | None = None


class BaseJobWorker:

    retryable_errors = set()

    resource_requirement = ResourceRequirement()

    def __init__(
        self,
    ):

        self.pause_requested = False

        self.cancel_requested = False

    def execute(
        self,
        job,
        context,
    ):

        raise NotImplementedError

    def request_pause(
        self,
    ):

        self.pause_requested = True

    def request_resume(
        self,
    ):

        self.pause_requested = False

    def request_cancel(
        self,
    ):

        self.cancel_requested = True

    def check_control(
        self,
        job,
        context,
    ):

        if self.cancel_requested or job.state == "cancel_requested":

            raise JobCancelled(
                "job_cancel_requested"
            )

        if self.pause_requested or job.state == "pause_requested":

            raise JobPaused(
                "job_pause_requested"
            )

    def report_progress(
        self,
        job,
        context,
        current=0,
        total=0,
        stage="",
        message="",
        item_name="",
        started_at=None,
    ):

        job.progress_current = int(
            current
        )

        job.progress_total = int(
            total
        )

        job.progress_stage = stage

        job.progress_item_name = item_name

        job.progress_message = message

        if total:

            job.progress_percent = min(
                100.0,
                max(
                    0.0,
                    current * 100.0 / total,
                ),
            )

            if current > 0 and started_at:

                elapsed = max(
                    0.0,
                    time.time() - started_at,
                )

                remaining = (
                    elapsed / current
                ) * (
                    total - current
                )

                job.eta_seconds = max(
                    0.0,
                    remaining,
                )

        else:

            job.progress_percent = 0.0

            job.eta_seconds = None

        job.last_heartbeat_at = now_iso()

        context.repository.save(
            job
        )

        try:

            from services.app_events import AppEvents

            AppEvents.job_progress(
                {
                    "job": job.job_id,
                    "job_type": job.job_type,
                    "stage": job.progress_stage,
                    "current_file": item_name,
                    "current_item": job.progress_current,
                    "total_items": job.progress_total,
                    "percent": job.progress_percent,
                    "elapsed_seconds": (
                        time.time() - started_at
                    )
                    if started_at
                    else 0,
                    "estimated_remaining_seconds": job.eta_seconds
                    or 0,
                    "message": message,
                    "level": "info",
                    "valid": 0,
                    "suspicious": 0,
                    "errors": 0,
                }
            )

        except Exception:

            pass

    def write_log(
        self,
        job,
        context,
        message,
        level="info",
        stage="",
        data=None,
    ):

        return context.log_service.write(
            job,
            message,
            level=level,
            stage=stage,
            data=data,
        )

    def heartbeat(
        self,
        job,
        context,
    ):

        job.last_heartbeat_at = now_iso()

        context.repository.save(
            job
        )

    def checkpoint(
        self,
        job,
        context,
        state,
    ):

        job.recovery_state = dict(
            state or {}
        )

        context.repository.save(
            job
        )

    def cleanup(
        self,
        job,
        context,
    ):

        return None


class DemoProgressJobWorker(BaseJobWorker):

    resource_requirement = ResourceRequirement(
        profile_id="cpu_light",
        cpu_threads=1,
        ram_mb=128,
        disk_free_mb=32,
        requires_gpu=False,
        notes="Demo job nhẹ, không Train/Generate.",
    )

    def execute(
        self,
        job,
        context,
    ):

        total = int(
            job.payload.get(
                "steps",
                5,
            )
        )

        sleep_seconds = float(
            job.payload.get(
                "sleep_seconds",
                0,
            )
        )

        started = time.time()

        self.write_log(
            job,
            context,
            "Báº¯t Ä‘áº§u demo progress job.",
            stage="demo",
        )

        for index in range(
            1,
            total + 1,
        ):

            self.check_control(
                job,
                context,
            )

            if sleep_seconds:

                time.sleep(
                    sleep_seconds
                )

            self.report_progress(
                job,
                context,
                current=index,
                total=total,
                stage="demo",
                message=f"HoĂ n thĂ nh bÆ°á»›c {index}/{total}",
                item_name=f"step_{index}",
                started_at=started,
            )

        return {
            "ok": True,
            "steps": total,
        }


class ReferenceVerifyJobWorker(BaseJobWorker):

    resource_requirement = ResourceRequirement(
        profile_id="cpu_reference_verify",
        cpu_threads=1,
        ram_mb=256,
        disk_free_mb=64,
        requires_gpu=False,
        notes="Kiểm tra checksum/reference bằng CPU.",
    )

    def execute(
        self,
        job,
        context,
    ):

        asset_id = job.payload.get(
            "asset_id",
            "",
        )

        vault = job.payload.get(
            "vault_service",
            None,
        )

        if vault is None and context.app_context is not None:

            vault = getattr(
                context.app_context,
                "reference_vault_service",
                None,
            )

        if vault is None or not asset_id:

            raise ValueError(
                "reference_verify_missing_asset"
            )

        self.report_progress(
            job,
            context,
            1,
            2,
            "reference_verify",
            "Äang kiá»ƒm tra checksum reference.",
        )

        result = vault.verify_asset(
            asset_id
        )

        self.report_progress(
            job,
            context,
            2,
            2,
            "reference_verify",
            "HoĂ n thĂ nh kiá»ƒm tra reference.",
        )

        return {
            "ok": result.get(
                "ok",
                False,
            ),
            "asset_id": asset_id,
            "messages": result.get(
                "messages",
                [],
            ),
        }


class ProjectValidateJobWorker(BaseJobWorker):

    resource_requirement = ResourceRequirement(
        profile_id="cpu_project_validate",
        cpu_threads=1,
        ram_mb=256,
        disk_free_mb=64,
        requires_gpu=False,
        notes="Validate Project metadata bằng CPU.",
    )

    def execute(
        self,
        job,
        context,
    ):

        project = job.payload.get(
            "project",
        )

        service = job.payload.get(
            "validation_service",
        )

        if service is None and context.app_context is not None:

            service = getattr(
                context.app_context,
                "project_validation_service",
                None,
            )

        if project is None or service is None:

            raise ValueError(
                "project_validation_missing_project"
            )

        self.report_progress(
            job,
            context,
            1,
            1,
            "project_validate",
            "Äang kiá»ƒm tra Project.",
        )

        return service.validate(
            project
        )


class ProjectBackupJobWorker(BaseJobWorker):

    resource_requirement = ResourceRequirement(
        profile_id="cpu_project_backup",
        cpu_threads=1,
        ram_mb=256,
        disk_free_mb=512,
        requires_gpu=False,
        notes="Backup metadata Project cần kiểm tra dung lượng đĩa.",
    )

    def execute(
        self,
        job,
        context,
    ):

        project = job.payload.get(
            "project",
        )

        backup_service = job.payload.get(
            "backup_service",
        )

        if backup_service is None and context.app_context is not None:

            backup_service = getattr(
                context.app_context,
                "project_backup_service",
                None,
            )

        if project is None or backup_service is None:

            raise ValueError(
                "project_backup_missing_project"
            )

        if not job.payload.get(
            "allow_project_backup",
            False,
        ):

            raise ValueError(
                "project_backup_requires_explicit_test_scope"
            )

        self.report_progress(
            job,
            context,
            1,
            1,
            "project_backup",
            "Äang backup metadata Project.",
        )

        return backup_service.backup_project(
            project,
            reason="job_queue_smoke",
            mode="metadata",
        )


class GeneratePrepareJobWorker(BaseJobWorker):

    resource_requirement = ResourceRequirement(
        profile_id="cpu_generate_prepare",
        cpu_threads=1,
        ram_mb=256,
        disk_free_mb=128,
        requires_gpu=False,
        notes="Chuẩn bị Generate foundation: snapshot, plan, manifest; không synthesize audio.",
    )

    def execute(
        self,
        job,
        context,
    ):

        service = job.payload.get(
            "generate_session_service",
        )

        if service is not None and not hasattr(
            service,
            "validate_request",
        ):

            service = None

        if service is None and context.app_context is not None:

            service = getattr(
                context.app_context,
                "generate_session_service",
                None,
            )

        if service is None:

            from services.generate_session_service import (
                GenerateSessionService,
            )

            service = GenerateSessionService()

        request = dict(
            job.payload.get(
                "request",
                job.payload,
            )
            or {}
        )

        if not request.get(
            "project_id",
        ):

            request[
                "project_id"
            ] = job.project_id

        if not request.get(
            "voice_id",
        ):

            request[
                "voice_id"
            ] = job.voice_id

        started = time.time()

        self.report_progress(
            job,
            context,
            1,
            4,
            "generate_validate",
            "Đang kiểm tra Generate Request.",
            started_at=started,
        )

        validation = service.validate_request(
            request
        )

        if not validation.ok:

            return {
                "ok": False,
                "status": "blocked",
                "validation": validation.to_dict(),
            }

        self.report_progress(
            job,
            context,
            2,
            4,
            "generate_snapshot",
            "Đang tạo source snapshot.",
            started_at=started,
        )

        result = service.create_session(
            request
        )

        self.report_progress(
            job,
            context,
            3,
            4,
            "generate_plan",
            "Đã tạo Generate Plan và Manifest.",
            item_name=result[
                "session"
            ][
                "session_id"
            ],
            started_at=started,
        )

        self.report_progress(
            job,
            context,
            4,
            4,
            "generate_ready",
            "Generate foundation đã sẵn sàng để bước Generate thật sau này.",
            item_name=result[
                "session"
            ][
                "session_id"
            ],
            started_at=started,
        )

        return {
            "ok": True,
            "status": "ready",
            "session_id": result[
                "session"
            ][
                "session_id"
            ],
            "manifest": result.get(
                "manifest",
                {},
            ),
        }


class GenerateExecuteJobWorker(BaseJobWorker):

    thread_budget_engine_id = "vieneu"

    resource_requirement = ResourceRequirement(
        profile_id="cpu_generate_execute_vieneu",
        cpu_threads=2,
        ram_mb=4096,
        disk_free_mb=512,
        requires_gpu=False,
        notes="Generate thật bằng VieNeu-TTS CPU/ONNX subprocess.",
    )

    def execute(
        self,
        job,
        context,
    ):

        payload = dict(
            job.payload
            or {}
        )

        request = self.request_from_payload(
            payload.get(
                "request",
                payload,
            )
        )

        voice = self.voice_from_payload(
            payload.get(
                "voice",
                {},
            )
        )

        service = payload.get(
            "generate_pipeline_service",
        )

        if service is None and context.app_context is not None:

            service = getattr(
                context.app_context,
                "generate_pipeline_service",
                None,
            )

        if service is None:

            from services.generate_pipeline_service import (
                GeneratePipelineService,
            )

            engine_manager = None

            if context.app_context is not None:

                engine_manager = getattr(
                    context.app_context,
                    "engine_manager",
                    None,
                )

            service = GeneratePipelineService(
                engine_manager=engine_manager,
            )

        started = time.time()

        self.report_progress(
            job,
            context,
            1,
            2,
            "generate_execute",
            "Đang chạy Generate thật.",
            started_at=started,
        )

        result = service.run(
            request=request,
            voice=voice,
        )

        if not result.ok:

            raise RuntimeError(
                ",".join(
                    result.errors
                    or [
                        "generate_execute_failed"
                    ]
                )
            )

        self.report_progress(
            job,
            context,
            2,
            2,
            "generate_done",
            "Generate thật đã hoàn tất.",
            item_name=result.output_file,
            started_at=started,
        )

        return result.to_dict() if hasattr(
            result,
            "to_dict",
        ) else dict(
            result
        )

    def request_from_payload(
        self,
        data,
    ):

        data = dict(
            data
            or {}
        )

        selection = self.selection_from_payload(
            data.get(
                "selection",
                {},
            )
        )

        audio_profile = self.audio_profile_from_payload(
            data.get(
                "audio_profile",
                {},
            )
        )

        return GenerateRequest(
            text=data.get(
                "text",
                "",
            ),
            text_file=data.get(
                "text_file",
                "",
            ),
            output_file=data.get(
                "output_file",
                "",
            ),
            selection=selection,
            project_id=data.get(
                "project_id",
                "",
            ),
            job_id=data.get(
                "job_id",
                "",
            )
            or "",
            overwrite=bool(
                data.get(
                    "overwrite",
                    False,
                )
            ),
            audio_profile=audio_profile,
        )

    def selection_from_payload(
        self,
        data,
    ):

        data = dict(
            data
            or {}
        )

        speed = data.get(
            "speed",
            {},
        )

        if isinstance(
            speed,
            dict,
        ):

            speed = SpeedProfile(
                **{
                    key: value
                    for key, value in speed.items()
                    if key in SpeedProfile.__dataclass_fields__
                }
            )

        elif not isinstance(
            speed,
            SpeedProfile,
        ):

            speed = SpeedProfile()

        values = {
            key: value
            for key, value in data.items()
            if key in GenerateSelectionConfig.__dataclass_fields__
            and key != "speed"
        }

        values["speed"] = speed

        return GenerateSelectionConfig(
            **values
        )

    def audio_profile_from_payload(
        self,
        data,
    ):

        data = dict(
            data
            or {}
        )

        return GenerateAudioProfile(
            **{
                key: value
                for key, value in data.items()
                if key in GenerateAudioProfile.__dataclass_fields__
            }
        )

    def voice_from_payload(
        self,
        data,
    ):

        data = dict(
            data
            or {}
        )

        config = VoiceConfig.from_dict(
            data.get(
                "config",
                data,
            )
        )

        return SimpleNamespace(
            id=data.get(
                "id",
                config.voice_id,
            )
            or config.voice_id,
            name=data.get(
                "name",
                "",
            ),
            config=config,
            variants=data.get(
                "variants",
                config.variants,
            ),
        )

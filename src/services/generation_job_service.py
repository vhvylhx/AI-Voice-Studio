import hashlib
import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from models.api_generation_job import (
    JOB_CANCELLED,
    JOB_FAILED,
    JOB_INTERRUPTED,
    JOB_QUEUED,
    ApiGenerationJob,
)
from services.voice_catalog_service import VoiceCatalogService


class GenerationJobService:

    def __init__(
        self,
        root=None,
        voice_catalog=None,
        concurrency=1,
    ):

        self.root = Path(
            root or "workspace/api_jobs"
        )

        self.voice_catalog = (
            voice_catalog
            or VoiceCatalogService()
        )

        self.concurrency = int(
            concurrency or 1
        )

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def create_job(
        self,
        request,
    ):

        errors = self.validate_request(
            request
        )

        job = ApiGenerationJob(
            job_id=uuid4().hex,
            request_id=str(
                request.get(
                    "request_id",
                    "",
                )
            ),
            status=JOB_QUEUED,
            progress=0,
            current_stage="queued",
            message_vi="Job đã được đưa vào hàng đợi.",
            request=self.sanitize_request(
                request
            ),
        )

        job.ensure_created_at()

        if errors:

            job.status = JOB_FAILED

            job.current_stage = "validation"

            job.error_code = errors[0][
                "code"
            ]

            job.error_message_vi = errors[0][
                "message_vi"
            ]

            job.message_vi = job.error_message_vi

            job.completed_at = datetime.now().isoformat()

        self.write_job(
            job
        )

        return job

    def get_job(
        self,
        job_id,
    ):

        folder = self.job_dir(
            job_id
        )

        state = folder / "state.json"

        if not state.exists():

            return None

        return ApiGenerationJob.from_dict(
            json.loads(
                state.read_text(
                    encoding="utf-8"
                )
            )
        )

    def cancel_job(
        self,
        job_id,
    ):

        job = self.get_job(
            job_id
        )

        if job is None:

            return None

        if job.status in (
            JOB_FAILED,
            JOB_CANCELLED,
            "completed",
        ):

            return job

        job.status = JOB_CANCELLED

        job.current_stage = "cancelled"

        job.message_vi = "Job đã được hủy an toàn."

        job.completed_at = datetime.now().isoformat()

        self.write_job(
            job
        )

        return job

    def result_metadata(
        self,
        job_id,
    ):

        job = self.get_job(
            job_id
        )

        if job is None:

            return None

        if job.status != "completed":

            return {
                "error": "result_not_ready",
                "message_vi": "Audio chưa hoàn thành.",
                "job": job.to_dict(),
            }

        return job.result

    def recover_interrupted(
        self,
    ):

        recovered = []

        for state in self.root.glob(
            "*/state.json"
        ):

            job = ApiGenerationJob.from_dict(
                json.loads(
                    state.read_text(
                        encoding="utf-8"
                    )
                )
            )

            if job.status in (
                "preparing",
                "generating",
                "post_processing",
            ):

                job.status = JOB_INTERRUPTED

                job.message_vi = (
                    "Ứng dụng đã đóng khi job đang chạy. Job cần được kiểm tra lại."
                )

                self.write_job(
                    job
                )

                recovered.append(
                    job.job_id
                )

        return recovered

    def validate_request(
        self,
        request,
    ):

        errors = []

        voice_id = str(
            request.get(
                "voice_id",
                "",
            )
        ).strip()

        if not voice_id:

            errors.append(
                self.error(
                    "voice_required",
                    "Thiếu Voice ID.",
                )
            )

            return errors

        voice = self.voice_catalog.get_voice(
            voice_id
        )

        if voice is None:

            errors.append(
                self.error(
                    "voice_not_found",
                    "Không tìm thấy Voice.",
                )
            )

            return errors

        if not voice.get(
            "generation_ready",
            False,
        ):

            errors.append(
                self.error(
                    "voice_not_ready",
                    "Voice chưa sẵn sàng Generate. Cần model, reference audio và reference text hợp lệ.",
                )
            )

        if not str(
            request.get(
                "text",
                "",
            )
        ).strip():

            errors.append(
                self.error(
                    "text_empty",
                    "Nội dung cần tạo audio đang rỗng.",
                )
            )

        if request.get(
            "output_format",
            "wav",
        ) not in (
            "wav",
            "mp3",
        ):

            errors.append(
                self.error(
                    "output_format_invalid",
                    "Định dạng audio không được hỗ trợ.",
                )
            )

        style_profile_id = str(
            request.get(
                "style_profile_id",
                "",
            )
            or ""
        ).strip()

        if style_profile_id:

            readiness = self.voice_catalog.style_profile_service.readiness(
                style_profile_id
            )

            if readiness.get(
                "status"
            ) == "missing":

                errors.append(
                    self.error(
                        "style_profile_missing",
                        "Style Profile không tồn tại hoặc chưa được import trên máy này.",
                    )
                )

            else:

                errors.append(
                    self.error(
                        "style_profile_generation_not_supported",
                        "Generate engine hiện tại chưa áp dụng Style Profile thật. Không xử lý âm thầm để tránh sai chất giọng.",
                    )
                )

        style_mode = str(
            request.get(
                "style_mode",
                "inherit_voice_default",
            )
            or "inherit_voice_default"
        )

        if style_mode not in (
            "inherit_voice_default",
            "explicit",
            "disabled",
        ):

            errors.append(
                self.error(
                    "style_mode_invalid",
                    "style_mode không hợp lệ.",
                )
            )

        try:

            style_strength = float(
                request.get(
                    "style_strength",
                    1.0,
                )
            )

        except Exception:

            style_strength = -1

        if style_strength < 0 or style_strength > 1.5:

            errors.append(
                self.error(
                    "style_strength_invalid",
                    "style_strength phải nằm trong khoảng 0.0 đến 1.5.",
                )
            )

        return errors

    def write_job(
        self,
        job,
    ):

        folder = self.job_dir(
            job.job_id
        )

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        (folder / "logs").mkdir(
            exist_ok=True
        )

        (folder / "temp").mkdir(
            exist_ok=True
        )

        (folder / "output").mkdir(
            exist_ok=True
        )

        (folder / "request.json").write_text(
            json.dumps(
                job.request,
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        (folder / "state.json").write_text(
            json.dumps(
                job.to_dict(),
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def job_dir(
        self,
        job_id,
    ):

        safe = "".join(
            char
            for char in str(
                job_id
            )
            if char.isalnum()
            or char in (
                "-",
                "_",
            )
        )

        if not safe:

            safe = "invalid"

        return self.root / safe

    def sanitize_request(
        self,
        request,
    ):

        allowed = {
            "voice_id",
            "variant_id",
            "preset_id",
            "reference_style_id",
            "style_profile_id",
            "style_strength",
            "style_mode",
            "text",
            "language",
            "output_format",
            "sample_rate",
            "speed",
            "request_id",
            "metadata",
        }

        return {
            key: value
            for key, value in dict(
                request or {}
            ).items()
            if key in allowed
        }

    def error(
        self,
        code,
        message_vi,
    ):

        return {
            "code": code,
            "message_vi": message_vi,
        }

    def checksum(
        self,
        file,
    ):

        path = Path(
            file
        )

        if not path.exists():

            return ""

        return hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

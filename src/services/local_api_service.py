import json
import secrets
import threading
from http.server import BaseHTTPRequestHandler
from http.server import ThreadingHTTPServer
from urllib.parse import urlparse

from core import App
from models.local_api_config import LocalApiConfig
from services.feature_readiness_service import FeatureReadinessService
from services.generation_job_service import GenerationJobService
from services.generate_session_service import GenerateSessionService
from services.current_project_service import CurrentProjectService
from services.project_service import ProjectService
from services.style_profile_service import StyleProfileService
from services.voice_catalog_service import VoiceCatalogService


class LocalApiService:

    def __init__(
        self,
        config=None,
        voice_catalog=None,
        job_service=None,
        readiness=None,
        style_profiles=None,
        project_service=None,
        current_project=None,
        job_queue_service=None,
        job_log_service=None,
        resource_monitor_service=None,
        generate_session_service=None,
    ):

        self.config = LocalApiConfig.from_dict(
            config
            or self.load_config()
        )

        self.voice_catalog = (
            voice_catalog
            or VoiceCatalogService()
        )

        self.job_service = (
            job_service
            or GenerationJobService(
                concurrency=self.config.concurrency
            )
        )

        self.readiness = (
            readiness
            or FeatureReadinessService()
        )

        self.style_profiles = (
            style_profiles
            or StyleProfileService()
        )

        self.project_service = (
            project_service
            or ProjectService()
        )

        self.current_project = (
            current_project
            or CurrentProjectService
        )

        self.job_queue_service = job_queue_service

        self.job_log_service = job_log_service

        self.resource_monitor_service = resource_monitor_service

        self.generate_session_service = generate_session_service

        self.server = None

        self.thread = None

    def load_config(
        self,
    ):

        data = App.config.all()

        return {
            "local_api_enabled": data.get(
                "local_api_enabled",
                False,
            ),
            "local_api_host": data.get(
                "local_api_host",
                "127.0.0.1",
            ),
            "local_api_port": data.get(
                "local_api_port",
                8765,
            ),
            "local_api_token": data.get(
                "local_api_token",
                "",
            ),
            "local_api_auto_start": data.get(
                "local_api_auto_start",
                False,
            ),
            "allowed_origins": data.get(
                "allowed_origins",
                [],
            ),
            "output_access_policy": data.get(
                "output_access_policy",
                "managed_output_only",
            ),
            "concurrency": data.get(
                "local_api_concurrency",
                1,
            ),
        }

    def save_config(
        self,
    ):

        data = self.config.to_dict()

        App.config.set(
            "local_api_enabled",
            data[
                "local_api_enabled"
            ],
        )

        App.config.set(
            "local_api_host",
            data[
                "local_api_host"
            ],
        )

        App.config.set(
            "local_api_port",
            data[
                "local_api_port"
            ],
        )

        App.config.set(
            "local_api_token",
            data[
                "local_api_token"
            ],
        )

        App.config.set(
            "local_api_auto_start",
            data[
                "local_api_auto_start"
            ],
        )

        App.config.set(
            "allowed_origins",
            data[
                "allowed_origins"
            ],
        )

        App.config.set(
            "output_access_policy",
            data[
                "output_access_policy"
            ],
        )

        App.config.set(
            "local_api_concurrency",
            data[
                "concurrency"
            ],
        )

    def ensure_token(
        self,
    ):

        if not self.config.local_api_token:

            self.config.local_api_token = secrets.token_urlsafe(
                32
            )

            self.save_config()

        return self.config.local_api_token

    def regenerate_token(
        self,
    ):

        self.config.local_api_token = secrets.token_urlsafe(
            32
        )

        self.save_config()

        return self.config.local_api_token

    def status(
        self,
    ):

        return {
            "enabled": self.config.local_api_enabled,
            "running": self.server is not None,
            "host": self.config.local_api_host,
            "port": self.config.local_api_port,
            "base_url": self.base_url(),
            "requires_token": True,
            "concurrency": self.config.concurrency,
        }

    def base_url(
        self,
    ):

        return (
            f"http://{self.config.local_api_host}:"
            f"{int(self.config.local_api_port)}"
        )

    def start(
        self,
    ):

        if self.server is not None:

            return self.status()

        if not self.config.local_api_enabled:

            return {
                **self.status(),
                "message_vi": "API nội bộ đang tắt trong Settings.",
            }

        self.ensure_token()

        handler = self.handler_class()

        self.server = ThreadingHTTPServer(
            (
                self.config.local_api_host,
                int(
                    self.config.local_api_port
                ),
            ),
            handler,
        )

        self.thread = threading.Thread(
            target=self.server.serve_forever,
            daemon=True,
        )

        self.thread.start()

        return self.status()

    def stop(
        self,
    ):

        if self.server is not None:

            self.server.shutdown()

            self.server.server_close()

        self.server = None

        self.thread = None

        return self.status()

    def restart(
        self,
    ):

        self.stop()

        return self.start()

    def handler_class(
        self,
    ):

        service = self

        class Handler(BaseHTTPRequestHandler):

            def do_GET(
                self,
            ):

                service.handle(
                    self,
                    "GET",
                )

            def do_POST(
                self,
            ):

                service.handle(
                    self,
                    "POST",
                )

            def log_message(
                self,
                format,
                *args,
            ):

                return

        return Handler

    def handle(
        self,
        request,
        method,
    ):

        parsed = urlparse(
            request.path
        )

        path = parsed.path.rstrip(
            "/"
        ) or "/"

        if path == "/api/v1/health" and method == "GET":

            return self.write_json(
                request,
                200,
                self.health(),
            )

        if not self.authorized(
            request
        ):

            return self.write_json(
                request,
                401,
                {
                    "error": "unauthorized",
                    "message_vi": "Thiếu hoặc sai token API.",
                },
            )

        try:

            response = self.route(
                method,
                path,
                self.read_json(
                    request
                ),
            )

            return self.write_json(
                request,
                response.get(
                    "status_code",
                    200,
                ),
                response.get(
                    "body",
                    {},
                ),
            )

        except Exception as e:

            return self.write_json(
                request,
                500,
                {
                    "error": "internal_error",
                    "message_vi": "API gặp lỗi nội bộ.",
                    "technical_details": str(
                        e
                    ),
                },
            )

    def route(
        self,
        method,
        path,
        body,
    ):

        if method == "GET" and path == "/api/v1/capabilities":

            return self.response(
                self.capabilities()
            )

        if method == "GET" and path == "/api/v1/readiness":

            return self.response(
                self.readiness.summary()
            )

        if method == "GET" and path == "/api/v1/projects":

            return self.response(
                self.project_list()
            )

        if method == "GET" and path == "/api/v1/projects/current":

            return self.response(
                self.current_project_detail()
            )

        if method == "GET" and path == "/api/v1/workspace":

            return self.response(
                self.workspace_detail()
            )

        if method == "GET" and path == "/api/v1/jobs":

            return self.response(
                self.jobs_list()
            )

        if method == "GET" and path == "/api/v1/queue":

            return self.response(
                self.queue_detail()
            )

        if method == "GET" and path == "/api/v1/resources":

            return self.response(
                self.resources_summary()
            )

        if method == "GET" and path == "/api/v1/resources/hardware":

            return self.response(
                self.resources_hardware()
            )

        if method == "GET" and path == "/api/v1/resources/snapshot":

            return self.response(
                self.resources_snapshot()
            )

        if method == "GET" and path == "/api/v1/resources/policy":

            return self.response(
                self.resources_policy()
            )

        if method == "GET" and path == "/api/v1/resources/leases":

            return self.response(
                {
                    "items": self.resources_leases()
                }
            )

        if method == "GET" and path == "/api/v1/resources/waiting-jobs":

            return self.response(
                {
                    "items": self.resources_waiting_jobs()
                }
            )

        if method == "GET" and path == "/api/v1/generate/readiness":

            return self.response(
                self.generate_readiness()
            )

        if method == "GET" and path == "/api/v1/generate/sessions":

            return self.response(
                self.resolve_generate_session().list_sessions()
            )

        if method == "POST" and path == "/api/v1/generate/requests/validate":

            return self.response(
                self.resolve_generate_session()
                .validate_request(
                    body
                )
                .to_dict()
            )

        if method == "POST" and path == "/api/v1/generate/sessions":

            result = self.resolve_generate_session().create_session(
                body
            )

            return self.response(
                self.safe_generate_session_result(
                    result
                ),
                status_code=201
                if result[
                    "validation"
                ][
                    "ok"
                ]
                else 400,
            )

        if method == "GET" and path == "/api/v1/voices":

            return self.response(
                self.voice_catalog.list_voices()
            )

        if method == "GET" and path == "/api/v1/voice-catalog":

            return self.response(
                self.voice_catalog.catalog()
            )

        if method == "GET" and path == "/api/v1/style-profiles":

            return self.response(
                self.style_profile_list()
            )

        parts = [
            part
            for part in path.split(
                "/"
            )
            if part
        ]

        if (
            len(parts) == 4
            and parts[:3]
            == [
                "api",
                "v1",
                "jobs",
            ]
            and method == "GET"
        ):

            return self.response_or_404(
                self.job_detail(
                    parts[3]
                ),
                "job_not_found",
            )

        if (
            len(parts) == 5
            and parts[:3]
            == [
                "api",
                "v1",
                "generate",
            ]
            and parts[3] == "sessions"
            and method == "GET"
        ):

            return self.response_or_404(
                self.safe_generate_session_result(
                    self.resolve_generate_session().get_session(
                        parts[4]
                    )
                ),
                "generate_session_not_found",
            )

        if (
            len(parts) == 6
            and parts[:3]
            == [
                "api",
                "v1",
                "generate",
            ]
            and parts[3] == "sessions"
            and parts[5] == "plan"
            and method == "GET"
        ):

            return self.response_or_404(
                self.resolve_generate_session().get_plan(
                    parts[4]
                ),
                "generate_plan_not_found",
            )

        if (
            len(parts) == 6
            and parts[:3]
            == [
                "api",
                "v1",
                "generate",
            ]
            and parts[3] == "sessions"
            and parts[5] == "chapters"
            and method == "GET"
        ):

            return self.response_or_404(
                self.generate_plan_section(
                    parts[4],
                    "chapters",
                ),
                "generate_plan_not_found",
            )

        if (
            len(parts) == 6
            and parts[:3]
            == [
                "api",
                "v1",
                "generate",
            ]
            and parts[3] == "sessions"
            and parts[5] == "units"
            and method == "GET"
        ):

            return self.response_or_404(
                self.paginate(
                    self.generate_plan_section(
                        parts[4],
                        "units",
                    ),
                    body,
                ),
                "generate_plan_not_found",
            )

        if (
            len(parts) == 6
            and parts[:3]
            == [
                "api",
                "v1",
                "generate",
            ]
            and parts[3] == "sessions"
            and parts[5] == "attempts"
            and method == "GET"
        ):

            return self.response_or_404(
                self.generate_plan_section(
                    parts[4],
                    "attempts",
                ),
                "generate_plan_not_found",
            )

        if (
            len(parts) == 6
            and parts[:3]
            == [
                "api",
                "v1",
                "generate",
            ]
            and parts[3] == "sessions"
            and parts[5] == "artifacts"
            and method == "GET"
        ):

            return self.response_or_404(
                self.safe_generate_artifacts(
                    self.resolve_generate_session().list_artifacts(
                        parts[4]
                    )
                ),
                "generate_session_not_found",
            )

        if (
            len(parts) == 6
            and parts[:3]
            == [
                "api",
                "v1",
                "generate",
            ]
            and parts[3] == "sessions"
            and parts[5] == "manifest"
            and method == "GET"
        ):

            return self.response_or_404(
                self.safe_generate_manifest(
                    self.resolve_generate_session().get_manifest(
                        parts[4]
                    )
                ),
                "generate_manifest_not_found",
            )

        if (
            len(parts) == 6
            and parts[:3]
            == [
                "api",
                "v1",
                "generate",
            ]
            and parts[3] == "sessions"
            and parts[5] == "resume"
            and method == "GET"
        ):

            return self.response_or_404(
                self.resolve_generate_session().inspect_resume(
                    parts[4]
                ),
                "generate_session_not_found",
            )

        if (
            len(parts) == 6
            and parts[:3]
            == [
                "api",
                "v1",
                "generate",
            ]
            and parts[3] == "sessions"
            and parts[5] == "resume"
            and method == "POST"
        ):

            result = self.resolve_generate_session().execute_resume(
                parts[4],
                expected_fingerprint=body.get(
                    "expected_fingerprint",
                    "",
                ),
                provider=None,
            )

            return self.response(
                result,
                status_code=503
                if result.get(
                    "status"
                )
                == "UNAVAILABLE"
                else 409,
            )

        if (
            len(parts) == 8
            and parts[:3]
            == [
                "api",
                "v1",
                "generate",
            ]
            and parts[3] == "sessions"
            and parts[5] == "units"
            and parts[7] == "retry"
            and method == "GET"
        ):

            return self.response_or_404(
                self.resolve_generate_session().inspect_retry(
                    parts[4],
                    parts[6],
                ),
                "generate_unit_not_found",
            )

        if (
            len(parts) == 8
            and parts[:3]
            == [
                "api",
                "v1",
                "generate",
            ]
            and parts[3] == "sessions"
            and parts[5] == "units"
            and parts[7] == "retry"
            and method == "POST"
        ):

            result = self.resolve_generate_session().retry_unit(
                parts[4],
                parts[6],
                expected_fingerprint=body.get(
                    "expected_fingerprint",
                    "",
                ),
                provider=None,
            )

            return self.response(
                result,
                status_code=503
                if result.get(
                    "status"
                )
                == "UNAVAILABLE"
                else 409,
            )

        if (
            len(parts) == 8
            and parts[:3]
            == [
                "api",
                "v1",
                "generate",
            ]
            and parts[3] == "sessions"
            and parts[5] == "chapters"
            and parts[7] == "retry"
            and method == "POST"
        ):

            result = self.resolve_generate_session().retry_chapter(
                parts[4],
                parts[6],
                provider=None,
            )

            return self.response(
                result,
                status_code=503,
            )

        if (
            path == "/api/v1/generate/recovery"
            and method == "GET"
        ):

            return self.response(
                self.resolve_generate_session().inspect_recovery()
            )

        if (
            len(parts) == 7
            and parts[:3]
            == [
                "api",
                "v1",
                "generate",
            ]
            and parts[3] == "sessions"
            and parts[5] == "manifest"
            and parts[6] == "rebuild"
            and method == "POST"
        ):

            return self.response(
                self.safe_generate_session_result(
                    self.resolve_generate_session().rebuild_manifest(
                        parts[4]
                    )
                )
            )

        if (
            len(parts) == 5
            and parts[:3]
            == [
                "api",
                "v1",
                "jobs",
            ]
            and parts[4] == "logs"
            and method == "GET"
        ):

            return self.response_or_404(
                self.job_logs(
                    parts[3]
                ),
                "job_not_found",
            )

        if (
            len(parts) == 4
            and parts[:3]
            == [
                "api",
                "v1",
                "projects",
            ]
            and method == "GET"
        ):

            return self.response_or_404(
                self.project_detail(
                    parts[3]
                ),
                "project_not_found",
            )

        if (
            len(parts) == 5
            and parts[:3]
            == [
                "api",
                "v1",
                "projects",
            ]
            and parts[4] == "health"
            and method == "GET"
        ):

            return self.response_or_404(
                self.project_health(
                    parts[3]
                ),
                "project_not_found",
            )

        if (
            len(parts) == 4
            and parts[:3]
            == [
                "api",
                "v1",
                "voices",
            ]
            and method == "GET"
        ):

            voice = self.voice_catalog.get_voice(
                parts[3]
            )

            return self.response_or_404(
                voice,
                "voice_not_found",
            )

        if (
            len(parts) == 4
            and parts[:3]
            == [
                "api",
                "v1",
                "style-profiles",
            ]
            and method == "GET"
        ):

            return self.response_or_404(
                self.style_profile_detail(
                    parts[3]
                ),
                "style_profile_not_found",
            )

        if (
            len(parts) == 5
            and parts[:3]
            == [
                "api",
                "v1",
                "style-profiles",
            ]
            and parts[4] == "readiness"
            and method == "GET"
        ):

            return self.response(
                self.style_profiles.readiness(
                    parts[3]
                )
            )

        if (
            len(parts) == 5
            and parts[:3]
            == [
                "api",
                "v1",
                "voices",
            ]
            and parts[4] == "style-profile"
            and method == "GET"
        ):

            voice = self.voice_catalog.get_voice(
                parts[3]
            )

            return self.response_or_404(
                voice.get(
                    "reading_style",
                    {},
                )
                if voice
                else None,
                "voice_not_found",
            )

        if (
            len(parts) == 5
            and parts[:3]
            == [
                "api",
                "v1",
                "voices",
            ]
            and parts[4] == "variants"
            and method == "GET"
        ):

            variants = self.voice_catalog.list_variants(
                parts[3]
            )

            return self.response_or_404(
                variants,
                "voice_not_found",
            )

        if (
            path == "/api/v1/generation/jobs"
            and method == "POST"
        ):

            job = self.job_service.create_job(
                body
            )

            return self.response(
                {
                    "job_id": job.job_id,
                    "status": job.status,
                    "created_at": job.created_at,
                    "status_url": f"/api/v1/generation/jobs/{job.job_id}",
                    "message_vi": job.message_vi,
                },
                status_code=202
                if job.status == "queued"
                else 400,
            )

        if (
            len(parts) == 5
            and parts[:4]
            == [
                "api",
                "v1",
                "generation",
                "jobs",
            ]
            and method == "GET"
        ):

            job = self.job_service.get_job(
                parts[4]
            )

            return self.response_or_404(
                job.to_dict()
                if job
                else None,
                "job_not_found",
            )

        if (
            len(parts) == 6
            and parts[:4]
            == [
                "api",
                "v1",
                "generation",
                "jobs",
            ]
            and parts[5] == "cancel"
            and method == "POST"
        ):

            job = self.job_service.cancel_job(
                parts[4]
            )

            return self.response_or_404(
                job.to_dict()
                if job
                else None,
                "job_not_found",
            )

        if (
            len(parts) == 6
            and parts[:4]
            == [
                "api",
                "v1",
                "generation",
                "jobs",
            ]
            and parts[5] == "result"
            and method == "GET"
        ):

            result = self.job_service.result_metadata(
                parts[4]
            )

            return self.response_or_404(
                result,
                "job_not_found",
            )

        return self.response(
            {
                "error": "not_found",
                "message_vi": "Endpoint không tồn tại.",
            },
            status_code=404,
        )

    def authorized(
        self,
        request,
    ):

        token = self.ensure_token()

        auth = request.headers.get(
            "Authorization",
            "",
        )

        if auth == f"Bearer {token}":

            return True

        api_key = request.headers.get(
            "X-AVS-API-Key",
            "",
        )

        return api_key == token

    def health(
        self,
    ):

        summary = self.readiness.summary()

        return {
            "api_status": "running"
            if self.server
            else "available",
            "app_version": "0.1.0",
            "generation_available": "generation"
            not in summary.get(
                "blocking_features",
                [],
            ),
            "runtime_available": "training"
            not in summary.get(
                "blocking_features",
                [],
            ),
            "limited_mode": summary.get(
                "limited_mode",
                False,
            ),
            "timestamp": __import__(
                "datetime"
            ).datetime.datetime.now().isoformat(),
        }

    def capabilities(
        self,
    ):

        return {
            "supported_languages": [
                "vi",
            ],
            "supported_formats": [
                "wav",
                "mp3",
            ],
            "max_text_length": 10000,
            "job_api": True,
            "timeline_support": True,
            "variant_support": True,
            "reference_style_support": True,
            "style_profile_support": True,
            "job_queue_support": True,
            "resource_manager_support": True,
            "generate_foundation_support": True,
            "style_profile_generation_usage": "degraded",
            "current_limitations": [
                "MVP chưa tự chạy Generate thật qua API khi Voice chưa generation-ready.",
                "API mặc định chỉ bind localhost.",
            ],
        }

    def project_list(
        self,
    ):

        return {
            "items": [
                self.safe_project(
                    project
                )
                for project in self.project_service.list_projects(
                    include_archived=True
                )
            ]
        }

    def current_project_detail(
        self,
    ):

        if not self.current_project.has_project():

            return {
                "current_project": None,
                "message_vi": "Chưa mở dự án.",
            }

        return {
            "current_project": self.safe_project(
                self.current_project.get(),
                include_details=True,
            )
        }

    def project_detail(
        self,
        project_id,
    ):

        try:

            project = self.project_service.load(
                project_id
            )

        except Exception:

            return None

        return self.safe_project(
            project,
            include_details=True,
        )

    def project_health(
        self,
        project_id,
    ):

        try:

            return self.project_service.validate(
                project_id
            )

        except Exception:

            return None

    def workspace_detail(
        self,
    ):

        return {
            "application_workspace": "workspace",
            "projects_root": "projects",
            "current_project": (
                self.safe_project(
                    self.current_project.get()
                )
                if self.current_project.has_project()
                else None
            ),
        }

    def resolve_job_queue(
        self,
    ):

        if self.job_queue_service is not None:

            return self.job_queue_service

        try:

            from core.app_context import AppContext

            return AppContext.job_queue_service

        except Exception:

            return None

    def resolve_job_log(
        self,
    ):

        if self.job_log_service is not None:

            return self.job_log_service

        try:

            from core.app_context import AppContext

            return AppContext.job_log_service

        except Exception:

            return None

    def resolve_resource_monitor(
        self,
    ):

        if self.resource_monitor_service is not None:

            return self.resource_monitor_service

        try:

            from core.app_context import AppContext

            return AppContext.resource_monitor_service

        except Exception:

            return None

    def resolve_generate_session(
        self,
    ):

        if self.generate_session_service is not None:

            return self.generate_session_service

        try:

            from core.app_context import AppContext

            return AppContext.generate_session_service

        except Exception:

            return GenerateSessionService()

    def generate_readiness(
        self,
    ):

        return {
            "available": True,
            "status": "planning_ready_execution_unavailable",
            "message_vi": "Generate Pipeline foundation đã sẵn sàng lập request/session/plan/manifest. Chưa chạy Generate thật qua endpoint này.",
            "capabilities": {
                "planning": "READY",
                "source_snapshot": "READY",
                "normalization": "READY",
                "structure": "READY",
                "splitter": "READY",
                "frozen_plan": "READY",
                "manifest": "READY",
                "artifact_lifecycle": "READY",
                "generate_execution": "UNAVAILABLE",
                "preview_plan": "READY",
                "preview_audio": "UNAVAILABLE",
                "resume_inspection": "READY",
                "resume_execution": "UNAVAILABLE",
                "retry_inspection": "READY",
                "retry_execution": "UNAVAILABLE",
                "recovery": "READY",
                "basic_wav_validation": "READY",
                "full_audio_validation": "DEGRADED",
                "wav_output": "UNAVAILABLE",
                "mp3_output": "UNAVAILABLE",
                "local_api": "READY",
                "generate_ui": "DEGRADED",
            },
            "supports": [
                "request_validation",
                "source_snapshot",
                "text_structure",
                "no_loss_reconstruction",
                "frozen_plan_guard",
                "plan_manifest",
                "artifact_lifecycle_foundation",
                "resume_inspection",
                "retry_inspection",
                "resume_execution_orchestration",
                "retry_execution_orchestration",
                "recovery_inspection",
                "job_queue_prepare",
                "basic_wav_validation",
            ],
            "blocked_actions": [
                "real_inference",
                "engine_synthesis",
                "resume_execution",
                "retry_execution",
                "wav_output",
                "mp3_output",
            ],
        }

    def safe_generate_session_result(
        self,
        result,
    ):

        if result is None:

            return None

        data = dict(
            result
        )

        request = data.get(
            "request",
            {}
        )

        if request:

            request = dict(
                request
            )

            source = dict(
                request.get(
                    "source",
                    {},
                )
            )

            source.pop(
                "original_path",
                None,
            )

            request[
                "source"
            ] = source

            data[
                "request"
            ] = request

        manifest = data.get(
            "manifest",
        )

        if manifest:

            data[
                "manifest"
            ] = self.safe_generate_manifest(
                manifest
            )

        return data

    def safe_generate_manifest(
        self,
        manifest,
    ):

        if manifest is None:

            return None

        data = dict(
            manifest
        )

        source = dict(
            data.get(
                "source",
                {},
            )
        )

        source.pop(
            "original_path",
            None,
        )

        data[
            "source"
        ] = source

        data[
            "artifacts"
        ] = [
            {
                "kind": item.get(
                    "kind",
                    "",
                ),
                "path_ref": item.get(
                    "kind",
                    "",
                ),
            }
            for item in data.get(
                "artifacts",
                []
            )
        ]

        data[
            "artifact_records"
        ] = self.safe_generate_artifacts(
            {
                "items": data.get(
                    "artifact_records",
                    [],
                )
            }
        )[
            "items"
        ]

        return data

    def safe_artifact(
        self,
        artifact,
    ):

        data = dict(
            artifact
        )

        for key in [
            "planned_path",
            "temp_path",
            "final_path",
        ]:

            value = data.get(
                key,
                "",
            )

            data[
                key
            ] = {
                "available": bool(
                    value
                ),
                "path_ref": key,
            }

        return data

    def safe_generate_artifacts(
        self,
        result,
    ):

        if result is None:

            return None

        return {
            "items": [
                self.safe_artifact(
                    item
                )
                for item in result.get(
                    "items",
                    [],
                )
            ]
        }

    def generate_plan_section(
        self,
        session_id,
        section,
    ):

        plan = self.resolve_generate_session().get_plan(
            session_id
        )

        if not plan:

            return None

        return {
            "session_id": session_id,
            "items": plan.get(
                section,
                [],
            ),
            "total": len(
                plan.get(
                    section,
                    [],
                )
            ),
            "plan_checksum_sha256": plan.get(
                "plan_checksum_sha256",
                "",
            ),
        }

    def paginate(
        self,
        result,
        body,
    ):

        if result is None:

            return None

        items = result.get(
            "items",
            [],
        )

        offset = max(
            0,
            int(
                body.get(
                    "offset",
                    0,
                )
                or 0
            ),
        )

        limit = min(
            100,
            max(
                1,
                int(
                    body.get(
                        "limit",
                        50,
                    )
                    or 50
                ),
            ),
        )

        return {
            **result,
            "items": items[
                offset: offset
                + limit
            ],
            "offset": offset,
            "limit": limit,
            "total": len(
                items
            ),
        }

    def jobs_list(
        self,
    ):

        queue = self.resolve_job_queue()

        if queue is None:

            return {
                "items": [],
                "message_vi": "Job Queue chưa khởi tạo.",
            }

        return {
            "items": [
                job.safe_summary()
                for job in queue.list_jobs()
            ]
        }

    def queue_detail(
        self,
    ):

        queue = self.resolve_job_queue()

        if queue is None:

            return {
                "counts": {},
                "items": [],
            }

        return {
            "counts": queue.queue_counts(),
            "items": [
                job.safe_summary()
                for job in queue.list_jobs()
                if job.state
                in {
                    "queued",
                    "waiting_dependency",
                    "waiting_resource",
                    "running",
                    "paused",
                    "retry_wait",
                }
            ],
        }

    def resources_summary(
        self,
    ):

        monitor = self.resolve_resource_monitor()

        if monitor is None:

            return {
                "available": False,
                "message_vi": "Resource Manager chưa khởi tạo.",
            }

        data = monitor.summary()

        data["available"] = True

        return data

    def resources_hardware(
        self,
    ):

        monitor = self.resolve_resource_monitor()

        return monitor.hardware() if monitor else {}

    def resources_snapshot(
        self,
    ):

        monitor = self.resolve_resource_monitor()

        return monitor.snapshot() if monitor else {}

    def resources_policy(
        self,
    ):

        monitor = self.resolve_resource_monitor()

        return monitor.policy() if monitor else {}

    def resources_leases(
        self,
    ):

        monitor = self.resolve_resource_monitor()

        return monitor.leases() if monitor else []

    def resources_waiting_jobs(
        self,
    ):

        monitor = self.resolve_resource_monitor()

        return monitor.waiting_jobs() if monitor else []

    def job_detail(
        self,
        job_id,
    ):

        queue = self.resolve_job_queue()

        if queue is None:

            return None

        job = queue.get(
            job_id
        )

        if not job:

            return None

        return job.safe_summary()

    def job_logs(
        self,
        job_id,
    ):

        queue = self.resolve_job_queue()

        log_service = self.resolve_job_log()

        if queue is None or log_service is None:

            return None

        job = queue.get(
            job_id
        )

        if not job:

            return None

        return {
            "job_id": job.job_id,
            "lines": log_service.tail(
                job,
                lines=100,
            ),
        }

    def safe_project(
        self,
        project,
        include_details=False,
    ):

        data = {
            "project_id": project.id,
            "display_name": project.display_name,
            "status": project.config.status,
            "archive_state": project.config.archive_state,
            "health_state": project.config.health_state,
            "last_opened_at": project.config.last_opened_at,
            "favorite": project.config.favorite,
        }

        if include_details:

            data.update(
                {
                    "description": project.config.description,
                    "schema_version": project.config.schema_version,
                    "created_at": project.config.created_at,
                    "updated_at": project.config.updated_at,
                    "active_voice_id": project.config.active_voice_id,
                    "active_style_profile_id": project.config.active_style_profile_id,
                    "warnings": project.config.validation_messages,
                }
            )

        return data

    def style_profile_list(
        self,
    ):

        return {
            "items": [
                self.safe_style_profile(
                    profile
                )
                for profile in self.style_profiles.list_profiles()
            ],
        }

    def style_profile_detail(
        self,
        style_profile_id,
    ):

        try:

            profile = self.style_profiles.get_profile(
                style_profile_id
            )

        except Exception:

            return None

        return self.safe_style_profile(
            profile,
            include_summary=True,
        )

    def safe_style_profile(
        self,
        profile,
        include_summary=False,
    ):

        data = {
            "style_profile_id": profile.style_profile_id,
            "display_name": profile.display_name,
            "description": profile.description,
            "language": profile.language,
            "status": profile.status,
            "source_type": profile.source_type,
            "capabilities": profile.capabilities,
            "default_tags": profile.default_tags,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at,
        }

        if include_summary:

            data["source_summary"] = profile.source_summary

            data["extraction_summary"] = profile.extraction_summary

            data["portability"] = profile.portability

        return data

    def read_json(
        self,
        request,
    ):

        length = int(
            request.headers.get(
                "Content-Length",
                "0",
            )
            or 0
        )

        if length <= 0:

            return {}

        if length > 1024 * 1024:

            raise ValueError(
                "payload_too_large"
            )

        raw = request.rfile.read(
            length
        )

        return json.loads(
            raw.decode(
                "utf-8"
            )
            or "{}"
        )

    def write_json(
        self,
        request,
        status_code,
        body,
    ):

        payload = json.dumps(
            body,
            ensure_ascii=False,
        ).encode(
            "utf-8"
        )

        request.send_response(
            status_code
        )

        request.send_header(
            "Content-Type",
            "application/json; charset=utf-8",
        )

        request.send_header(
            "Content-Length",
            str(
                len(
                    payload
                )
            ),
        )

        request.end_headers()

        request.wfile.write(
            payload
        )

    def response(
        self,
        body,
        status_code=200,
    ):

        return {
            "status_code": status_code,
            "body": body,
        }

    def response_or_404(
        self,
        body,
        code,
    ):

        if body is None:

            return self.response(
                {
                    "error": code,
                    "message_vi": "Không tìm thấy dữ liệu yêu cầu.",
                },
                status_code=404,
            )

        return self.response(
            body
        )

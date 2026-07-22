from models.feature_readiness import (
    STATUS_AVAILABLE,
    STATUS_BLOCKED,
    STATUS_DEGRADED,
    FeatureReadiness,
)
from services.runtime_environment_manager import RuntimeEnvironmentManager


class FeatureReadinessService:

    def __init__(
        self,
        environment=None,
    ):

        self.environment = (
            environment
            or RuntimeEnvironmentManager()
        )

    def all(
        self,
    ):

        status = self.environment.full_status()

        return [
            self.app_shell(
                status
            ),
            self.simple_available(
                "project_management",
                "Quản lý Project",
            ),
            self.simple_available(
                "project_registry",
                "Project Registry",
            ),
            self.simple_available(
                "project_create",
                "Tạo Project",
            ),
            self.simple_available(
                "project_open",
                "Mở Project",
            ),
            self.simple_available(
                "project_close",
                "Đóng Project",
            ),
            self.simple_available(
                "project_switch",
                "Chuyển Project",
            ),
            self.simple_available(
                "project_recent",
                "Project gần đây",
            ),
            self.simple_available(
                "project_rename",
                "Đổi tên Project",
            ),
            self.simple_available(
                "project_duplicate",
                "Nhân bản Project",
            ),
            self.simple_available(
                "project_archive",
                "Archive Project",
            ),
            self.simple_available(
                "project_restore_archive",
                "Khôi phục Archive Project",
            ),
            self.simple_available(
                "project_export",
                "Export Project",
            ),
            self.simple_available(
                "project_import",
                "Import Project",
            ),
            self.simple_available(
                "project_backup",
                "Backup Project",
            ),
            self.simple_available(
                "project_restore",
                "Restore Project",
            ),
            self.simple_available(
                "project_validation",
                "Project Validation",
            ),
            self.simple_available(
                "project_repair",
                "Project Repair",
            ),
            self.simple_available(
                "workspace_resolution",
                "Workspace Resolution",
            ),
            self.simple_available(
                "import_txt",
                "Nhập TXT",
            ),
            self.import_docx(
                status
            ),
            self.simple_available(
                "dataset_scan",
                "Quét Dataset",
            ),
            self.simple_available(
                "dataset_health",
                "Dataset Health",
            ),
            self.simple_available(
                "dataset_repair",
                "Dataset Repair",
            ),
            self.simple_available(
                "dataset_review",
                "Dataset Review",
            ),
            self.style_profile_management(),
            self.style_profile_extraction(),
            self.style_profile_import_export(),
            self.style_profile_voice_link(),
            self.style_profile_generation_usage(),
            self.training_reference_selection(),
            self.speaker_reference_audio(),
            self.style_profile_selection(),
            self.style_profile_creation_request(),
            self.audio_text_pair_validation(),
            self.training_reference_resolution(),
            self.reference_vault(),
            self.reference_registry(),
            self.reference_asset_import(),
            self.reference_asset_integrity(),
            self.reference_asset_deduplication(),
            self.audio_text_pair_persistence(),
            self.speaker_reference_persistence(),
            self.training_reference_persistence(),
            self.style_source_persistence(),
            self.stable_segment_identity(),
            self.reference_backup(),
            self.reference_restore(),
            self.reference_export(),
            self.reference_import(),
            self.reference_relink(),
            self.reference_repair(),
            self.job_model(),
            self.job_repository(),
            self.persistent_queue(),
            self.job_runner(),
            self.job_progress(),
            self.job_eta(),
            self.job_logs(),
            self.job_pause(),
            self.job_resume(),
            self.job_cancel(),
            self.job_retry(),
            self.job_priority(),
            self.job_dependencies(),
            self.job_recovery(),
            self.queue_ui(),
            self.dashboard_job_summary(),
            self.resource_models(),
            self.hardware_detection(),
            self.resource_snapshots(),
            self.resource_requirements(),
            self.resource_decisions(),
            self.resource_policies(),
            self.resource_leases(),
            self.resource_queue_scheduling(),
            self.resource_monitor_ui(),
            self.resource_local_api(),
            self.generate_request_foundation(),
            self.generate_session_persistence(),
            self.generate_source_snapshot(),
            self.generate_normalization(),
            self.generate_structure_detection(),
            self.generate_splitter(),
            self.generate_frozen_plan(),
            self.generate_plan_manifest(),
            self.generate_artifact_lifecycle(),
            self.generate_preview_plan(),
            self.generate_preview_audio(),
            self.generate_resume_inspection(),
            self.generate_resume_execution(),
            self.generate_retry_inspection(),
            self.generate_retry_execution(),
            self.generate_recovery(),
            self.generate_basic_wav_validation(),
            self.generate_full_audio_validation(),
            self.generate_wav_output(),
            self.generate_mp3_output(),
            self.generate_job_queue_integration(),
            self.generate_resource_integration(),
            self.generate_local_api_foundation(),
            self.generate_ui_foundation(),
            self.voice_rename(),
            self.style_profile_rename(),
            self.scrollable_training_page(),
            self.responsive_window_resize(),
            self.alignment(
                status
            ),
            self.training(
                status
            ),
            self.generation(
                status
            ),
            self.local_api(
                status
            ),
            self.testing(
                status
            ),
            self.runtime_validation(
                status
            ),
        ]

    def summary(
        self,
    ):

        items = [
            item.to_dict()
            for item in self.all()
        ]

        return {
            "items": items,
            "limited_mode": any(
                item[
                    "degraded"
                ]
                for item in items
            )
            or any(
                item[
                    "blocked"
                ]
                for item in items
            ),
            "blocking_features": [
                item[
                    "feature_id"
                ]
                for item in items
                if item[
                    "blocked"
                ]
            ],
        }

    def by_id(
        self,
        feature_id,
    ):

        for item in self.all():

            if item.feature_id == feature_id:

                return item

        return FeatureReadiness(
            feature_id=feature_id,
            name_vi=feature_id,
            status=STATUS_BLOCKED,
            missing_components=[
                "feature_unknown",
            ],
            remediation=[
                "Tính năng chưa được đăng ký trong FeatureReadinessService.",
            ],
        )

    def simple_available(
        self,
        feature_id,
        name_vi,
    ):

        return FeatureReadiness(
            feature_id=feature_id,
            name_vi=name_vi,
            status=STATUS_AVAILABLE,
            available=True,
            blocked=False,
        )

    def app_shell(
        self,
        status,
    ):

        app = status[
            "app"
        ]

        missing = []

        if not app.get(
            "ready_for_ui"
        ):

            missing.append(
                "PySide6"
            )

        return self.feature(
            feature_id="app_shell",
            name_vi="Giao diện chính",
            required=[
                "Python",
                "PySide6",
            ],
            missing=missing,
            remediation=[
                "Cài dependency ứng dụng: python -m pip install -r requirements.txt",
            ],
            details=app,
        )

    def import_docx(
        self,
        status,
    ):

        app = status[
            "app"
        ]

        missing = []

        if not app[
            "packages"
        ].get(
            "docx",
            False,
        ):

            missing.append(
                "python-docx"
            )

        return self.feature(
            "import_docx",
            "Nhập DOCX",
            [
                "python-docx",
            ],
            missing,
            [
                "Cài python-docx hoặc chỉ dùng TXT.",
            ],
            app,
            optional=True,
        )

    def alignment(
        self,
        status,
    ):

        missing = []

        if not status[
            "alignment"
        ].get(
            "faster_whisper",
            False,
        ):

            missing.append(
                "faster-whisper"
            )

        if not status[
            "ffmpeg"
        ].get(
            "available",
            False,
        ):

            missing.append(
                "ffmpeg"
            )

        return self.feature(
            "alignment",
            "Alignment",
            [
                "faster-whisper",
                "ffmpeg",
            ],
            missing,
            [
                "Cài faster-whisper và FFmpeg trước khi chạy Alignment.",
            ],
            status,
            optional=True,
        )

    def training(
        self,
        status,
    ):

        missing = []

        if not status[
            "voice_runtime"
        ].get(
            "ready",
            False,
        ):

            missing.append(
                "GPT-SoVITS Runtime"
            )

        return self.feature(
            "training",
            "Training",
            [
                "GPT-SoVITS Runtime",
                "metadata.list hợp lệ",
            ],
            missing,
            [
                "Cấu hình Runtime Profile và chạy train validation trước.",
            ],
            status[
                "voice_runtime"
            ],
            optional=True,
        )

    def generation(
        self,
        status,
    ):

        missing = []

        if not status[
            "voice_runtime"
        ].get(
            "ready",
            False,
        ):

            missing.append(
                "GPT-SoVITS Runtime"
            )

        if not status[
            "ffmpeg"
        ].get(
            "available",
            False,
        ):

            missing.append(
                "ffmpeg"
            )

        return self.feature(
            "generation",
            "Tạo Audio",
            [
                "Voice model",
                "Runtime",
                "FFmpeg",
            ],
            missing,
            [
                "Cấu hình Runtime, Voice model và FFmpeg trước khi Generate.",
            ],
            status,
            optional=True,
        )

    def local_api(
        self,
        status,
    ):

        return FeatureReadiness(
            feature_id="local_api",
            name_vi="API nội bộ",
            status=STATUS_AVAILABLE,
            available=True,
            blocked=False,
            required_components=[
                "Python stdlib http.server",
            ],
            remediation=[
                "Bật API trong Settings -> API & Tích hợp khi cần.",
            ],
            settings_target="settings.local_api",
            technical_details={
                "framework": "stdlib_http_server",
                "auto_start": False,
            },
        )

    def testing(
        self,
        status,
    ):

        app = status[
            "app"
        ]

        missing = []

        if not app.get(
            "ready_for_tests"
        ):

            missing.append(
                "pytest"
            )

        return self.feature(
            "testing",
            "Bộ kiểm tra phát triển",
            [
                "pytest",
            ],
            missing,
            [
                "Cài pytest nếu cần chạy test bằng pytest.",
            ],
            app,
            optional=True,
        )

    def runtime_validation(
        self,
        status,
    ):

        return self.feature(
            "runtime_validation",
            "Kiểm tra Runtime",
            [
                "RuntimeEnvironmentManager",
            ],
            [],
            [],
            status,
        )

    def style_profile_management(
        self,
    ):

        return FeatureReadiness(
            feature_id="style_profile_management",
            name_vi="Quản lý Phong cách đọc",
            status=STATUS_AVAILABLE,
            available=True,
            blocked=False,
            required_components=[
                "StyleProfileRepository",
                "StyleProfileService",
            ],
            remediation=[],
            settings_target="settings.style_profiles",
            technical_details={
                "schema": "style_profile_v1",
            },
        )

    def style_profile_extraction(
        self,
    ):

        return FeatureReadiness(
            feature_id="style_profile_extraction",
            name_vi="Trích xuất Voice DNA",
            status=STATUS_BLOCKED,
            available=False,
            degraded=False,
            blocked=True,
            required_components=[
                "prosody_analyzer",
                "alignment_features",
                "reference_index_builder",
            ],
            missing_components=[
                "prosody_analyzer",
            ],
            remediation=[
                "Sprint này chỉ chuẩn hóa schema và trạng thái. Chưa đánh dấu extraction hoàn tất khi chưa có analyzer thật.",
            ],
            settings_target="style_profiles.extraction",
            technical_details={
                "current_state": "placeholder_contract_only",
            },
        )

    def style_profile_import_export(
        self,
    ):

        return FeatureReadiness(
            feature_id="style_profile_import_export",
            name_vi="Backup / Import / Export Style Profile",
            status=STATUS_AVAILABLE,
            available=True,
            blocked=False,
            required_components=[
                ".avstyle package",
                "checksum validation",
            ],
            remediation=[],
            settings_target="style_profiles.backup_restore",
            technical_details={
                "default_export": "analysis_data_only",
            },
        )

    def style_profile_voice_link(
        self,
    ):

        return FeatureReadiness(
            feature_id="style_profile_voice_link",
            name_vi="Liên kết Voice với Phong cách đọc",
            status=STATUS_AVAILABLE,
            available=True,
            blocked=False,
            required_components=[
                "VoiceConfig.reading_style",
                "Variant style fields",
            ],
            remediation=[],
            settings_target="voice.reading_style",
            technical_details={
                "variant_scope": "migration_safe",
            },
        )

    def style_profile_generation_usage(
        self,
    ):

        return FeatureReadiness(
            feature_id="style_profile_generation_usage",
            name_vi="Dùng Phong cách đọc khi Generate",
            status=STATUS_DEGRADED,
            available=False,
            degraded=True,
            blocked=False,
            required_components=[
                "GenerateRequest style fields",
                "Engine Adapter style support",
            ],
            missing_components=[
                "engine_style_profile_application",
            ],
            remediation=[
                "GenerateRequest đã có style_profile_id/style_strength/style_mode, nhưng engine hiện tại chưa áp dụng Style Profile thật.",
            ],
            settings_target="generate.style_profile",
            technical_details={
                "validation_policy": "do_not_silently_ignore",
            },
        )

    def training_reference_selection(
        self,
    ):

        return self.simple_available(
            "training_reference_selection",
            "Chọn dữ liệu tham chiếu Training",
        )

    def speaker_reference_audio(
        self,
    ):

        return self.simple_available(
            "speaker_reference_audio",
            "Âm thanh tham chiếu clone giọng",
        )

    def style_profile_selection(
        self,
    ):

        return self.simple_available(
            "style_profile_selection",
            "Chọn Phong cách đọc",
        )

    def style_profile_creation_request(
        self,
    ):

        return FeatureReadiness(
            feature_id="style_profile_creation_request",
            name_vi="Tạo yêu cầu Phong cách đọc",
            status=STATUS_DEGRADED,
            available=True,
            degraded=True,
            blocked=False,
            required_components=[
                "StyleProfileService",
                "StyleProfileExtractionService",
            ],
            missing_components=[
                "prosody_analyzer",
            ],
            remediation=[
                "Có thể tạo draft/pending request; chưa tạo Voice DNA thật khi analyzer chưa sẵn sàng.",
            ],
            technical_details={
                "analyzer_ready": False,
            },
        )

    def audio_text_pair_validation(
        self,
    ):

        return self.simple_available(
            "audio_text_pair_validation",
            "Kiểm tra cặp Audio + Text",
        )

    def training_reference_resolution(
        self,
    ):

        return self.simple_available(
            "training_reference_resolution",
            "Resolve dữ liệu tham chiếu Training",
        )

    def reference_vault(
        self,
    ):

        return self.simple_available(
            "reference_vault",
            "Kho dữ liệu tham chiếu",
        )

    def reference_registry(
        self,
    ):

        return self.simple_available(
            "reference_registry",
            "Reference Registry",
        )

    def reference_asset_import(
        self,
    ):

        return self.simple_available(
            "reference_asset_import",
            "Import reference vào Vault",
        )

    def reference_asset_integrity(
        self,
    ):

        return self.simple_available(
            "reference_asset_integrity",
            "Kiểm tra checksum reference",
        )

    def reference_asset_deduplication(
        self,
    ):

        return self.simple_available(
            "reference_asset_deduplication",
            "Chống copy trùng reference",
        )

    def audio_text_pair_persistence(
        self,
    ):

        return self.simple_available(
            "audio_text_pair_persistence",
            "Lưu manifest cặp Audio + Text",
        )

    def speaker_reference_persistence(
        self,
    ):

        return self.simple_available(
            "speaker_reference_persistence",
            "Speaker Reference bền vững",
        )

    def training_reference_persistence(
        self,
    ):

        return self.simple_available(
            "training_reference_persistence",
            "Training Reference bền vững",
        )

    def style_source_persistence(
        self,
    ):

        return self.simple_available(
            "style_source_persistence",
            "Lưu source draft Style Profile",
        )

    def stable_segment_identity(
        self,
    ):

        return self.simple_available(
            "stable_segment_identity",
            "Stable ID cho segment",
        )

    def reference_backup(
        self,
    ):

        return self.simple_available(
            "reference_backup",
            "Backup reference",
        )

    def reference_restore(
        self,
    ):

        return self.simple_available(
            "reference_restore",
            "Restore reference",
        )

    def reference_export(
        self,
    ):

        return self.simple_available(
            "reference_export",
            "Export reference",
        )

    def reference_import(
        self,
    ):

        return self.simple_available(
            "reference_import",
            "Import reference",
        )

    def reference_relink(
        self,
    ):

        return self.simple_available(
            "reference_relink",
            "Relink external reference",
        )

    def reference_repair(
        self,
    ):

        return self.simple_available(
            "reference_repair",
            "Repair reference an toàn",
        )

    def voice_rename(
        self,
    ):

        return self.simple_available(
            "voice_rename",
            "Đổi tên Voice",
        )

    def job_model(
        self,
    ):

        return self.simple_available(
            "job_model",
            "Job model",
        )

    def job_repository(
        self,
    ):

        return self.simple_available(
            "job_repository",
            "Job repository",
        )

    def persistent_queue(
        self,
    ):

        return self.simple_available(
            "persistent_queue",
            "Hàng đợi bền vững",
        )

    def job_runner(
        self,
    ):

        return self.simple_available(
            "job_runner",
            "Job runner",
        )

    def job_progress(
        self,
    ):

        return self.simple_available(
            "job_progress",
            "Tiến độ Job",
        )

    def job_eta(
        self,
    ):

        return self.simple_available(
            "job_eta",
            "ETA Job",
        )

    def job_logs(
        self,
    ):

        return self.simple_available(
            "job_logs",
            "Log Job",
        )

    def job_pause(
        self,
    ):

        return self.simple_available(
            "job_pause",
            "Pause Job",
        )

    def job_resume(
        self,
    ):

        return self.simple_available(
            "job_resume",
            "Resume Job",
        )

    def job_cancel(
        self,
    ):

        return self.simple_available(
            "job_cancel",
            "Cancel Job",
        )

    def job_retry(
        self,
    ):

        return self.simple_available(
            "job_retry",
            "Retry Job",
        )

    def job_priority(
        self,
    ):

        return self.simple_available(
            "job_priority",
            "Priority Job",
        )

    def job_dependencies(
        self,
    ):

        return self.simple_available(
            "job_dependencies",
            "Dependency Job",
        )

    def job_recovery(
        self,
    ):

        return self.simple_available(
            "job_recovery",
            "Recovery Job",
        )

    def queue_ui(
        self,
    ):

        return self.simple_available(
            "queue_ui",
            "Giao diện Hàng đợi",
        )

    def dashboard_job_summary(
        self,
    ):

        return self.simple_available(
            "dashboard_job_summary",
            "Dashboard Job Summary",
        )

    def resource_models(
        self,
    ):

        return self.simple_available(
            "resource_models",
            "Resource models",
        )

    def hardware_detection(
        self,
    ):

        return self.simple_available(
            "hardware_detection",
            "Phát hiện phần cứng",
        )

    def resource_snapshots(
        self,
    ):

        return self.simple_available(
            "resource_snapshots",
            "Resource snapshots",
        )

    def resource_requirements(
        self,
    ):

        return self.simple_available(
            "resource_requirements",
            "Resource requirements",
        )

    def resource_decisions(
        self,
    ):

        return self.simple_available(
            "resource_decisions",
            "Resource decisions",
        )

    def resource_policies(
        self,
    ):

        return self.simple_available(
            "resource_policies",
            "Resource policies",
        )

    def resource_leases(
        self,
    ):

        return self.simple_available(
            "resource_leases",
            "Resource leases",
        )

    def resource_queue_scheduling(
        self,
    ):

        return self.simple_available(
            "resource_queue_scheduling",
            "Resource-aware queue scheduling",
        )

    def resource_monitor_ui(
        self,
    ):

        return self.simple_available(
            "resource_monitor_ui",
            "Resource Monitor UI",
        )

    def resource_local_api(
        self,
    ):

        return self.simple_available(
            "resource_local_api",
            "Resource Local API",
        )

    def generate_request_foundation(
        self,
    ):

        return self.simple_available(
            "generate_request_foundation",
            "Generate Request foundation",
        )

    def generate_session_persistence(
        self,
    ):

        return self.simple_available(
            "generate_session_persistence",
            "Generate Session persistence",
        )

    def generate_source_snapshot(
        self,
    ):

        return self.simple_available(
            "generate_source_snapshot",
            "Generate source snapshot",
        )

    def generate_plan_manifest(
        self,
    ):

        return self.simple_available(
            "generate_plan_manifest",
            "Generate Plan / Manifest",
        )

    def generate_normalization(
        self,
    ):

        return self.simple_available(
            "generate_normalization",
            "Generate Text Normalization",
        )

    def generate_structure_detection(
        self,
    ):

        return self.simple_available(
            "generate_structure",
            "Generate Structure Detection",
        )

    def generate_splitter(
        self,
    ):

        return self.simple_available(
            "generate_splitter",
            "Generate Text Splitter",
        )

    def generate_frozen_plan(
        self,
    ):

        return self.simple_available(
            "generate_frozen_plan",
            "Generate Frozen Plan",
        )

    def generate_artifact_lifecycle(
        self,
    ):

        return self.simple_available(
            "generate_artifact_lifecycle",
            "Generate Artifact Lifecycle foundation",
        )

    def generate_preview_plan(
        self,
    ):

        return self.simple_available(
            "generate_preview_plan",
            "Generate Preview Plan",
        )

    def generate_preview_audio(
        self,
    ):

        return FeatureReadiness(
            feature_id="generate_preview_audio",
            name_vi="Generate Preview Audio",
            status=STATUS_DEGRADED,
            available=False,
            degraded=True,
            blocked=True,
            required_components=[
                "generate_unit_production_handler",
                "valid_voice_model",
                "runtime_doctor_ready",
            ],
            missing_components=[
                "valid_voice_model_or_runtime",
            ],
            remediation=[
                "AVS-014.16 chưa triển khai production Generate Unit handler; không tạo audio giả.",
            ],
            settings_target="generate.execution",
            technical_details={
                "truth_status": "DEGRADED",
                "production_handler": True,
            },
        )

    def generate_resume_inspection(
        self,
    ):

        return self.simple_available(
            "generate_resume_inspection",
            "Generate Resume Inspection",
        )

    def generate_resume_execution(
        self,
    ):

        return FeatureReadiness(
            feature_id="generate_resume_execution",
            name_vi="Generate Resume Execution",
            status=STATUS_DEGRADED,
            available=False,
            degraded=True,
            blocked=True,
            required_components=[
                "generate_unit_production_handler",
                "runtime_doctor_ready",
            ],
            missing_components=[
                "runtime_or_voice_not_ready",
            ],
            remediation=[
                "Hiện mới có resume inspection; resume execution cần worker generate_unit thật ở sprint sau.",
            ],
            technical_details={
                "truth_status": "DEGRADED",
                "production_handler": True,
            },
        )

    def generate_retry_inspection(
        self,
    ):

        return self.simple_available(
            "generate_retry_inspection",
            "Generate Retry Inspection",
        )

    def generate_retry_execution(
        self,
    ):

        return FeatureReadiness(
            feature_id="generate_retry_execution",
            name_vi="Generate Retry Execution",
            status=STATUS_DEGRADED,
            available=False,
            degraded=True,
            blocked=True,
            required_components=[
                "generate_unit_production_handler",
                "runtime_doctor_ready",
            ],
            missing_components=[
                "runtime_or_voice_not_ready",
            ],
            remediation=[
                "Hiện mới có retry inspection; retry execution chưa được bật để tránh duplicate/fake output.",
            ],
            technical_details={
                "truth_status": "DEGRADED",
                "production_handler": True,
            },
        )

    def generate_recovery(
        self,
    ):

        return self.simple_available(
            "generate_recovery",
            "Generate Recovery foundation",
        )

    def generate_basic_wav_validation(
        self,
    ):

        return self.simple_available(
            "generate_basic_wav_validation",
            "Generate Basic WAV Validation",
        )

    def generate_full_audio_validation(
        self,
    ):

        return FeatureReadiness(
            feature_id="generate_full_audio_validation",
            name_vi="Generate Full Audio Validation",
            status=STATUS_DEGRADED,
            available=False,
            degraded=True,
            blocked=False,
            required_components=[
                "ffprobe_validation",
                "codec_policy",
                "duration_policy",
            ],
            missing_components=[
                "full_audio_validation_policy",
            ],
            remediation=[
                "AVS-014.16 chỉ có WAV validation cơ bản bằng Python stdlib; full validation cần sprint audio output sau.",
            ],
            technical_details={
                "truth_status": "DEGRADED",
            },
        )

    def generate_wav_output(
        self,
    ):

        return FeatureReadiness(
            feature_id="generate_wav_output",
            name_vi="Generate WAV Output",
            status=STATUS_DEGRADED,
            available=False,
            degraded=True,
            blocked=True,
            required_components=[
                "generate_unit_production_handler",
                "runtime_doctor_ready",
                "valid_voice_model",
            ],
            missing_components=[
                "runtime_or_voice_not_ready",
            ],
            remediation=[
                "WAV output thật chưa bật trong AVS-014.16 foundation.",
            ],
            technical_details={
                "truth_status": "DEGRADED",
                "production_handler": True,
            },
        )

    def generate_mp3_output(
        self,
    ):

        return FeatureReadiness(
            feature_id="generate_mp3_output",
            name_vi="Generate MP3 Output",
            status=STATUS_BLOCKED,
            available=False,
            blocked=True,
            required_components=[
                "generate_unit_production_handler",
                "mp3_export_pipeline",
            ],
            missing_components=[
                "generate_unit_production_handler",
            ],
            remediation=[
                "MP3 output thật chưa bật trong AVS-014.16 foundation.",
            ],
            technical_details={
                "truth_status": "UNAVAILABLE",
            },
        )

    def generate_job_queue_integration(
        self,
    ):

        return self.simple_available(
            "generate_job_queue_integration",
            "Generate Job Queue prepare worker",
        )

    def generate_resource_integration(
        self,
    ):

        return self.simple_available(
            "generate_resource_integration",
            "Generate ResourceRequirement foundation",
        )

    def generate_local_api_foundation(
        self,
    ):

        return self.simple_available(
            "generate_local_api",
            "Generate Local API foundation",
        )

    def generate_ui_foundation(
        self,
    ):

        return FeatureReadiness(
            feature_id="generate_ui",
            name_vi="Generate UI foundation",
            status=STATUS_DEGRADED,
            available=True,
            degraded=True,
            blocked=False,
            required_components=[
                "PySide6",
                "AudioPage",
                "GenerateOptionsPanel",
            ],
            missing_components=[
                "dedicated_session_plan_view_polish",
            ],
            remediation=[
                "UI Generate hien co nen form/panel; session detail chuyen sau khi production execution duoc noi.",
            ],
            technical_details={
                "truth_status": "DEGRADED",
            },
        )

    def style_profile_rename(
        self,
    ):

        return self.simple_available(
            "style_profile_rename",
            "Đổi tên Phong cách đọc",
        )

    def scrollable_training_page(
        self,
    ):

        return self.simple_available(
            "scrollable_training_page",
            "Training Page có scroll",
        )

    def responsive_window_resize(
        self,
    ):

        return self.simple_available(
            "responsive_window_resize",
            "Cửa sổ co giãn responsive",
        )

    def feature(
        self,
        feature_id,
        name_vi,
        required,
        missing,
        remediation,
        details,
        optional=False,
    ):

        if missing:

            status = (
                STATUS_DEGRADED
                if optional
                else STATUS_BLOCKED
            )

        else:

            status = STATUS_AVAILABLE

        return FeatureReadiness(
            feature_id=feature_id,
            name_vi=name_vi,
            status=status,
            available=not missing,
            degraded=bool(
                missing
                and optional
            ),
            blocked=bool(
                missing
                and not optional
            ),
            required_components=required,
            missing_components=missing,
            remediation=remediation if missing else [],
            settings_target="settings.runtime",
            technical_details=details,
        )

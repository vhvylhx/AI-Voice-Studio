class AppContextMeta(type):

    def __getattr__(
        cls,
        name,
    ):

        if name in cls._context_names:

            cls.initialize()

            return getattr(
                cls,
                name,
            )

        raise AttributeError(
            name
        )


class AppContext(metaclass=AppContextMeta):

    #
    # Services
    #

    _initialized = False

    _context_names = {
        "project_service",
        "voice_service",
        "queue_service",
        "job_repository",
        "job_queue_service",
        "job_runner",
        "job_handler_registry",
        "job_log_service",
        "job_recovery_service",
        "hardware_detection_service",
        "resource_snapshot_service",
        "resource_policy_service",
        "resource_decision_service",
        "resource_lease_manager",
        "resource_monitor_service",
        "thread_budget_capability_registry",
        "thread_budget_service",
        "generate_repository",
        "generate_session_service",
        "generate_text_structure_service",
        "log_service",
        "dataset_service",
        "training_service",
        "runtime_service",
        "style_profile_service",
        "training_reference_service",
        "reference_vault_service",
        "reference_registry_service",
        "project_registry",
        "project_validation_service",
        "project_backup_service",
        "project_package_service",
        "current_project",
        "current_voice",
        "engine_manager",
    }

    @classmethod
    def initialize(cls):

        if cls._initialized:

            return

        from services.project_service import ProjectService
        from services.project_backup_service import ProjectBackupService
        from services.project_package_service import ProjectPackageService
        from services.project_registry_service import ProjectRegistryService
        from services.project_validation_service import ProjectValidationService
        from services.voice_service import VoiceService

        from services.current_project_service import CurrentProjectService
        from services.current_voice_service import CurrentVoiceService

        from services.queue_service import QueueService
        from services.job_handler_registry import JobHandlerRegistry
        from services.job_log_service import JobLogService
        from services.job_queue_service import JobQueueService
        from services.job_recovery_service import JobRecoveryService
        from services.job_repository import JobRepository
        from services.job_runner import JobRunner
        from services.hardware_detection_service import HardwareDetectionService
        from services.resource_decision_service import ResourceDecisionService
        from services.resource_lease_manager import ResourceLeaseManager
        from services.resource_monitor_service import ResourceMonitorService
        from services.resource_policy_service import ResourcePolicyService
        from services.resource_snapshot_service import ResourceSnapshotService
        from services.thread_budget_capability_registry import (
            build_default_thread_budget_registry,
        )
        from services.thread_budget_service import ThreadBudgetService
        from services.generate_repository import GenerateRepository
        from services.generate_session_service import GenerateSessionService
        from services.generate_text_structure_service import (
            GenerateTextStructureService,
        )
        from services.log_service import LogService
        from services.dataset_service import DatasetService
        from services.training_service import TrainingService
        from services.runtime_service import RuntimeService
        from services.style_profile_service import StyleProfileService
        from services.training_reference_service import TrainingReferenceService
        from services.reference_registry_service import ReferenceRegistryService
        from services.reference_vault_service import ReferenceVaultService

        from core.engine_manager import EngineManager

        from engines.mock_engine import MockEngine
        from engines.gpt_sovits_engine import GPTSoVITSEngine
        from engines.vieneu_tts_engine import VieNeuTTSEngine

        cls.project_service = ProjectService()

        cls.project_registry = ProjectRegistryService(
            cls.project_service.root
        )

        cls.project_validation_service = ProjectValidationService()

        cls.project_backup_service = ProjectBackupService()

        cls.project_package_service = ProjectPackageService()

        cls.voice_service = VoiceService()

        cls.queue_service = QueueService()

        cls.job_repository = JobRepository()

        cls.job_handler_registry = JobHandlerRegistry()

        cls.job_log_service = JobLogService(
            cls.job_repository
        )

        cls.hardware_detection_service = HardwareDetectionService()

        cls.resource_policy_service = ResourcePolicyService()

        cls.resource_snapshot_service = ResourceSnapshotService(
            hardware_detection=cls.hardware_detection_service,
            policy_service=cls.resource_policy_service,
        )

        cls.resource_decision_service = ResourceDecisionService(
            snapshot_service=cls.resource_snapshot_service,
            policy_service=cls.resource_policy_service,
        )

        cls.resource_lease_manager = ResourceLeaseManager(
            root=cls.job_repository.root / "resources",
            policy_service=cls.resource_policy_service,
        )

        cls.job_queue_service = JobQueueService(
            cls.job_repository,
            handler_registry=cls.job_handler_registry,
            resource_decision_service=cls.resource_decision_service,
            resource_lease_manager=cls.resource_lease_manager,
        )

        cls.job_recovery_service = JobRecoveryService(
            cls.job_repository
        )

        cls.job_recovery_service.recover_startup()

        cls.resource_lease_manager.cleanup_stale()

        cls.resource_monitor_service = ResourceMonitorService(
            hardware_detection=cls.hardware_detection_service,
            snapshot_service=cls.resource_snapshot_service,
            policy_service=cls.resource_policy_service,
            lease_manager=cls.resource_lease_manager,
            job_queue_service=cls.job_queue_service,
        )

        cls.generate_repository = GenerateRepository()

        cls.generate_text_structure_service = GenerateTextStructureService()

        cls.generate_session_service = GenerateSessionService(
            repository=cls.generate_repository,
            text_structure=cls.generate_text_structure_service,
        )

        cls.log_service = LogService()

        cls.dataset_service = DatasetService()

        cls.training_service = TrainingService()

        cls.runtime_service = RuntimeService()

        cls.style_profile_service = StyleProfileService(
            voice_service=cls.voice_service
        )

        cls.reference_registry_service = ReferenceRegistryService()

        cls.reference_vault_service = ReferenceVaultService(
            registry_service=cls.reference_registry_service
        )

        cls.training_reference_service = TrainingReferenceService(
            style_profile_service=cls.style_profile_service,
            vault_service=cls.reference_vault_service,
        )

        cls.current_project = CurrentProjectService

        cls.current_voice = CurrentVoiceService

        cls.engine_manager = EngineManager()

        cls.engine_manager.register(
            MockEngine()
        )

        vieneu = VieNeuTTSEngine()

        vieneu.initialize()

        cls.engine_manager.register(
            vieneu
        )

        gpt = GPTSoVITSEngine()

        gpt.initialize()

        cls.engine_manager.register(
            gpt
        )

        cls.thread_budget_capability_registry = (
            build_default_thread_budget_registry(
                cls.engine_manager
            )
        )

        cls.thread_budget_service = ThreadBudgetService(
            policy_service=cls.resource_policy_service,
            capability_registry=cls.thread_budget_capability_registry,
        )

        cls.job_runner = JobRunner(
            repository=cls.job_repository,
            queue_service=cls.job_queue_service,
            handler_registry=cls.job_handler_registry,
            log_service=cls.job_log_service,
            app_context=cls,
            thread_budget_service=cls.thread_budget_service,
        )

        cls._initialized = True

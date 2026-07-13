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
        "log_service",
        "dataset_service",
        "training_service",
        "runtime_service",
        "current_project",
        "current_voice",
        "engine_manager",
    }

    @classmethod
    def initialize(cls):

        if cls._initialized:

            return

        from services.project_service import ProjectService
        from services.voice_service import VoiceService

        from services.current_project_service import CurrentProjectService
        from services.current_voice_service import CurrentVoiceService

        from services.queue_service import QueueService
        from services.log_service import LogService
        from services.dataset_service import DatasetService
        from services.training_service import TrainingService
        from services.runtime_service import RuntimeService

        from core.engine_manager import EngineManager

        from engines.mock_engine import MockEngine
        from engines.gpt_sovits_engine import GPTSoVITSEngine

        cls.project_service = ProjectService()

        cls.voice_service = VoiceService()

        cls.queue_service = QueueService()

        cls.log_service = LogService()

        cls.dataset_service = DatasetService()

        cls.training_service = TrainingService()

        cls.runtime_service = RuntimeService()

        cls.current_project = CurrentProjectService

        cls.current_voice = CurrentVoiceService

        cls.engine_manager = EngineManager()

        cls.engine_manager.register(
            MockEngine()
        )

        gpt = GPTSoVITSEngine()

        gpt.initialize()

        cls.engine_manager.register(
            gpt
        )

        cls._initialized = True

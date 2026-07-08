from services.project_service import ProjectService
from services.voice_service import VoiceService

from services.current_project_service import CurrentProjectService
from services.current_voice_service import CurrentVoiceService

from services.queue_service import QueueService

from engines.manager import EngineManager
from engines.mock_engine import MockEngine
from engines.xtts_engine import XTTSEngine


class AppContext:

    project_service = ProjectService()

    voice_service = VoiceService()

    queue_service = QueueService()

    current_project = CurrentProjectService

    current_voice = CurrentVoiceService

    engine_manager = EngineManager()


AppContext.engine_manager.register(
    MockEngine()
)

xtts = XTTSEngine()

xtts.initialize()

AppContext.engine_manager.register(
    xtts
)
from src.models.dashboard_model import DashboardModel
from src.services.workspace_service import WorkspaceService


class DashboardService:

    def __init__(self):
        self.workspace = WorkspaceService()

    def load(self):

        result = self.workspace.scan()

        model = DashboardModel()

        model.voice_count = result["voices"]
        model.audio_count = result["audio"]
        model.docx_count = result["docx"]
        model.txt_count = result["txt"]

        return model
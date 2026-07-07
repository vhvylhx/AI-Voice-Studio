from services.workspace_service import WorkspaceService


class DatasetService:

    def __init__(self):

        self.workspace = WorkspaceService()

    def load(self):

        return self.workspace.load()
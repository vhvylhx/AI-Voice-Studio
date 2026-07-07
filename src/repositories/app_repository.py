from core import AppPaths

from .base_repository import BaseRepository


class AppRepository(BaseRepository):

    def __init__(self):

        super().__init__(
            AppPaths.PROJECTS / "current_project.json"
        )

    def get_current_project(self):

        data = self.load()

        return data.get("project")

    def set_current_project(
        self,
        name
    ):

        self.save({
            "project": name
        })
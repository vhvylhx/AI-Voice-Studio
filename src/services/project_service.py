from src.core import App
from src.repositories import project_repository

from .base_service import BaseService


class ProjectService(BaseService):

    def __init__(self):
        super().__init__(App)

    def load(self):
        return project_repository.load(
            {
                "name": "",
                "voice": "",
                "engine": "",
                "model": "",
                "output": "",
                "queue": []
            }
        )

    def save(self, data):
        project_repository.save(data)
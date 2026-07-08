import json
from pathlib import Path

from models.project_config import ProjectConfig
from models.project_model import ProjectModel


class ProjectService:

    def __init__(self):

        self.root = Path("projects")

        self.root.mkdir(
            parents=True,
            exist_ok=True
        )

    def create(self, name: str):

        project = self.root / name

        project.mkdir(
            parents=True,
            exist_ok=True
        )

        (project / "text").mkdir(exist_ok=True)
        (project / "audio").mkdir(exist_ok=True)
        (project / "voices").mkdir(exist_ok=True)
        (project / "export").mkdir(exist_ok=True)
        (project / "cache").mkdir(exist_ok=True)
        (project / "logs").mkdir(exist_ok=True)

        config = ProjectConfig()

        with open(
            project / "project.json",
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                config.__dict__,
                f,
                indent=4,
                ensure_ascii=False
            )

        return self.load(name)

    def load(self, name: str):

        project = self.root / name

        with open(
            project / "project.json",
            "r",
            encoding="utf-8"
        ) as f:

            config = ProjectConfig(
                **json.load(f)
            )

        return ProjectModel(
            name=name,
            path=project,
            input_dir=project / "text",
            output_dir=project / "audio",
            voices_dir=project / "voices",
            cache_dir=project / "cache",
            log_dir=project / "logs",
            config=config
        )

    def list(self):

        projects = []

        if not self.root.exists():

            return projects

        for folder in self.root.iterdir():

            if folder.is_dir():

                if (folder / "project.json").exists():

                    projects.append(folder.name)

        return sorted(projects)

    def exists(self, name: str):

        return (self.root / name).exists()

    def delete(self, name: str):

        import shutil

        project = self.root / name

        if project.exists():

            shutil.rmtree(project)

    def rename(
        self,
        old_name: str,
        new_name: str
    ):

        old = self.root / old_name

        new = self.root / new_name

        if old.exists():

            old.rename(new)
from pathlib import Path

from core import AppPaths


class ProjectRepository:

    def __init__(self):

        self.root = AppPaths.PROJECTS

    def list(self):

        result = []

        if not self.root.exists():

            return result

        for folder in self.root.iterdir():

            if not folder.is_dir():

                continue

            if (folder / "project.json").exists():

                result.append(folder.name)

        return sorted(result)

    def exists(
        self,
        name
    ):

        return (
            self.root / name
        ).exists()

    def path(
        self,
        name
    ):

        return self.root / name

    def config(
        self,
        name
    ):

        return (
            self.root /
            name /
            "project.json"
        )
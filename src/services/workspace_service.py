from pathlib import Path
import shutil
import zipfile

from services.workspace_scanner import WorkspaceScanner


class WorkspaceService:

    CACHE_DIR = Path(
        "cache"
    ) / "workspace"

    def __init__(self):

        self.workspace = Path(
            "workspace"
        )

        self.cache = self.CACHE_DIR

        self.ensure()

        self.scanner = WorkspaceScanner()

    def ensure(self):

        self.workspace.mkdir(
            parents=True,
            exist_ok=True
        )

        self.cache.mkdir(
            parents=True,
            exist_ok=True
        )

    def set_workspace(
        self,
        path,
    ):

        self.workspace = Path(path)

        self.ensure()

    def get_workspace_path(self):

        return self.workspace

    def get_cache_path(self):

        return self.cache

    def get_workspace(self):

        return str(
            self.get_workspace_path()
        )

    def get_cache(self):

        return str(
            self.get_cache_path()
        )

    def load(self):

        self.ensure()

        return self.scanner.scan(
            self.workspace
        )

    def scan(self):

        model = self.load()

        return self.summary(
            model
        )

    def summary(
        self,
        model=None,
    ):

        if model is None:

            model = self.load()

        return {

            "voices": model.dataset_count,

            "docx": model.total_docx,

            "txt": model.total_txt,

            "audio": (
                model.total_mp3
                + model.total_wav
            ),
        }

    def import_folder(
        self,
        folder,
    ):

        folder = Path(folder)

        for file in folder.iterdir():

            if file.is_file():

                shutil.copy2(
                    file,
                    self.workspace
                )

    def import_zip(
        self,
        zip_file,
    ):

        with zipfile.ZipFile(
            zip_file,
            "r"
        ) as z:

            z.extractall(
                self.workspace
            )

    def clear(self):

        for item in self.workspace.iterdir():

            if item.is_dir():

                shutil.rmtree(
                    item
                )

            else:

                item.unlink()

from pathlib import Path

from core.app_context import AppContext

from models.text_file_model import TextFileModel


class TextService:

    def list(self):

        if not AppContext.current_project.has_project():

            return []

        root = AppContext.current_project.get().input_dir

        result = []

        for file in sorted(root.iterdir()):

            if not file.is_file():
                continue

            if file.suffix.lower() not in (
                ".txt",
                ".docx",
            ):
                continue

            result.append(
                TextFileModel(
                    name=file.stem,
                    path=file,
                    extension=file.suffix.lower(),
                    output=(
                        AppContext.current_project.get().output_dir
                        / f"{file.stem}.wav"
                    ),
                )
            )

        return result
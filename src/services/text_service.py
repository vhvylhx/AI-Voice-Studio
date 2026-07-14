from pathlib import Path
import re

from core.app_context import AppContext

from models.text_file_model import TextFileModel


class TextService:

    CHINESE_RE = re.compile(
        r"[\u3400-\u9FFF]"
    )

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

    def read(
        self,
        file,
    ):

        file = Path(file)

        if file.suffix.lower() == ".txt":

            return file.read_text(
                encoding="utf-8",
                errors="ignore",
            )

        if file.suffix.lower() == ".docx":

            from docx import Document

            doc = Document(file)

            return "\n".join(
                p.text
                for p in doc.paragraphs
            )

        return ""

    def contains_chinese(
        self,
        text,
    ):

        return bool(
            self.CHINESE_RE.search(text)
        )

## ===== KẾT THÚC PART 1 =====
    def is_test_file(
        self,
        file,
    ):

        name = Path(file).stem.lower()

        return "test" in name

    def normalize(
        self,
        text,
    ):

        text = text.replace(
            "\r",
            "\n",
        )

        while "\n\n\n" in text:

            text = text.replace(
                "\n\n\n",
                "\n\n",
            )

        return text.strip()

    def extract_chapter_number(
        self,
        file,
    ):

        name = Path(file).stem

        m = re.search(
            r"(\d+)",
            name,
        )

        if not m:

            return None

        return int(
            m.group(1)
        )

    def match_audio_name(
        self,
        text_file,
        audio_files,
    ):

        chapter = self.extract_chapter_number(
            text_file
        )

        if chapter is None:

            return None

        for audio in audio_files:

            if (
                self.extract_chapter_number(
                    audio
                )
                == chapter
            ):

                return audio

        return None


## ===== KẾT THÚC FILE =====
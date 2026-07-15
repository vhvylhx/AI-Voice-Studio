from difflib import SequenceMatcher
from pathlib import Path
import re
import unicodedata


class TextMatchingService:

    TEST_WORD = "test"

    def is_test_file(
        self,
        file,
    ):

        stem = self.normalize_name(
            Path(file).stem
        )

        tokens = [
            token
            for token in re.split(
                r"[^a-z0-9]+",
                stem,
            )
            if token
        ]

        for token in tokens:

            if token == self.TEST_WORD:

                return True

            if (
                len(token) >= 3
                and SequenceMatcher(
                    None,
                    token,
                    self.TEST_WORD,
                ).ratio()
                >= 0.75
            ):

                return True

        return False

    def normalize_name(
        self,
        text,
    ):

        text = unicodedata.normalize(
            "NFD",
            text or "",
        )

        text = "".join(
            char
            for char in text
            if unicodedata.category(
                char
            )
            != "Mn"
        )

        text = text.replace(
            "đ",
            "d",
        ).replace(
            "Đ",
            "D",
        )

        text = text.lower()

        text = re.sub(
            r"[^a-z0-9]+",
            " ",
            text,
        )

        return re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

    def chapter_info(
        self,
        file,
    ):

        stem = self.normalize_name(
            Path(file).stem
        )

        numbers = re.findall(
            r"\d+",
            stem,
        )

        if not numbers:

            return {
                "chapter": None,
                "part": None,
                "stem": stem,
            }

        return {
            "chapter": int(
                numbers[0]
            ),
            "part": (
                int(
                    numbers[1]
                )
                if len(numbers) > 1
                else 0
            ),
            "stem": stem,
        }

    def content_chapter(
        self,
        text,
    ):

        normalized = self.normalize_name(
            text
        )

        match = re.search(
            r"\b(chuong|chapter)\s+(\d+)\b",
            normalized,
        )

        if not match:

            return None

        return int(
            match.group(
                2
            )
        )

    def filename_content_mismatch(
        self,
        file,
        text,
    ):

        filename_chapter = self.chapter_info(
            file
        )["chapter"]

        content_chapter = self.content_chapter(
            text
        )

        if (
            filename_chapter is None
            or content_chapter is None
        ):

            return False

        return filename_chapter != content_chapter

    def match_audio(
        self,
        text_file,
        audio_records,
    ):

        text_info = self.chapter_info(
            text_file
        )

        matched = []

        if text_info["chapter"] is None:

            return matched

        for audio_record in audio_records:

            audio_info = self.chapter_info(
                audio_record["file"]
            )

            if audio_info["chapter"] != text_info["chapter"]:

                continue

            audio_record["match_rule"] = "chapter_number"

            audio_record["match_key"] = text_info["chapter"]

            audio_record["audio_part"] = audio_info["part"]

            matched.append(
                audio_record
            )

        return sorted(
            matched,
            key=lambda item: self.audio_sort_key(
                item
            ),
        )

    def duplicate_key(
        self,
        file,
        kind,
    ):

        info = self.chapter_info(
            file
        )

        if info["chapter"] is None:

            return (
                "invalid",
                info["stem"],
            )

        if kind == "audio":

            return (
                "chapter_part",
                info["chapter"],
                info["part"],
            )

        return (
            "chapter",
            info["chapter"],
        )

    def audio_sort_key(
        self,
        audio_record,
    ):

        return (
            audio_record.get(
                "audio_part",
                0,
            )
            or 0,
            str(
                audio_record["file"]
            ).lower(),
        )

    def match_key(
        self,
        file,
    ):

        return Path(file).stem.strip().lower()

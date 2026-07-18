import hashlib
import re
from pathlib import Path

from models.generate_pipeline_foundation import (
    GenerateChapterRecord,
    GenerateDocumentRecord,
    GenerateReconstructionReport,
    GenerateSourceSnapshot,
    GenerateUnitRecord,
)


class GenerateTextStructureService:

    sentence_pattern = re.compile(
        r"(?<=[.!?。！？…])\s+"
    )

    chapter_pattern = re.compile(
        r"^\s*(chương|chapter)\s+[\w\d]+",
        re.IGNORECASE,
    )

    def read_source(
        self,
        text="",
        text_file="",
    ):

        if text:

            return text, "pasted_text", ""

        if not text_file:

            return "", "pasted_text", ""

        path = Path(
            text_file
        )

        suffix = path.suffix.lower()

        if suffix == ".txt":

            return (
                path.read_text(
                    encoding="utf-8"
                ),
                "txt",
                str(
                    path
                ),
            )

        if suffix == ".docx":

            try:

                from docx import Document

            except Exception as exc:

                raise RuntimeError(
                    "python_docx_missing"
                ) from exc

            document = Document(
                str(
                    path
                )
            )

            return (
                "\n".join(
                    paragraph.text
                    for paragraph in document.paragraphs
                ),
                "docx",
                str(
                    path
                ),
            )

        raise ValueError(
            "generate_source_format_unsupported"
        )

    def normalize(
        self,
        text,
    ):

        text = (
            text.replace(
                "\r\n",
                "\n",
            )
            .replace(
                "\r",
                "\n",
            )
            .replace(
                "\ufeff",
                "",
            )
        )

        lines = [
            re.sub(
                r"[ \t]+",
                " ",
                line,
            ).strip()
            for line in text.split(
                "\n"
            )
        ]

        paragraphs = []

        current = []

        for line in lines:

            if not line:

                if current:

                    paragraphs.append(
                        " ".join(
                            current
                        ).strip()
                    )

                    current = []

                continue

            current.append(
                line
            )

        if current:

            paragraphs.append(
                " ".join(
                    current
                ).strip()
            )

        return "\n\n".join(
            paragraph
            for paragraph in paragraphs
            if paragraph
        )

    def split_sentences(
        self,
        paragraph,
    ):

        parts = [
            item.strip()
            for item in self.sentence_pattern.split(
                paragraph
            )
            if item.strip()
        ]

        return parts or [
            paragraph.strip()
        ]

    def checksum(
        self,
        text,
    ):

        return hashlib.sha256(
            text.encode(
                "utf-8"
            )
        ).hexdigest()

    def reconstruct_units(
        self,
        units,
    ):

        return "".join(
            unit.text + unit.separator_after
            for unit in units
        )

    def first_mismatch_index(
        self,
        left,
        right,
    ):

        for index, pair in enumerate(
            zip(
                left,
                right,
            )
        ):

            if pair[0] != pair[1]:

                return index

        if len(
            left
        ) != len(
            right
        ):

            return min(
                len(
                    left
                ),
                len(
                    right
                ),
            )

        return -1

    def verify_reconstruction(
        self,
        source_text,
        normalized_text,
        units,
    ):

        reconstructed = self.reconstruct_units(
            units
        )

        ok = reconstructed == normalized_text

        return GenerateReconstructionReport(
            ok=ok,
            source_checksum_sha256=self.checksum(
                source_text
            ),
            normalized_checksum_sha256=self.checksum(
                normalized_text
            ),
            reconstructed_checksum_sha256=self.checksum(
                reconstructed
            ),
            mismatch_index=-1
            if ok
            else self.first_mismatch_index(
                normalized_text,
                reconstructed,
            ),
            message_vi=(
                "Reconstruction khớp chính xác với normalized text."
                if ok
                else "Reconstruction không khớp normalized text."
            ),
        )

        return parts or [
            paragraph.strip()
        ]

    def split_long_sentence(
        self,
        text,
        max_characters,
    ):

        if len(
            text
        ) <= max_characters:

            return [
                text
            ]

        words = text.split()

        units = []

        current = []

        for word in words:

            candidate = " ".join(
                current
                + [
                    word,
                ]
            )

            if current and len(
                candidate
            ) > max_characters:

                units.append(
                    " ".join(
                        current
                    )
                )

                current = [
                    word,
                ]

            else:

                current.append(
                    word
                )

        if current:

            units.append(
                " ".join(
                    current
                )
            )

        return [
            item
            for item in units
            if item.strip()
        ]

    def build_structure(
        self,
        text,
        session_id,
        max_unit_characters=700,
        language="vi",
    ):

        normalized = self.normalize(
            text
        )

        document = GenerateDocumentRecord(
            session_id=session_id,
            title="Generate Document",
            character_count=len(
                normalized
            ),
            language=language,
        )

        chapters = []

        units = []

        current_chapter = None

        paragraphs = [
            item
            for item in normalized.split(
                "\n\n"
            )
            if item.strip()
        ]

        if not paragraphs:

            chapter = GenerateChapterRecord(
                document_id=document.document_id,
                title="Nội dung",
                order=1,
            )

            chapters.append(
                chapter
            )

            document.chapter_ids.append(
                chapter.chapter_id
            )

            return document, chapters, units, normalized

        for paragraph_index, paragraph in enumerate(
            paragraphs
        ):

            if (
                current_chapter is None
                or self.chapter_pattern.match(
                    paragraph
                )
            ):

                current_chapter = GenerateChapterRecord(
                    document_id=document.document_id,
                    title=paragraph[:120]
                    if self.chapter_pattern.match(
                        paragraph
                    )
                    else "Nội dung",
                    order=len(
                        chapters
                    )
                    + 1,
                    start_index=len(
                        units
                    ),
                )

                chapters.append(
                    current_chapter
                )

                document.chapter_ids.append(
                    current_chapter.chapter_id
                )

            sentence_parts = []

            for sentence in self.split_sentences(
                paragraph
            ):

                chunks = self.split_long_sentence(
                    sentence,
                    max_unit_characters,
                )

                for chunk in chunks:

                    sentence_parts.append(
                        chunk
                    )

            for part_index, unit_text in enumerate(
                sentence_parts
            ):

                if not unit_text.strip():

                    continue

                is_last_part = (
                    part_index
                    == len(
                        sentence_parts
                    )
                    - 1
                )

                is_last_paragraph = (
                    paragraph_index
                    == len(
                        paragraphs
                    )
                    - 1
                )

                separator_after = (
                    "\n\n"
                    if is_last_part
                    and not is_last_paragraph
                    else " "
                    if not is_last_part
                    else ""
                )

                unit = GenerateUnitRecord(
                    chapter_id=current_chapter.chapter_id,
                    order=len(
                        units
                    )
                    + 1,
                    text=unit_text,
                    normalized_text=self.normalize(
                        unit_text
                    ),
                    boundary="chapter_title"
                    if self.chapter_pattern.match(
                        paragraph
                    )
                    else "sentence",
                    separator_after=separator_after,
                    estimated_characters=len(
                        unit_text
                    ),
                )

                units.append(
                    unit
                )

                current_chapter.unit_ids.append(
                    unit.unit_id
                )

            current_chapter.end_index = len(
                units
            )

        document.unit_count = len(
            units
        )

        return document, chapters, units, normalized

    def make_snapshot(
        self,
        text,
        source_type,
        original_path,
        snapshot_path,
        language="vi",
    ):

        checksum = hashlib.sha256(
            text.encode(
                "utf-8"
            )
        ).hexdigest()

        return GenerateSourceSnapshot(
            source_type=source_type,
            original_path=original_path,
            snapshot_path=str(
                snapshot_path
            ),
            checksum_sha256=checksum,
            character_count=len(
                text
            ),
            line_count=len(
                text.splitlines()
            ),
            language=language,
        )

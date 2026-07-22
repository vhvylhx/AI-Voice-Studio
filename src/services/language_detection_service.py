from __future__ import annotations

import re

from models.language_capability import (
    LanguageDetectionResult,
    LanguageSegment,
)
from services.language_catalog_service import LanguageCatalogService


VIETNAMESE_CHARS = set(
    "ăâđêôơưáàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệ"
    "íìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ"
)


class LanguageDetectionService:

    def __init__(
        self,
        catalog=None,
    ):

        self.catalog = catalog or LanguageCatalogService()

    def detect(
        self,
        text,
        explicit_language="",
    ):

        explicit = self.catalog.normalize(
            explicit_language
        ) if explicit_language else ""

        detected = self.detect_heuristic(
            text
        )

        if explicit:

            warnings = []

            if (
                detected.language_code
                and detected.language_code != explicit
                and detected.confidence >= 0.75
            ):

                warnings.append(
                    "explicit_language_mismatch"
                )

            return LanguageDetectionResult(
                language_code=explicit,
                confidence=1.0,
                method="explicit",
                warnings=warnings,
            )

        return detected

    def detect_heuristic(
        self,
        text,
    ):

        raw = str(
            text or ""
        )

        if not raw.strip():

            return LanguageDetectionResult(
                language_code="",
                confidence=0.0,
                warnings=[
                    "empty_text",
                ],
            )

        scores = {
            "vi": 0,
            "zh": 0,
            "en": 0,
            "ja": 0,
            "ko": 0,
            "yue": 0,
        }

        lowered = raw.lower()

        for char in lowered:

            code = ord(
                char
            )

            if char in VIETNAMESE_CHARS:

                scores["vi"] += 4

            elif 0x4E00 <= code <= 0x9FFF:

                scores["zh"] += 3

            elif 0x3040 <= code <= 0x30FF:

                scores["ja"] += 4

            elif 0xAC00 <= code <= 0xD7AF:

                scores["ko"] += 4

            elif "a" <= char <= "z":

                scores["en"] += 1

        if re.search(
            r"\b(xin|chào|không|được|tiếng|người|mình|của)\b",
            lowered,
        ):

            scores["vi"] += 20

        if re.search(
            r"\b(the|and|hello|everyone|this|is|test)\b",
            lowered,
        ):

            scores["en"] += 4

        if re.search(
            r"[嘅咗啲佢哋冇唔]",
            raw,
        ):

            scores["yue"] += 5

        if scores["ja"]:

            scores["zh"] = max(
                0,
                scores["zh"] - 1,
            )

        best = max(
            scores,
            key=lambda key: scores[key],
        )

        total = sum(
            scores.values()
        )

        if not total or scores[best] <= 0:

            return LanguageDetectionResult(
                language_code="en",
                confidence=0.4,
                warnings=[
                    "low_confidence_default_latin",
                ],
            )

        confidence = min(
            1.0,
            scores[best] / max(
                1,
                total,
            ),
        )

        warnings = []

        if best == "zh" and scores["yue"] > 0:

            best = "yue"

        if confidence < 0.6:

            warnings.append(
                "low_confidence"
            )

        return LanguageDetectionResult(
            language_code=best,
            confidence=round(
                confidence,
                4,
            ),
            warnings=warnings,
        )

    def segment_text(
        self,
        text,
        explicit_language="",
    ):

        raw = str(
            text or ""
        )

        if not raw.strip():

            return []

        parts = list(
            re.finditer(
                r"[^。.!?\n]+[。.!?]?",
                raw,
            )
        )

        if not parts:

            result = self.detect(
                raw,
                explicit_language=explicit_language,
            )

            return [
                LanguageSegment(
                    segment_id="lang_000001",
                    text=raw,
                    language_code=result.language_code,
                    confidence=result.confidence,
                    start_index=0,
                    end_index=len(
                        raw
                    ),
                    warnings=result.warnings,
                )
            ]

        segments = []

        for index, match in enumerate(
            parts,
            start=1,
        ):

            chunk = match.group(
                0
            )

            if not chunk.strip():

                continue

            result = self.detect(
                chunk,
                explicit_language=explicit_language,
            )

            segments.append(
                LanguageSegment(
                    segment_id=f"lang_{index:06d}",
                    text=chunk.strip(),
                    language_code=result.language_code,
                    confidence=result.confidence,
                    start_index=match.start(),
                    end_index=match.end(),
                    warnings=result.warnings,
                )
            )

        return segments

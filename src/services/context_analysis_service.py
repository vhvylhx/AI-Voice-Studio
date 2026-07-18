import re


class ContextAnalysisService:

    def split_text(
        self,
        text,
        max_chars=420,
    ):

        text = str(
            text or ""
        ).strip()

        if not text:

            return []

        paragraphs = re.split(
            r"\n\s*\n",
            text,
        )

        segments = []

        for paragraph in paragraphs:

            paragraph = paragraph.strip()

            if not paragraph:

                continue

            boundary = "paragraph"

            if paragraph.startswith(
                (
                    "-",
                    "“",
                    "\"",
                )
            ):

                boundary = "dialogue"

            for sentence in self.split_sentences(
                paragraph,
            ):

                for chunk in self.split_long_sentence(
                    sentence,
                    max_chars=max_chars,
                ):

                    segments.append(
                        {
                            "text": chunk,
                            "boundary": boundary,
                            "mid_word": False,
                            "mid_sentence": False,
                        }
                    )

        return segments

    def split_sentences(
        self,
        text,
    ):

        parts = re.split(
            r"(?<=[.!?…])\s+",
            text.strip(),
        )

        return [
            part.strip()
            for part in parts
            if part.strip()
        ]

    def split_long_sentence(
        self,
        text,
        max_chars=420,
    ):

        text = text.strip()

        if len(text) <= max_chars:

            return [
                text
            ]

        pieces = re.split(
            r"(?<=[,;:])\s+",
            text,
        )

        chunks = []

        current = ""

        for piece in pieces:

            if (
                current
                and len(current)
                + 1
                + len(piece)
                > max_chars
            ):

                chunks.append(
                    current.strip()
                )

                current = piece

            else:

                current = (
                    f"{current} {piece}".strip()
                )

        if current:

            chunks.append(
                current.strip()
            )

        return [
            chunk
            for chunk in chunks
            if chunk
        ]

    def analyze(
        self,
        segments,
        variant_ids,
        style_ids,
    ):

        analyzed = []

        for segment in segments:

            text = segment.get(
                "text",
                "",
            )

            variant_candidates = self.score_ids(
                variant_ids,
                text,
            )

            style_candidates = self.score_ids(
                style_ids,
                text,
            )

            analyzed.append(
                {
                    **segment,
                    "variant_id": (
                        variant_candidates[0]["id"]
                        if variant_candidates
                        else ""
                    ),
                    "style_id": (
                        style_candidates[0]["id"]
                        if style_candidates
                        else ""
                    ),
                    "confidence": (
                        variant_candidates[0]["confidence"]
                        if variant_candidates
                        else 0.0
                    ),
                    "variant_candidates": variant_candidates,
                    "style_candidates": style_candidates,
                }
            )

        return analyzed

    def score_ids(
        self,
        ids,
        text,
    ):

        lowered = text.lower()

        scored = []

        for item in ids or []:

            score = 0.5

            if item in lowered:

                score = 0.9

            if (
                "!" in text
                and item in {
                    "dramatic",
                    "expressive",
                    "emotional_female",
                    "emotional_male",
                }
            ):

                score = 0.8

            scored.append(
                {
                    "id": item,
                    "confidence": score,
                }
            )

        return sorted(
            scored,
            key=lambda item: item["confidence"],
            reverse=True,
        )

import re
from dataclasses import dataclass
from pathlib import Path

from models.generate_config import (
    GENERATE_MODE_AI_STYLE,
    GENERATE_MODE_STANDARD,
    GenerateChunk,
    GeneratePlan,
    GenerateSelectionConfig,
    SpeedProfile,
    StyleDecision,
    StyleTimeline,
    VariantDecision,
    VariantTimeline,
)


@dataclass
class GenerateValidationResult:

    ok: bool = True

    errors: list[str] | None = None

    warnings: list[str] | None = None

    allowed_variant_ids: list[str] | None = None

    allowed_style_ids: list[str] | None = None

    def __post_init__(self):

        if self.errors is None:

            self.errors = []

        if self.warnings is None:

            self.warnings = []

        if self.allowed_variant_ids is None:

            self.allowed_variant_ids = []

        if self.allowed_style_ids is None:

            self.allowed_style_ids = []

        self.ok = not self.errors


class GeneratePlanningService:

    def validate_selection(
        self,
        config: GenerateSelectionConfig,
        voice_variants,
        style_ids=None,
    ):

        style_ids = style_ids or []

        errors = []

        warnings = []

        if not config.voice_id:

            errors.append(
                "voice_required"
            )

        variant_ids = self.variant_ids(
            voice_variants
        )

        allowed_variants = self.resolve_allowed(
            allow_all=config.allow_all_variants,
            selected_ids=config.allowed_variant_ids,
            all_ids=variant_ids,
        )

        allowed_styles = self.resolve_allowed(
            allow_all=config.allow_all_styles,
            selected_ids=config.allowed_style_ids,
            all_ids=style_ids,
        )

        if config.mode == GENERATE_MODE_STANDARD:

            if not config.selected_variant_id:

                errors.append(
                    "variant_required"
                )

            elif config.selected_variant_id not in variant_ids:

                errors.append(
                    "variant_not_found"
                )

            else:

                allowed_variants = [
                    config.selected_variant_id
                ]

        elif config.mode == GENERATE_MODE_AI_STYLE:

            if not allowed_variants:

                errors.append(
                    "no_variant_selected"
                )

            if not allowed_styles:

                errors.append(
                    "no_style_selected"
                )

        else:

            errors.append(
                "generate_mode_invalid"
            )

        speed_errors = self.validate_speed(
            config.speed
        )

        errors.extend(
            speed_errors
        )

        return GenerateValidationResult(
            errors=errors,
            warnings=warnings,
            allowed_variant_ids=allowed_variants,
            allowed_style_ids=allowed_styles,
        )

    def variant_ids(
        self,
        voice_variants,
    ):

        result = []

        for variant in voice_variants or []:

            if isinstance(
                variant,
                dict,
            ):

                variant_id = variant.get(
                    "id",
                    "",
                )

            else:

                variant_id = getattr(
                    variant,
                    "variant_id",
                    "",
                )

            if variant_id:

                result.append(
                    variant_id
                )

        return result

    def resolve_allowed(
        self,
        allow_all,
        selected_ids,
        all_ids,
    ):

        if allow_all:

            return list(
                all_ids
            )

        all_set = set(
            all_ids
        )

        return [
            item
            for item in selected_ids or []
            if item in all_set
        ]

    def validate_speed(
        self,
        speed: SpeedProfile,
    ):

        errors = []

        value = float(
            speed.speed
        )

        if value in speed.preset_speeds:

            return errors

        if not speed.allow_custom:

            errors.append(
                "speed_not_allowed"
            )

            return errors

        if (
            speed.custom_min is None
            or speed.custom_max is None
        ):

            errors.append(
                "custom_speed_limit_required"
            )

            return errors

        if not (
            speed.custom_min
            <= value
            <= speed.custom_max
        ):

            errors.append(
                "custom_speed_out_of_range"
            )

        return errors

    def choose_variant(
        self,
        config,
        allowed_variant_ids,
        candidate_id="",
        confidence=0.0,
        candidates=None,
    ):

        variant_id = self.choose_in_scope(
            candidate_id=candidate_id,
            default_id=config.default_variant_id,
            allowed_ids=allowed_variant_ids,
            candidates=candidates,
        )

        reason = "candidate"

        if candidate_id != variant_id:

            if (
                config.default_variant_id
                and variant_id == config.default_variant_id
            ):

                reason = "default_variant"

            else:

                reason = "best_allowed_variant"

        if (
            candidates
            and reason == "best_allowed_variant"
        ):

            confidence = self.candidate_confidence(
                variant_id,
                candidates,
            )

        return variant_id, confidence, reason

    def choose_style(
        self,
        config,
        allowed_style_ids,
        candidate_id="",
        confidence=0.0,
        candidates=None,
    ):

        style_id = self.choose_in_scope(
            candidate_id=candidate_id,
            default_id=config.default_style_id,
            allowed_ids=allowed_style_ids,
            candidates=candidates,
        )

        reason = "candidate"

        if candidate_id != style_id:

            if (
                config.default_style_id
                and style_id == config.default_style_id
            ):

                reason = "default_style"

            else:

                reason = "best_allowed_style"

        if (
            candidates
            and reason == "best_allowed_style"
        ):

            confidence = self.candidate_confidence(
                style_id,
                candidates,
            )

        return style_id, confidence, reason

    def choose_in_scope(
        self,
        candidate_id,
        default_id,
        allowed_ids,
        candidates=None,
    ):

        if candidate_id in allowed_ids:

            return candidate_id

        if default_id in allowed_ids:

            return default_id

        best_id = self.best_allowed_candidate(
            allowed_ids,
            candidates,
        )

        if best_id:

            return best_id

        if allowed_ids:

            return allowed_ids[0]

        return ""

    def best_allowed_candidate(
        self,
        allowed_ids,
        candidates,
    ):

        if not candidates:

            return ""

        allowed_set = set(
            allowed_ids
        )

        best_id = ""

        best_confidence = -1.0

        for candidate in candidates:

            candidate_id = candidate.get(
                "id",
                "",
            )

            confidence = float(
                candidate.get(
                    "confidence",
                    0.0,
                )
            )

            if candidate_id not in allowed_set:

                continue

            if confidence > best_confidence:

                best_id = candidate_id

                best_confidence = confidence

        return best_id

    def candidate_confidence(
        self,
        candidate_id,
        candidates,
    ):

        for candidate in candidates or []:

            if candidate.get(
                "id",
                "",
            ) == candidate_id:

                return float(
                    candidate.get(
                        "confidence",
                        0.0,
                    )
                )

        return 0.0

    def build_variant_timeline(
        self,
        segments,
        config,
        allowed_variant_ids,
    ):

        items = []

        for index, segment in enumerate(
            segments
        ):

            if not self.is_safe_boundary(
                segment
            ):

                continue

            variant_id, confidence, reason = (
                self.choose_variant(
                    config=config,
                    allowed_variant_ids=allowed_variant_ids,
                    candidate_id=segment.get(
                        "variant_id",
                        "",
                    ),
                    confidence=float(
                        segment.get(
                            "confidence",
                            0.0,
                        )
                    ),
                    candidates=segment.get(
                        "variant_candidates",
                        None,
                    ),
                )
            )

            if not variant_id:

                continue

            items.append(
                VariantDecision(
                    segment_index=index,
                    text=segment.get(
                        "text",
                        "",
                    ),
                    variant_id=variant_id,
                    confidence=confidence,
                    reason=reason,
                )
            )

        return VariantTimeline(
            items=self.merge_adjacent_variant(
                items
            )
        )

    def build_style_timeline(
        self,
        segments,
        config,
        allowed_style_ids,
    ):

        items = []

        for index, segment in enumerate(
            segments
        ):

            if not self.is_safe_boundary(
                segment
            ):

                continue

            style_id, confidence, reason = (
                self.choose_style(
                    config=config,
                    allowed_style_ids=allowed_style_ids,
                    candidate_id=segment.get(
                        "style_id",
                        "",
                    ),
                    confidence=float(
                        segment.get(
                            "confidence",
                            0.0,
                        )
                    ),
                    candidates=segment.get(
                        "style_candidates",
                        None,
                    ),
                )
            )

            if not style_id:

                continue

            items.append(
                StyleDecision(
                    segment_index=index,
                    text=segment.get(
                        "text",
                        "",
                    ),
                    style_id=style_id,
                    confidence=confidence,
                    reason=reason,
                )
            )

        return StyleTimeline(
            items=self.merge_adjacent_style(
                items
            )
        )

    def is_safe_boundary(
        self,
        segment,
    ):

        if segment.get(
            "mid_word",
            False,
        ):

            return False

        if segment.get(
            "mid_sentence",
            False,
        ):

            return False

        text = segment.get(
            "text",
            "",
        ).strip()

        if not text:

            return False

        if segment.get(
            "boundary",
            "",
        ) in {
            "sentence",
            "paragraph",
            "dialogue",
            "scene",
            "pause",
        }:

            return True

        return bool(
            re.search(
                r'[.!?…"\']$',
                text,
            )
        )

    def merge_adjacent_variant(
        self,
        items,
    ):

        merged = []

        for item in items:

            if (
                merged
                and merged[-1].variant_id
                == item.variant_id
            ):

                continue

            merged.append(
                item
            )

        return merged

    def merge_adjacent_style(
        self,
        items,
    ):

        merged = []

        for item in items:

            if (
                merged
                and merged[-1].style_id
                == item.style_id
            ):

                continue

            merged.append(
                item
            )

        return merged

    def assert_output_clean(
        self,
        output_folder,
    ):

        output = Path(
            output_folder
        )

        temp_names = {
            "temp",
            ".temp",
            "tmp",
        }

        for item in output.iterdir():

            if item.name.lower() in temp_names:

                raise ValueError(
                    "temp_file_in_output"
                )

    def build_plan(
        self,
        job_id,
        segments,
        config,
        allowed_variant_ids,
        allowed_style_ids,
        temp_dir,
    ):

        variant_timeline = self.build_variant_timeline(
            segments,
            config,
            allowed_variant_ids,
        )

        style_timeline = self.build_style_timeline(
            segments,
            config,
            allowed_style_ids,
        )

        chunks = []

        for index, segment in enumerate(
            segments
        ):

            variant_id = self.timeline_value(
                variant_timeline.items,
                index,
                "variant_id",
            )

            style_id = self.timeline_value(
                style_timeline.items,
                index,
                "style_id",
            )

            if not variant_id:

                variant_id, _, _ = self.choose_variant(
                    config,
                    allowed_variant_ids,
                    candidates=segment.get(
                        "variant_candidates",
                        None,
                    ),
                )

            if not style_id:

                style_id, _, _ = self.choose_style(
                    config,
                    allowed_style_ids,
                    candidates=segment.get(
                        "style_candidates",
                        None,
                    ),
                )

            if not variant_id:

                raise RuntimeError(
                    "variant_scope_empty"
                )

            if (
                config.mode == GENERATE_MODE_AI_STYLE
                and not style_id
            ):

                raise RuntimeError(
                    "style_scope_empty"
                )

            chunks.append(
                GenerateChunk(
                    chunk_id=f"chunk_{index + 1:04d}",
                    text=segment.get(
                        "text",
                        "",
                    ),
                    voice_id=config.voice_id,
                    variant_id=variant_id,
                    style_id=style_id,
                    preset_id=config.preset_id,
                    reference_style_id=config.reference_style_id,
                    speed=config.speed.speed,
                    output_temp_path=str(
                        Path(temp_dir)
                        / "chunks"
                        / f"chunk_{index + 1:04d}.wav"
                    ),
                    boundary=segment.get(
                        "boundary",
                        "sentence",
                    ),
                )
            )

        return GeneratePlan(
            job_id=job_id,
            chunks=self.merge_same_config_chunks(
                chunks
            ),
            variant_timeline=variant_timeline,
            style_timeline=style_timeline,
        )

    def timeline_value(
        self,
        items,
        segment_index,
        attr,
    ):

        value = ""

        for item in items:

            if item.segment_index <= segment_index:

                value = getattr(
                    item,
                    attr,
                    "",
                )

        return value

    def merge_same_config_chunks(
        self,
        chunks,
        max_chars=900,
    ):

        merged = []

        for chunk in chunks:

            if not merged:

                merged.append(
                    chunk
                )

                continue

            previous = merged[-1]

            same_config = (
                previous.voice_id == chunk.voice_id
                and previous.variant_id == chunk.variant_id
                and previous.style_id == chunk.style_id
                and previous.preset_id == chunk.preset_id
                and previous.reference_style_id
                == chunk.reference_style_id
                and previous.speed == chunk.speed
            )

            if (
                same_config
                and len(previous.text)
                + 1
                + len(chunk.text)
                <= max_chars
            ):

                previous.text = (
                    previous.text
                    + "\n"
                    + chunk.text
                )

                continue

            merged.append(
                chunk
            )

        for index, chunk in enumerate(
            merged,
            start=1,
        ):

            chunk.chunk_id = f"chunk_{index:04d}"

            chunk.output_temp_path = str(
                Path(chunk.output_temp_path).parent
                / f"{chunk.chunk_id}.wav"
            )

        return merged

from pathlib import Path
import json
import re
import time

from models.alignment_quality_config import AlignmentQualityConfig
from services.alignment_service import AlignmentSegment
from services.alignment_service import AlignmentService
from services.audio_service import AudioService
from services.train_audio_prep_service import TrainAudioPrepService


class SuspiciousRecoveryService:

    def __init__(self):

        self.alignment = AlignmentService()

        self.audio = AudioService()

        self.prep = TrainAudioPrepService()

    def recover(
        self,
        alignment_dir,
        output_dir,
        reasons=None,
        source_limit=None,
        full_run=False,
    ):

        alignment_dir = Path(
            alignment_dir
        )

        output_dir = Path(
            output_dir
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        clips_dir = output_dir / "clips"

        transcripts_dir = output_dir / "transcripts"

        clips_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        transcripts_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        state = self.read_json(
            alignment_dir / "alignment_state.json"
        )

        report = self.read_json(
            alignment_dir / "alignment_report.json"
        )

        config = AlignmentQualityConfig.from_dict(
            report.get(
                "quality_config",
                {},
            )
        )

        runtime = report.get(
            "alignment_runtime",
            {},
        )

        valid_before = [
            dict(
                item
            )
            for item in state.get(
                "valid",
                [],
            )
        ]

        suspicious = state.get(
            "suspicious",
            [],
        )

        selected = self.select_suspicious(
            suspicious,
            reasons,
            source_limit,
        )

        started = time.time()

        recovered = []

        still_suspicious = []

        rejected = []

        used_audio = {
            item.get(
                "audio",
                "",
            )
            for item in valid_before
        }

        for source_audio, items in selected.items():

            source_result = self.recover_source(
                source_audio,
                items,
                output_dir,
                clips_dir,
                transcripts_dir,
                config,
                runtime,
                used_audio,
            )

            recovered.extend(
                source_result["recovered_valid"]
            )

            still_suspicious.extend(
                source_result["still_suspicious"]
            )

            rejected.extend(
                source_result["rejected"]
            )

        final_valid = valid_before + recovered

        metadata_file = output_dir / "metadata.list"

        self.write_metadata(
            metadata_file,
            final_valid,
        )

        final_validation = self.prep.validate_metadata_file(
            metadata_file
        )

        recovery_report = self.create_report(
            alignment_dir,
            output_dir,
            valid_before,
            recovered,
            still_suspicious,
            rejected,
            final_validation,
            config,
            full_run,
            started,
        )

        self.write_json(
            output_dir / "recovery_report.json",
            recovery_report,
        )

        return recovery_report

    def select_suspicious(
        self,
        suspicious,
        reasons=None,
        source_limit=None,
    ):

        reasons = set(
            reasons
            or [
                "no_alignment_match",
                "similarity_too_low",
                "source_error_rate_exceeded",
            ]
        )

        grouped = {}

        for item in suspicious:

            if item.get(
                "code"
            ) not in reasons:

                continue

            source_audio = item.get(
                "source_audio",
                "",
            )

            grouped.setdefault(
                source_audio,
                [],
            ).append(
                item
            )

        if source_limit is None:

            return grouped

        limited = {}

        for source_audio in grouped:

            limited[source_audio] = grouped[source_audio]

            if len(
                limited
            ) >= int(
                source_limit
            ):

                break

        return limited

    def recover_source(
        self,
        source_audio,
        items,
        output_dir,
        clips_dir,
        transcripts_dir,
        config,
        runtime,
        used_audio,
    ):

        result = {
            "recovered_valid": [],
            "still_suspicious": [],
            "rejected": [],
        }

        source_audio_path = Path(
            source_audio
        )

        if not source_audio_path.exists():

            for item in items:

                result["rejected"].append(
                    self.recovery_item(
                        item,
                        "source_audio_missing",
                        "rejected",
                    )
                )

            return result

        try:

            transcript = self.alignment.transcribe(
                source_audio_path,
                language=config.language,
                model=config.alignment_model,
                device=runtime.get(
                    "device",
                    config.alignment_device,
                ),
                compute_type=runtime.get(
                    "compute_type",
                    config.alignment_compute_type,
                ),
                model_path=runtime.get(
                    "model_path",
                    "",
                ),
                python_executable=runtime.get(
                    "python_executable",
                    None,
                ),
                cuda_available=(
                    runtime.get(
                        "device",
                        "cpu",
                    )
                    == "cuda"
                ),
            )

        except Exception as e:

            for item in items:

                result["still_suspicious"].append(
                    self.recovery_item(
                        item,
                        "asr_failed",
                        "still_suspicious",
                        message=str(
                            e
                        ),
                    )
                )

            return result

        cursor = 0

        ordered_items = sorted(
            items,
            key=lambda item: (
                float(
                    item.get(
                        "start",
                        0,
                    )
                    or 0
                ),
                item.get(
                    "code",
                    "",
                ),
            ),
        )

        for item_index, item in enumerate(
            ordered_items,
            start=1,
        ):

            candidates = self.target_text_candidates(
                item
            )

            match = self.find_sequential_match(
                transcript,
                candidates,
                cursor,
                config,
                expected_start=item.get(
                    "start",
                    0,
                ),
            )

            if match is None:

                result["still_suspicious"].append(
                    self.recovery_item(
                        item,
                        "no_recovery_match",
                        "still_suspicious",
                    )
                )

                continue

            if not match.get(
                "accepted",
                False,
            ):

                segment = match["segment"]

                result["still_suspicious"].append(
                    self.recovery_item(
                        item,
                        "similarity_too_low",
                        "still_suspicious",
                        new_similarity=segment.score,
                        asr_text=segment.asr_text,
                        original_text=segment.text,
                        start=segment.start,
                        end=segment.end,
                    )
                )

                cursor = match["next_cursor"]

                continue

            cursor = match["next_cursor"]

            clip_id = self.recovery_clip_id(
                source_audio_path,
                item_index,
            )

            clip = self.create_recovered_clip(
                item,
                match["segment"],
                clip_id,
                clips_dir,
                transcripts_dir,
                config,
                used_audio,
            )

            if clip["status"] == "valid":

                result["recovered_valid"].append(
                    clip
                )

                used_audio.add(
                    clip["audio"]
                )

            else:

                result["still_suspicious"].append(
                    clip
                )

        return result

    def target_text_candidates(
        self,
        item,
    ):

        original_text = item.get(
            "original_text",
            "",
        )

        sentences = self.prep.split_sentences(
            original_text
        )

        if not sentences:

            return [
                original_text
            ]

        candidates = []

        for index in range(
            len(
                sentences
            )
        ):

            for size in (
                1,
                2,
                3,
            ):

                chunk = sentences[
                    index : index + size
                ]

                if len(
                    chunk
                ) != size:

                    continue

                candidates.append(
                    " ".join(
                        chunk
                    ).strip()
                )

        return candidates

    def find_sequential_match(
        self,
        transcript,
        text_candidates,
        cursor,
        config,
        expected_start=0,
    ):

        best = None

        nearest_index = self.nearest_transcript_index(
            transcript,
            expected_start,
        )

        search_start = cursor

        if nearest_index is not None:

            search_start = max(
                cursor,
                nearest_index - 3,
            )

        window_end = min(
            len(
                transcript
            ),
            search_start + 8,
        )

        for start_index in range(
            search_start,
            window_end,
        ):

            for segment_count in (
                1,
                2,
                3,
            ):

                end_index = start_index + segment_count

                if end_index > len(
                    transcript
                ):

                    continue

                asr_segments = transcript[
                    start_index:end_index
                ]

                segment = self.combine_asr_segments(
                    asr_segments
                )

                if not self.timestamp_valid(
                    segment
                ):

                    continue

                for text in text_candidates:

                    score = self.alignment.score_text(
                        segment["text"],
                        text,
                    )

                    if best is None or score > best["score"]:

                        best = {
                            "score": float(
                                score
                            ),
                            "text": text,
                            "asr_text": segment["text"],
                            "start": segment["start"],
                            "end": segment["end"],
                            "words": segment["words"],
                            "next_cursor": end_index,
                        }

        if best is None:

            return None

        return {
            "accepted": (
                best["score"] >= config.similarity_threshold
            ),
            "next_cursor": best["next_cursor"],
            "segment": AlignmentSegment(
                text=best["text"],
                start=best["start"],
                end=best["end"],
                score=best["score"],
                asr_text=best["asr_text"],
                language=config.language,
                words=best["words"],
            ),
        }

    def nearest_transcript_index(
        self,
        transcript,
        expected_start,
    ):

        expected_start = float(
            expected_start or 0
        )

        if expected_start <= 0 or not transcript:

            return None

        best_index = 0

        best_distance = None

        for index, segment in enumerate(
            transcript
        ):

            distance = abs(
                float(
                    segment.get(
                        "start",
                        0,
                    )
                )
                - expected_start
            )

            if best_distance is None or distance < best_distance:

                best_distance = distance

                best_index = index

        return best_index

    def combine_asr_segments(
        self,
        segments,
    ):

        words = []

        for segment in segments:

            words.extend(
                segment.get(
                    "words",
                    [],
                )
                or []
            )

        return {
            "text": " ".join(
                segment.get(
                    "text",
                    "",
                ).strip()
                for segment in segments
                if segment.get(
                    "text",
                    "",
                ).strip()
            ).strip(),
            "start": float(
                segments[0].get(
                    "start",
                    0,
                )
            ),
            "end": float(
                segments[-1].get(
                    "end",
                    0,
                )
            ),
            "words": words,
        }

    def create_recovered_clip(
        self,
        suspicious_item,
        match,
        clip_id,
        clips_dir,
        transcripts_dir,
        config,
        used_audio,
    ):

        duration = float(
            match.end
        ) - float(
            match.start
        )

        invalid = self.prep.validate_candidate(
            {
                "audio": suspicious_item.get(
                    "source_audio",
                    "",
                ),
                "text": suspicious_item.get(
                    "source_text",
                    "",
                ),
            },
            match,
            match.start,
            match.end,
            duration,
            config,
        )

        if invalid:

            return self.recovery_item(
                suspicious_item,
                invalid.get(
                    "code",
                    "candidate_invalid",
                ),
                "still_suspicious",
                new_similarity=match.score,
                asr_text=match.asr_text,
                original_text=match.text,
                start=match.start,
                end=match.end,
            )

        clip_file = clips_dir / f"{clip_id}.wav"

        if str(
            clip_file
        ) in used_audio:

            return self.recovery_item(
                suspicious_item,
                "duplicate_recovery_clip",
                "rejected",
                new_similarity=match.score,
            )

        transcript_file = transcripts_dir / f"{clip_id}.txt"

        try:

            self.audio.convert_segment_wav(
                suspicious_item["source_audio"],
                clip_file,
                match.start,
                duration,
                sample_rate=config.sample_rate,
            )

            clip_info = self.audio.probe(
                clip_file
            )

        except Exception as e:

            return self.recovery_item(
                suspicious_item,
                "audio_probe_failed",
                "still_suspicious",
                new_similarity=match.score,
                message=str(
                    e
                ),
            )

        audio_invalid = self.prep.validate_output_audio(
            {
                "audio": suspicious_item.get(
                    "source_audio",
                    "",
                ),
                "text": suspicious_item.get(
                    "source_text",
                    "",
                ),
            },
            match,
            clip_info,
            match.start,
            duration,
            config,
        )

        if audio_invalid:

            return self.recovery_item(
                suspicious_item,
                audio_invalid.get(
                    "code",
                    "audio_invalid",
                ),
                "still_suspicious",
                new_similarity=match.score,
            )

        transcript_file.write_text(
            match.text,
            encoding="utf-8",
        )

        return {
            "id": clip_id,
            "status": "valid",
            "audio": str(
                clip_file
            ),
            "transcript": str(
                transcript_file
            ),
            "source_audio": suspicious_item.get(
                "source_audio",
                "",
            ),
            "source_text": suspicious_item.get(
                "source_text",
                "",
            ),
            "speaker": self.prep.speaker_name(
                suspicious_item.get(
                    "source_audio",
                    "",
                )
            ),
            "language": config.language,
            "content": match.text,
            "asr_text": match.asr_text,
            "match_score": float(
                match.score
            ),
            "old_similarity": float(
                suspicious_item.get(
                    "similarity",
                    0,
                )
                or 0
            ),
            "recovery_method": "sequential_asr_window",
            "start": float(
                match.start
            ),
            "end": float(
                match.end
            ),
            "duration": clip_info["duration"],
            "sample_rate": clip_info["sample_rate"],
            "channels": clip_info["channels"],
            "codec": clip_info["codec"],
            "metadata_enabled": True,
        }

    def recovery_item(
        self,
        suspicious_item,
        reason,
        status,
        new_similarity=None,
        asr_text=None,
        original_text=None,
        start=None,
        end=None,
        message="",
    ):

        start_value = (
            suspicious_item.get(
                "start",
                0,
            )
            if start is None
            else start
        )

        end_value = (
            suspicious_item.get(
                "end",
                0,
            )
            if end is None
            else end
        )

        return {
            "status": status,
            "reason": reason,
            "recovery_method": "sequential_asr_window",
            "old_reason": suspicious_item.get(
                "code",
                "",
            ),
            "old_similarity": float(
                suspicious_item.get(
                    "similarity",
                    0,
                )
                or 0
            ),
            "new_similarity": (
                float(
                    new_similarity
                )
                if new_similarity is not None
                else 0
            ),
            "source_file": suspicious_item.get(
                "source_audio",
                "",
            ),
            "source_text": suspicious_item.get(
                "source_text",
                "",
            ),
            "start": float(
                start_value or 0
            ),
            "end": float(
                end_value or 0
            ),
            "duration": max(
                0.0,
                float(
                    end_value or 0
                )
                - float(
                    start_value or 0
                ),
            ),
            "original_text": (
                original_text
                if original_text is not None
                else suspicious_item.get(
                    "original_text",
                    "",
                )
            ),
            "asr_text": (
                asr_text
                if asr_text is not None
                else suspicious_item.get(
                    "asr_text",
                    "",
                )
            ),
            "message": message,
        }

    def create_report(
        self,
        alignment_dir,
        output_dir,
        valid_before,
        recovered,
        still_suspicious,
        rejected,
        metadata_validation,
        config,
        full_run,
        started,
    ):

        final_valid = valid_before + recovered

        metadata_clips = [
            item
            for item in final_valid
            if item.get(
                "metadata_enabled",
                True,
            )
        ]

        similarities = [
            float(
                item.get(
                    "match_score",
                    item.get(
                        "similarity",
                        0,
                    ),
                )
                or 0
            )
            for item in metadata_clips
        ]

        total_duration = sum(
            float(
                item.get(
                    "duration",
                    0,
                )
                or 0
            )
            for item in metadata_clips
        )

        reason_counts = {}

        for item in still_suspicious:

            reason = item.get(
                "old_reason",
                item.get(
                    "reason",
                    "unknown",
                ),
            )

            reason_counts[reason] = reason_counts.get(
                reason,
                0,
            ) + 1

        return {
            "schema_version": 1,
            "alignment_dir": str(
                alignment_dir
            ),
            "output_dir": str(
                output_dir
            ),
            "full_run": bool(
                full_run
            ),
            "quality_config": config.to_dict(),
            "summary": {
                "valid_before": len(
                    valid_before
                ),
                "valid_after": len(
                    metadata_clips
                ),
                "recovered_valid": len(
                    recovered
                ),
                "still_suspicious": len(
                    still_suspicious
                ),
                "rejected": len(
                    rejected
                ),
                "total_duration": total_duration,
                "similarity_min": min(
                    similarities
                )
                if similarities
                else 0,
                "similarity_avg": (
                    sum(
                        similarities
                    )
                    / len(
                        similarities
                    )
                    if similarities
                    else 0
                ),
                "similarity_max": max(
                    similarities
                )
                if similarities
                else 0,
                "still_suspicious_by_reason": reason_counts,
                "elapsed_seconds": time.time() - started,
            },
            "recovered_valid": recovered,
            "still_suspicious": still_suspicious,
            "rejected": rejected,
            "metadata_path": str(
                Path(
                    output_dir
                )
                / "metadata.list"
            ),
            "metadata_validation": metadata_validation,
        }

    def write_metadata(
        self,
        metadata_file,
        valid,
    ):

        lines = []

        seen_audio = set()

        for clip in valid:

            if not clip.get(
                "metadata_enabled",
                True,
            ):

                continue

            audio = clip.get(
                "audio",
                "",
            )

            if not audio or audio in seen_audio:

                continue

            seen_audio.add(
                audio
            )

            lines.append(
                f"{audio}|{clip['speaker']}|{clip['language']}|{clip['content']}"
            )

        metadata_file.write_text(
            "\n".join(
                lines
            ),
            encoding="utf-8",
        )

    def timestamp_valid(
        self,
        segment,
    ):

        return (
            segment.get(
                "end",
                0,
            )
            > segment.get(
                "start",
                0,
            )
            and bool(
                segment.get(
                    "text",
                    "",
                ).strip()
            )
        )

    def recovery_clip_id(
        self,
        audio_file,
        index,
    ):

        stem = re.sub(
            r"[^A-Za-z0-9_-]+",
            "_",
            Path(
                audio_file
            ).stem,
        ).strip(
            "_"
        )

        return f"recovery_{stem}_{index:03d}"

    def read_json(
        self,
        file,
    ):

        return json.loads(
            Path(
                file
            ).read_text(
                encoding="utf-8"
            )
        )

    def write_json(
        self,
        file,
        data,
    ):

        Path(
            file
        ).write_text(
            json.dumps(
                data,
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

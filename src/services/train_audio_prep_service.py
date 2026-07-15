from pathlib import Path
import json
import math
import re
import time

from models.alignment_quality_config import AlignmentQualityConfig
from services.alignment_service import AlignmentSegment
from services.alignment_service import AlignmentService
from services.audio_service import AudioService
from services.dataset_segmentation_service import DatasetSegmentationService
from services.dataset_review_service import DatasetReviewService
from services.runtime_service import RuntimeService


class TrainAudioPrepService:

    def __init__(self):

        self.audio = AudioService()

        self.alignment = AlignmentService()

        self.segmentation = DatasetSegmentationService()

        self.progress_events = []

    def prepare(
        self,
        source,
        dataset_dir,
        segmentation_dir,
        output_dir,
        engine_path=None,
        limit=None,
        sample_rate=32000,
        max_clip_duration=10.0,
        min_clip_duration=2.0,
        alignment_model="small",
        alignment_language="vi",
        alignment_threshold=90,
        alignment_device="auto",
        alignment_compute_type=None,
        allow_fallback=False,
        quality_config=None,
        progress_callback=None,
        review_report=None,
    ):

        config = self.create_quality_config(
            quality_config,
            sample_rate,
            max_clip_duration,
            min_clip_duration,
            alignment_model,
            alignment_language,
            alignment_threshold,
            alignment_device,
            alignment_compute_type,
            allow_fallback,
        )

        output_dir = Path(output_dir)

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

        started = time.time()

        self.progress_events = []

        self.emit_progress(
            "segmentation",
            "",
            0,
            1,
            started,
            "Dang tao segmentation dataset.",
            "info",
            progress_callback,
        )

        segmentation = self.segmentation.prepare(
            source,
            dataset_dir,
            segmentation_dir,
        )

        if self.dataset_health_has_errors(
            segmentation,
            review_report,
        ):

            report = self.create_dataset_health_blocked_report(
                segmentation,
                config,
                review_report,
            )

            manifest = {
                "schema_version": 2,
                "summary": report["summary"],
                "quality_config": report["quality_config"],
                "valid_clips": [],
                "suspicious_clips": [],
            }

            self.write_outputs(
                output_dir,
                manifest,
                report,
                [],
                report["errors"],
            )

            return {
                "valid": [],
                "suspicious": [],
                "errors": report["errors"],
                "manifest": manifest,
                "report": report,
                "progress": self.progress_events,
            }

        source_segments = segmentation.get(
            "valid",
            [],
        )

        if limit is not None:

            source_segments = source_segments[: int(limit)]

        preprocessing_tools = self.detect_gpt_sovits_tools(
            engine_path
        )

        runtime_status = RuntimeService().status()

        alignment_model_cache = self.default_model_cache(
            engine_path
        )

        alignment_runtime = self.alignment.validate_runtime(
            model=config.alignment_model,
            model_cache=alignment_model_cache,
            python_executable=(
                runtime_status.gpt_sovits_python
                or None
            ),
            cuda_available=runtime_status.cuda_available,
            device=config.alignment_device,
            compute_type=config.alignment_compute_type,
            check_load=True,
        )

        valid = []

        suspicious = []

        errors = []

        source_reports = []

        total = len(
            source_segments
        )

        for item_index, source_segment in enumerate(
            source_segments,
            start=1,
        ):

            self.emit_progress(
                "alignment",
                source_segment.get(
                    "audio",
                    "",
                ),
                item_index,
                total,
                started,
                "Dang align audio voi text bang Faster-Whisper.",
                "info",
                progress_callback,
            )

            try:

                source_report = self.process_source_segment(
                    source_segment,
                    clips_dir,
                    transcripts_dir,
                    valid,
                    suspicious,
                    errors,
                    config,
                    alignment_runtime,
                    alignment_model_cache,
                )

                source_reports.append(
                    source_report
                )

            except Exception as e:

                errors.append(
                    {
                        "audio": source_segment.get(
                            "audio",
                            "",
                        ),
                        "text": source_segment.get(
                            "text",
                            "",
                        ),
                        "code": "clip_prepare_failed",
                        "message": str(
                            e
                        ),
                    }
                )

        self.finalize_weak_sources(
            valid,
            source_reports,
            config,
        )

        report = self.create_report(
            valid,
            suspicious,
            errors,
            config,
            preprocessing_tools,
            alignment_runtime,
            segmentation,
            source_reports,
        )

        manifest = self.create_manifest(
            valid,
            suspicious,
            report,
        )

        self.write_outputs(
            output_dir,
            manifest,
            report,
            valid,
            errors,
        )

        self.emit_progress(
            "done",
            "",
            total,
            total,
            started,
            "Hoan tat chuan bi audio alignment.",
            "success",
            progress_callback,
        )

        return {
            "valid": valid,
            "suspicious": suspicious,
            "errors": errors,
            "manifest": manifest,
            "report": report,
            "progress": self.progress_events,
        }

    def dataset_health_has_errors(
        self,
        segmentation,
        review_report=None,
    ):

        health = segmentation.get(
            "health",
            {},
        )

        if (
            health.get(
                "blocking_errors",
                0,
            )
            <= 0
        ):

            return False

        if review_report is None:

            return True

        return not DatasetReviewService().can_train(
            dataset_result=segmentation.get(
                "dataset",
                {},
            ),
            review_report=review_report,
        )

    def dataset_health_reviewed(
        self,
        segmentation,
        review_report=None,
    ):

        return (
            not self.dataset_health_has_errors(
                segmentation,
                review_report,
            )
        )

    def create_dataset_health_blocked_report(
        self,
        segmentation,
        config,
        review_report=None,
    ):

        dataset = segmentation.get(
            "dataset",
            {},
        )

        errors = dataset.get(
            "errors",
            [],
        )

        health = segmentation.get(
            "health",
            {},
        )

        return {
            "schema_version": 2,
            "quality_config": config.to_dict(),
            "summary": {
                "valid_clips": 0,
                "metadata_clips": 0,
                "suspicious_clips": 0,
                "errors": len(
                    errors
                ),
                "valid_duration": 0,
                "suspicious_duration": 0,
                "sample_rate": config.sample_rate,
                "source_segments": 0,
                "dataset_health": health,
                "dataset_review": review_report or {},
                "blocked": True,
                "block_reason": "dataset_health_failed",
            },
            "dataset_health": health,
            "dataset_review": review_report or {},
            "valid": [],
            "suspicious": [],
            "errors": errors,
            "progress": self.progress_events,
        }

    def create_quality_config(
        self,
        quality_config,
        sample_rate,
        max_clip_duration,
        min_clip_duration,
        alignment_model,
        alignment_language,
        alignment_threshold,
        alignment_device,
        alignment_compute_type,
        allow_fallback,
    ):

        if quality_config is not None:

            return AlignmentQualityConfig.from_dict(
                quality_config
            )

        return AlignmentQualityConfig(
            similarity_threshold=float(
                alignment_threshold
            ),
            min_clip_duration=float(
                min_clip_duration
            ),
            max_clip_duration=float(
                max_clip_duration
            ),
            sample_rate=int(
                sample_rate
            ),
            language=alignment_language,
            alignment_model=alignment_model,
            alignment_device=alignment_device,
            alignment_compute_type=alignment_compute_type,
            allow_ratio_fallback=bool(
                allow_fallback
            ),
        )

    def process_source_segment(
        self,
        source_segment,
        clips_dir,
        transcripts_dir,
        valid,
        suspicious,
        errors,
        config,
        alignment_runtime,
        alignment_model_cache,
    ):

        audio_file = Path(
            source_segment["audio"]
        )

        text = source_segment.get(
            "content",
            "",
        )

        source_report = self.create_source_report(
            source_segment
        )

        try:

            matches = self.alignment.align(
                audio_file,
                text,
                threshold=config.similarity_threshold,
                language=config.language,
                model=config.alignment_model,
                device=alignment_runtime.get(
                    "device",
                    config.alignment_device,
                ),
                compute_type=alignment_runtime.get(
                    "compute_type",
                    config.alignment_compute_type,
                ),
                model_path=alignment_runtime.get(
                    "model_path",
                    "",
                ),
                model_cache=alignment_model_cache,
                python_executable=alignment_runtime.get(
                    "python_executable",
                    None,
                ),
                cuda_available=(
                    alignment_runtime.get(
                        "device",
                        "cpu",
                    )
                    == "cuda"
                ),
            )

        except Exception as e:

            item = self.create_suspicious(
                source_segment,
                "",
                "asr_failed",
                f"Khong chay duoc Faster-Whisper alignment: {e}",
                0,
                0,
                asr_text="",
                similarity=0,
            )

            suspicious.append(
                item
            )

            self.update_source_report(
                source_report,
                item,
            )

            return source_report

        if not matches:

            item = self.create_suspicious(
                source_segment,
                text,
                "no_alignment_match",
                "ASR chay xong nhung khong co doan nao khop text goc du nguong.",
                0,
                0,
                asr_text="",
                similarity=0,
            )

            suspicious.append(
                item
            )

            self.update_source_report(
                source_report,
                item,
            )

            return source_report

        for index, match in enumerate(
            matches,
            start=1,
        ):

            candidates = self.split_match(
                match,
                config,
            )

            for sub_index, candidate in enumerate(
                candidates,
                start=1,
            ):

                if source_report["skipped_entire_file"]:

                    break

                self.create_aligned_clip(
                    source_segment,
                    candidate,
                    index,
                    sub_index,
                    clips_dir,
                    transcripts_dir,
                    valid,
                    suspicious,
                    config,
                    source_report,
                )

                if self.source_error_rate_exceeded(
                    source_report,
                    config,
                ):

                    item = self.create_suspicious(
                        source_segment,
                        candidate.text,
                        "source_error_rate_exceeded",
                        "Ty le loi/nghi ngo cua source file vuot nguong cho phep.",
                        candidate.start,
                        max(
                            0.0,
                            candidate.end - candidate.start,
                        ),
                        asr_text=candidate.asr_text,
                        similarity=candidate.score,
                    )

                    suspicious.append(
                        item
                    )

                    self.update_source_report(
                        source_report,
                        item,
                    )

                    source_report["skipped_entire_file"] = True

                    source_report["skip_reason"] = "source_error_rate_exceeded"

                    break

        return source_report

    def split_match(
        self,
        match,
        config,
    ):

        duration = float(
            match.end
        ) - float(
            match.start
        )

        if duration <= config.max_clip_duration:

            return [
                match
            ]

        words = [
            word
            for word in (
                match.words
                or []
            )
            if word.get(
                "word",
                "",
            ).strip()
            and word.get(
                "end",
                0,
            )
            > word.get(
                "start",
                0,
            )
        ]

        if not words:

            return [
                match
            ]

        sentence_chunks = self.split_words_by_sentence(
            words,
            config,
        )

        final_chunks = []

        for chunk in sentence_chunks:

            if self.words_duration(
                chunk
            ) <= config.max_clip_duration:

                final_chunks.append(
                    chunk
                )

                continue

            final_chunks.extend(
                self.split_words_by_duration(
                    chunk,
                    config,
                )
            )

        segments = []

        original_sentences = self.split_sentences(
            match.text
        )

        for chunk_index, chunk in enumerate(
            final_chunks
        ):

            if not chunk:

                continue

            asr_text = self.words_text(
                chunk
            )

            original_text = (
                original_sentences[chunk_index]
                if chunk_index < len(
                    original_sentences
                )
                else match.text
            )

            score = self.score_chunk_text(
                asr_text,
                original_text,
            )

            segments.append(
                AlignmentSegment(
                    text=original_text,
                    start=float(
                        chunk[0]["start"]
                    ),
                    end=float(
                        chunk[-1]["end"]
                    ),
                    score=float(
                        score
                    ),
                    asr_text=asr_text,
                    language=match.language,
                    words=chunk,
                )
            )

        return segments or [
            match
        ]

    def score_chunk_text(
        self,
        asr_text,
        original_text,
    ):

        asr_norm = self.alignment.normalize(
            asr_text
        )

        original_norm = self.alignment.normalize(
            original_text
        )

        asr_tokens = [
            token
            for token in re.split(
                r"\W+",
                asr_norm,
            )
            if token
        ]

        original_tokens = [
            token
            for token in re.split(
                r"\W+",
                original_norm,
            )
            if token
        ]

        if (
            asr_tokens
            and original_tokens
            and set(
                asr_tokens
            ).issubset(
                set(
                    original_tokens
                )
            )
        ):

            return 100.0

        return self.alignment.score_text(
            asr_text,
            original_text,
        )

    def split_words_by_sentence(
        self,
        words,
        config,
    ):

        chunks = []

        current = []

        for word in words:

            current.append(
                word
            )

            token = word.get(
                "word",
                "",
            ).strip()

            duration = self.words_duration(
                current
            )

            if (
                self.is_sentence_boundary(
                    token
                )
                and duration >= config.min_clip_duration
            ):

                chunks.append(
                    current
                )

                current = []

        if current:

            if (
                chunks
                and self.words_duration(
                    current
                )
                < config.min_clip_duration
            ):

                chunks[-1].extend(
                    current
                )

            else:

                chunks.append(
                    current
                )

        return chunks

    def split_words_by_duration(
        self,
        words,
        config,
    ):

        chunks = []

        current = []

        for word in words:

            if not current:

                current.append(
                    word
                )

                continue

            next_duration = (
                float(
                    word["end"]
                )
                - float(
                    current[0]["start"]
                )
            )

            if (
                next_duration > config.target_clip_duration
                and self.words_duration(
                    current
                )
                >= config.min_clip_duration
            ):

                chunks.append(
                    current
                )

                current = [
                    word
                ]

                continue

            current.append(
                word
            )

        if current:

            if (
                chunks
                and self.words_duration(
                    current
                )
                < config.min_clip_duration
            ):

                chunks[-1].extend(
                    current
                )

            else:

                chunks.append(
                    current
                )

        safe_chunks = []

        for chunk in chunks:

            if self.words_duration(
                chunk
            ) <= config.max_clip_duration:

                safe_chunks.append(
                    chunk
                )

                continue

            safe_chunks.extend(
                self.force_split_words(
                    chunk,
                    config,
                )
            )

        return safe_chunks

    def force_split_words(
        self,
        words,
        config,
    ):

        chunks = []

        current = []

        for word in words:

            if (
                current
                and float(
                    word["end"]
                )
                - float(
                    current[0]["start"]
                )
                > config.max_clip_duration
            ):

                chunks.append(
                    current
                )

                current = []

            current.append(
                word
            )

        if current:

            chunks.append(
                current
            )

        return chunks

    def create_aligned_clip(
        self,
        source_segment,
        match,
        index,
        sub_index,
        clips_dir,
        transcripts_dir,
        valid,
        suspicious,
        config,
        source_report,
    ):

        audio_file = Path(
            source_segment["audio"]
        )

        start = max(
            0.0,
            float(
                match.start
            ),
        )

        end = float(
            match.end
        )

        duration = end - start

        invalid = self.validate_candidate(
            source_segment,
            match,
            start,
            end,
            duration,
            config,
        )

        if invalid:

            suspicious.append(
                invalid
            )

            self.update_source_report(
                source_report,
                invalid,
            )

            return

        clip_id = f"{source_segment['id']}_{index:03d}_{sub_index:03d}"

        clip_file = clips_dir / f"{clip_id}.wav"

        transcript_file = transcripts_dir / f"{clip_id}.txt"

        try:

            self.audio.convert_segment_wav(
                audio_file,
                clip_file,
                start,
                duration,
                sample_rate=config.sample_rate,
            )

            clip_info = self.audio.probe(
                clip_file
            )

        except Exception as e:

            item = self.create_suspicious(
                source_segment,
                match.text,
                "audio_probe_failed",
                f"Khong tao/doc duoc clip WAV bang ffmpeg/ffprobe: {e}",
                start,
                duration,
                asr_text=match.asr_text,
                similarity=match.score,
            )

            suspicious.append(
                item
            )

            self.update_source_report(
                source_report,
                item,
            )

            return

        audio_invalid = self.validate_output_audio(
            source_segment,
            match,
            clip_info,
            start,
            duration,
            config,
        )

        if audio_invalid:

            suspicious.append(
                audio_invalid
            )

            self.update_source_report(
                source_report,
                audio_invalid,
            )

            return

        transcript_file.write_text(
            match.text,
            encoding="utf-8",
        )

        clip = {
            "id": clip_id,
            "status": "valid",
            "audio": str(
                clip_file
            ),
            "transcript": str(
                transcript_file
            ),
            "source_audio": str(
                audio_file
            ),
            "source_text": source_segment.get(
                "text",
                "",
            ),
            "speaker": self.speaker_name(
                audio_file
            ),
            "language": config.language,
            "content": match.text,
            "asr_text": match.asr_text,
            "match_score": float(
                match.score
            ),
            "start": start,
            "end": end,
            "duration": clip_info["duration"],
            "sample_rate": clip_info["sample_rate"],
            "channels": clip_info["channels"],
            "codec": clip_info["codec"],
            "metadata_enabled": True,
        }

        valid.append(
            clip
        )

        self.update_source_report(
            source_report,
            clip,
        )

    def validate_candidate(
        self,
        source_segment,
        match,
        start,
        end,
        duration,
        config,
    ):

        if end <= start:

            return self.create_suspicious(
                source_segment,
                match.text,
                "timestamp_invalid",
                "Timestamp ASR khong hop le.",
                start,
                duration,
                asr_text=match.asr_text,
                similarity=match.score,
            )

        if not (
            match.text
            or ""
        ).strip():

            return self.create_suspicious(
                source_segment,
                match.text,
                "no_alignment_match",
                "Transcript rong sau khi align.",
                start,
                duration,
                asr_text=match.asr_text,
                similarity=match.score,
            )

        if float(
            match.score
        ) < config.similarity_threshold:

            return self.create_suspicious(
                source_segment,
                match.text,
                "similarity_too_low",
                "Similarity thap hon nguong quality-first.",
                start,
                duration,
                asr_text=match.asr_text,
                similarity=match.score,
            )

        if duration < config.min_clip_duration:

            return self.create_suspicious(
                source_segment,
                match.text,
                "clip_too_short",
                "Clip ASR ngan hon nguong toi thieu.",
                start,
                duration,
                asr_text=match.asr_text,
                similarity=match.score,
            )

        if duration > config.max_clip_duration:

            return self.create_suspicious(
                source_segment,
                match.text,
                "clip_too_long",
                "Clip ASR dai hon nguong toi da sau khi split.",
                start,
                duration,
                asr_text=match.asr_text,
                similarity=match.score,
            )

        return None

    def validate_output_audio(
        self,
        source_segment,
        match,
        clip_info,
        start,
        duration,
        config,
    ):

        if (
            clip_info.get(
                "channels"
            )
            != 1
            or clip_info.get(
                "codec"
            )
            != "pcm_s16le"
            or clip_info.get(
                "sample_rate"
            )
            != config.sample_rate
        ):

            return self.create_suspicious(
                source_segment,
                match.text,
                "audio_probe_failed",
                "Clip WAV khong dung mono/pcm_s16le/sample rate.",
                start,
                duration,
                asr_text=match.asr_text,
                similarity=match.score,
            )

        return None

    def process_fallback_source_segment(
        self,
        source_segment,
        clips_dir,
        transcripts_dir,
        valid,
        suspicious,
        sample_rate,
        max_clip_duration,
        min_clip_duration,
    ):

        audio_file = Path(
            source_segment["audio"]
        )

        duration = float(
            source_segment["duration"]
        )

        text = source_segment.get(
            "content",
            "",
        )

        chunks = self.create_text_chunks(
            text,
            duration,
            max_clip_duration,
        )

        cursor = 0.0

        text_length = sum(
            len(chunk)
            for chunk in chunks
        )

        for index, chunk in enumerate(
            chunks,
            start=1,
        ):

            if index == len(chunks):

                clip_duration = max(
                    0.0,
                    duration - cursor,
                )

            else:

                ratio = len(chunk) / max(
                    text_length,
                    1,
                )

                clip_duration = duration * ratio

            if clip_duration < min_clip_duration:

                suspicious.append(
                    self.create_suspicious(
                        source_segment,
                        chunk,
                        "fallback_clip_too_short",
                        "Fallback theo ty le tao clip ngan hon nguong toi thieu.",
                        cursor,
                        clip_duration,
                    )
                )

                cursor += clip_duration

                continue

            clip_id = f"{source_segment['id']}_fallback_{index:03d}"

            clip_file = clips_dir / f"{clip_id}.wav"

            transcript_file = transcripts_dir / f"{clip_id}.txt"

            self.audio.convert_segment_wav(
                audio_file,
                clip_file,
                cursor,
                clip_duration,
                sample_rate=sample_rate,
            )

            transcript_file.write_text(
                chunk,
                encoding="utf-8",
            )

            clip_info = self.audio.probe(
                clip_file
            )

            suspicious.append(
                {
                    "id": clip_id,
                    "status": "suspicious",
                    "code": "fallback_ratio_unverified",
                    "message": "Clip duoc tao bang fallback ty le ky tu, chua co ASR match.",
                    "audio": str(
                        clip_file
                    ),
                    "transcript": str(
                        transcript_file
                    ),
                    "source_audio": str(
                        audio_file
                    ),
                    "source_text": source_segment.get(
                        "text",
                        "",
                    ),
                    "start": cursor,
                    "duration": clip_info["duration"],
                    "sample_rate": clip_info["sample_rate"],
                    "channels": clip_info["channels"],
                    "text_length": len(
                        chunk
                    ),
                }
            )

            cursor += clip_duration

    def create_text_chunks(
        self,
        text,
        duration,
        max_clip_duration,
    ):

        sentences = self.split_sentences(
            text
        )

        if not sentences:

            return []

        chunk_count = max(
            1,
            math.ceil(
                duration / max_clip_duration
            ),
        )

        target_length = max(
            1,
            math.ceil(
                len(text) / chunk_count
            ),
        )

        chunks = []

        current = []

        current_length = 0

        for sentence in sentences:

            if (
                current
                and current_length + len(sentence) > target_length
                and len(chunks) < chunk_count - 1
            ):

                chunks.append(
                    " ".join(
                        current
                    ).strip()
                )

                current = []

                current_length = 0

            current.append(
                sentence
            )

            current_length += len(
                sentence
            )

        if current:

            chunks.append(
                " ".join(
                    current
                ).strip()
            )

        return [
            chunk
            for chunk in chunks
            if chunk
        ]

    def split_sentences(
        self,
        text,
    ):

        normalized = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        if not normalized:

            return []

        parts = re.findall(
            r".+?(?:[.!?。！？…]+|$)",
            normalized,
        )

        return [
            part.strip()
            for part in parts
            if part.strip()
        ]

    def create_suspicious(
        self,
        source_segment,
        text,
        code,
        message,
        start,
        duration,
        asr_text="",
        similarity=0,
    ):

        return {
            "status": "suspicious",
            "code": code,
            "message": message,
            "source_audio": source_segment.get(
                "audio",
                "",
            ),
            "source_text": source_segment.get(
                "text",
                "",
            ),
            "start": float(
                start or 0
            ),
            "end": float(
                start or 0
            )
            + float(
                duration or 0
            ),
            "duration": float(
                duration or 0
            ),
            "similarity": float(
                similarity or 0
            ),
            "original_text": text,
            "asr_text": asr_text or "",
            "text_length": len(
                text or ""
            ),
        }

    def create_source_report(
        self,
        source_segment,
    ):

        return {
            "source_audio": source_segment.get(
                "audio",
                "",
            ),
            "source_text": source_segment.get(
                "text",
                "",
            ),
            "total_segments": 0,
            "valid_segments": 0,
            "suspicious_segments": 0,
            "error_segments": 0,
            "skipped_entire_file": False,
            "skip_reason": "",
            "weak_source": False,
            "similarity_min": None,
            "similarity_avg": 0,
            "similarity_max": None,
            "valid_duration": 0,
            "_similarities": [],
        }

    def update_source_report(
        self,
        report,
        item,
    ):

        report["total_segments"] += 1

        if item.get(
            "status"
        ) == "valid":

            report["valid_segments"] += 1

            report["valid_duration"] += float(
                item.get(
                    "duration",
                    0,
                )
            )

            similarity = item.get(
                "match_score",
                item.get(
                    "similarity",
                    0,
                ),
            )

        elif item.get(
            "status"
        ) == "error":

            report["error_segments"] += 1

            similarity = item.get(
                "similarity",
                0,
            )

        else:

            report["suspicious_segments"] += 1

            similarity = item.get(
                "similarity",
                0,
            )

        if similarity is not None:

            report["_similarities"].append(
                float(
                    similarity
                )
            )

            values = report["_similarities"]

            report["similarity_min"] = min(
                values
            )

            report["similarity_avg"] = sum(
                values
            ) / len(
                values
            )

            report["similarity_max"] = max(
                values
            )

    def source_error_rate_exceeded(
        self,
        report,
        config,
    ):

        total = report.get(
            "total_segments",
            0,
        )

        if total <= 0:

            return False

        bad = (
            report.get(
                "suspicious_segments",
                0,
            )
            + report.get(
                "error_segments",
                0,
            )
        )

        return (
            bad / total
        ) > config.max_source_error_rate

    def finalize_weak_sources(
        self,
        valid,
        source_reports,
        config,
    ):

        weak_sources = set()

        for report in source_reports:

            if (
                report.get(
                    "valid_segments",
                    0,
                )
                < config.min_valid_segments_per_source
            ):

                report["weak_source"] = True

                weak_sources.add(
                    report.get(
                        "source_audio",
                        "",
                    )
                )

            report.pop(
                "_similarities",
                None,
            )

        if config.include_weak_source_in_metadata:

            return

        for clip in valid:

            if clip.get(
                "source_audio"
            ) in weak_sources:

                clip["metadata_enabled"] = False

                clip["metadata_skip_reason"] = "weak_source"

    def words_duration(
        self,
        words,
    ):

        if not words:

            return 0

        return float(
            words[-1]["end"]
        ) - float(
            words[0]["start"]
        )

    def words_text(
        self,
        words,
    ):

        return " ".join(
            word.get(
                "word",
                "",
            ).strip()
            for word in words
            if word.get(
                "word",
                "",
            ).strip()
        ).strip()

    def is_sentence_boundary(
        self,
        token,
    ):

        return bool(
            re.search(
                r"[.!?。！？…]$",
                token or "",
            )
        )

    def emit_progress(
        self,
        stage,
        current_file,
        current_item,
        total_items,
        started,
        message,
        level,
        progress_callback=None,
    ):

        elapsed = max(
            0.0,
            time.time() - started,
        )

        total_items = max(
            0,
            int(
                total_items or 0
            ),
        )

        current_item = max(
            0,
            int(
                current_item or 0
            ),
        )

        percent = (
            current_item / total_items * 100
            if total_items
            else 0
        )

        estimated = (
            elapsed / current_item * (total_items - current_item)
            if current_item and total_items and current_item < total_items
            else 0
        )

        payload = {
            "stage": stage,
            "current_file": current_file,
            "current_item": current_item,
            "total_items": total_items,
            "percent": percent,
            "elapsed_seconds": elapsed,
            "estimated_remaining_seconds": estimated,
            "message": message,
            "level": level,
        }

        self.progress_events.append(
            payload
        )

        if progress_callback:

            progress_callback(
                payload
            )

        return payload

    def speaker_name(
        self,
        audio_file,
    ):

        return Path(
            audio_file
        ).parent.name or "speaker"

    def detect_gpt_sovits_tools(
        self,
        engine_path,
    ):

        if not engine_path:

            return {
                "engine_path": "",
                "available": False,
                "tools": {},
            }

        root = Path(
            engine_path
        )

        tools = {
            "slice_audio": root / "tools" / "slice_audio.py",
            "slicer2": root / "tools" / "slicer2.py",
            "asr_fasterwhisper": root / "tools" / "asr" / "fasterwhisper_asr.py",
            "asr_funasr": root / "tools" / "asr" / "funasr_asr.py",
            "denoise": root / "tools" / "cmd-denoise.py",
            "format_text": root / "GPT_SoVITS" / "prepare_datasets" / "1-get-text.py",
            "hubert_wav32k": root / "GPT_SoVITS" / "prepare_datasets" / "2-get-hubert-wav32k.py",
            "semantic": root / "GPT_SoVITS" / "prepare_datasets" / "3-get-semantic.py",
        }

        return {
            "engine_path": str(
                root
            ),
            "available": root.exists(),
            "tools": {
                name: {
                    "path": str(
                        path
                    ),
                    "exists": path.exists(),
                }
                for name, path in tools.items()
            },
        }

    def default_model_cache(
        self,
        engine_path,
    ):

        if not engine_path:

            return ""

        return str(
            Path(engine_path)
            / "tools"
            / "asr"
            / "models"
        )

    def create_report(
        self,
        valid,
        suspicious,
        errors,
        config,
        preprocessing_tools,
        alignment_runtime,
        segmentation,
        source_reports,
    ):

        valid_duration = sum(
            item["duration"]
            for item in valid
        )

        suspicious_duration = sum(
            item.get(
                "duration",
                0,
            )
            for item in suspicious
        )

        metadata_clips = [
            item
            for item in valid
            if item.get(
                "metadata_enabled",
                True,
            )
        ]

        return {
            "schema_version": 2,
            "quality_config": config.to_dict(),
            "summary": {
                "valid_clips": len(
                    valid
                ),
                "metadata_clips": len(
                    metadata_clips
                ),
                "suspicious_clips": len(
                    suspicious
                ),
                "errors": len(
                    errors
                ),
                "valid_duration": valid_duration,
                "suspicious_duration": suspicious_duration,
                "sample_rate": config.sample_rate,
                "source_segments": len(
                    segmentation.get(
                        "valid",
                        [],
                    )
                ),
            },
            "preprocessing_tools": preprocessing_tools,
            "alignment_runtime": alignment_runtime,
            "source_reports": source_reports,
            "valid": valid,
            "suspicious": suspicious,
            "errors": errors,
            "progress": self.progress_events,
        }

    def create_manifest(
        self,
        valid,
        suspicious,
        report,
    ):

        return {
            "schema_version": 2,
            "summary": report["summary"],
            "quality_config": report["quality_config"],
            "sample_rate": report["summary"]["sample_rate"],
            "valid_clips": [
                self.serialize_clip(
                    clip
                )
                for clip in valid
            ],
            "suspicious_clips": [
                self.serialize_clip(
                    clip
                )
                for clip in suspicious
                if "audio" in clip
            ],
        }

    def serialize_clip(
        self,
        clip,
    ):

        return {
            key: value
            for key, value in clip.items()
            if key not in (
                "content",
                "message",
            )
        }

    def write_outputs(
        self,
        output_dir,
        manifest,
        report,
        valid,
        errors,
    ):

        self.write_json(
            output_dir / "alignment_manifest.json",
            manifest,
        )

        self.write_json(
            output_dir / "alignment_report.json",
            report,
        )

        metadata = []

        for clip in valid:

            if not clip.get(
                "metadata_enabled",
                True,
            ):

                continue

            metadata.append(
                f"{clip['audio']}|{clip['speaker']}|{clip['language']}|{clip['content']}"
            )

        (output_dir / "metadata.list").write_text(
            "\n".join(
                metadata
            ),
            encoding="utf-8",
        )

        (output_dir / "errors.log").write_text(
            "\n".join(
                f"{error.get('audio', '')} | {error.get('code', '')} | {error.get('message', '')}"
                for error in errors
            ),
            encoding="utf-8",
        )

    def write_json(
        self,
        file,
        data,
    ):

        with open(
            file,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False,
            )

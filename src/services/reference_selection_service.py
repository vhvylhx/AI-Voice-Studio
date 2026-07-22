from __future__ import annotations

import hashlib
import json
import math
import statistics
import sys
import wave
from array import array
from collections import Counter
from pathlib import Path


class ReferenceSelectionService:
    """Chọn reference từ metadata/alignment authority, không dùng candidate cache làm authority."""

    SCHEMA_VERSION = 1
    DEFAULT_TOP_LIMIT = 50
    DEFAULT_FREEZE_LIMIT = 20
    MIN_DURATION_SECONDS = 1.5
    MAX_DURATION_SECONDS = 15.0
    MAX_CLIPPING_RATIO = 0.005
    MAX_DC_OFFSET = 0.05
    MAX_LEADING_SILENCE_SECONDS = 1.5
    MAX_TRAILING_SILENCE_SECONDS = 1.5
    MIN_SPEECH_RATIO = 0.45
    MIN_HARMONIC_NOISE_INDICATOR = 0.08
    BOUNDARY_FRAGMENT_PENALTY = 0.25
    REQUIRED_EVIDENCE_KEYS = (
        "id",
        "source_audio",
        "source_text",
        "alignment_similarity",
    )
    OPTIONAL_EVIDENCE_KEYS = (
        "duplicate",
        "suspicious",
        "invalid",
        "ai_generated",
        "music_heavy",
        "multiple_speakers",
    )

    def select(
        self,
        metadata_file,
        output_dir,
        *,
        alignment_manifest_file=None,
        alignment_report_file=None,
        dataset_health_file=None,
        calibration_evidence=None,
        top_limit=DEFAULT_TOP_LIMIT,
        freeze_limit=DEFAULT_FREEZE_LIMIT,
    ):
        """Scan authority dataset, rank, diversify và freeze holdout bất biến."""
        metadata_path = Path(metadata_file)
        output_path = Path(output_dir)

        if top_limit < 1:
            raise ValueError("top_limit phai lon hon 0.")
        if freeze_limit < 1:
            raise ValueError("freeze_limit phai lon hon 0.")
        if freeze_limit > top_limit:
            raise ValueError("freeze_limit khong duoc lon hon top_limit.")
        if not metadata_path.is_file():
            raise FileNotFoundError(
                f"Khong tim thay metadata authority: {metadata_path}"
            )

        alignment_manifest = self.load_json(alignment_manifest_file)
        alignment_report = self.load_json(alignment_report_file)
        dataset_health = self.load_json(dataset_health_file)
        calibration = self.normalize_calibration_evidence(calibration_evidence)

        authority_rows = self.read_metadata(metadata_path)
        evidence_index = self.build_evidence_index(
            alignment_manifest,
            alignment_report,
            dataset_health,
        )

        scanned = []
        rejected = []
        seen_hashes = set()

        for row in authority_rows:
            candidate = self.scan_candidate(
                row,
                metadata_path.parent,
                evidence_index,
                seen_hashes,
            )
            scanned.append(candidate)
            if candidate["filter_status"] == "rejected":
                rejected.append(candidate)

        accepted = [
            candidate
            for candidate in scanned
            if candidate["filter_status"] == "accepted"
        ]
        self.apply_pitch_distribution(accepted)
        for candidate in accepted:
            candidate["score"] = self.score_candidate(candidate, calibration)

        ranked = sorted(
            accepted,
            key=lambda item: (
                -item["score"]["total"],
                item["clip_id"],
            ),
        )
        top50 = ranked[:top_limit]
        diversified = self.diversify(top50, freeze_limit)
        self.freeze_ids(diversified)

        output_path.mkdir(parents=True, exist_ok=True)
        ranking_manifest = self.create_ranking_manifest(
            metadata_path,
            calibration,
            scanned,
            rejected,
            top50,
            diversified,
        )
        holdout_manifest = self.create_holdout_manifest(
            metadata_path,
            diversified,
        )
        self.write_json(
            output_path / "reference_selection_manifest.json",
            ranking_manifest,
        )
        self.write_json(
            output_path / "evaluation_holdout_manifest.json",
            holdout_manifest,
        )
        selection_report = self.create_selection_report(
            metadata_path,
            ranking_manifest,
            holdout_manifest,
        )
        self.write_json(
            output_path / "selection_report.json",
            selection_report,
        )

        return {
            "status": "READY",
            "dataset_scanned": len(scanned),
            "filter_summary": ranking_manifest["filter_summary"],
            "ranking_summary": ranking_manifest["ranking_summary"],
            "calibration_evidence": calibration,
            "top50": top50,
            "top20": diversified,
            "ranking_manifest": ranking_manifest,
            "holdout_manifest": holdout_manifest,
            "selection_report": selection_report,
            "blockers": [],
        }

    def read_metadata(self, metadata_path):
        rows = []
        for line_number, line in enumerate(
            metadata_path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if not line.strip():
                continue
            parts = line.split("|", 3)
            if len(parts) != 4:
                rows.append(
                    {
                        "clip_id": f"metadata-line-{line_number}",
                        "metadata_line": line_number,
                        "audio": "",
                        "speaker": "",
                        "language": "",
                        "transcript": "",
                        "metadata_error": "metadata_row_invalid",
                    }
                )
                continue
            audio, speaker, language, transcript = parts
            rows.append(
                {
                    "clip_id": self.clip_id(audio, line_number),
                    "metadata_line": line_number,
                    "audio": audio.strip(),
                    "speaker": speaker.strip(),
                    "language": language.strip(),
                    "transcript": transcript.strip(),
                }
            )
        return rows

    def scan_candidate(self, row, metadata_root, evidence_index, seen_hashes):
        candidate = dict(row)
        candidate["rejection_reasons"] = []
        evidence = self.resolve_evidence(row, evidence_index)
        candidate["evidence_presence"] = evidence.pop("_present_keys", [])
        candidate["evidence"] = evidence
        candidate["evidence_warnings"] = []
        source_audio = candidate["evidence"].get("source_audio")
        candidate["source_id"] = (
            str(source_audio).replace("\\", "/")
            if source_audio
            else self.source_id(row["audio"])
        )
        candidate["chapter_id"] = (
            Path(source_audio).stem
            if source_audio
            else self.chapter_id(row["audio"])
        )
        candidate["metrics"] = {}
        self.apply_evidence_policy(candidate)

        if row.get("metadata_error"):
            candidate["rejection_reasons"].append(row["metadata_error"])
        if not row["transcript"]:
            candidate["rejection_reasons"].append("transcript_empty")
        candidate["text_quality_flags"] = self.text_quality_flags(
            row.get("transcript", "")
        )

        audio_path = self.resolve_audio_path(row["audio"], metadata_root)
        candidate["audio_path"] = str(audio_path)

        if not audio_path.is_file():
            candidate["rejection_reasons"].append("audio_missing")
        else:
            try:
                audio_metrics = self.audio_metrics(audio_path)
                candidate["metrics"] = audio_metrics
                candidate["audio_sha256"] = self.sha256(audio_path)
                if candidate["audio_sha256"] in seen_hashes:
                    candidate["rejection_reasons"].append("duplicate")
                else:
                    seen_hashes.add(candidate["audio_sha256"])
            except (OSError, wave.Error, ValueError):
                candidate["rejection_reasons"].append("corrupt_or_unreadable")

        self.apply_filter_rules(candidate)
        candidate["filter_status"] = (
            "rejected"
            if candidate["rejection_reasons"]
            else "accepted"
        )
        return candidate

    def apply_evidence_policy(self, candidate):
        presence = set(candidate["evidence_presence"])
        missing_required = [
            key
            for key in self.REQUIRED_EVIDENCE_KEYS
            if key not in presence
        ]
        missing_optional = [
            key
            for key in self.OPTIONAL_EVIDENCE_KEYS
            if key not in presence
        ]
        candidate["evidence_integrity"] = {
            "required": {
                key: key in presence
                for key in self.REQUIRED_EVIDENCE_KEYS
            },
            "optional": {
                key: key in presence
                for key in self.OPTIONAL_EVIDENCE_KEYS
            },
            "missing_required": missing_required,
            "missing_optional": missing_optional,
        }
        candidate["evidence_warnings"].extend(
            f"optional_evidence_missing_{key}"
            for key in missing_optional
        )
        candidate["rejection_reasons"].extend(
            f"required_evidence_missing_{key}"
            for key in missing_required
        )

    def apply_filter_rules(self, candidate):
        evidence = candidate["evidence"]
        metrics = candidate["metrics"]
        for key, reason in (
            ("duplicate", "duplicate"),
            ("suspicious", "suspicious"),
            ("invalid", "invalid"),
            ("ai_generated", "ai_generated"),
            ("music_heavy", "music_heavy"),
            ("multiple_speakers", "multiple_speakers"),
        ):
            if evidence.get(key) is True:
                candidate["rejection_reasons"].append(reason)

        if not metrics:
            return
        if metrics["duration_seconds"] < self.MIN_DURATION_SECONDS:
            candidate["rejection_reasons"].append("duration_too_short")
        if metrics["duration_seconds"] > self.MAX_DURATION_SECONDS:
            candidate["rejection_reasons"].append("duration_too_long")
        if metrics["clipping_ratio"] > self.MAX_CLIPPING_RATIO:
            candidate["rejection_reasons"].append("clipping")
        if abs(metrics["dc_offset"]) > self.MAX_DC_OFFSET:
            candidate["rejection_reasons"].append("dc_offset_excessive")
        if metrics["speech_ratio"] < self.MIN_SPEECH_RATIO:
            candidate["rejection_reasons"].append("speech_ratio_low")
        if (
            metrics["harmonic_noise_indicator"] is not None
            and metrics["harmonic_noise_indicator"]
            < self.MIN_HARMONIC_NOISE_INDICATOR
        ):
            candidate["rejection_reasons"].append("noise_high")

        candidate["rejection_reasons"] = sorted(
            set(candidate["rejection_reasons"])
        )

    def resolve_audio_path(self, audio, metadata_root):
        audio_path = Path(audio)
        if audio_path.is_absolute():
            return audio_path

        metadata_relative = metadata_root / audio_path
        if metadata_relative.is_file():
            return metadata_relative

        cwd_relative = Path.cwd() / audio_path
        if cwd_relative.is_file():
            return cwd_relative

        return metadata_relative

    def audio_metrics(self, audio_path):
        if audio_path.suffix.lower() != ".wav":
            raise ValueError("Chi WAV PCM duoc phan tich trong selection engine.")
        with wave.open(str(audio_path), "rb") as handle:
            channels = handle.getnchannels()
            sample_rate = handle.getframerate()
            sample_width = handle.getsampwidth()
            frame_count = handle.getnframes()
            raw = handle.readframes(frame_count)

        if not sample_rate or channels < 1 or sample_width not in (2, 4):
            raise ValueError("PCM WAV khong hop le.")
        values = self.decode_pcm(raw, sample_width, channels)
        if not values or not all(math.isfinite(value) for value in values):
            raise ValueError("Audio rong hoac khong huu han.")

        duration = len(values) / sample_rate
        peak = max(abs(value) for value in values)
        rms = math.sqrt(sum(value * value for value in values) / len(values))
        clipping = sum(1 for value in values if abs(value) >= 0.99) / len(values)
        dc_offset = sum(values) / len(values)
        leading, trailing, active = self.silence_edges(values, sample_rate, peak)
        pitch_values = self.pitch_values(values, sample_rate)
        hnr = self.harmonic_noise_indicator(values, sample_rate)

        return {
            "duration_seconds": round(duration, 6),
            "sample_rate": sample_rate,
            "channels": channels,
            "peak": peak,
            "rms": rms,
            "clipping_ratio": clipping,
            "dc_offset": dc_offset,
            "leading_silence_seconds": leading,
            "trailing_silence_seconds": trailing,
            "speech_ratio": active / duration if duration else 0.0,
            "pitch_median_hz": statistics.median(pitch_values) if pitch_values else None,
            "pitch_stability_hz": (
                statistics.pstdev(pitch_values)
                if len(pitch_values) > 1
                else None
            ),
            "harmonic_noise_indicator": hnr,
        }

    def decode_pcm(self, raw, sample_width, channels):
        type_code = "h" if sample_width == 2 else "i"
        scale = 32768.0 if sample_width == 2 else 2147483648.0
        samples = array(type_code)
        samples.frombytes(raw)
        if sys.byteorder != "little":
            samples.byteswap()
        if channels == 1:
            return [sample / scale for sample in samples]

        values = []
        usable = len(samples) - (len(samples) % channels)
        for offset in range(0, usable, channels):
            frame = samples[offset : offset + channels]
            values.append(sum(frame) / (len(frame) * scale))
        return values

    def silence_edges(self, values, sample_rate, peak):
        threshold = max(0.01, peak * 0.03)
        frame = max(1, int(0.03 * sample_rate))
        hop = max(1, int(0.05 * sample_rate))
        active = []
        for start in range(0, max(1, len(values) - frame + 1), hop):
            chunk = values[start : start + frame]
            if not chunk:
                continue
            rms = math.sqrt(sum(value * value for value in chunk) / len(chunk))
            if rms > threshold:
                active.append(start)
        if not active:
            duration = len(values) / sample_rate
            return duration, duration, 0.0
        leading = active[0] / sample_rate
        trailing = max(0.0, (len(values) - (active[-1] + frame)) / sample_rate)
        active_duration = max(0.0, (active[-1] + frame - active[0]) / sample_rate)
        return leading, trailing, active_duration

    def pitch_values(self, values, sample_rate):
        frame = int(0.04 * sample_rate)
        hop = int(0.02 * sample_rate)
        pitches = []
        if len(values) < frame:
            return pitches
        frame_starts = list(range(0, len(values) - frame + 1, hop))
        if len(frame_starts) > 16:
            stride = max(1, len(frame_starts) // 16)
            frame_starts = frame_starts[::stride][:16]
        for start in frame_starts:
            segment = values[start : start + frame]
            mean = sum(segment) / len(segment)
            centered = [value - mean for value in segment]
            energy = sum(value * value for value in centered)
            if energy / len(centered) < 0.000225:
                continue
            crossings = 0
            previous = centered[0]
            for value in centered[1:]:
                if (previous <= 0 < value) or (previous >= 0 > value):
                    crossings += 1
                previous = value
            frequency = crossings * sample_rate / (2 * len(centered))
            if 70 <= frequency <= 450:
                pitches.append(frequency)
        return pitches

    def harmonic_noise_indicator(self, values, sample_rate):
        if len(values) < 256:
            return None
        window = min(len(values), max(256, int(sample_rate * 0.1)))
        start = max(0, (len(values) - window) // 2)
        end = start + window
        middle = values[start:end]
        if sample_rate > 2000:
            step = max(1, sample_rate // 2000)
            middle = middle[::step]
            sample_rate = sample_rate // step
        mean = sum(middle) / len(middle)
        centered = [value - mean for value in middle]
        energy = sum(value * value for value in centered)
        if energy <= 1e-8:
            return None
        upper = min(len(centered) - 1, max(2, int(sample_rate / 70)))
        maximum = max(
            sum(
                centered[index] * centered[index + lag]
                for index in range(len(centered) - lag)
            )
            for lag in range(1, upper)
        )
        return maximum / energy

    def apply_pitch_distribution(self, candidates):
        pitch_values = [
            item["metrics"]["pitch_median_hz"]
            for item in candidates
            if item["metrics"].get("pitch_median_hz") is not None
        ]
        center = statistics.median(pitch_values) if pitch_values else None
        spread = statistics.median(
            [abs(value - center) for value in pitch_values]
        ) if center is not None else None
        for candidate in candidates:
            candidate["pitch_distribution_center_hz"] = center
            candidate["pitch_distribution_mad_hz"] = spread

    def score_candidate(self, candidate, calibration):
        metrics = candidate["metrics"]
        evidence = candidate["evidence"]
        duration_score = self.target_score(
            metrics["duration_seconds"],
            target=6.0,
            tolerance=5.0,
        )
        speech_score = self.clamp(metrics["speech_ratio"])
        leading_score = self.inverse_score(
            metrics["leading_silence_seconds"],
            1.0,
        )
        trailing_score = self.inverse_score(
            metrics["trailing_silence_seconds"],
            1.0,
        )
        dc_score = self.inverse_score(abs(metrics["dc_offset"]), 0.03)
        clipping_score = self.inverse_score(metrics["clipping_ratio"], 0.003)
        noise_score = self.clamp(metrics["harmonic_noise_indicator"] or 0.0)
        transcript_score = self.transcript_quality(candidate["transcript"], evidence)
        flags = candidate.get("text_quality_flags", {})
        if flags.get("boundary_fragment") or flags.get("ends_with_ellipsis"):
            transcript_score *= 1 - self.BOUNDARY_FRAGMENT_PENALTY
        stability = metrics["pitch_stability_hz"]
        pitch_stability_score = (
            self.inverse_score(stability, 55.0)
            if stability is not None
            else 0.4
        )
        pitch_center_score = self.pitch_center_score(candidate)
        calibration_score = self.calibration_score(candidate, calibration)

        components = {
            "duration": duration_score,
            "speech_ratio": speech_score,
            "leading_silence": leading_score,
            "trailing_silence": trailing_score,
            "dc_offset": dc_score,
            "clipping": clipping_score,
            "noise": noise_score,
            "transcript_quality": transcript_score,
            "pitch_stability": pitch_stability_score,
            "pitch_distribution_center": pitch_center_score,
            "harmonic_noise": noise_score,
            "calibration": calibration_score,
        }
        weights = {
            "duration": 0.08,
            "speech_ratio": 0.12,
            "leading_silence": 0.08,
            "trailing_silence": 0.04,
            "dc_offset": 0.08,
            "clipping": 0.1,
            "noise": 0.11,
            "transcript_quality": 0.11,
            "pitch_stability": 0.08,
            "pitch_distribution_center": 0.1,
            "harmonic_noise": 0.0,
            "calibration": 0.1,
        }
        total = sum(
            components[name] * weight
            for name, weight in weights.items()
        )
        return {
            "total": round(total * 100, 4),
            "components": {
                key: round(value * 100, 4)
                for key, value in components.items()
            },
            "weights": weights,
        }

    def calibration_score(self, candidate, calibration):
        metrics = candidate["metrics"]
        score = (
            0.30 * self.inverse_score(metrics["clipping_ratio"], 0.003)
            + 0.20 * self.clamp(metrics["harmonic_noise_indicator"] or 0.0)
            + 0.20 * self.pitch_center_score(candidate)
            + 0.15 * self.inverse_score(
                metrics["leading_silence_seconds"],
                1.0,
            )
            + 0.15 * self.inverse_score(abs(metrics["dc_offset"]), 0.03)
        )
        return score if calibration["applied"] else 0.5

    def transcript_quality(self, transcript, evidence):
        tokens = [token for token in transcript.split() if token]
        length_score = self.clamp(len(tokens) / 8)
        alignment_score = evidence.get("alignment_similarity")
        if isinstance(alignment_score, (int, float)):
            return 0.6 * length_score + 0.4 * self.clamp(alignment_score / 100)
        return length_score

    def text_quality_flags(self, transcript):
        text = (transcript or "").strip()
        ends_with_ellipsis = text.endswith("...")
        complete_sentence = bool(
            text
            and text[-1] in ".?!"
            and not ends_with_ellipsis
        )
        return {
            "complete_sentence": complete_sentence,
            "ends_with_ellipsis": ends_with_ellipsis,
            "boundary_fragment": bool(text and not complete_sentence),
        }

    def pitch_center_score(self, candidate):
        pitch = candidate["metrics"].get("pitch_median_hz")
        center = candidate.get("pitch_distribution_center_hz")
        spread = candidate.get("pitch_distribution_mad_hz")
        if pitch is None or center is None:
            return 0.5
        return self.inverse_score(abs(pitch - center), max(spread or 1.0, 20.0))

    def diversify(self, ranked, freeze_limit):
        remaining = list(ranked)
        selected = []
        source_counts = Counter()
        chapter_counts = Counter()
        while remaining and len(selected) < freeze_limit:
            choice = max(
                remaining,
                key=lambda item: (
                    item["score"]["total"]
                    + self.diversity_bonus(item, source_counts, chapter_counts),
                    item["clip_id"],
                ),
            )
            selected.append(choice)
            remaining.remove(choice)
            source_counts[choice["source_id"]] += 1
            chapter_counts[choice["chapter_id"]] += 1
        for rank, candidate in enumerate(selected, start=1):
            candidate["freeze_rank"] = rank
        return selected

    def diversity_bonus(self, candidate, source_counts, chapter_counts):
        bonus = 0.0
        if source_counts[candidate["source_id"]] == 0:
            bonus += 12.0
        if chapter_counts[candidate["chapter_id"]] == 0:
            bonus += 6.0
        if candidate["metrics"]["duration_seconds"] >= 7.0:
            bonus += 2.0
        transcript = candidate["transcript"].lower()
        if any(marker in transcript for marker in ("toi", "anh", "co", "da")):
            bonus += 1.0
        return bonus

    def freeze_ids(self, candidates):
        for candidate in candidates:
            candidate["freeze_status"] = "frozen"
            candidate["exclude_from_future_training"] = True

    def create_ranking_manifest(
        self,
        metadata_path,
        calibration,
        scanned,
        rejected,
        top50,
        top20,
    ):
        reason_counts = Counter(
            reason
            for candidate in rejected
            for reason in candidate["rejection_reasons"]
        )
        return {
            "schema_version": self.SCHEMA_VERSION,
            "artifact_type": "REFERENCE_SELECTION",
            "authority": {
                "metadata_list": str(metadata_path),
                "candidate_cache_used_as_authority": False,
            },
            "calibration_evidence": calibration,
            "dataset_scanned": len(scanned),
            "filter_summary": {
                "accepted": len(scanned) - len(rejected),
                "rejected": len(rejected),
                "rejection_reasons": dict(sorted(reason_counts.items())),
            },
            "ranking_summary": {
                "top_limit": len(top50),
                "freeze_limit": len(top20),
                "source_count_top20": len(
                    {item["source_id"] for item in top20}
                ),
                "chapter_count_top20": len(
                    {item["chapter_id"] for item in top20}
                ),
            },
            "evidence_coverage": self.evidence_coverage_summary(scanned),
            "rejected": rejected,
            "top50": top50,
            "top20": top20,
        }

    def create_holdout_manifest(self, metadata_path, top20):
        return {
            "schema_version": self.SCHEMA_VERSION,
            "artifact_type": "EVALUATION_HOLDOUT",
            "authority_metadata_list": str(metadata_path),
            "exclude_from_future_training": True,
            "holdout_count": len(top20),
            "items": [
                {
                    "clip_id": item["clip_id"],
                    "audio": item["audio"],
                    "audio_sha256": item.get("audio_sha256"),
                    "source_id": item["source_id"],
                    "chapter_id": item["chapter_id"],
                    "freeze_rank": item["freeze_rank"],
                    "exclude_from_future_training": True,
                }
                for item in top20
            ],
        }

    def create_selection_report(
        self,
        metadata_path,
        ranking_manifest,
        holdout_manifest,
    ):
        top20 = ranking_manifest["top20"]
        top50 = ranking_manifest["top50"]
        scores = [item["score"]["total"] for item in top20]
        durations = [
            item["metrics"]["duration_seconds"]
            for item in top20
        ]
        source_counts = Counter(item["source_id"] for item in top20)
        chapter_counts = Counter(item["chapter_id"] for item in top20)

        return {
            "schema_version": self.SCHEMA_VERSION,
            "artifact_type": "REFERENCE_SELECTION_REPORT",
            "authority_metadata_list": str(metadata_path),
            "status": "READY",
            "dataset_scanned": ranking_manifest["dataset_scanned"],
            "accepted_clips": ranking_manifest["filter_summary"]["accepted"],
            "rejected_clips": ranking_manifest["filter_summary"]["rejected"],
            "rejection_reasons": ranking_manifest["filter_summary"][
                "rejection_reasons"
            ],
            "evidence_coverage": ranking_manifest["evidence_coverage"],
            "top50_count": len(top50),
            "frozen_top20_count": len(top20),
            "holdout_count": holdout_manifest["holdout_count"],
            "all_frozen_excluded_from_future_training": all(
                item.get("freeze_status") == "frozen"
                and item.get("exclude_from_future_training") is True
                for item in top20
            ),
            "all_holdout_excluded_from_future_training": all(
                item.get("exclude_from_future_training") is True
                for item in holdout_manifest["items"]
            ),
            "score_summary": {
                "min": round(min(scores), 4) if scores else None,
                "median": round(statistics.median(scores), 4)
                if scores
                else None,
                "max": round(max(scores), 4) if scores else None,
            },
            "duration_summary": {
                "min_seconds": round(min(durations), 6)
                if durations
                else None,
                "median_seconds": round(statistics.median(durations), 6)
                if durations
                else None,
                "max_seconds": round(max(durations), 6)
                if durations
                else None,
            },
            "diversity_summary": {
                "source_count_top20": len(source_counts),
                "chapter_count_top20": len(chapter_counts),
                "sources": dict(sorted(source_counts.items())),
                "chapters": dict(sorted(chapter_counts.items())),
            },
            "calibration_summary": ranking_manifest["calibration_evidence"],
        }

    def normalize_calibration_evidence(self, calibration_evidence):
        supplied = calibration_evidence or {}
        return {
            "applied": True,
            "evidence_source": supplied.get(
                "evidence_source",
                "AVS-014.24 controlled canary analysis",
            ),
            "observations": {
                "output_01": "identity_gan_hon_nhung_re_hon",
                "output_02": "sach_hon_nhung_identity_yeu_hon",
                "output_03": "toi_hon_va_giu_identity_kem",
                "reference": "co_the_co_leading_silence_va_dc_offset",
            },
            "selection_intent": (
                "uu_tien_sach_gan_output_02, identity/pitch_on_dinh, "
                "tranh_reference_re_va_toi_phang"
            ),
        }

    def build_evidence_index(
        self,
        alignment_manifest,
        alignment_report,
        dataset_health,
    ):
        index = {}
        for payload in (alignment_manifest, alignment_report, dataset_health):
            self.collect_evidence(index, payload)
        return index

    def collect_evidence(self, index, payload):
        if isinstance(payload, list):
            for item in payload:
                self.collect_evidence(index, item)
            return
        if not isinstance(payload, dict):
            return

        audio = payload.get("audio") or payload.get("path")
        if isinstance(audio, str) and audio:
            key = self.path_key(audio)
            item = index.setdefault(key, {})
            item.update(
                {
                    key: value
                    for key, value in payload.items()
                    if key
                    in {
                        "status",
                        "code",
                        "similarity",
                        "alignment_similarity",
                        "id",
                        "source_audio",
                        "source_text",
                        "duplicate",
                        "ai_generated",
                        "music_heavy",
                        "multiple_speakers",
                        "invalid",
                        "suspicious",
                    }
                }
            )
            status = str(payload.get("status", "")).lower()
            code = str(payload.get("code", "")).lower()
            if status == "suspicious" or code:
                item["suspicious"] = True
            if "similarity" in payload:
                item["alignment_similarity"] = payload["similarity"]
            elif "match_score" in payload:
                item["alignment_similarity"] = payload["match_score"]

        for value in payload.values():
            if isinstance(value, (dict, list)):
                self.collect_evidence(index, value)

    def resolve_evidence(self, row, evidence_index):
        evidence = dict(evidence_index.get(self.path_key(row["audio"]), {}))
        return {
            "_present_keys": sorted(evidence.keys()),
            "duplicate": evidence.get("duplicate") is True,
            "suspicious": evidence.get("suspicious") is True,
            "invalid": evidence.get("invalid") is True,
            "ai_generated": evidence.get("ai_generated") is True,
            "music_heavy": evidence.get("music_heavy") is True,
            "multiple_speakers": evidence.get("multiple_speakers") is True,
            "alignment_similarity": evidence.get("alignment_similarity"),
            "id": evidence.get("id"),
            "source_audio": evidence.get("source_audio"),
            "source_text": evidence.get("source_text"),
        }

    def evidence_coverage_summary(self, candidates):
        summary = {
            "dataset_scanned": len(candidates),
            "required": {},
            "optional": {},
            "missing_required_candidates": 0,
            "optional_warning_candidates": 0,
            "warning_counts": {},
        }
        warning_counts = Counter()
        for key in self.REQUIRED_EVIDENCE_KEYS:
            present = sum(
                1
                for candidate in candidates
                if key in candidate["evidence_presence"]
            )
            summary["required"][key] = {
                "present": present,
                "missing": len(candidates) - present,
            }
        for key in self.OPTIONAL_EVIDENCE_KEYS:
            present = sum(
                1
                for candidate in candidates
                if key in candidate["evidence_presence"]
            )
            summary["optional"][key] = {
                "present": present,
                "missing": len(candidates) - present,
            }
        for candidate in candidates:
            integrity = candidate["evidence_integrity"]
            if integrity["missing_required"]:
                summary["missing_required_candidates"] += 1
            if candidate["evidence_warnings"]:
                summary["optional_warning_candidates"] += 1
            warning_counts.update(candidate["evidence_warnings"])
        summary["warning_counts"] = dict(sorted(warning_counts.items()))
        return summary

    def source_id(self, audio):
        path = Path(audio)
        return str(path.parent).replace("\\", "/") or "root"

    def chapter_id(self, audio):
        parts = Path(audio).parts
        return parts[0] if len(parts) > 1 else self.source_id(audio)

    def clip_id(self, audio, line_number):
        digest = hashlib.sha256(
            f"{audio}|{line_number}".encode("utf-8")
        ).hexdigest()[:16]
        return f"ref-{digest}"

    def path_key(self, path):
        return str(path).replace("\\", "/").lower()

    def sha256(self, path):
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def target_score(self, value, target, tolerance):
        return self.clamp(1 - abs(value - target) / tolerance)

    def inverse_score(self, value, maximum):
        return self.clamp(1 - value / maximum)

    def clamp(self, value):
        return max(0.0, min(1.0, float(value)))

    def load_json(self, path):
        if not path:
            return {}
        candidate = Path(path)
        if not candidate.is_file():
            return {}
        return json.loads(candidate.read_text(encoding="utf-8"))

    def write_json(self, path, payload):
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import wave
from datetime import datetime, timezone
from pathlib import Path


class VoicePreviewBenchmarkService:

    PAIR_COUNT = 20
    RUNTIME_SAMPLE_RATE = 48000
    RUNTIME_CHANNELS = 1
    RUNTIME_SAMPLE_WIDTH = 2
    PREVIEW_READY = "READY"
    PREVIEW_FAILED = "FAILED"
    PREVIEW_UNAVAILABLE = "UNAVAILABLE"
    AVS016_PAIR_COUNT = 20
    AVS016_PREVIEW_PER_PAIR = 2
    MAX_REFERENCE_CHARS_PER_SECOND = 28.0
    MAX_REFERENCE_SYLLABLES_PER_SECOND = 7.5
    MIN_REFERENCE_CHARS_PER_SECOND = 6.0
    MIN_REFERENCE_SYLLABLES_PER_SECOND = 1.5
    REVIEW_PREVIEW_REFERENCE_RATIO = 1.75
    BLOCK_PREVIEW_REFERENCE_RATIO = 2.4

    APPROVAL_STATES = {
        "UNKNOWN",
        "KEEP",
        "MAYBE",
        "REJECT",
        "APPROVED",
    }

    REQUIRED_REFERENCE_FLAGS = (
        "clean",
        "transcript_correct",
        "not_duplicate",
        "not_suspicious",
        "not_ai_generated",
        "not_clipping",
        "no_large_noise",
    )

    FORBIDDEN_TRANSCRIPT_PATTERN = re.compile(
        r"[\d]|[^\w\sÀ-ỹà-ỹ]",
        re.UNICODE,
    )

    def prepare_round(
        self,
        output_root,
        voice_id,
        benchmark_transcript,
        references,
        round_id=None,
    ):
        root = Path(output_root)
        selected_round_id = (
            round_id
            if round_id is not None
            else self.next_round_id(root)
        )
        round_dir = root / selected_round_id
        preview_version = self.round_preview_version(
            selected_round_id
        )

        self.validate_benchmark_transcript(
            benchmark_transcript
        )
        selected = self.select_references(
            references
        )

        if round_dir.exists():
            raise FileExistsError(
                "Benchmark Round da ton tai, khong duoc ghi de."
            )

        round_dir.mkdir(
            parents=True,
            exist_ok=False,
        )

        try:
            pairs = []

            for index, reference in enumerate(
                selected,
                start=1,
            ):
                pair_id = f"pair_{index:03d}"
                pair_dir = round_dir / pair_id
                pair_dir.mkdir()

                source_audio = Path(
                    reference["audio_path"]
                )
                source_transcript = Path(
                    reference["transcript_path"]
                )

                reference_audio = pair_dir / "reference.wav"
                reference_text = (
                    pair_dir
                    / "reference_transcript.txt"
                )
                new_text = (
                    pair_dir
                    / "new_transcript.txt"
                )

                shutil.copy2(
                    source_audio,
                    reference_audio,
                )
                shutil.copy2(
                    source_transcript,
                    reference_text,
                )
                new_text.write_text(
                    benchmark_transcript.strip(),
                    encoding="utf-8",
                )

                manifest = self.create_pair_manifest(
                    pair_id=pair_id,
                    voice_id=voice_id,
                    round_id=selected_round_id,
                    reference=reference,
                    benchmark_transcript=benchmark_transcript,
                    preview_version=preview_version,
                )
                manifest_path = (
                    pair_dir
                    / "pair_manifest.json"
                )
                self.write_json_new(
                    manifest_path,
                    manifest,
                )

                pairs.append(
                    {
                        "pair_id": pair_id,
                        "manifest_path": str(
                            manifest_path
                        ),
                        "approval_state": "UNKNOWN",
                    }
                )

            round_manifest = {
                "schema_version": 2,
                "kind": "voice_preview_benchmark_round",
                "voice_id": voice_id,
                "round_id": selected_round_id,
                "pair_count": self.PAIR_COUNT,
                "benchmark_transcript": (
                    benchmark_transcript.strip()
                ),
                "pairs": pairs,
                "created_at": self.timestamp(),
            }
            round_manifest_path = (
                round_dir
                / "benchmark_manifest.json"
            )
            self.write_json_new(
                round_manifest_path,
                round_manifest,
            )

            return {
                "status": "PREPARED",
                "manifest_path": str(
                    round_manifest_path
                ),
                "round_dir": str(round_dir),
                "round_id": selected_round_id,
                "pair_count": len(pairs),
            }
        except Exception:
            # Chi xoa output diagnostic moi tao trong workspace caller cung cap,
            # khong tac dong reference nguon.
            shutil.rmtree(
                round_dir,
                ignore_errors=True,
            )
            raise

    def generate_previews(
        self,
        benchmark_manifest_path,
        runtime_profile,
        generation_runner=None,
    ):
        """Sinh hai preview cho moi Pair trong Round diagnostic da chuan bi.

        ``generation_runner`` chi la seam test. Khi khong truyen, service goi
        isolated VieNeu CPU/ONNX runtime da duoc profile chi dinh; khong goi
        EngineManager, khong bind Voice production va khong co hau ky audio.
        """
        round_manifest_path = Path(benchmark_manifest_path)
        round_manifest = self.load_json(
            round_manifest_path
        )
        round_dir = round_manifest_path.parent
        self.validate_round_manifest(
            round_manifest,
            round_dir,
            allow_generated=True,
        )
        profile = self.validate_runtime_profile(
            runtime_profile
        )
        runner = generation_runner or self.run_isolated_vieneu

        results = []
        for pair in round_manifest["pairs"]:
            pair_manifest_path = self.resolve_pair_manifest_path(
                round_dir,
                pair,
            )
            pair_dir = pair_manifest_path.parent
            pair_manifest = self.load_pair_manifest(
                pair_manifest_path,
                allow_generated=True,
            )
            pair_results = []

            for preview_name, transcript_file in (
                (
                    "same_preview",
                    "reference_transcript.txt",
                ),
                (
                    "new_preview",
                    "new_transcript.txt",
                ),
            ):
                preview = pair_manifest["previews"][preview_name]
                output_path = pair_dir / preview["file"]

                if output_path.exists():
                    raise FileExistsError(
                        "Preview da ton tai, khong duoc ghi de: "
                        + str(output_path)
                    )

                text_path = pair_dir / transcript_file
                transcript = text_path.read_text(
                    encoding="utf-8",
                ).strip()
                if not transcript:
                    raise ValueError(
                        "Transcript Preview khong duoc rong."
                    )

                request = {
                    "pair_id": pair_manifest["pair_id"],
                    "preview_name": preview_name,
                    "text": transcript,
                    "reference_audio_path": str(
                        pair_dir / "reference.wav"
                    ),
                    "output_path": str(output_path),
                    "runtime_profile": profile,
                }

                try:
                    runner(request)
                    validation = self.validate_preview_wav(
                        output_path,
                        expected_sample_rate=profile[
                            "sample_rate"
                        ],
                    )
                except Exception as error:
                    preview.update(
                        {
                            "status": self.PREVIEW_FAILED,
                            "generation_timestamp": self.timestamp(),
                            "runtime_profile": profile,
                            "error": str(error),
                        }
                    )
                    self.write_json_replace(
                        pair_manifest_path,
                        pair_manifest,
                    )
                    raise

                preview.update(
                    {
                        "status": self.PREVIEW_READY,
                        "path": self.relative_path(
                            output_path,
                            round_dir,
                        ),
                        "checksum": self.sha256(output_path),
                        "duration": validation["duration"],
                        "generation_timestamp": self.timestamp(),
                        "runtime_profile": profile,
                        "validation": validation,
                    }
                )
                preview.pop("error", None)
                self.write_json_replace(
                    pair_manifest_path,
                    pair_manifest,
                )
                pair_results.append(
                    {
                        "preview_name": preview_name,
                        "path": str(output_path),
                        "validation": validation,
                    }
                )

            results.append(
                {
                    "pair_id": pair_manifest["pair_id"],
                    "previews": pair_results,
                }
            )

        round_manifest["generation_status"] = self.PREVIEW_READY
        round_manifest["generated_at"] = self.timestamp()
        round_manifest["runtime_profile"] = profile
        self.write_json_replace(
            round_manifest_path,
            round_manifest)
        return {
            "status": self.PREVIEW_READY,
            "round_id": round_manifest["round_id"],
            "pair_count": len(results),
            "pairs": results,
        }

    def prepare_avs016_sprint6_round(
        self,
        output_root,
        voice_id,
        frozen_top20_manifest_path,
        round_id=None,
    ):
        root = Path(output_root)
        source_manifest_path = Path(frozen_top20_manifest_path)
        source_manifest = self.load_json(source_manifest_path)
        top20 = self.validate_frozen_top20_manifest(
            source_manifest,
            source_manifest_path,
        )
        selected_round_id = (
            round_id
            if round_id is not None
            else self.next_round_id(root)
        )
        preview_version = self.round_preview_version(
            selected_round_id
        )
        round_dir = root / selected_round_id

        if round_dir.exists():
            raise FileExistsError(
                "Preview Round da ton tai, khong duoc ghi de."
            )

        round_dir.mkdir(
            parents=True,
            exist_ok=False,
        )

        try:
            pairs = []
            for index, reference in enumerate(
                top20,
                start=1,
            ):
                pair_id = f"pair_{index:03d}"
                preview_id = f"preview_{index:03d}"
                pair_dir = round_dir / pair_id
                pair_dir.mkdir()

                source_audio = Path(reference["audio_path"])
                reference_audio = pair_dir / "reference.wav"
                transcript_path = pair_dir / "transcript.txt"
                shutil.copy2(source_audio, reference_audio)
                transcript_input = self.normalize_preview_transcript(
                    reference["transcript"]
                )
                transcript_text = transcript_input["normalized_text"]
                transcript_path.write_text(
                    transcript_text,
                    encoding="utf-8",
                )

                pair_manifest = self.create_avs016_pair_manifest(
                    pair_id=pair_id,
                    preview_id=preview_id,
                    voice_id=voice_id,
                    round_id=selected_round_id,
                    reference=reference,
                    source_manifest_path=source_manifest_path,
                    preview_version=preview_version,
                    transcript_input=transcript_input,
                )
                pair_manifest_path = pair_dir / "pair_manifest.json"
                self.write_json_new(
                    pair_manifest_path,
                    pair_manifest,
                )
                pairs.append(
                    {
                        "pair_id": pair_id,
                        "preview_id": preview_id,
                        "manifest_path": self.relative_path(
                            pair_manifest_path,
                            round_dir,
                        ),
                    }
                )

            round_manifest = {
                "schema_version": 1,
                "kind": "avs016_preview_generation_round",
                "voice_id": voice_id,
                "round_id": selected_round_id,
                "source_frozen_top20_manifest": str(
                    source_manifest_path
                ),
                "pair_count": self.AVS016_PAIR_COUNT,
                "preview_count": (
                    self.AVS016_PAIR_COUNT
                    * self.AVS016_PREVIEW_PER_PAIR
                ),
                "sample_rate": self.RUNTIME_SAMPLE_RATE,
                "channels": self.RUNTIME_CHANNELS,
                "sample_width": self.RUNTIME_SAMPLE_WIDTH,
                "pairs": pairs,
                "created_at": self.timestamp(),
                "constraints": {
                    "top20_modified": False,
                    "train": False,
                    "lora": False,
                    "runtime_binding": False,
                    "production_inference": False,
                    "source_audio_as_output": False,
                },
            }
            round_manifest_path = (
                round_dir
                / "preview_manifest.json"
            )
            self.write_json_new(
                round_manifest_path,
                round_manifest,
            )

            return {
                "status": "PREPARED",
                "manifest_path": str(round_manifest_path),
                "round_dir": str(round_dir),
                "round_id": selected_round_id,
                "pair_count": len(pairs),
                "preview_count": round_manifest["preview_count"],
            }
        except Exception:
            shutil.rmtree(
                round_dir,
                ignore_errors=True,
            )
            raise

    def generate_avs016_sprint6_previews(
        self,
        preview_manifest_path,
        runtime_profile,
        generation_runner=None,
        pair_ids=None,
    ):
        round_manifest_path = Path(preview_manifest_path)
        round_manifest = self.load_json(round_manifest_path)
        round_dir = round_manifest_path.parent
        self.validate_avs016_round_manifest(
            round_manifest,
            round_dir,
            allow_generated=True,
        )
        profile = self.validate_runtime_profile(runtime_profile)
        runner = generation_runner or self.run_isolated_vieneu

        pair_results = []
        generated_files = []
        transcript_mismatches = []
        selected_pair_ids = set(pair_ids or [])

        for pair in round_manifest["pairs"]:
            pair_manifest_path = self.resolve_pair_manifest_path(
                round_dir,
                pair,
            )
            pair_dir = pair_manifest_path.parent
            pair_manifest = self.load_avs016_pair_manifest(
                pair_manifest_path,
                allow_generated=True,
            )
            transcript_path = pair_dir / pair_manifest[
                "transcript"
            ]["file"]
            transcript = transcript_path.read_text(
                encoding="utf-8",
            ).strip()
            if not transcript:
                raise ValueError("Transcript preview khong duoc rong.")

            pair_result = {
                "pair_id": pair_manifest["pair_id"],
                "preview_id": pair_manifest["preview_id"],
                "reference_id": pair_manifest["reference"][
                    "reference_id"
                ],
                "transcript_sha256": self.sha256(transcript_path),
                "previews": {},
            }

            if selected_pair_ids and pair_manifest["pair_id"] not in selected_pair_ids:
                for preview_name in ("ai_preview", "benchmark_preview"):
                    preview = pair_manifest[preview_name]
                    if preview.get("status") != self.PREVIEW_READY:
                        raise ValueError(
                            "Pair carry-forward chua READY: "
                            + pair_manifest["pair_id"]
                        )
                    output_path = round_dir / preview["path"]
                    if not output_path.is_file():
                        raise ValueError(
                            "Thieu preview carry-forward: "
                            + str(output_path)
                        )
                    generated_files.append(output_path)
                    pair_result["previews"][preview_name] = {
                        "path": str(output_path),
                        "checksum": preview["checksum"],
                        "duration": preview["duration"],
                        "validation": preview["validation"],
                        "duration_integrity": preview.get(
                            "duration_integrity",
                            {},
                        ),
                        "carried_forward": True,
                    }
                pair_results.append(pair_result)
                continue

            for preview_name in ("ai_preview", "benchmark_preview"):
                preview = pair_manifest[preview_name]
                output_path = pair_dir / preview["file"]
                if output_path.exists():
                    raise FileExistsError(
                        "Preview da ton tai, khong duoc ghi de: "
                        + str(output_path)
                    )
                request = {
                    "pair_id": pair_manifest["pair_id"],
                    "preview_id": pair_manifest["preview_id"],
                    "preview_name": preview_name,
                    "text": transcript,
                    "reference_audio_path": str(
                        pair_dir / "reference.wav"
                    ),
                    "output_path": str(output_path),
                    "runtime_profile": profile,
                    "seed": preview.get("seed"),
                    "inference_parameters": preview.get(
                        "inference_parameters",
                        {},
                    ),
                }

                try:
                    runner(request)
                    validation = self.validate_preview_wav(
                        output_path,
                        expected_sample_rate=profile["sample_rate"],
                    )
                    generated_checksum = self.sha256(output_path)
                    duration_integrity = (
                        self.preview_duration_integrity(
                            reference_duration=pair_manifest[
                                "reference"
                            ]["preflight_integrity"][
                                "reference_duration_seconds"
                            ],
                            preview_duration=validation["duration"],
                        )
                    )
                    if (
                        generated_checksum
                        == pair_manifest["reference"][
                            "audio_sha256"
                        ]
                    ):
                        raise ValueError(
                            "Preview output trung checksum audio goc."
                        )
                    if duration_integrity["status"] == "BLOCK":
                        raise ValueError(
                            "Preview/reference duration ratio BLOCK."
                        )
                except Exception as error:
                    preview.update(
                        {
                            "status": self.PREVIEW_FAILED,
                            "generation_timestamp": self.timestamp(),
                            "runtime_profile": profile,
                            "error": str(error),
                        }
                    )
                    self.write_json_replace(
                        pair_manifest_path,
                        pair_manifest,
                    )
                    raise

                preview.update(
                    {
                        "status": self.PREVIEW_READY,
                        "path": self.relative_path(
                            output_path,
                            round_dir,
                        ),
                        "checksum": generated_checksum,
                        "duration": validation["duration"],
                        "generation_timestamp": self.timestamp(),
                        "runtime_profile": profile,
                        "model_revision": self.model_revision_from_profile(
                            profile
                        ),
                        "seed": preview.get("seed"),
                        "inference_parameters": preview.get(
                            "inference_parameters",
                            {},
                        ),
                        "transcript_file": pair_manifest[
                            "transcript"
                        ]["file"],
                        "transcript_sha256": pair_result[
                            "transcript_sha256"
                        ],
                        "validation": validation,
                        "duration_integrity": duration_integrity,
                    }
                )
                preview.pop("error", None)
                generated_files.append(output_path)
                pair_result["previews"][preview_name] = {
                    "path": str(output_path),
                    "checksum": generated_checksum,
                    "duration": validation["duration"],
                    "validation": validation,
                    "duration_integrity": duration_integrity,
                }

            ai_preview = pair_manifest["ai_preview"]
            benchmark_preview = pair_manifest["benchmark_preview"]
            if (
                ai_preview.get("transcript_sha256")
                != benchmark_preview.get("transcript_sha256")
            ):
                transcript_mismatches.append(
                    pair_manifest["preview_id"]
                )

            self.write_json_replace(
                pair_manifest_path,
                pair_manifest,
            )
            pair_results.append(pair_result)

        report = self.create_avs016_preview_report(
            round_manifest,
            pair_results,
            generated_files,
            transcript_mismatches,
            profile,
        )
        report_path = round_dir / "preview_report.json"
        self.write_json_new(report_path, report)

        round_manifest["generation_status"] = (
            self.PREVIEW_READY
            if report["status"] == "READY"
            else "INVALID"
        )
        round_manifest["generated_at"] = self.timestamp()
        round_manifest["runtime_profile"] = profile
        round_manifest["preview_report"] = "preview_report.json"
        self.write_json_replace(
            round_manifest_path,
            round_manifest,
        )
        return {
            "status": report["status"],
            "round_id": round_manifest["round_id"],
            "pair_count": report["pair_count"],
            "preview_count": report["preview_count"],
            "report_path": str(report_path),
            "pairs": pair_results,
        }

    def run_isolated_vieneu(
        self,
        request,
    ):
        """Chay VieNeu CPU/ONNX trong virtual environment isolated da lock."""
        profile = request["runtime_profile"]
        runtime_python = Path(profile["runtime_python"])
        if not runtime_python.is_file():
            raise FileNotFoundError(
                "Khong tim thay Python runtime VieNeu isolated."
            )

        app_root = Path(profile["app_root"])
        cache_root = app_root / "cache"
        cache_root.mkdir(parents=True, exist_ok=True)

        runner_source = self.create_vieneu_runner_source(
            request
        )
        with tempfile.TemporaryDirectory(
            prefix="avs016_preview_",
            dir=str(cache_root),
        ) as temporary_dir:
            runner_path = Path(temporary_dir) / "runner.py"
            runner_path.write_text(
                runner_source,
                encoding="utf-8",
            )
            environment = os.environ.copy()
            environment.update(
                {
                    "CUDA_VISIBLE_DEVICES": "",
                    "OMP_NUM_THREADS": "2",
                    "MKL_NUM_THREADS": "2",
                    "OPENBLAS_NUM_THREADS": "2",
                    "HF_HUB_OFFLINE": "1",
                }
            )
            completed = subprocess.run(
                [str(runtime_python), str(runner_path)],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=environment,
            )
        if completed.returncode != 0:
            raise RuntimeError(
                "VieNeu isolated preview generation that bai: "
                + completed.stderr.strip()[-1000:]
            )

    def create_vieneu_runner_source(
        self,
        request,
    ):
        profile = request["runtime_profile"]
        params = request.get("inference_parameters") or {}
        seed = int(request.get("seed") or 0)
        return f'''from __future__ import annotations

import random
import wave
from pathlib import Path

import numpy as np
import soundfile as sf
from vieneu._v3_turbo_engine.onnx_runtime_lite import OnnxV3LiteEngine

model_root = Path({profile["model_root"]!r})
codec_root = Path({profile["codec_root"]!r})
reference_audio = Path({request["reference_audio_path"]!r})
output_path = Path({request["output_path"]!r})
text = {request["text"]!r}
seed = {seed!r}
random.seed(seed)
np.random.seed(seed)

engine = OnnxV3LiteEngine(
    checkpoint_path=str(model_root),
    onnx_dir=str(model_root / "onnx_int8"),
    codec_dir=str(codec_root),
    onnx_subfolder="onnx_int8",
    threads=2,
)
speaker_emb, ref_codes = engine.prepare_reference(
    str(reference_audio),
    denoise=True,
    use_ref_codes=True,
)
audio = engine.infer(
    text=text,
    speaker_emb=speaker_emb,
    ref_codes=ref_codes,
    style="tu_nhien",
    use_ref_codes=True,
    temperature={params.get("temperature", 0.70)!r},
    top_k={params.get("top_k", 20)!r},
    top_p={params.get("top_p", 0.95)!r},
    max_new_frames={params.get("max_new_frames", 520)!r},
    repetition_penalty={params.get("repetition_penalty", 1.2)!r},
)
output_path.parent.mkdir(parents=True, exist_ok=True)
sf.write(
    str(output_path),
    np.asarray(audio, dtype=np.float32),
    {profile["sample_rate"]},
    subtype="PCM_16",
)
'''

    def validate_runtime_profile(
        self,
        runtime_profile,
    ):
        if not isinstance(runtime_profile, dict):
            raise ValueError(
                "Runtime profile Preview khong hop le."
            )
        required = (
            "app_root",
            "runtime_python",
            "model_root",
            "codec_root",
        )
        missing = [
            key
            for key in required
            if not runtime_profile.get(key)
        ]
        if missing:
            raise ValueError(
                "Runtime profile Preview thieu: "
                + ", ".join(missing)
            )
        profile = dict(runtime_profile)
        profile["backend"] = profile.get(
            "backend",
            "CPU_ONNX",
        )
        if profile["backend"] != "CPU_ONNX":
            raise ValueError(
                "Preview Benchmark chi cho phep CPU_ONNX."
            )
        profile["sample_rate"] = int(
            profile.get(
                "sample_rate",
                self.RUNTIME_SAMPLE_RATE,
            )
        )
        if profile["sample_rate"] <= 0:
            raise ValueError(
                "Sample rate runtime Preview khong hop le."
            )
        return profile

    def validate_preview_wav(
        self,
        preview_path,
        expected_sample_rate=None,
    ):
        path = Path(preview_path)
        if not path.is_file():
            raise ValueError(
                "Preview WAV khong duoc tao."
            )

        try:
            with wave.open(str(path), "rb") as wav:
                channels = wav.getnchannels()
                sample_rate = wav.getframerate()
                sample_width = wav.getsampwidth()
                frame_count = wav.getnframes()
                compressed = wav.getcomptype() != "NONE"
                raw = wav.readframes(frame_count)
        except (EOFError, wave.Error) as error:
            raise ValueError(
                "Preview WAV corrupt: " + str(error)
            ) from error

        target_rate = (
            None
            if expected_sample_rate == "ANY"
            else self.RUNTIME_SAMPLE_RATE
            if expected_sample_rate is None
            else int(expected_sample_rate)
        )
        if target_rate is not None and sample_rate != target_rate:
            raise ValueError(
                "Preview WAV sai sample rate runtime."
            )
        if channels != self.RUNTIME_CHANNELS:
            raise ValueError(
                "Preview WAV phai la mono."
            )
        if sample_width != self.RUNTIME_SAMPLE_WIDTH:
            raise ValueError(
                "Preview WAV phai la PCM16."
            )
        if compressed or frame_count <= 0:
            raise ValueError(
                "Preview WAV corrupt hoac khong co duration."
            )
        if len(raw) != frame_count * channels * sample_width:
            raise ValueError(
                "Preview WAV truncated."
            )

        samples = memoryview(raw).cast("h")
        peak = max(
            (abs(sample) for sample in samples),
            default=0,
        )
        if peak == 0:
            raise ValueError(
                "Preview WAV khong duoc toan im lang."
            )

        return {
            "status": "PASS",
            "duration": frame_count / sample_rate,
            "sample_rate": sample_rate,
            "channels": channels,
            "sample_width": sample_width,
            "frame_count": frame_count,
            "nonsilent": True,
        }

    def select_references(
        self,
        references,
    ):
        eligible = []

        for reference in references:
            self.validate_reference(
                reference
            )

            if all(
                reference.get(flag) is True
                for flag in self.REQUIRED_REFERENCE_FLAGS
            ):
                eligible.append(
                    dict(reference)
                )

        if len(eligible) < self.PAIR_COUNT:
            raise ValueError(
                "Can it nhat 20 reference dat dieu kien Benchmark."
            )

        return eligible[:self.PAIR_COUNT]

    def validate_reference(
        self,
        reference,
    ):
        required = (
            "reference_id",
            "audio_path",
            "transcript_path",
        )

        missing = [
            key
            for key in required
            if not reference.get(key)
        ]

        if missing:
            raise ValueError(
                "Reference Benchmark thieu: "
                + ", ".join(missing)
            )

        audio_path = Path(
            reference["audio_path"]
        )
        transcript_path = Path(
            reference["transcript_path"]
        )

        if (
            not audio_path.is_file()
            or audio_path.suffix.lower() != ".wav"
        ):
            raise ValueError(
                "Reference Benchmark phai la file WAV hop le."
            )

        if not transcript_path.is_file():
            raise ValueError(
                "Khong tim thay transcript cua Reference."
            )

        if not transcript_path.read_text(
            encoding="utf-8",
        ).strip():
            raise ValueError(
                "Transcript cua Reference khong duoc rong."
            )

    def validate_benchmark_transcript(
        self,
        transcript,
    ):
        text = (transcript or "").strip()

        if not text:
            raise ValueError(
                "Benchmark transcript khong duoc rong."
            )

        if self.FORBIDDEN_TRANSCRIPT_PATTERN.search(
            text
        ):
            raise ValueError(
                "Benchmark transcript khong duoc co so, ky hieu, "
                "ten rieng, tieng Anh hoac emotion cue."
            )

        words = [
            word
            for word in text.split()
            if word
        ]

        if len(words) < 15 or len(words) > 35:
            raise ValueError(
                "Benchmark transcript phai co do dai uoc tinh "
                "tu 6 den 10 giay."
            )

    def create_pair_manifest(
        self,
        pair_id,
        voice_id,
        round_id,
        reference,
        benchmark_transcript,
        preview_version,
    ):
        return {
            "schema_version": 2,
            "kind": "voice_preview_benchmark_pair",
            "pair_id": pair_id,
            "voice_id": voice_id,
            "round_id": round_id,
            "reference": {
                "reference_id": reference["reference_id"],
                "audio_file": "reference.wav",
                "transcript_file": (
                    "reference_transcript.txt"
                ),
            },
            "benchmark_transcript_file": (
                "new_transcript.txt"
            ),
            "benchmark_transcript": (
                benchmark_transcript.strip()
            ),
            "previews": {
                "same_preview": self.create_preview_record(
                    "same_preview",
                    preview_version,
                    "AI tu generate dung transcript cua reference; "
                    "khong copy audio goc va khong hau ky.",
                ),
                "new_preview": self.create_preview_record(
                    "new_preview",
                    preview_version,
                    "AI tu generate bang benchmark transcript dung "
                    "chung cho tat ca Pair; khong hau ky.",
                ),
            },
            "approval_state": "UNKNOWN",
            "created_at": self.timestamp(),
        }

    def create_preview_record(
        self,
        name,
        version,
        contract,
    ):
        return {
            "file": f"{name}_v{version}.wav",
            "version": version,
            "status": self.PREVIEW_UNAVAILABLE,
            "contract": contract,
        }

    def validate_frozen_top20_manifest(
        self,
        manifest,
        manifest_path,
    ):
        if (
            manifest.get("artifact_type")
            != "REFERENCE_SELECTION"
        ):
            raise ValueError(
                "Manifest Top20 phai la REFERENCE_SELECTION."
            )
        top20 = manifest.get("top20", [])
        if len(top20) != self.AVS016_PAIR_COUNT:
            raise ValueError("Frozen Top20 phai co dung 20 item.")
        expected_ranks = list(
            range(1, self.AVS016_PAIR_COUNT + 1)
        )
        ranks = [item.get("freeze_rank") for item in top20]
        if ranks != expected_ranks:
            raise ValueError(
                "Frozen Top20 phai giu freeze_rank 1 den 20."
            )

        seen_clip_ids = set()
        normalized = []
        for item in top20:
            if item.get("freeze_status") != "frozen":
                raise ValueError("Top20 chua duoc freeze.")
            if item.get("exclude_from_future_training") is not True:
                raise ValueError(
                    "Top20 phai exclude_from_future_training."
                )
            clip_id = item.get("clip_id")
            if not clip_id or clip_id in seen_clip_ids:
                raise ValueError("Top20 clip_id khong hop le.")
            seen_clip_ids.add(clip_id)
            audio_path = Path(
                item.get("audio_path") or item.get("audio") or ""
            )
            if not audio_path.is_absolute():
                audio_path = Path.cwd() / audio_path
            if not audio_path.is_file():
                raise ValueError(
                    "Khong tim thay audio Top20: " + str(audio_path)
                )
            transcript = (item.get("transcript") or "").strip()
            if not transcript:
                raise ValueError("Transcript Top20 khong duoc rong.")
            reference = dict(item)
            reference["audio_path"] = str(audio_path)
            reference["source_manifest"] = str(manifest_path)
            normalized.append(reference)
        return normalized

    def create_avs016_pair_manifest(
        self,
        pair_id,
        preview_id,
        voice_id,
        round_id,
        reference,
        source_manifest_path,
        preview_version,
        transcript_input=None,
    ):
        transcript_input = transcript_input or self.normalize_preview_transcript(
            reference["transcript"]
        )
        transcript_text = transcript_input["normalized_text"]
        reference_id = (
            reference.get("evidence", {}).get("id")
            or reference["clip_id"]
        )
        reference_audio_sha256 = reference.get("audio_sha256") or self.sha256(
            reference["audio_path"]
        )
        preflight = self.reference_preflight_integrity(
            reference_id=reference_id,
            transcript=transcript_text,
            audio_path=reference["audio_path"],
        )
        if preflight["status"] == "BLOCK":
            raise ValueError(
                "Reference preflight BLOCK: " + reference_id
            )
        return {
            "schema_version": 1,
            "kind": "avs016_preview_generation_pair",
            "pair_id": pair_id,
            "preview_id": preview_id,
            "voice_id": voice_id,
            "round_id": round_id,
            "source_frozen_top20_manifest": str(
                source_manifest_path
            ),
            "reference": {
                "reference_id": reference_id,
                "clip_id": reference["clip_id"],
                "freeze_rank": reference["freeze_rank"],
                "source_audio": reference.get("source_id"),
                "source_chapter": reference.get("chapter_id"),
                "audio_file": "reference.wav",
                "audio_path": reference["audio_path"],
                "audio_sha256": reference_audio_sha256,
                "conditioning_reference_id": reference_id,
                "conditioning_reference_path": reference["audio_path"],
                "conditioning_reference_checksum": reference_audio_sha256,
                "exclude_from_future_training": True,
                "preflight_integrity": preflight,
            },
            "transcript": {
                "file": "transcript.txt",
                "language": reference.get("language", "vi"),
                "text": transcript_text,
                "sha256": self.sha256_text(transcript_text),
                "source_text": transcript_input["source_text"],
                "source_sha256": self.sha256_text(
                    transcript_input["source_text"]
                ),
                "normalization": transcript_input["normalization"],
                "text_quality": self.text_quality_flags(transcript_text),
            },
            "ai_preview": self.create_avs016_preview_record(
                "ai_preview",
                preview_version,
                "AI Preview synthesize moi tu reference Top20; "
                "khong copy audio goc.",
            ),
            "benchmark_preview": self.create_avs016_preview_record(
                "benchmark_preview",
                preview_version,
                "Benchmark Preview synthesize moi voi cung transcript; "
                "khong copy audio goc.",
            ),
            "created_at": self.timestamp(),
        }

    def create_avs016_preview_record(
        self,
        name,
        version,
        contract,
    ):
        return {
            "file": f"{name}_v{version}.wav",
            "version": version,
            "status": self.PREVIEW_UNAVAILABLE,
            "contract": contract,
            "benchmark_voice_profile": (
                "VieNeu CPU_ONNX diagnostic Thu Minh reference clone"
            ),
            "model_revision": None,
            "seed": 0,
            "inference_parameters": {
                "speed": 1.0,
                "temperature": 0.70,
                "top_k": 20,
                "top_p": 0.95,
                "max_new_frames": 520,
                "repetition_penalty": 1.2,
            },
            "comparison_reason": (
                "ai_preview va benchmark_preview dung cung transcript "
                "nhung la hai inference call doc lap de do on dinh "
                "diagnostic; khong phai approval training."
            ),
        }

    def normalize_preview_transcript(
        self,
        transcript,
    ):
        source_text = transcript or ""
        normalized = source_text.strip()
        actions = []
        if normalized != source_text:
            actions.append("strip_outer_whitespace")

        cleaned = re.sub(r'^(?:["“”]\s*)+', "", normalized)
        if cleaned != normalized:
            actions.append("remove_leading_unmatched_quotes")
            normalized = cleaned.strip()

        if normalized.count('"') % 2 == 1 and normalized.startswith('"'):
            normalized = normalized[1:].strip()
            actions.append("remove_unmatched_open_quote")

        return {
            "source_text": source_text,
            "normalized_text": normalized,
            "normalization": {
                "status": "NORMALIZED" if actions else "UNCHANGED",
                "actions": actions,
                "source_preserved": True,
            },
        }

    def text_quality_flags(
        self,
        transcript,
    ):
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

    def reference_preflight_integrity(
        self,
        reference_id,
        transcript,
        audio_path,
    ):
        validation = self.validate_preview_wav(
            audio_path,
            expected_sample_rate="ANY",
        )
        duration = validation["duration"]
        text = (transcript or "").strip()
        syllable_count = len([part for part in text.split() if part])
        chars_per_second = len(text) / duration if duration else 0.0
        syllables_per_second = (
            syllable_count / duration if duration else 0.0
        )
        blockers = []
        warnings = []

        if chars_per_second > self.MAX_REFERENCE_CHARS_PER_SECOND:
            blockers.append("reference_chars_per_second_too_high")
        if syllables_per_second > self.MAX_REFERENCE_SYLLABLES_PER_SECOND:
            blockers.append("reference_syllables_per_second_too_high")
        if chars_per_second < self.MIN_REFERENCE_CHARS_PER_SECOND:
            warnings.append("reference_chars_per_second_low")
        if syllables_per_second < self.MIN_REFERENCE_SYLLABLES_PER_SECOND:
            warnings.append("reference_syllables_per_second_low")

        flags = self.text_quality_flags(text)
        if flags["ends_with_ellipsis"]:
            warnings.append("transcript_ends_with_ellipsis")
        if flags["boundary_fragment"]:
            warnings.append("transcript_boundary_fragment")

        status = "BLOCK" if blockers else "REVIEW" if warnings else "PASS"
        return {
            "status": status,
            "reference_id": reference_id,
            "reference_duration_seconds": duration,
            "transcript_char_count": len(text),
            "transcript_syllable_count": syllable_count,
            "chars_per_second": round(chars_per_second, 4),
            "syllables_per_second": round(syllables_per_second, 4),
            "blockers": blockers,
            "warnings": warnings,
            "text_quality": flags,
        }

    def preview_duration_integrity(
        self,
        reference_duration,
        preview_duration,
    ):
        ratio = (
            preview_duration / reference_duration
            if reference_duration
            else 0.0
        )
        blockers = []
        warnings = []
        if ratio > self.BLOCK_PREVIEW_REFERENCE_RATIO:
            blockers.append("preview_reference_duration_ratio_too_high")
        elif ratio > self.REVIEW_PREVIEW_REFERENCE_RATIO:
            warnings.append("preview_reference_duration_ratio_review")
        status = "BLOCK" if blockers else "REVIEW" if warnings else "PASS"
        return {
            "status": status,
            "ratio": round(ratio, 4),
            "reference_duration_seconds": reference_duration,
            "preview_duration_seconds": preview_duration,
            "blockers": blockers,
            "warnings": warnings,
        }

    def model_revision_from_profile(
        self,
        runtime_profile,
    ):
        return (
            runtime_profile.get("model_revision")
            or Path(runtime_profile.get("model_root", "")).name
        )

    def create_avs016_sprint8_reference_manifest(
        self,
        frozen_top20_manifest_path,
        output_dir,
        blocked_reference_ids,
        *,
        review_evidence_paths=None,
    ):
        source_path = Path(frozen_top20_manifest_path)
        source = self.load_json(source_path)
        top20 = list(source.get("top20", []))
        top50 = list(source.get("top50", []))
        blocked = set(blocked_reference_ids)
        if len(top20) != self.AVS016_PAIR_COUNT:
            raise ValueError("Source Top20 khong du 20 item.")

        removed = []
        kept = []
        for item in top20:
            reference_id = self.reference_id_from_selection_item(item)
            if reference_id in blocked or item.get("clip_id") in blocked:
                removed.append(item)
            else:
                kept.append(item)
        if not removed:
            raise ValueError("Khong tim thay reference can thay.")

        used_clip_ids = {item["clip_id"] for item in kept}
        removed_clip_ids = {item["clip_id"] for item in removed}
        replacement = None
        for item in top50:
            reference_id = self.reference_id_from_selection_item(item)
            if reference_id in blocked or item.get("clip_id") in blocked:
                continue
            if item.get("clip_id") in removed_clip_ids:
                continue
            if item.get("clip_id") in used_clip_ids:
                continue
            audio_path = item.get("audio_path") or item.get("audio")
            if not audio_path:
                continue
            if not Path(audio_path).is_absolute():
                audio_path = Path.cwd() / audio_path
            try:
                preflight = self.reference_preflight_integrity(
                    reference_id=reference_id,
                    transcript=self.normalize_preview_transcript(
                        item.get("transcript", "")
                    )["normalized_text"],
                    audio_path=audio_path,
                )
            except (OSError, ValueError):
                continue
            if preflight["status"] == "BLOCK":
                continue
            replacement = dict(item)
            break
        if replacement is None:
            raise ValueError("Khong tim thay candidate Top50 thay the.")

        removed_ranks = [item["freeze_rank"] for item in removed]
        replacement["freeze_rank"] = removed_ranks[0]
        replacement["freeze_status"] = "frozen"
        replacement["exclude_from_future_training"] = True
        adjusted = sorted(
            kept + [replacement],
            key=lambda item: item["freeze_rank"],
        )

        manifest = dict(source)
        manifest["top20"] = adjusted
        manifest["sprint8_review_integration"] = {
            "status": "READY_FOR_ROUND02",
            "removed_reference_ids": [
                self.reference_id_from_selection_item(item)
                for item in removed
            ],
            "replacement_reference_id": (
                self.reference_id_from_selection_item(replacement)
            ),
            "review_evidence_paths": list(review_evidence_paths or []),
            "training_approval": False,
            "note": (
                "Ranking/review evidence chi dung de prepare Round02; "
                "khong phai phe duyet Training."
            ),
        }
        manifest["ranking_summary"] = dict(
            manifest.get("ranking_summary", {})
        )
        manifest["ranking_summary"]["freeze_limit"] = len(adjusted)
        manifest["ranking_summary"]["sprint8_pair_replaced"] = True

        holdout = self.create_avs016_holdout_from_top20(
            source,
            adjusted,
        )
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        manifest_path = output_path / "reference_selection_manifest.json"
        holdout_path = output_path / "evaluation_holdout_manifest.json"
        self.write_json_new(manifest_path, manifest)
        self.write_json_new(holdout_path, holdout)
        return {
            "status": "READY",
            "manifest_path": str(manifest_path),
            "holdout_manifest_path": str(holdout_path),
            "removed": removed,
            "replacement": replacement,
        }

    def create_avs016_holdout_from_top20(
        self,
        source_manifest,
        top20,
    ):
        return {
            "schema_version": source_manifest.get("schema_version", 1),
            "artifact_type": "EVALUATION_HOLDOUT",
            "authority_metadata_list": source_manifest.get(
                "authority",
                {},
            ).get("metadata_list"),
            "exclude_from_future_training": True,
            "holdout_count": len(top20),
            "items": [
                {
                    "clip_id": item["clip_id"],
                    "audio": item.get("audio") or item.get("audio_path"),
                    "audio_sha256": item.get("audio_sha256"),
                    "source_id": item["source_id"],
                    "chapter_id": item["chapter_id"],
                    "freeze_rank": item["freeze_rank"],
                    "exclude_from_future_training": True,
                }
                for item in top20
            ],
        }

    def reference_id_from_selection_item(
        self,
        item,
    ):
        return item.get("evidence", {}).get("id") or item.get("clip_id")

    def validate_avs016_round_manifest(
        self,
        manifest,
        round_dir,
        allow_generated=False,
    ):
        if (
            manifest.get("kind")
            != "avs016_preview_generation_round"
        ):
            raise ValueError("Sai kind cua Preview manifest.")
        if manifest.get("pair_count") != self.AVS016_PAIR_COUNT:
            raise ValueError("Preview Round phai co dung 20 Pair.")
        if (
            manifest.get("preview_count")
            != self.AVS016_PAIR_COUNT
            * self.AVS016_PREVIEW_PER_PAIR
        ):
            raise ValueError("Preview Round phai co dung 40 WAV.")
        pairs = manifest.get("pairs", [])
        if len(pairs) != self.AVS016_PAIR_COUNT:
            raise ValueError("Danh sach Pair khong du 20.")
        expected_ids = [
            f"pair_{index:03d}"
            for index in range(1, self.AVS016_PAIR_COUNT + 1)
        ]
        if [pair.get("pair_id") for pair in pairs] != expected_ids:
            raise ValueError("Pair ID phai tu pair_001 den pair_020.")
        for pair in pairs:
            if not pair.get("preview_id"):
                raise ValueError("Pair thieu preview_id.")
            self.load_avs016_pair_manifest(
                self.resolve_pair_manifest_path(round_dir, pair),
                allow_generated=allow_generated,
            )

    def load_avs016_pair_manifest(
        self,
        path,
        allow_generated=False,
    ):
        manifest = self.load_json(path)
        if (
            manifest.get("kind")
            != "avs016_preview_generation_pair"
        ):
            raise ValueError("Sai kind cua AVS-016 pair manifest.")
        if not manifest.get("preview_id"):
            raise ValueError("Pair manifest thieu preview_id.")
        reference = manifest.get("reference", {})
        transcript = manifest.get("transcript", {})
        if not reference.get("reference_id"):
            raise ValueError("Pair manifest thieu reference.")
        if not reference.get("conditioning_reference_checksum"):
            raise ValueError("Pair manifest thieu conditioning reference.")
        preflight = reference.get("preflight_integrity", {})
        if preflight.get("status") == "BLOCK":
            raise ValueError("Pair manifest co preflight BLOCK.")
        if not preflight.get("reference_duration_seconds"):
            raise ValueError("Pair manifest thieu preflight integrity.")
        if not transcript.get("file") or not transcript.get("sha256"):
            raise ValueError("Pair manifest thieu transcript.")
        if not transcript.get("source_sha256"):
            raise ValueError("Pair manifest thieu transcript provenance.")
        for name in ("ai_preview", "benchmark_preview"):
            preview = manifest.get(name, {})
            version = preview.get("version")
            if (
                not isinstance(version, int)
                or version < 1
                or preview.get("file")
                != f"{name}_v{version}.wav"
            ):
                raise ValueError("Pair manifest thieu preview contract.")
            status = preview.get("status")
            if status == self.PREVIEW_UNAVAILABLE:
                continue
            if not allow_generated:
                raise ValueError(
                    "Preview generation chua duoc phep co WAV san."
                )
            if not preview.get("model_revision"):
                raise ValueError("Preview manifest thieu model revision.")
            if "seed" not in preview:
                raise ValueError("Preview manifest thieu seed.")
            if not preview.get("inference_parameters"):
                raise ValueError(
                    "Preview manifest thieu inference parameters."
                )
            if status not in (
                self.PREVIEW_READY,
                self.PREVIEW_FAILED,
            ):
                raise ValueError("Trang thai Preview khong hop le.")
        return manifest

    def create_avs016_preview_report(
        self,
        round_manifest,
        pair_results,
        generated_files,
        transcript_mismatches,
        runtime_profile,
    ):
        preview_count = sum(
            len(pair["previews"])
            for pair in pair_results
        )
        missing_files = [
            str(path)
            for path in generated_files
            if not Path(path).is_file()
        ]
        status = (
            "READY"
            if len(pair_results) == self.AVS016_PAIR_COUNT
            and preview_count
            == self.AVS016_PAIR_COUNT
            * self.AVS016_PREVIEW_PER_PAIR
            and not transcript_mismatches
            and not missing_files
            else "INVALID"
        )
        return {
            "schema_version": 1,
            "artifact_type": "AVS016_PREVIEW_REPORT",
            "status": status,
            "voice_id": round_manifest["voice_id"],
            "round_id": round_manifest["round_id"],
            "source_frozen_top20_manifest": round_manifest[
                "source_frozen_top20_manifest"
            ],
            "pair_count": len(pair_results),
            "preview_count": preview_count,
            "expected_pair_count": self.AVS016_PAIR_COUNT,
            "expected_preview_count": (
                self.AVS016_PAIR_COUNT
                * self.AVS016_PREVIEW_PER_PAIR
            ),
            "ai_preview_count": sum(
                1
                for pair in pair_results
                if "ai_preview" in pair["previews"]
            ),
            "benchmark_preview_count": sum(
                1
                for pair in pair_results
                if "benchmark_preview" in pair["previews"]
            ),
            "transcript_identity": {
                "status": "PASS"
                if not transcript_mismatches
                else "FAIL",
                "mismatched_preview_ids": transcript_mismatches,
            },
            "output_policy": {
                "source_audio_as_output": False,
                "all_outputs_synthesized": True,
                "sample_rate": runtime_profile["sample_rate"],
                "channels": self.RUNTIME_CHANNELS,
                "sample_width": self.RUNTIME_SAMPLE_WIDTH,
            },
            "constraints": round_manifest["constraints"],
            "runtime_profile": runtime_profile,
            "pairs": pair_results,
            "generated_at": self.timestamp(),
        }

    def next_round_id(
        self,
        output_root,
    ):
        root = Path(output_root)
        highest = 0
        if root.is_dir():
            for child in root.iterdir():
                match = re.fullmatch(
                    r"Round(\d+)",
                    child.name,
                )
                if child.is_dir() and match:
                    highest = max(
                        highest,
                        int(match.group(1)),
                    )
        return f"Round{highest + 1:02d}"

    def round_preview_version(
        self,
        round_id,
    ):
        match = re.fullmatch(
            r"Round(\d+)",
            round_id or "",
        )

        if not match or int(match.group(1)) < 1:
            raise ValueError(
                "Round ID phai theo dang Round01, Round02."
            )

        return int(match.group(1))

    def update_approval(
        self,
        pair_manifest_path,
        approval_state,
    ):
        if approval_state not in self.APPROVAL_STATES:
            raise ValueError(
                "Approval state Benchmark khong hop le."
            )

        path = Path(pair_manifest_path)
        manifest = self.load_pair_manifest(
            path,
            allow_generated=True,
        )
        manifest["approval_state"] = approval_state
        manifest["updated_at"] = self.timestamp()
        self.write_json_replace(
            path,
            manifest,
        )

        return manifest

    def training_status(
        self,
        benchmark_manifest_path,
    ):
        if not benchmark_manifest_path:
            return {
                "status": "MISSING",
                "training_allowed": False,
                "approved_pair_count": 0,
                "blockers": [
                    "benchmark_manifest_missing",
                ],
            }

        path = Path(benchmark_manifest_path)

        if not path.is_file():
            return {
                "status": "MISSING",
                "training_allowed": False,
                "approved_pair_count": 0,
                "blockers": [
                    "benchmark_manifest_not_found",
                ],
            }

        try:
            manifest = self.load_json(path)
            self.validate_round_manifest(
                manifest,
                path.parent,
                allow_generated=True,
            )
        except (
            OSError,
            ValueError,
            json.JSONDecodeError,
        ) as error:
            return {
                "status": "INVALID",
                "training_allowed": False,
                "approved_pair_count": 0,
                "blockers": [
                    f"benchmark_manifest_invalid: {error}",
                ],
            }

        approved = 0

        for pair in manifest["pairs"]:
            pair_path = self.resolve_pair_manifest_path(
                path.parent,
                pair,
            )
            pair_manifest = self.load_pair_manifest(
                pair_path,
                allow_generated=True,
            )

            if (
                pair_manifest.get("approval_state")
                == "APPROVED"
            ):
                approved += 1

        return {
            "status": "READY"
            if approved
            else "PENDING_APPROVAL",
            "training_allowed": bool(approved),
            "approved_pair_count": approved,
            "blockers": []
            if approved
            else [
                "benchmark_pair_approval_required",
            ],
        }

    def validate_round_manifest(
        self,
        manifest,
        round_dir,
        allow_generated=False,
    ):
        if (
            manifest.get("kind")
            != "voice_preview_benchmark_round"
        ):
            raise ValueError(
                "Sai kind cua benchmark manifest."
            )

        if manifest.get("pair_count") != self.PAIR_COUNT:
            raise ValueError(
                "Benchmark phai co dung 20 Pair."
            )

        pairs = manifest.get("pairs", [])

        if len(pairs) != self.PAIR_COUNT:
            raise ValueError(
                "Danh sach Benchmark Pair khong du 20."
            )

        expected_ids = [
            f"pair_{index:03d}"
            for index in range(
                1,
                self.PAIR_COUNT + 1,
            )
        ]

        if [
            pair.get("pair_id")
            for pair in pairs
        ] != expected_ids:
            raise ValueError(
                "Pair ID Benchmark phai tu pair_001 den pair_020."
            )

        self.validate_benchmark_transcript(
            manifest.get(
                "benchmark_transcript",
                "",
            )
        )

        for pair in pairs:
            self.load_pair_manifest(
                self.resolve_pair_manifest_path(
                    round_dir,
                    pair,
                ),
                allow_generated=allow_generated,
            )

    def resolve_pair_manifest_path(
        self,
        round_dir,
        pair,
    ):
        pair_path = Path(
            pair.get(
                "manifest_path",
                "",
            )
        )
        if not pair_path.is_absolute():
            pair_path = Path(round_dir) / pair_path
        return pair_path

    def load_pair_manifest(
        self,
        path,
        allow_generated=False,
    ):
        manifest = self.load_json(path)

        if (
            manifest.get("kind")
            != "voice_preview_benchmark_pair"
        ):
            raise ValueError(
                "Sai kind cua pair manifest."
            )

        if (
            manifest.get("approval_state")
            not in self.APPROVAL_STATES
        ):
            raise ValueError(
                "Approval state trong pair manifest khong hop le."
            )

        previews = manifest.get(
            "previews",
            {},
        )

        for name in (
            "same_preview",
            "new_preview",
        ):
            preview = previews.get(
                name,
                {},
            )
            version = preview.get("version")

            if (
                not isinstance(version, int)
                or version < 1
                or preview.get("file")
                != f"{name}_v{version}.wav"
            ):
                raise ValueError(
                    "Pair manifest thieu preview contract."
                )

            status = preview.get("status")
            if status == self.PREVIEW_UNAVAILABLE:
                continue
            if not allow_generated:
                raise ValueError(
                    "Sprint Foundation khong duoc co preview da generate."
                )
            if status not in (
                self.PREVIEW_READY,
                self.PREVIEW_FAILED,
            ):
                raise ValueError(
                    "Trang thai Preview khong hop le."
                )

        return manifest

    def write_json_new(
        self,
        path,
        data,
    ):
        if Path(path).exists():
            raise FileExistsError(
                "Khong duoc ghi de Benchmark manifest."
            )

        Path(path).write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def write_json_replace(
        self,
        path,
        data,
    ):
        Path(path).write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def load_json(
        self,
        path,
    ):
        return json.loads(
            Path(path).read_text(
                encoding="utf-8",
            )
        )

    def sha256(
        self,
        path,
    ):
        digest = hashlib.sha256()
        with Path(path).open("rb") as source:
            for chunk in iter(
                lambda: source.read(1024 * 1024),
                b"",
            ):
                digest.update(chunk)
        return digest.hexdigest()

    def sha256_text(
        self,
        text,
    ):
        return hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()

    def relative_path(
        self,
        path,
        root,
    ):
        return str(
            Path(path).resolve().relative_to(
                Path(root).resolve()
            )
        ).replace("\\", "/")

    def timestamp(
        self,
    ):
        return datetime.now(
            timezone.utc
        ).isoformat()

from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
import json
import os
import re
import subprocess
import sys

try:

    from rapidfuzz import fuzz

except Exception:

    fuzz = None

try:

    from faster_whisper import WhisperModel

except Exception:

    WhisperModel = None


@dataclass
class AlignmentSegment:

    text: str

    start: float

    end: float

    score: float

    asr_text: str = ""

    language: str = ""

    words: list | None = None


class AlignmentService:

    MODEL_DIR_NAMES = {
        "tiny": "faster-whisper-tiny",
        "base": "faster-whisper-base",
        "small": "faster-whisper-small",
        "medium": "faster-whisper-medium",
        "large": "faster-whisper-large-v3",
        "large-v3": "faster-whisper-large-v3",
        "large-v3-turbo": "faster-whisper-large-v3-turbo",
    }

    def __init__(self):

        self.model = None

        self.model_name = None

        self.device = None

        self.compute_type = None

    #
    # Runtime
    #

    def validate_runtime(
        self,
        model="small",
        model_path="",
        model_cache="",
        python_executable=None,
        cuda_available=False,
        device="auto",
        compute_type=None,
        check_load=False,
    ):

        python_executable = str(
            python_executable
            or sys.executable
        )

        package = self.check_package(
            python_executable
        )

        if not package["available"]:

            return self.runtime_result(
                ready=False,
                status="package_missing",
                message="Chưa cài faster-whisper trong Python runtime.",
                python_executable=python_executable,
                model=model,
                model_path="",
                device="",
                compute_type="",
                package=package,
            )

        resolved_model = self.resolve_model_path(
            model=model,
            model_path=model_path,
            model_cache=model_cache,
        )

        if not resolved_model:

            return self.runtime_result(
                ready=False,
                status="model_missing",
                message="Chưa tìm thấy Faster-Whisper model local.",
                python_executable=python_executable,
                model=model,
                model_path="",
                device="",
                compute_type="",
                package=package,
            )

        resolved_device = self.resolve_device(
            device,
            cuda_available,
        )

        if resolved_device == "cuda_unavailable":

            return self.runtime_result(
                ready=False,
                status="cuda_unavailable",
                message="Yêu cầu CUDA nhưng RuntimeService báo CUDA chưa khả dụng.",
                python_executable=python_executable,
                model=model,
                model_path=resolved_model,
                device="cuda",
                compute_type="",
                package=package,
            )

        resolved_compute = self.resolve_compute_type(
            compute_type,
            resolved_device,
        )

        result = self.runtime_result(
            ready=True,
            status="ready",
            message="Faster-Whisper runtime sẵn sàng.",
            python_executable=python_executable,
            model=model,
            model_path=resolved_model,
            device=resolved_device,
            compute_type=resolved_compute,
            package=package,
        )

        if check_load and compute_type is None:

            working_compute = self.select_working_compute_type(
                result
            )

            if working_compute:

                result["compute_type"] = working_compute

                return result

            result["ready"] = False

            result["status"] = "model_load_failed"

            result["message"] = "Không load được Faster-Whisper model với các compute_type mặc định."

            return result

        if check_load:

            load = self.check_model_load(
                result
            )

            if not load["ready"]:

                result["ready"] = False

                result["status"] = "model_load_failed"

                result["message"] = load["message"]

        return result

    def select_working_compute_type(
        self,
        runtime,
    ):

        candidates = (
            [
                "float16",
                "int8_float16",
                "int8",
                "float32",
            ]
            if runtime["device"] == "cuda"
            else [
                "int8",
                "float32",
            ]
        )

        for compute_type in candidates:

            test_runtime = dict(
                runtime
            )

            test_runtime["compute_type"] = compute_type

            if self.check_model_load(
                test_runtime
            )["ready"]:

                return compute_type

        return ""

    def runtime_result(
        self,
        ready,
        status,
        message,
        python_executable,
        model,
        model_path,
        device,
        compute_type,
        package,
    ):

        return {
            "ready": ready,
            "status": status,
            "message": message,
            "python_executable": python_executable,
            "model": model,
            "model_path": model_path,
            "device": device,
            "compute_type": compute_type,
            "package": package,
        }

    def check_package(
        self,
        python_executable=None,
    ):

        python_executable = str(
            python_executable
            or sys.executable
        )

        command = [
            python_executable,
            "-c",
            (
                "import json, faster_whisper; "
                "print(json.dumps({'available': True, "
                "'version': getattr(faster_whisper, '__version__', '')}))"
            ),
        ]

        try:

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=20,
            )

        except Exception as e:

            return {
                "available": False,
                "version": "",
                "error": str(
                    e
                ),
            }

        if result.returncode != 0:

            return {
                "available": False,
                "version": "",
                "error": (
                    result.stderr.strip()
                    or result.stdout.strip()
                ),
            }

        try:

            return json.loads(
                result.stdout.strip()
            )

        except Exception:

            return {
                "available": True,
                "version": "",
                "error": "",
            }

    def resolve_model_path(
        self,
        model="small",
        model_path="",
        model_cache="",
    ):

        candidates = []

        if model_path:

            candidates.append(
                Path(model_path)
            )

        model_value = Path(
            str(model)
        )

        if model_value.exists():

            candidates.append(
                model_value
            )

        if model_cache:

            cache = Path(
                model_cache
            )

            names = [
                str(model),
                self.MODEL_DIR_NAMES.get(
                    str(model),
                    "",
                ),
            ]

            for name in names:

                if name:

                    candidates.append(
                        cache / name
                    )

        candidates.extend(
            self.huggingface_cache_candidates(
                model
            )
        )

        for candidate in candidates:

            if self.is_model_dir(
                candidate
            ):

                return str(
                    candidate
                )

        return ""

    def huggingface_cache_candidates(
        self,
        model,
    ):

        model = str(
            model
        )

        repo = (
            Path.home()
            / ".cache"
            / "huggingface"
            / "hub"
            / f"models--Systran--faster-whisper-{model}"
            / "snapshots"
        )

        if not repo.exists():

            return []

        return sorted(
            [
                item
                for item in repo.iterdir()
                if item.is_dir()
            ],
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )

    def is_model_dir(
        self,
        path,
    ):

        path = Path(
            path
        )

        if not path.exists() or not path.is_dir():

            return False

        required = [
            "config.json",
            "model.bin",
            "tokenizer.json",
        ]

        return all(
            (
                path / name
            ).exists()
            for name in required
        )

    def resolve_device(
        self,
        device,
        cuda_available,
    ):

        if device == "auto":

            return (
                "cuda"
                if cuda_available
                else "cpu"
            )

        if device == "cuda" and not cuda_available:

            return "cuda_unavailable"

        return device

    def resolve_compute_type(
        self,
        compute_type,
        device,
    ):

        if compute_type:

            return compute_type

        if device == "cuda":

            return "float16"

        return "int8"

    def check_model_load(
        self,
        runtime,
    ):

        code = (
            "from faster_whisper import WhisperModel\n"
            "WhisperModel("
            "r'''%s''', device=r'''%s''', compute_type=r'''%s''')\n"
            "print('OK')\n"
        ) % (
            runtime["model_path"],
            runtime["device"],
            runtime["compute_type"],
        )

        try:

            result = subprocess.run(
                [
                    runtime["python_executable"],
                    "-c",
                    code,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

        except Exception as e:

            return {
                "ready": False,
                "message": str(
                    e
                ),
            }

        if result.returncode != 0:

            return {
                "ready": False,
                "message": (
                    result.stderr.strip()
                    or result.stdout.strip()
                ),
            }

        return {
            "ready": True,
            "message": "OK",
        }

    #
    # Whisper
    #

    def load_model(

        self,

        model="small",

        device="auto",

        compute_type="int8",

    ):

        if WhisperModel is None:

            raise RuntimeError(
                "Chưa cài faster-whisper."
            )

        if (
            self.model is not None
            and self.model_name == model
            and self.device == device
            and self.compute_type == compute_type
        ):

            return

        self.model = WhisperModel(

            model,

            device=device,

            compute_type=compute_type,

        )

        self.model_name = model

        self.device = device

        self.compute_type = compute_type

    #
    # Speech -> Text
    #

    def transcribe(

        self,

        audio_file,

        language=None,

        model="small",

        device="auto",

        compute_type="int8",

        model_path="",

        model_cache="",

        python_executable=None,

        cuda_available=False,

    ):

        runtime = self.validate_runtime(
            model=model,
            model_path=model_path,
            model_cache=model_cache,
            python_executable=python_executable,
            cuda_available=cuda_available,
            device=device,
            compute_type=compute_type,
        )

        if not runtime["ready"]:

            raise RuntimeError(
                f"{runtime['status']}: {runtime['message']}"
            )

        if Path(
            runtime["python_executable"]
        ) != Path(
            sys.executable
        ):

            return self.transcribe_external(
                audio_file,
                language,
                runtime,
            )

        self.load_model(
            model=runtime["model_path"],
            device=runtime["device"],
            compute_type=runtime["compute_type"],
        )

        segments, info = self.model.transcribe(

            str(audio_file),

            beam_size=5,

            vad_filter=True,

            word_timestamps=True,

            language=language,

        )

        result = []

        detected_language = getattr(
            info,
            "language",
            "",
        )

        for segment in segments:

            words = []

            for word in getattr(
                segment,
                "words",
                [],
            ) or []:

                if (
                    getattr(
                        word,
                        "start",
                        None,
                    )
                    is None
                    or getattr(
                        word,
                        "end",
                        None,
                    )
                    is None
                ):

                    continue

                words.append(
                    {
                        "word": (
                            getattr(
                                word,
                                "word",
                                "",
                            )
                            or ""
                        ).strip(),
                        "start": float(
                            word.start
                        ),
                        "end": float(
                            word.end
                        ),
                    }
                )

            result.append(

                {

                    "text": segment.text.strip(),

                    "start": float(segment.start),

                    "end": float(segment.end),

                    "language": detected_language,

                    "words": words,

                }

            )

        return result

    def transcribe_external(
        self,
        audio_file,
        language,
        runtime,
    ):

        code = r"""
import json
import sys
from faster_whisper import WhisperModel

audio_file = sys.argv[1]
model_path = sys.argv[2]
device = sys.argv[3]
compute_type = sys.argv[4]
language = sys.argv[5] or None

model = WhisperModel(
    model_path,
    device=device,
    compute_type=compute_type,
)

segments, info = model.transcribe(
    audio=audio_file,
    beam_size=5,
    vad_filter=True,
    word_timestamps=True,
    language=language,
)

result = []
for segment in segments:
    words = []
    for word in getattr(segment, "words", []) or []:
        if getattr(word, "start", None) is None or getattr(word, "end", None) is None:
            continue
        words.append({
            "word": (getattr(word, "word", "") or "").strip(),
            "start": float(word.start),
            "end": float(word.end),
        })
    result.append({
        "text": (segment.text or "").strip(),
        "start": float(segment.start),
        "end": float(segment.end),
        "language": getattr(info, "language", ""),
        "words": words,
    })

print(json.dumps(result, ensure_ascii=False))
"""

        command = [
            runtime["python_executable"],
            "-c",
            code,
            str(audio_file),
            runtime["model_path"],
            runtime["device"],
            runtime["compute_type"],
            language or "",
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env={
                **os.environ,
                "PYTHONIOENCODING": "utf-8",
            },
            timeout=600,
        )

        if result.returncode != 0:

            raise RuntimeError(
                result.stderr.strip()
                or result.stdout.strip()
                or "Faster-Whisper transcribe failed."
            )

        return json.loads(
            result.stdout.strip() or "[]"
        )

    #
    # Normalize
    #

    def normalize(

        self,

        text,

    ):

        text = (

            text

            .replace("\n", " ")

            .replace("\r", " ")

            .replace("…", "...")

            .strip()

            .lower()

        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text

    #
    # Match
    #

    def match(

        self,

        transcript,

        original_text,

        threshold=80,

    ):

        candidates = self.split_candidates(
            original_text
        )

        matches = []

        for segment in transcript:

            spoken = self.normalize(

                segment["text"]

            )

            best_text = ""

            best_score = 0

            for candidate in candidates:

                score = self.score_text(
                    spoken,
                    candidate,
                )

                if score > best_score:

                    best_score = score

                    best_text = candidate

            if best_score < threshold:

                continue

            matches.append(

                AlignmentSegment(

                    text=best_text,

                    start=float(segment["start"]),

                    end=float(segment["end"]),

                    score=float(best_score),

                    asr_text=segment["text"],

                    language=segment.get(
                        "language",
                        "",
                    ),

                    words=segment.get(
                        "words",
                        [],
                    ),

                )

            )

        return matches

    def score_text(
        self,
        spoken,
        candidate,
    ):

        candidate = self.normalize(
            candidate
        )

        if fuzz is not None:

            return fuzz.token_set_ratio(
                spoken,
                candidate,
            )

        return (
            SequenceMatcher(
                None,
                spoken,
                candidate,
            ).ratio()
            * 100
        )

    def split_candidates(
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

        sentences = re.findall(
            r".+?(?:[.!?。！？…]+|$)",
            normalized,
        )

        candidates = [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

        if candidates:

            return candidates

        return [
            normalized
        ]

    #
    # Align
    #

    def align(

        self,

        audio_file,

        original_text,

        threshold=80,

        language=None,

        model="small",

        device="auto",

        compute_type="int8",

        model_path="",

        model_cache="",

        python_executable=None,

        cuda_available=False,

    ):

        transcript = self.transcribe(

            audio_file,

            language=language,

            model=model,

            device=device,

            compute_type=compute_type,

            model_path=model_path,

            model_cache=model_cache,

            python_executable=python_executable,

            cuda_available=cuda_available,

        )

        return self.match(

            transcript,

            original_text,

            threshold,

        )

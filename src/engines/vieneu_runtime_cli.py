from __future__ import annotations

import argparse
import json
from pathlib import Path
import wave


def required_paths(
    model_root,
    codec_root,
):

    onnx_dir = model_root / "onnx_int8"

    return {
        "model_root": model_root,
        "model_onnx_dir": onnx_dir,
        "model_prefill": onnx_dir / "vieneu_prefill.onnx",
        "model_decode_step": onnx_dir / "vieneu_decode_step.onnx",
        "model_acoustic_cached": onnx_dir / "vieneu_acoustic_cached.onnx",
        "model_heads": onnx_dir / "vieneu_v3_heads.npz",
        "codec_root": codec_root,
    }


def missing_paths(
    model_root,
    codec_root,
):

    return [
        name
        for name, path in required_paths(
            model_root,
            codec_root,
        ).items()
        if not path.exists()
    ]


def wav_info(
    path,
):

    with wave.open(
        str(
            path
        ),
        "rb",
    ) as wav:

        sample_rate = wav.getframerate()
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        frame_count = wav.getnframes()

    return {
        "path": str(
            path
        ),
        "exists": path.exists(),
        "size": path.stat().st_size,
        "sample_rate": sample_rate,
        "channels": channels,
        "sample_width": sample_width,
        "duration": frame_count / sample_rate
        if sample_rate
        else 0,
        "ok": bool(
            path.exists()
            and path.stat().st_size > 44
            and sample_rate == 48000
            and channels == 1
            and sample_width == 2
            and frame_count > 0
        ),
    }


def save_wav(
    path,
    audio,
):

    import numpy as np
    import soundfile as sf

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    sf.write(
        str(
            path
        ),
        np.asarray(
            audio,
            dtype=np.float32,
        ),
        48000,
        subtype="PCM_16",
    )


def probe(
    args,
):

    import numpy  # noqa: F401
    import soundfile  # noqa: F401
    from vieneu._v3_turbo_engine.onnx_runtime_lite import (  # noqa: F401
        OnnxV3LiteEngine,
    )

    missing = missing_paths(
        args.model_root,
        args.codec_root,
    )

    if missing:

        return {
            "ready": False,
            "status": "UNAVAILABLE",
            "reason": "vieneu_model_missing",
            "missing": missing,
            "model_root": str(
                args.model_root
            ),
            "codec_root": str(
                args.codec_root
            ),
        }

    return {
        "ready": True,
        "status": "READY",
        "backend": "CPU_ONNX",
        "sample_rate": 48000,
        "model_root": str(
            args.model_root
        ),
        "codec_root": str(
            args.codec_root
        ),
    }


def generate(
    args,
):

    import numpy as np
    from vieneu._v3_turbo_engine.onnx_runtime_lite import OnnxV3LiteEngine

    status = probe(
        args
    )

    if not status.get(
        "ready"
    ):

        raise RuntimeError(
            json.dumps(
                status,
                ensure_ascii=False,
            )
        )

    text = args.text_file.read_text(
        encoding="utf-8",
        errors="ignore",
    ).strip()

    if not text:

        raise RuntimeError(
            "text_empty"
        )

    if not args.reference_audio.exists():

        raise RuntimeError(
            f"reference_audio_missing:{args.reference_audio}"
        )

    if args.output_file.exists():

        raise RuntimeError(
            f"output_exists:{args.output_file}"
        )

    engine = OnnxV3LiteEngine(
        checkpoint_path=str(
            args.model_root
        ),
        onnx_dir=str(
            args.model_root / "onnx_int8"
        ),
        codec_dir=str(
            args.codec_root
        ),
        onnx_subfolder="onnx_int8",
        threads=args.threads,
    )

    speaker_emb, ref_codes = engine.prepare_reference(
        str(
            args.reference_audio
        ),
        denoise=args.denoise,
        use_ref_codes=True,
    )

    audio = engine.infer(
        text=text,
        speaker_emb=speaker_emb,
        ref_codes=ref_codes,
        style=args.style,
        use_ref_codes=True,
        temperature=args.temperature,
        top_k=args.top_k,
        top_p=args.top_p,
        max_new_frames=args.max_new_frames,
        repetition_penalty=1.2,
    )

    save_wav(
        args.output_file,
        audio,
    )

    validation = wav_info(
        args.output_file
    )

    if not validation["ok"]:

        raise RuntimeError(
            "wav_invalid:"
            + json.dumps(
                validation,
                ensure_ascii=False,
            )
        )

    return {
        "ready": True,
        "status": "SUCCESS",
        "engine_id": "vieneu",
        "backend": "CPU_ONNX",
        "sample_rate": 48000,
        "reference_audio": str(
            args.reference_audio
        ),
        "reference_text": args.reference_text,
        "text": text,
        "wav": validation,
    }


def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--probe",
        action="store_true",
    )

    parser.add_argument(
        "--model-root",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--codec-root",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--text-file",
        type=Path,
    )

    parser.add_argument(
        "--output-file",
        type=Path,
    )

    parser.add_argument(
        "--reference-audio",
        type=Path,
    )

    parser.add_argument(
        "--reference-text",
        default="",
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=0.70,
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=20,
    )

    parser.add_argument(
        "--top-p",
        type=float,
        default=0.95,
    )

    parser.add_argument(
        "--style",
        default="tu_nhien",
    )

    parser.add_argument(
        "--denoise",
        action="store_true",
    )

    parser.add_argument(
        "--max-new-frames",
        type=int,
        default=520,
    )

    parser.add_argument(
        "--threads",
        type=int,
        default=2,
    )

    return parser.parse_args()


def main():

    args = parse_args()

    if args.probe:

        result = probe(
            args
        )

    else:

        result = generate(
            args
        )

    print(
        json.dumps(
            result,
            ensure_ascii=True,
        )
    )

    return 0 if result.get(
        "ready",
        False,
    ) else 1


if __name__ == "__main__":

    raise SystemExit(
        main()
    )

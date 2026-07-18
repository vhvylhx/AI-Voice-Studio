from pathlib import Path
import subprocess

from models.generate_config import GenerateAudioProfile


class AudioMergeService:

    def __init__(
        self,
        ffmpeg="ffmpeg",
    ):

        self.ffmpeg = ffmpeg

    def merge(
        self,
        chunk_files,
        output_file,
        work_dir,
        profile=None,
    ):

        profile = profile or GenerateAudioProfile()

        output = Path(
            output_file
        )

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        files = [
            Path(file)
            for file in chunk_files
        ]

        if not files:

            raise RuntimeError(
                "no_audio_chunks"
            )

        for file in files:

            if not file.exists():

                raise RuntimeError(
                    f"chunk_missing:{file}"
                )

        work = Path(
            work_dir
        )

        work.mkdir(
            parents=True,
            exist_ok=True,
        )

        concat_file = work / "concat.txt"

        concat_file.write_text(
            "\n".join(
                f"file '{file.as_posix()}'"
                for file in files
            ),
            encoding="utf-8",
        )

        temp_wav = (
            output
            if output.suffix.lower() == ".wav"
            else work / "merged.wav"
        )

        self.run([
            self.ffmpeg,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-ac",
            "1",
            "-ar",
            "32000",
            "-acodec",
            "pcm_s16le",
            str(temp_wav),
        ])

        if output.suffix.lower() == ".mp3":

            self.run([
                self.ffmpeg,
                "-y",
                "-i",
                str(temp_wav),
                "-b:a",
                f"{profile.mp3_bitrate_kbps}k",
                str(output),
            ])

        return output

    def run(
        self,
        command,
    ):

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if result.returncode != 0:

            raise RuntimeError(
                result.stderr.strip()
                or "audio_merge_failed"
            )

        return result

    def output_suffix(
        self,
        output_format,
    ):

        value = str(
            output_format or "wav"
        ).lower()

        if value not in {
            "wav",
            "mp3",
        }:

            raise ValueError(
                "output_format_invalid"
            )

        return f".{value}"

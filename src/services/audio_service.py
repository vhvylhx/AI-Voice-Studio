from pathlib import Path
import subprocess
import json


class AudioService:

    def __init__(self):

        self.ffmpeg = "ffmpeg"

        self.ffprobe = "ffprobe"

    def duration(
        self,
        audio,
    ):

        info = self.probe(
            audio
        )

        return info["duration"]

    def probe(
        self,
        audio,
    ):

        audio = str(audio)

        cmd = [

            self.ffprobe,

            "-v",
            "error",

            "-print_format",
            "json",

            "-show_format",

            "-show_streams",

            audio,

        ]

        result = subprocess.run(

            cmd,

            capture_output=True,

            text=True,

            encoding="utf-8",

            errors="replace",

        )

        if result.returncode != 0:

            raise RuntimeError(
                result.stderr.strip()
                or "Không đọc được audio bằng ffprobe."
            )

        data = json.loads(
            result.stdout
        )

        audio_stream = None

        for stream in data.get(
            "streams",
            [],
        ):

            if stream.get(
                "codec_type"
            ) == "audio":

                audio_stream = stream

                break

        if audio_stream is None:

            raise RuntimeError(
                "File không có audio stream."
            )

        duration = (
            audio_stream.get("duration")
            or data.get("format", {}).get("duration")
            or 0
        )

        return {
            "duration": float(duration),
            "sample_rate": int(
                audio_stream.get(
                    "sample_rate",
                    0,
                )
            ),
            "channels": int(
                audio_stream.get(
                    "channels",
                    0,
                )
            ),
            "channel_layout": audio_stream.get(
                "channel_layout",
                "",
            ),
            "codec": audio_stream.get(
                "codec_name",
                "",
            ),
            "format": data.get(
                "format",
                {},
            ).get(
                "format_name",
                "",
            ),
            "bit_rate": int(
                data.get(
                    "format",
                    {},
                ).get(
                    "bit_rate",
                    0,
                )
                or 0
            ),
        }

    def is_mono(
        self,
        audio,
    ):

        info = self.probe(
            audio
        )

        return info["channels"] == 1

    def convert_wav(
        self,
        input_file,
        output_file,
        sample_rate=32000,
    ):

        output = Path(output_file)

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        cmd = [

            self.ffmpeg,

            "-y",

            "-i",
            str(input_file),

            "-ac",
            "1",

            "-ar",
            str(sample_rate),

            str(output),

        ]

        subprocess.run(
            cmd,
            check=True,
        )

        return output

    def convert_segment_wav(
        self,
        input_file,
        output_file,
        start,
        duration,
        sample_rate=32000,
    ):

        output = Path(output_file)

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        cmd = [

            self.ffmpeg,

            "-y",

            "-ss",
            str(start),

            "-i",
            str(input_file),

            "-t",
            str(duration),

            "-ac",
            "1",

            "-ar",
            str(sample_rate),

            "-vn",

            "-acodec",
            "pcm_s16le",

            str(output),

        ]

        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        return output

    def cut(
        self,
        input_file,
        output_file,
        start,
        end,
    ):

        output = Path(output_file)

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        cmd = [

            self.ffmpeg,

            "-y",

            "-i",
            str(input_file),

            "-ss",
            str(start),

            "-to",
            str(end),

            "-c",
            "copy",

            str(output),

        ]

        subprocess.run(
            cmd,
            check=True,
        )

        return output

    def normalize(
        self,
        input_file,
        output_file,
    ):

        output = Path(output_file)

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        cmd = [

            self.ffmpeg,

            "-y",

            "-i",
            str(input_file),

            "-af",
            "loudnorm",

            str(output),

        ]

        subprocess.run(
            cmd,
            check=True,
        )

        return output

    def resample(
        self,
        input_file,
        output_file,
        sample_rate=32000,
    ):

        output = Path(output_file)

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        cmd = [

            self.ffmpeg,

            "-y",

            "-i",
            str(input_file),

            "-ar",
            str(sample_rate),

            str(output),

        ]

        subprocess.run(
            cmd,
            check=True,
        )

        return output

    def silence_detect(
        self,
        input_file,
    ):

        """
        TODO

        Sprint sau:
            ffmpeg silencedetect
            hoặc
            py-webrtcvad

        Trả về:

        [
            (start, end),
            ...
        ]
        """

        return []

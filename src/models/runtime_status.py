from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field


@dataclass
class RuntimeStatus:

    #
    # Python
    #

    python_available: bool = False

    python_version: str = ""

    python_executable: str = ""

    #
    # FFmpeg
    #

    ffmpeg_available: bool = False

    ffmpeg_version: str = ""

    #
    # NVIDIA / CUDA
    #

    nvidia_available: bool = False

    cuda_available: bool = False

    cuda_version: str = ""

    gpu_available: bool = False

    gpu_name: str = ""

    gpu_driver: str = ""

    #
    # GPT-SoVITS
    #

    gpt_sovits_ready: bool = False

    gpt_sovits_path: str = ""

    gpt_sovits_python: str = ""

    gpt_sovits_webui: str = ""

    gpt_sovits_cli: str = ""

    #
    # Engine
    #

    engine_id: str = ""

    engine_name: str = ""

    engine_available: bool = False

    engine_running: bool = False

    #
    # Summary
    #

    ready: bool = False

    errors: list[str] = field(
        default_factory=list
    )

    def to_dict(self):

        return asdict(
            self
        )

from dataclasses import dataclass, field


@dataclass
class EngineInfo:

    #
    # Basic
    #

    id: str

    name: str

    version: str = ""

    author: str = ""

    description: str = ""

    #
    # Install
    #

    executable: str = ""

    default_path: str = ""

    engine_path: str = ""

    installed: bool = False

    running: bool = False

    available: bool = False

    selected: bool = False

    #
    # Environment
    #

    python_version: str = ""

    python_executable: str = ""

    ffmpeg_available: bool = False

    cuda_version: str = ""

    cuda_available: bool = False

    nvidia_available: bool = False

    gpu_name: str = ""

    gpu_driver: str = ""

    #
    # Capability
    #

    can_generate: bool = True

    can_train: bool = True

    can_preview: bool = True

    #
    # Supported
    #

    supported_languages: list[str] = field(
        default_factory=lambda: [
            "vi",
        ]
    )

    supported_formats: list[str] = field(
        default_factory=lambda: [
            "wav",
            "mp3",
        ]
    )

    #
    # API
    #

    api_host: str = "127.0.0.1"

    api_port: int = 9880

    #
    # Runtime
    #

    last_error: str = ""

    runtime_status: dict = field(
        default_factory=dict
    )

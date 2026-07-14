from dataclasses import dataclass


@dataclass
class EngineModel:

    #
    # Basic
    #

    id: str

    path: str

    #
    # Info
    #

    version: str = ""

    python_version: str = ""

    cuda_version: str = ""

    #
    # State
    #

    enabled: bool = True

    installed: bool = False

    default: bool = False
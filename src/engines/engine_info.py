from dataclasses import dataclass


@dataclass
class EngineInfo:

    id: str

    name: str

    version: str

    author: str

    description: str

    supported_languages: list[str]
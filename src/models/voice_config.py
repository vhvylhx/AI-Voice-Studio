from dataclasses import dataclass


@dataclass
class VoiceConfig:

    engine: str = "mock"

    model: str = ""

    language: str = "vi"

    speed: float = 1.0

    pitch: float = 1.0

    volume: float = 1.0

    temperature: float = 1.0

    top_p: float = 1.0
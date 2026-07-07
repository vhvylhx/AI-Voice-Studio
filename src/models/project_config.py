from dataclasses import dataclass


@dataclass
class ProjectConfig:

    engine: str = ""

    voice: str = ""

    rule: str = ""

    output_format: str = "mp3"

    auto_skip_exists: bool = True

    auto_resume: bool = True
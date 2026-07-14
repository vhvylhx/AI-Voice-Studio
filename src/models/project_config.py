from dataclasses import dataclass
from dataclasses import fields


@dataclass
class ProjectConfig:

    #
    # Schema
    #

    schema_version: int = 1

    #
    # Voice
    #

    voice: str = ""

    #
    # Engine
    #

    engine: str = ""

    #
    # Rule
    #

    rule: str = ""

    #
    # Output
    #

    output_format: str = "mp3"

    #
    # Folder
    #

    text_folder: str = "text"

    audio_folder: str = "audio"

    export_folder: str = "export"

    #
    # Queue
    #

    auto_skip_exists: bool = True

    auto_resume: bool = True

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        if data is None:

            data = {}

        names = {
            field.name
            for field in fields(cls)
        }

        migrated = {}

        for name in names:

            if name in data:

                migrated[name] = data[name]

        return cls(
            **migrated
        )

    def to_dict(self):

        return {
            field.name: getattr(
                self,
                field.name,
            )
            for field in fields(self)
        }

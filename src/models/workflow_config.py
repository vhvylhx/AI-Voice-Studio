from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class WorkflowConfig:

    source_mode: str = "same_folder"

    input_folder: str = ""

    audio_folder: str = ""

    text_folder: str = ""

    output_folder: str = ""

    use_input_folder_as_output: bool = True

    auto_repair: bool = True

    review_mode: str = "auto"

    selected_voice_id: str = ""

    runtime_profile_id: str = ""

    def resolved_output_folder(
        self,
    ):

        if self.use_input_folder_as_output:

            if self.input_folder:

                return self.input_folder

            if (
                self.audio_folder
                and self.audio_folder == self.text_folder
            ):

                return self.audio_folder

            return self.input_folder

        return self.output_folder

    def validate(
        self,
    ):

        errors = []

        if (
            not self.input_folder
            and not self.audio_folder
            and not self.text_folder
        ):

            errors.append(
                "input_folder_required"
            )

        if (
            self.audio_folder
            and not self.text_folder
        ):

            errors.append(
                "text_folder_required"
            )

        if (
            self.text_folder
            and not self.audio_folder
        ):

            errors.append(
                "audio_folder_required"
            )

        if (
            not self.use_input_folder_as_output
            and not self.output_folder
        ):

            errors.append(
                "output_folder_required"
            )

        return errors

    def to_dict(
        self,
    ):

        return asdict(
            self
        )

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        if isinstance(
            data,
            cls,
        ):

            return data

        data = data or {}

        return cls(
            source_mode=str(
                data.get(
                    "source_mode",
                    "same_folder"
                    if (
                        data.get(
                            "input_folder",
                            "",
                        )
                        or data.get(
                            "audio_folder",
                            "",
                        )
                        == data.get(
                            "text_folder",
                            "",
                        )
                    )
                    else "separate_folders",
                )
            ),
            input_folder=str(
                data.get(
                    "input_folder",
                    "",
                )
            ),
            audio_folder=str(
                data.get(
                    "audio_folder",
                    data.get(
                        "input_folder",
                        "",
                    ),
                )
            ),
            text_folder=str(
                data.get(
                    "text_folder",
                    data.get(
                        "input_folder",
                        "",
                    ),
                )
            ),
            output_folder=str(
                data.get(
                    "output_folder",
                    "",
                )
            ),
            use_input_folder_as_output=bool(
                data.get(
                    "use_input_folder_as_output",
                    True,
                )
            ),
            auto_repair=bool(
                data.get(
                    "auto_repair",
                    True,
                )
            ),
            review_mode=str(
                data.get(
                    "review_mode",
                    "auto",
                )
            ),
            selected_voice_id=str(
                data.get(
                    "selected_voice_id",
                    "",
                )
            ),
            runtime_profile_id=str(
                data.get(
                    "runtime_profile_id",
                    "",
                )
            ),
        )

    @classmethod
    def from_paths(
        cls,
        input_folder,
        source_mode="same_folder",
        audio_folder="",
        text_folder="",
        output_folder="",
        use_input_folder_as_output=True,
        auto_repair=True,
        review_mode="auto",
        selected_voice_id="",
        runtime_profile_id="",
    ):

        return cls(
            source_mode=source_mode,
            input_folder=str(
                Path(
                    input_folder
                )
            )
            if input_folder
            else "",
            audio_folder=str(
                Path(
                    audio_folder
                )
            )
            if audio_folder
            else "",
            text_folder=str(
                Path(
                    text_folder
                )
            )
            if text_folder
            else "",
            output_folder=str(
                Path(
                    output_folder
                )
            )
            if output_folder
            else "",
            use_input_folder_as_output=use_input_folder_as_output,
            auto_repair=auto_repair,
            review_mode=review_mode,
            selected_voice_id=selected_voice_id,
            runtime_profile_id=runtime_profile_id,
        )

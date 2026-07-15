from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class WorkflowConfig:

    input_folder: str = ""

    output_folder: str = ""

    use_input_folder_as_output: bool = True

    auto_repair: bool = True

    review_mode: str = "auto"

    def resolved_output_folder(
        self,
    ):

        if self.use_input_folder_as_output:

            return self.input_folder

        return self.output_folder

    def validate(
        self,
    ):

        errors = []

        if not self.input_folder:

            errors.append(
                "input_folder_required"
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
            input_folder=str(
                data.get(
                    "input_folder",
                    "",
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
        )

    @classmethod
    def from_paths(
        cls,
        input_folder,
        output_folder="",
        use_input_folder_as_output=True,
        auto_repair=True,
        review_mode="auto",
    ):

        return cls(
            input_folder=str(
                Path(
                    input_folder
                )
            )
            if input_folder
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
        )

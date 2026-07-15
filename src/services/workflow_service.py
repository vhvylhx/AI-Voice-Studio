from pathlib import Path

from config.workflow_config import DEFAULT_WORKFLOW_CONFIG
from models.workflow_config import WorkflowConfig


class WorkflowService:

    def create_config(
        self,
        input_folder="",
        output_folder="",
        use_input_folder_as_output=True,
        auto_repair=True,
        review_mode="auto",
    ):

        return WorkflowConfig.from_paths(
            input_folder=input_folder,
            output_folder=output_folder,
            use_input_folder_as_output=use_input_folder_as_output,
            auto_repair=auto_repair,
            review_mode=review_mode,
        )

    def default_config(
        self,
    ):

        return WorkflowConfig.from_dict(
            DEFAULT_WORKFLOW_CONFIG
        )

    def resolve_output_folder(
        self,
        config,
    ):

        config = WorkflowConfig.from_dict(
            config
        )

        output = config.resolved_output_folder()

        return Path(
            output
        ) if output else Path()

    def validate(
        self,
        config,
    ):

        config = WorkflowConfig.from_dict(
            config
        )

        errors = config.validate()

        return {
            "ready": not errors,
            "errors": errors,
            "input_folder": config.input_folder,
            "output_folder": config.resolved_output_folder(),
            "use_input_folder_as_output": config.use_input_folder_as_output,
            "auto_repair": config.auto_repair,
            "review_mode": config.review_mode,
        }

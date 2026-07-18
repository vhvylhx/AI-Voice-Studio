from pathlib import Path

from config.workflow_config import DEFAULT_WORKFLOW_CONFIG
from models.workflow_config import WorkflowConfig


class WorkflowService:

    def create_config(
        self,
        input_folder="",
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

        return WorkflowConfig.from_paths(
            input_folder=input_folder,
            source_mode=source_mode,
            audio_folder=audio_folder,
            text_folder=text_folder,
            output_folder=output_folder,
            use_input_folder_as_output=use_input_folder_as_output,
            auto_repair=auto_repair,
            review_mode=review_mode,
            selected_voice_id=selected_voice_id,
            runtime_profile_id=runtime_profile_id,
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
            "source_mode": config.source_mode,
            "input_folder": config.input_folder,
            "audio_folder": config.audio_folder,
            "text_folder": config.text_folder,
            "output_folder": config.resolved_output_folder(),
            "use_input_folder_as_output": config.use_input_folder_as_output,
            "auto_repair": config.auto_repair,
            "review_mode": config.review_mode,
            "selected_voice_id": config.selected_voice_id,
            "runtime_profile_id": config.runtime_profile_id,
        }

    def create_same_folder_config(
        self,
        folder,
        output_folder="",
        use_input_folder_as_output=True,
        **kwargs,
    ):

        return self.create_config(
            input_folder=folder,
            source_mode="same_folder",
            audio_folder=folder,
            text_folder=folder,
            output_folder=output_folder,
            use_input_folder_as_output=use_input_folder_as_output,
            **kwargs,
        )

    def create_separate_folder_config(
        self,
        audio_folder,
        text_folder,
        output_folder="",
        **kwargs,
    ):

        return self.create_config(
            input_folder="",
            source_mode="separate_folders",
            audio_folder=audio_folder,
            text_folder=text_folder,
            output_folder=output_folder,
            use_input_folder_as_output=False,
            **kwargs,
        )

    def detect_legacy_workspace(
        self,
        voice_name,
        workspace_root="workspace",
    ):

        folder = Path(
            workspace_root
        ) / str(
            voice_name
        )

        if not folder.exists():

            return None

        return self.create_same_folder_config(
            folder=folder,
            output_folder="",
            use_input_folder_as_output=True,
        )

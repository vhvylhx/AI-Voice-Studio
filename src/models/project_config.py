from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from datetime import datetime
from uuid import uuid4


@dataclass
class ProjectConfig:

    #
    # Schema
    #

    schema_version: int = 2

    project_id: str = ""

    display_name: str = ""

    description: str = ""

    created_at: str = ""

    updated_at: str = ""

    last_opened_at: str = ""

    status: str = "active"

    archive_state: str = "active"

    workspace_root: str = ""

    project_root: str = ""

    app_version_created: str = ""

    app_version_last_opened: str = ""

    source_project_id: str = ""

    duplicated_from_project_id: str = ""

    imported_from: dict = field(
        default_factory=dict
    )

    tags: list[str] = field(
        default_factory=list
    )

    favorite: bool = False

    notes: str = ""

    health_state: str = "unknown"

    validation_messages: list[dict] = field(
        default_factory=list
    )

    reference_summary: dict = field(
        default_factory=dict
    )

    relative_paths: dict = field(
        default_factory=dict
    )

    project_settings: dict = field(
        default_factory=dict
    )

    active_voice_id: str = ""

    active_style_profile_id: str = ""

    active_training_config_id: str = ""

    active_generate_config_id: str = ""

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
    # Last Dataset Workflow
    #

    last_audio_folder: str = ""

    last_text_folder: str = ""

    last_output_folder: str = ""

    last_source_mode: str = "same_folder"

    last_use_input_as_output: bool = True

    last_voice_id: str = ""

    last_runtime_profile_id: str = ""

    #
    # Last Runtime Training Profile
    #

    training_profile_mode: str = "auto"

    auto_detect_hardware: bool = True

    training_runtime_profile_id: str = ""

    training_compute_mode: str = "auto"

    training_batch_size: int = 1

    training_num_workers: int = 0

    training_vram_profile: str = "low_vram"

    training_gpt_epochs: int = 20

    training_sovits_epochs: int = 50

    training_save_interval: int = 1

    training_pretrained_model_version: str = "v2Pro"

    training_resume_policy: str = "manual"

    training_custom_config: dict = field(
        default_factory=dict
    )

    training_hardware_fingerprint: str = ""

    #
    # Last Generate Selection
    #

    last_generate_mode: str = "standard"

    last_generate_voice_id: str = ""

    last_generate_variant_id: str = ""

    last_generate_allow_all_variants: bool = False

    last_generate_variant_ids: list[str] = field(
        default_factory=list
    )

    last_generate_allow_all_styles: bool = False

    last_generate_style_ids: list[str] = field(
        default_factory=list
    )

    last_generate_speed: float = 1.0

    last_generate_preset_id: str = ""

    last_generate_reference_style_id: str = ""

    last_generate_text_profile_id: str = ""

    last_generate_input_path: str = ""

    last_generate_output_folder: str = ""

    last_generate_output_name: str = ""

    last_generate_output_format: str = "wav"

    last_generate_mp3_bitrate_kbps: int = 192

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

        config = cls(
            **migrated
        )

        config.normalize()

        return config

    def normalize(
        self,
    ):

        if not self.created_at:

            self.created_at = datetime.now().isoformat()

        if not self.updated_at:

            self.updated_at = self.created_at

        if not self.status:

            self.status = "active"

        if not self.archive_state:

            self.archive_state = (
                "archived"
                if self.status == "archived"
                else "active"
            )

        if self.archive_state == "archived":

            self.status = "archived"

        return self

    def ensure_project_id(
        self,
    ):

        if not self.project_id:

            self.project_id = uuid4().hex

        return self.project_id

    def to_dict(self):

        return {
            field.name: getattr(
                self,
                field.name,
            )
            for field in fields(self)
        }

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field


REFERENCE_MODE_APP_STYLE_PROFILE = "app_style_profile"
REFERENCE_MODE_CREATE_STYLE_PROFILE = "create_style_profile_from_audio_text"
REFERENCE_MODE_SPEAKER_REFERENCE_ONLY = "speaker_reference_only"
REFERENCE_MODE_NONE = "none"

SPEAKER_REFERENCE_SELECTED_FILE = "selected_file"
SPEAKER_REFERENCE_SELECTED_FOLDER = "selected_folder"
SPEAKER_REFERENCE_TRAINING_DATASET = "training_dataset"
SPEAKER_REFERENCE_VOICE_DEFAULT = "voice_default"
SPEAKER_REFERENCE_NONE = "none"

VALID_REFERENCE_MODES = {
    REFERENCE_MODE_APP_STYLE_PROFILE,
    REFERENCE_MODE_CREATE_STYLE_PROFILE,
    REFERENCE_MODE_SPEAKER_REFERENCE_ONLY,
    REFERENCE_MODE_NONE,
}

VALID_SPEAKER_REFERENCE_MODES = {
    SPEAKER_REFERENCE_SELECTED_FILE,
    SPEAKER_REFERENCE_SELECTED_FOLDER,
    SPEAKER_REFERENCE_TRAINING_DATASET,
    SPEAKER_REFERENCE_VOICE_DEFAULT,
    SPEAKER_REFERENCE_NONE,
}


@dataclass
class TrainingReferenceConfig:

    schema_version: int = 1

    reference_mode: str = REFERENCE_MODE_NONE

    style_profile_id: str = ""

    speaker_reference_asset_id: str = ""

    speaker_reference_text_asset_id: str = ""

    audio_text_manifest_id: str = ""

    dataset_id: str = ""

    dataset_item_ids: list[str] = field(
        default_factory=list
    )

    validation_report_ids: list[str] = field(
        default_factory=list
    )

    style_strength: float = 1.0

    create_style_profile: bool = False

    style_profile_draft_id: str = ""

    speaker_reference_mode: str = SPEAKER_REFERENCE_NONE

    speaker_reference_audio: str = ""

    speaker_reference_text: str = ""

    speaker_reference_folder: str = ""

    use_training_dataset_as_reference: bool = False

    selected_training_segment_ids: list[str] = field(
        default_factory=list
    )

    selected_segment_asset_ids: list[str] = field(
        default_factory=list
    )

    auto_select_training_reference: bool = False

    reference_source_origin: str = ""

    last_validated_at: str = ""

    validation_state: str = "pending"

    validation_messages: list[dict] = field(
        default_factory=list
    )

    def normalize(
        self,
    ):

        if self.reference_mode not in VALID_REFERENCE_MODES:

            self.reference_mode = REFERENCE_MODE_NONE

        if self.speaker_reference_mode not in VALID_SPEAKER_REFERENCE_MODES:

            self.speaker_reference_mode = SPEAKER_REFERENCE_NONE

        try:

            self.style_strength = float(
                self.style_strength
            )

        except Exception:

            self.style_strength = 1.0

        self.selected_training_segment_ids = [
            str(
                item
            )
            for item in self.selected_training_segment_ids or []
        ]

        self.dataset_item_ids = [
            str(
                item
            )
            for item in self.dataset_item_ids or []
        ]

        self.validation_report_ids = [
            str(
                item
            )
            for item in self.validation_report_ids or []
        ]

        self.selected_segment_asset_ids = [
            str(
                item
            )
            for item in self.selected_segment_asset_ids or []
        ]

        self.validation_messages = [
            dict(
                item
            )
            for item in self.validation_messages or []
            if isinstance(
                item,
                dict,
            )
        ]

        return self

    def active_style_profile_id(
        self,
    ):

        if self.reference_mode == REFERENCE_MODE_APP_STYLE_PROFILE:

            return self.style_profile_id

        if self.reference_mode == REFERENCE_MODE_CREATE_STYLE_PROFILE:

            return self.style_profile_draft_id

        return ""

    def to_dict(
        self,
    ):

        return asdict(
            self.normalize()
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

            return data.normalize()

        data = data or {}

        names = set(
            cls.__dataclass_fields__.keys()
        )

        config = cls(
            **{
                key: value
                for key, value in data.items()
                if key in names
            }
        )

        return config.normalize()

from dataclasses import asdict
from dataclasses import dataclass


@dataclass
class AlignmentQualityConfig:

    similarity_threshold: float = 90.0

    min_clip_duration: float = 2.0

    max_clip_duration: float = 10.0

    target_clip_duration: float = 6.0

    max_source_error_rate: float = 0.35

    min_valid_segments_per_source: int = 3

    allow_ratio_fallback: bool = False

    sample_rate: int = 32000

    language: str = "vi"

    alignment_model: str = "small"

    alignment_device: str = "auto"

    alignment_compute_type: str | None = None

    include_weak_source_in_metadata: bool = False

    def to_dict(self):

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
            **{
                key: value
                for key, value in data.items()
                if key in cls.__dataclass_fields__
            }
        )

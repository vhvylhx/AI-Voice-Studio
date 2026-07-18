from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime


JOB_QUEUED = "queued"
JOB_PREPARING = "preparing"
JOB_GENERATING = "generating"
JOB_POST_PROCESSING = "post_processing"
JOB_COMPLETED = "completed"
JOB_FAILED = "failed"
JOB_CANCELLED = "cancelled"
JOB_INTERRUPTED = "interrupted"


@dataclass
class ApiGenerationJob:

    job_id: str = ""

    request_id: str = ""

    status: str = JOB_QUEUED

    progress: int = 0

    current_stage: str = ""

    message_vi: str = ""

    created_at: str = ""

    started_at: str = ""

    completed_at: str = ""

    error_code: str = ""

    error_message_vi: str = ""

    request: dict = field(
        default_factory=dict
    )

    result: dict = field(
        default_factory=dict
    )

    def ensure_created_at(
        self,
    ):

        if not self.created_at:

            self.created_at = datetime.now().isoformat()

        return self.created_at

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
            **{
                key: value
                for key, value in data.items()
                if key in cls.__dataclass_fields__
            }
        )

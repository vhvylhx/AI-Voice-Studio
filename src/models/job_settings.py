from dataclasses import dataclass


@dataclass
class JobQueueSettings:

    auto_start_queue: bool = False

    max_concurrent_jobs: int = 1

    completed_history_retention_days: int = 30

    auto_retry: bool = False

    default_max_retries: int = 0

    confirm_cancel: bool = True

    confirm_close_with_active_jobs: bool = True

    log_retention_days: int = 30

    auto_resume_interrupted_jobs: bool = False

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        data = dict(
            data or {}
        )

        allowed = {
            field_name
            for field_name in cls.__dataclass_fields__
        }

        return cls(
            **{
                key: value
                for key, value in data.items()
                if key in allowed
            }
        )

    def to_dict(self):

        return {
            "auto_start_queue": self.auto_start_queue,
            "max_concurrent_jobs": int(
                self.max_concurrent_jobs
            ),
            "completed_history_retention_days": int(
                self.completed_history_retention_days
            ),
            "auto_retry": self.auto_retry,
            "default_max_retries": int(
                self.default_max_retries
            ),
            "confirm_cancel": self.confirm_cancel,
            "confirm_close_with_active_jobs": self.confirm_close_with_active_jobs,
            "log_retention_days": int(
                self.log_retention_days
            ),
            "auto_resume_interrupted_jobs": self.auto_resume_interrupted_jobs,
        }

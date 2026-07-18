import json
from datetime import datetime
from pathlib import Path


class JobLogService:

    def __init__(
        self,
        repository=None,
    ):

        self.repository = repository

    def log_file(
        self,
        job,
    ):

        if job.log_path:

            return Path(
                job.log_path
            )

        if self.repository is None:

            return Path(
                "workspace/jobs/jobs"
            ) / job.job_id / "job.log"

        return self.repository.job_dir(
            job.job_id
        ) / "job.log"

    def write(
        self,
        job,
        message,
        level="info",
        stage="",
        data=None,
    ):

        file = self.log_file(
            job
        )

        file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = {
            "time": datetime.now().isoformat(),
            "level": level,
            "job_id": job.job_id,
            "stage": stage
            or job.progress_stage,
            "message": str(
                message
            ),
            "data": data
            or {},
        }

        with open(
            file,
            "a",
            encoding="utf-8",
        ) as handle:

            handle.write(
                json.dumps(
                    payload,
                    ensure_ascii=False,
                )
                + "\n"
            )

        try:

            from services.app_events import AppEvents

            AppEvents.log_message(
                {
                    "time": payload[
                        "time"
                    ],
                    "level": level,
                    "category": f"job:{job.job_id}",
                    "message": payload[
                        "message"
                    ],
                }
            )

        except Exception:

            pass

        return payload

    def tail(
        self,
        job,
        lines=100,
    ):

        file = self.log_file(
            job
        )

        if not file.exists():

            return []

        content = file.read_text(
            encoding="utf-8",
            errors="replace",
        ).splitlines()

        return content[
            -int(
                lines
            ):
        ]

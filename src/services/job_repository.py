import json
import os
import shutil
from pathlib import Path

from models.job_model import (
    JOB_PRIORITIES,
    JobModel,
    now_iso,
)


class JobRepository:

    def __init__(
        self,
        root="workspace/jobs",
    ):

        self.root = Path(
            root
        )

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.jobs_root = self.root / "jobs"

        self.corrupt_root = self.root / "corrupt"

        self.jobs_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.corrupt_root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def next_id(
        self,
    ):

        highest = 0

        for folder in self.jobs_root.glob(
            "job_*"
        ):

            try:

                highest = max(
                    highest,
                    int(
                        folder.name.split(
                            "_"
                        )[-1]
                    ),
                )

            except Exception:

                continue

        return f"job_{highest + 1:06d}"

    def job_dir(
        self,
        job_id,
    ):

        return self.jobs_root / self.safe_id(
            job_id
        )

    def job_file(
        self,
        job_id,
    ):

        return self.job_dir(
            job_id
        ) / "job.json"

    def save(
        self,
        job,
    ):

        job = JobModel.from_dict(
            job.to_dict()
            if hasattr(
                job,
                "to_dict",
            )
            else job
        )

        job.touch()

        folder = self.job_dir(
            job.job_id
        )

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not job.log_path:

            job.log_path = str(
                folder / "job.log"
            )

        self.atomic_write_json(
            folder / "job.json",
            job.to_dict(),
        )

        return job

    def load(
        self,
        job_id,
    ):

        file = self.job_file(
            job_id
        )

        if not file.exists():

            return None

        try:

            return JobModel.from_dict(
                json.loads(
                    file.read_text(
                        encoding="utf-8"
                    )
                )
            )

        except Exception:

            self.quarantine(
                file
            )

            return None

    def list_jobs(
        self,
        state=None,
        project_id=None,
        job_type=None,
    ):

        jobs = []

        for file in self.jobs_root.glob(
            "*/job.json"
        ):

            job = self.load(
                file.parent.name
            )

            if job is None:

                continue

            if state and job.state != state:

                continue

            if project_id and job.project_id != project_id:

                continue

            if job_type and job.job_type != job_type:

                continue

            jobs.append(
                job
            )

        jobs.sort(
            key=lambda item: (
                -JOB_PRIORITIES.get(
                    item.priority,
                    20,
                ),
                item.created_at,
            )
        )

        return jobs

    def update_state(
        self,
        job,
        state,
    ):

        job.state = state

        job.updated_at = now_iso()

        return self.save(
            job
        )

    def recover_startup(
        self,
    ):

        recovered = []

        for job in self.list_jobs():

            if job.state in {
                "running",
                "pause_requested",
                "resume_requested",
                "cancel_requested",
                "cancelling",
            }:

                previous_state = job.state

                job.state = "interrupted"

                job.recovery_state[
                    "startup_recovery"
                ] = {
                    "previous_state": previous_state,
                    "recovered_at": now_iso(),
                    "policy": "manual_resume_required",
                }

                self.save(
                    job
                )

                recovered.append(
                    job.job_id
                )

        return recovered

    def atomic_write_json(
        self,
        file,
        data,
    ):

        file = Path(
            file
        )

        file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp = file.with_suffix(
            file.suffix + ".tmp"
        )

        with open(
            temp,
            "w",
            encoding="utf-8",
        ) as handle:

            json.dump(
                data,
                handle,
                indent=4,
                ensure_ascii=False,
            )

            handle.flush()

        os.replace(
            temp,
            file
        )

    def quarantine(
        self,
        file,
    ):

        file = Path(
            file
        )

        target = (
            self.corrupt_root
            / f"{file.parent.name}_{now_iso().replace(':', '-')}.json"
        )

        try:

            shutil.copy2(
                file,
                target,
            )

        except Exception:

            pass

    def safe_id(
        self,
        value,
    ):

        return "".join(
            char
            for char in str(
                value
            )
            if char.isalnum()
            or char in {
                "_",
                "-",
            }
        )

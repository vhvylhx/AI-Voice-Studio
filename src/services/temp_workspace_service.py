import shutil
from pathlib import Path
from uuid import uuid4

from models.generate_config import (
    TEMP_STATUS_CANCEL,
    TEMP_STATUS_ERROR,
    TEMP_STATUS_PAUSE,
    TEMP_STATUS_STOPPED,
    TEMP_STATUS_SUCCESS,
    TempWorkspace,
)


class TempWorkspaceService:

    def __init__(
        self,
        root="temp",
    ):

        self.root = Path(
            root
        )

    def create(
        self,
        kind="generate",
        job_id="",
        resume=False,
    ):

        job_id = job_id or uuid4().hex

        work_dir = (
            self.root
            / kind
            / job_id
        )

        work_dir.mkdir(
            parents=True,
            exist_ok=resume,
        )

        return TempWorkspace(
            job_id=job_id,
            kind=kind,
            root=str(
                self.root
            ),
            work_dir=str(
                work_dir
            ),
        )

    def finish(
        self,
        workspace,
        status,
    ):

        work_dir = Path(
            workspace.work_dir
        )

        if (
            status == TEMP_STATUS_SUCCESS
            and workspace.cleanup_on_success
            and work_dir.exists()
        ):

            shutil.rmtree(
                work_dir
            )

            return "cleaned"

        if status in {
            TEMP_STATUS_ERROR,
            TEMP_STATUS_PAUSE,
            TEMP_STATUS_STOPPED,
        }:

            return "kept"

        if status == TEMP_STATUS_CANCEL:

            return "needs_user_choice"

        return "kept"

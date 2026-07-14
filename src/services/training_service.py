from pathlib import Path
import traceback

from core.app_context import AppContext

from services.dataset_service import DatasetService
from services.log_service import LogService


class TrainingService:

    def __init__(self):

        self.dataset = DatasetService()

        self.log = LogService()

    def prepare_dataset(
        self,
        source,
        voice,
    ):

        try:

            dataset_dir = (
                voice.path
                / "dataset"
            )

            result = self.dataset.prepare(
                source,
                dataset_dir,
            )

            AppContext.engine_manager.select(
                voice.config.engine
            )

            AppContext.engine_manager.validate_dataset(
                result
            )

            self.log.info(
                "train",
                f"{voice.name} : Dataset OK ({len(result['items'])} cặp)"
            )

            return result

        except Exception:

            error = traceback.format_exc()

            self.log.error(
                "train",
                error,
            )

            raise

    def train(
        self,
        voice,
        dataset,
    ):

        try:

            if not voice.config.engine:

                raise Exception(
                    "Voice chưa chọn Engine."
                )

            AppContext.engine_manager.select(
                voice.config.engine
            )

            self.log.info(
                "train",
                f"Bắt đầu train : {voice.name}"
            )

            AppContext.engine_manager.train(
                voice,
                dataset,
            )

            voice.status = "ready"

            AppContext.voice_service.save(
                voice
            )

            self.log.info(
                "train",
                f"Train thành công : {voice.name}"
            )

            return True

        except Exception:

            error = traceback.format_exc()

            self.log.error(
                "train",
                error,
            )

            raise

    def create_preview(
        self,
        voice,
    ):

        try:

            if not voice.config.engine:

                raise Exception(
                    "Voice chưa chọn Engine."
                )

            AppContext.engine_manager.select(
                voice.config.engine
            )

            preview = (
                voice.path
                / "preview.wav"
            )

            AppContext.engine_manager.create_preview(
                voice,
                preview,
            )

            self.log.info(
                "train",
                f"Tạo preview : {preview.name}"
            )

            return preview

        except Exception:

            error = traceback.format_exc()

            self.log.error(
                "train",
                error,
            )

            raise
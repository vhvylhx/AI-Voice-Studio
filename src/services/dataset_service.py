from pathlib import Path

from config.app_config import WORKSPACE_DIR
from models.dataset_info import DatasetInfo


class DatasetService:

    def scan(self) -> list[DatasetInfo]:

        # Nếu chưa có thì tự tạo
        WORKSPACE_DIR.mkdir(exist_ok=True)

        datasets = []

        for folder in sorted(WORKSPACE_DIR.iterdir()):

            if not folder.is_dir():
                continue

            mp3_count = len(list(folder.glob("*.mp3")))
            docx_count = len(list(folder.glob("*.docx")))
            txt_count = len(list(folder.glob("*.txt")))

            datasets.append(
                DatasetInfo(
                    name=folder.name,
                    path=folder,
                    mp3_count=mp3_count,
                    docx_count=docx_count,
                    txt_count=txt_count,
                )
            )

        return datasets
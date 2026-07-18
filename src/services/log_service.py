from datetime import datetime
from pathlib import Path


class LogService:

    def __init__(self):

        self.root = Path("logs")

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _file(
        self,
        category,
    ):

        today = datetime.now().strftime(
            "%Y-%m-%d"
        )

        folder = self.root / today

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        return folder / f"{category}.log"

    def write(
        self,
        category,
        message,
        level="INFO",
    ):

        file = self._file(
            category
        )

        now = datetime.now().strftime(
            "%H:%M:%S"
        )

        with open(
            file,
            "a",
            encoding="utf-8",
        ) as f:

            f.write(
                f"[{now}] [{level}] {message}\n"
            )

        try:

            from services.app_events import AppEvents

            AppEvents.log_message(
                {
                    "time": now,
                    "category": category,
                    "message": message,
                    "level": level.lower(),
                }
            )

        except Exception:

            pass

    def info(
        self,
        category,
        message,
    ):

        self.write(
            category,
            message,
            "INFO",
        )

    def warning(
        self,
        category,
        message,
    ):

        self.write(
            category,
            message,
            "WARNING",
        )

    def error(
        self,
        category,
        message,
    ):

        self.write(
            category,
            message,
            "ERROR",
        )

    def exception(
        self,
        category,
        exc,
    ):

        self.error(
            category,
            str(exc),
        )

    def read(
        self,
        category,
    ):

        file = self._file(
            category
        )

        if not file.exists():

            return ""

        return file.read_text(
            encoding="utf-8"
        )

    def clear(
        self,
        category,
    ):

        file = self._file(
            category
        )

        if file.exists():

            file.unlink()

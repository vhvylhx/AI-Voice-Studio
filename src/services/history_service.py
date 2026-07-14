from datetime import datetime
from pathlib import Path


class HistoryService:

    def __init__(self):

        self.root = Path(
            "logs/text_history"
        )

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(
        self,
        source_file,
        report,
    ):

        if not report:

            return

        source = Path(source_file)

        log_file = (
            self.root
            / f"{source.stem}.log"
        )

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        with open(
            log_file,
            "a",
            encoding="utf-8",
        ) as f:

            f.write(
                "=" * 60 + "\n"
            )

            f.write(
                f"{now}\n"
            )

            f.write(
                f"File : {source.name}\n\n"
            )

            for item in report:

                f.write(
                    f"- {item}\n"
                )

            f.write("\n")

    def clear(self):

        for file in self.root.glob(
            "*.log"
        ):

            file.unlink()

    def list(self):

        return sorted(
            self.root.glob("*.log")
        )
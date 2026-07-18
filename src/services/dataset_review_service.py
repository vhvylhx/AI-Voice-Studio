from pathlib import Path
import json

from models.dataset_review import DatasetReviewConfig
from models.dataset_review import DatasetReviewItem


class DatasetReviewService:

    BLOCKING_CODES = (
        "missing_audio",
        "missing_text",
        "test_version",
        "invalid_filename",
        "filename_content_mismatch",
        "duplicate",
        "empty_file",
        "empty_content",
        "broken_file",
    )

    REVIEW_OPTIONAL_CODES = (
        "test_version",
        "broken_file",
        "empty_file",
        "filename_content_mismatch",
    )

    VALID_STATUSES = (
        "pending",
        "approved",
        "rejected",
        "ignored",
    )

    REVIEWED_STATUSES = (
        "approved",
        "rejected",
        "ignored",
    )

    DEFAULT_AUTO_DECISIONS = {
        "test_version": "ignored",
        "broken_file": "rejected",
        "empty_file": "rejected",
        "empty_content": "rejected",
        "missing_audio": "ignored",
        "missing_text": "ignored",
        "invalid_filename": "ignored",
        "filename_content_mismatch": "rejected",
    }

    def create_review(
        self,
        dataset_result=None,
        repair_report=None,
        output_dir=None,
        config=None,
    ):

        config = DatasetReviewConfig.from_dict(
            config
        )

        status = self.normalize_status(
            config.default_status
        )

        items = [
            self.create_item(
                issue,
                status,
            )
            for issue in self.collect_issues(
                dataset_result,
                repair_report,
            )
        ]

        report = self.create_report(
            items,
            dataset_result,
            repair_report,
            config,
        )

        if output_dir is not None:

            output_dir = Path(
                output_dir
            )

            output_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            self.write_json(
                output_dir / config.report_file,
                report,
            )

        return report

    def collect_issues(
        self,
        dataset_result=None,
        repair_report=None,
    ):

        if repair_report is not None:

            return [
                issue
                for issue in repair_report.get(
                    "skipped",
                    [],
                )
                if issue.get(
                    "code"
                )
                in self.BLOCKING_CODES
            ]

        dataset_result = dataset_result or {}

        return [
            error
            for error in dataset_result.get(
                "errors",
                [],
            )
            if error.get(
                "code"
            )
            in self.BLOCKING_CODES
        ]

    def create_item(
        self,
        issue,
        status,
    ):

        file = issue.get(
            "file",
            "",
        )

        source_audio = issue.get(
            "source_audio",
            "",
        )

        source_text = issue.get(
            "source_text",
            "",
        )

        suffix = Path(
            file
        ).suffix.lower()

        if (
            not source_audio
            and suffix in (
                ".mp3",
                ".wav",
                ".flac",
                ".m4a",
            )
        ):

            source_audio = file

        if (
            not source_text
            and suffix in (
                ".txt",
                ".docx",
            )
        ):

            source_text = file

        code = issue.get(
            "code",
            "",
        )

        return DatasetReviewItem(
            source_audio=source_audio,
            source_text=source_text,
            reason=issue.get(
                "reason",
                issue.get(
                    "message",
                    "",
                ),
            ),
            suggestion=issue.get(
                "suggestion",
                "",
            ),
            status=status,
            code=code,
            file=file,
            review_required=code
            in self.REVIEW_OPTIONAL_CODES,
        ).to_dict()

    def create_report(
        self,
        items,
        dataset_result,
        repair_report,
        config,
    ):

        summary = self.create_summary(
            items,
            dataset_result,
            repair_report,
        )

        return {
            "schema_version": 1,
            "mode": config.mode,
            "items": items,
            "summary": summary,
            "filters": self.available_filters(
                items
            ),
        }

    def create_summary(
        self,
        items,
        dataset_result=None,
        repair_report=None,
    ):

        counts = {
            "total": len(
                items
            ),
            "pending": 0,
            "approved": 0,
            "rejected": 0,
            "ignored": 0,
        }

        for item in items:

            status = item.get(
                "status",
                "pending",
            )

            if status in counts:

                counts[status] += 1

        blocking_errors = self.blocking_errors(
            dataset_result,
            repair_report,
            items,
        )

        all_reviewed = self.all_reviewed(
            items
        )

        counts["blocking_errors"] = blocking_errors
        counts["all_reviewed"] = all_reviewed
        counts["train_allowed"] = (
            blocking_errors == 0
            or all_reviewed
        )

        return counts

    def blocking_errors(
        self,
        dataset_result=None,
        repair_report=None,
        items=None,
    ):

        if repair_report is not None:

            return int(
                repair_report.get(
                    "after",
                    {},
                ).get(
                    "blocking_errors",
                    len(
                        items or []
                    ),
                )
            )

        dataset_result = dataset_result or {}

        return int(
            dataset_result.get(
                "health",
                {},
            ).get(
                "blocking_errors",
                len(
                    items or []
                ),
            )
        )

    def can_train(
        self,
        dataset_result=None,
        repair_report=None,
        review_report=None,
    ):

        blocking_errors = self.blocking_errors(
            dataset_result,
            repair_report,
            (
                review_report or {}
            ).get(
                "items",
                [],
            ),
        )

        if blocking_errors == 0:

            return True

        if review_report is None:

            return False

        return self.all_reviewed(
            review_report.get(
                "items",
                [],
            )
        )

    def all_reviewed(
        self,
        items,
    ):

        if not items:

            return True

        return all(
            item.get(
                "status"
            )
            in self.REVIEWED_STATUSES
            for item in items
        )

    def approve_all(
        self,
        review_report,
    ):

        return self.set_status(
            review_report,
            "approved",
        )

    def reject_all(
        self,
        review_report,
    ):

        return self.set_status(
            review_report,
            "rejected",
        )

    def ignore_all(
        self,
        review_report,
    ):

        return self.set_status(
            review_report,
            "ignored",
        )

    def apply_decisions(
        self,
        review_report,
        decisions,
    ):

        result = dict(
            review_report
        )

        items = []

        for item in review_report.get(
            "items",
            [],
        ):

            item = dict(
                item
            )

            status = decisions.get(
                item.get(
                    "code",
                    "",
                )
            )

            if status is not None:

                item["status"] = self.normalize_status(
                    status
                )

            items.append(
                item
            )

        result["items"] = items
        result["summary"] = self.create_summary(
            items
        )
        result["filters"] = self.available_filters(
            items
        )

        return result

    def auto_review(
        self,
        review_report,
        decisions=None,
    ):

        decisions = decisions or self.DEFAULT_AUTO_DECISIONS

        result = self.apply_decisions(
            review_report,
            decisions,
        )

        result["mode"] = "auto"
        result["auto_review"] = True
        result["auto_decisions"] = dict(
            decisions
        )

        return result

    def write_report(
        self,
        review_report,
        output_dir,
        report_file="review_report.json",
    ):

        output_dir = Path(
            output_dir
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.write_json(
            output_dir / report_file,
            review_report,
        )

        return output_dir / report_file

    def set_status(
        self,
        review_report,
        status,
        reason=None,
        code=None,
    ):

        status = self.normalize_status(
            status
        )

        result = dict(
            review_report
        )

        items = []

        for item in review_report.get(
            "items",
            [],
        ):

            item = dict(
                item
            )

            if self.matches_filter(
                item,
                reason,
                code,
            ):

                item["status"] = status

            items.append(
                item
            )

        result["items"] = items
        result["summary"] = self.create_summary(
            items
        )
        result["filters"] = self.available_filters(
            items
        )

        return result

    def matches_filter(
        self,
        item,
        reason,
        code,
    ):

        if (
            reason is not None
            and item.get(
                "reason",
                "",
            )
            != reason
        ):

            return False

        if (
            code is not None
            and item.get(
                "code",
                "",
            )
            != code
        ):

            return False

        return True

    def available_filters(
        self,
        items,
    ):

        return {
            "reasons": sorted(
                {
                    item.get(
                        "reason",
                        "",
                    )
                    for item in items
                    if item.get(
                        "reason",
                        "",
                    )
                }
            ),
            "codes": sorted(
                {
                    item.get(
                        "code",
                        "",
                    )
                    for item in items
                    if item.get(
                        "code",
                        "",
                    )
                }
            ),
        }

    def normalize_status(
        self,
        status,
    ):

        status = str(
            status or "pending"
        )

        if status not in self.VALID_STATUSES:

            return "pending"

        return status

    def write_json(
        self,
        file,
        data,
    ):

        with open(
            file,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False,
            )

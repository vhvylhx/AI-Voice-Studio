from pathlib import Path
import json
import shutil

from config.dataset_repair_config import DEFAULT_DATASET_REPAIR_CONFIG
from models.dataset_repair import DatasetRepairConfig
from models.dataset_repair import DatasetRepairIssue


class DatasetRepairService:

    ISSUE_RULES = {
        "duplicate": {
            "repairable": True,
            "safe_action": "copy_to_ignored",
        },
        "empty_file": {
            "repairable": False,
            "safe_action": "skip",
        },
        "broken_file": {
            "repairable": False,
            "safe_action": "skip",
        },
        "missing_audio": {
            "repairable": False,
            "safe_action": "skip",
        },
        "missing_text": {
            "repairable": False,
            "safe_action": "skip",
        },
        "filename_content_mismatch": {
            "repairable": False,
            "safe_action": "skip",
        },
        "test_version": {
            "repairable": False,
            "safe_action": "skip",
        },
        "invalid_filename": {
            "repairable": False,
            "safe_action": "skip",
        },
    }

    def default_config(
        self,
    ):

        return DatasetRepairConfig.from_dict(
            DEFAULT_DATASET_REPAIR_CONFIG
        )

    def normalize_config(
        self,
        config=None,
    ):

        if config is None:

            return self.default_config()

        return DatasetRepairConfig.from_dict(
            config
        )

    def detect(
        self,
        dataset_result,
    ):

        issues = []

        for error in dataset_result.get(
            "errors",
            [],
        ):

            issue = self.detect_issue(
                error
            )

            if issue is not None:

                issues.append(
                    issue
                )

        return issues

    def detect_issue(
        self,
        error,
    ):

        code = error.get(
            "code",
            "",
        )

        rule = self.ISSUE_RULES.get(
            code
        )

        if rule is None:

            return None

        return DatasetRepairIssue(
            code=code,
            file=error.get(
                "file",
                "",
            ),
            reason=error.get(
                "reason",
                error.get(
                    "message",
                    "",
                ),
            ),
            suggestion=error.get(
                "suggestion",
                "",
            ),
            repairable=bool(
                rule.get(
                    "repairable",
                    False,
                )
            ),
            metadata={
                "safe_action": rule.get(
                    "safe_action",
                    "skip",
                ),
            },
        )

    def repair(
        self,
        dataset_result,
        output_dir,
        config=None,
    ):

        config = self.normalize_config(
            config
        )

        output_dir = Path(
            output_dir
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        ignored_dir = output_dir / config.ignored_folder

        issues = self.detect(
            dataset_result
        )

        repaired = []

        skipped = []

        for issue in issues:

            if (
                config.auto_repair
                and config.review_mode == "auto"
                and issue.repairable
            ):

                result = self.repair_issue(
                    issue,
                    ignored_dir,
                )

                if result.action == "repaired":

                    repaired.append(
                        result
                    )

                    continue

                skipped.append(
                    result
                )

                continue

            skipped.append(
                self.skip(
                    issue
                )
            )

        report = self.report(
            dataset_result,
            repaired,
            skipped,
            output_dir,
            config,
        )

        self.write_json(
            output_dir / config.report_file,
            report,
        )

        return report

    def repair_issue(
        self,
        issue,
        ignored_dir,
    ):

        if issue.code == "duplicate":

            return self.repair_duplicate(
                issue,
                ignored_dir,
            )

        return self.skip(
            issue
        )

    def repair_duplicate(
        self,
        issue,
        ignored_dir,
    ):

        source = Path(
            issue.file
        )

        if not source.exists():

            issue.action = "skipped"
            issue.reason = "File trùng không còn tồn tại để đưa vào ignored."
            issue.metadata["skip_reason"] = "source_missing"

            return issue

        ignored_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        target = self.safe_ignored_path(
            ignored_dir,
            source,
        )

        try:

            shutil.copy2(
                source,
                target,
            )

        except Exception as e:

            issue.action = "skipped"
            issue.metadata["skip_reason"] = "copy_failed"
            issue.metadata["error"] = str(
                e
            )

            return issue

        issue.action = "repaired"
        issue.repaired_file = str(
            target
        )
        issue.metadata["repair_action"] = "copied_to_ignored"

        return issue

    def skip(
        self,
        issue,
    ):

        issue.action = "skipped"

        if not issue.metadata.get(
            "skip_reason"
        ):

            issue.metadata["skip_reason"] = (
                "manual_review_required"
                if issue.repairable
                else "not_safe_to_repair"
            )

        return issue

    def report(
        self,
        dataset_result,
        repaired,
        skipped,
        output_dir,
        config,
    ):

        before = dict(
            dataset_result.get(
                "health",
                {},
            )
        )

        after = self.create_after_health(
            before,
            repaired,
        )

        return {
            "schema_version": 1,
            "mode": config.review_mode,
            "auto_repair": config.auto_repair,
            "output_dir": str(
                output_dir
            ),
            "before": before,
            "repaired": [
                issue.to_dict()
                for issue in repaired
            ],
            "skipped": [
                issue.to_dict()
                for issue in skipped
            ],
            "after": after,
            "final_usable_percent": after.get(
                "usable_percent",
                0.0,
            ),
        }

    def create_after_health(
        self,
        before,
        repaired,
    ):

        after = dict(
            before
        )

        repaired_by_code = {}

        for issue in repaired:

            repaired_by_code[issue.code] = (
                repaired_by_code.get(
                    issue.code,
                    0,
                )
                + 1
            )

        for code, count in repaired_by_code.items():

            if code not in after:

                continue

            after[code] = max(
                0,
                after.get(
                    code,
                    0,
                )
                - count,
            )

        if "blocking_errors" in after:

            after["blocking_errors"] = max(
                0,
                after.get(
                    "blocking_errors",
                    0,
                )
                - len(
                    repaired
                ),
            )

        return after

    def safe_ignored_path(
        self,
        ignored_dir,
        source,
    ):

        target = ignored_dir / source.name

        if not target.exists():

            return target

        stem = source.stem

        suffix = source.suffix

        index = 2

        while True:

            candidate = ignored_dir / f"{stem}_{index}{suffix}"

            if not candidate.exists():

                return candidate

            index += 1

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

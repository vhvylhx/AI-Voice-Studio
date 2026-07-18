import platform
import shutil
from pathlib import Path

from models.bootstrap_status import BootstrapStatus
from models.bootstrap_status import SetupIssue
from services.feature_readiness_service import FeatureReadinessService
from services.runtime_environment_manager import RuntimeEnvironmentManager


class BootstrapService:

    def __init__(
        self,
        app_root=None,
        environment=None,
        readiness=None,
    ):

        self.app_root = Path(
            app_root or Path.cwd()
        ).resolve()

        self.environment = (
            environment
            or RuntimeEnvironmentManager(
                app_root=self.app_root
            )
        )

        self.readiness = (
            readiness
            or FeatureReadinessService(
                self.environment
            )
        )

    def check(
        self,
    ):

        issues = []

        self.check_windows(
            issues
        )

        self.check_read_write(
            issues
        )

        self.check_disk_space(
            issues
        )

        readiness = self.readiness.summary()

        app_shell = self.readiness.by_id(
            "app_shell"
        )

        if app_shell.blocked:

            issues.append(
                SetupIssue(
                    component="app_shell",
                    status="missing",
                    message_vi="Thiếu thành phần để mở giao diện chính.",
                    remediation=app_shell.remediation,
                    critical=True,
                )
            )

        mode = "full"

        can_start = True

        if any(
            issue.critical
            for issue in issues
        ):

            mode = "setup_required"

            can_start = False

        elif readiness.get(
            "limited_mode",
            False,
        ):

            mode = "limited"

        return BootstrapStatus(
            mode=mode,
            can_start_main_app=can_start,
            limited_mode=mode == "limited",
            issues=issues,
            technical_details={
                "readiness": readiness,
                "environment": self.environment.full_status(),
            },
        )

    def startup_target(
        self,
    ):

        status = self.check()

        if status.can_start_main_app:

            return {
                "target": "main_application",
                "status": status.to_dict(),
            }

        return {
            "target": "first_run_setup",
            "status": status.to_dict(),
        }

    def check_windows(
        self,
        issues,
    ):

        if platform.system().lower() != "windows":

            issues.append(
                SetupIssue(
                    component="windows",
                    status="unsupported",
                    message_vi="AI Voice Studio hiện ưu tiên Desktop Windows.",
                    remediation=[
                        "Chạy trên Windows hoặc kiểm tra lại gói phát hành phù hợp.",
                    ],
                    critical=False,
                )
            )

    def check_read_write(
        self,
        issues,
    ):

        probe = self.app_root / "temp" / "bootstrap_write_test.tmp"

        try:

            probe.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            probe.write_text(
                "ok",
                encoding="utf-8",
            )

            probe.unlink()

        except Exception:

            issues.append(
                SetupIssue(
                    component="file_permission",
                    status="blocked",
                    message_vi="Ứng dụng không có quyền ghi trong thư mục hiện tại.",
                    remediation=[
                        "Di chuyển app sang thư mục có quyền ghi hoặc chạy với quyền phù hợp.",
                    ],
                    critical=True,
                )
            )

    def check_disk_space(
        self,
        issues,
    ):

        usage = shutil.disk_usage(
            self.app_root
        )

        free_gb = usage.free / 1024 / 1024 / 1024

        if free_gb < 2:

            issues.append(
                SetupIssue(
                    component="disk_space",
                    status="low",
                    message_vi="Dung lượng ổ đĩa còn thấp.",
                    remediation=[
                        "Nên trống tối thiểu vài GB trước khi xử lý audio/model.",
                    ],
                    critical=False,
                )
            )

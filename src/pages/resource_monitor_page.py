import json

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QGroupBox,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.app_context import AppContext


class ResourceMonitorPage(QWidget):

    def __init__(
        self,
    ):

        super().__init__()

        self.build_ui()

        self.refresh()

        self.timer = QTimer(
            self
        )

        self.timer.timeout.connect(
            self.refresh
        )

        self.timer.start(
            3000
        )

    def build_ui(
        self,
    ):

        root = QVBoxLayout(
            self
        )

        title = QLabel(
            "Resource Monitor"
        )

        title.setStyleSheet(
            "font-size:22px;font-weight:bold;"
        )

        root.addWidget(
            title
        )

        self.summary = QLabel(
            "-"
        )

        self.summary.setWordWrap(
            True
        )

        summary_box = QGroupBox(
            "Tổng quan tài nguyên"
        )

        summary_layout = QVBoxLayout(
            summary_box
        )

        summary_layout.addWidget(
            self.summary
        )

        self.detail = QTextEdit()

        self.detail.setReadOnly(
            True
        )

        self.refresh_button = QPushButton(
            "Làm mới"
        )

        self.refresh_button.clicked.connect(
            self.refresh
        )

        root.addWidget(
            summary_box
        )

        root.addWidget(
            self.detail
        )

        root.addWidget(
            self.refresh_button
        )

    def refresh(
        self,
    ):

        try:

            data = AppContext.resource_monitor_service.summary()

        except Exception as exc:

            self.summary.setText(
                f"Resource Manager chưa sẵn sàng: {exc}"
            )

            self.detail.setPlainText(
                ""
            )

            return

        snapshot = data.get(
            "snapshot",
            {},
        )

        hardware = data.get(
            "hardware",
            {},
        )

        gpus = hardware.get(
            "gpu_devices",
            [],
        )

        self.summary.setText(
            " | ".join(
                [
                    f"Pressure: {data.get('pressure_state', '-')}",
                    f"CPU: {snapshot.get('cpu_percent', 0):.1f}%",
                    f"RAM: {snapshot.get('ram_available_mb', 0)} MiB trống",
                    f"Disk: {snapshot.get('disk_free_mb', 0)} MiB trống",
                    f"GPU: {len(gpus)}",
                    f"Lease: {len(data.get('leases', []))}",
                    f"Chờ tài nguyên: {len(data.get('waiting_jobs', []))}",
                ]
            )
        )

        self.detail.setPlainText(
            json.dumps(
                data,
                indent=4,
                ensure_ascii=False,
            )
        )

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QPushButton,
    QLabel,
    QTextEdit,
    QComboBox,
    QCheckBox,
    QSpinBox,
    QDialog,
    QApplication,
    QLineEdit,
)

from services.runtime_training_help_service import RuntimeTrainingHelpService
from services.runtime_training_profile_service import RuntimeTrainingProfileService
from services.resource_policy_service import ResourcePolicyService
from services.local_api_service import LocalApiService
from services.style_profile_service import StyleProfileService
from models.runtime_training_profile import RuntimeTrainingProfile

import json


class SettingsPage(QWidget):

    def __init__(self):

        super().__init__()

        self.training_help_service = RuntimeTrainingHelpService()
        self.training_profile_service = RuntimeTrainingProfileService()
        self.resource_policy_service = ResourcePolicyService()
        self.local_api_service = LocalApiService()
        self.style_profile_service = StyleProfileService()
        self.last_training_detection = {}
        self.last_runtime_validation = {}
        self.last_effective_training_profile = None
        self.custom_profile_backup = {}
        self.current_training_profile_key = "auto"

        root = QVBoxLayout(self)

        #
        # Engine
        #

        engine_box = QGroupBox(
            "Engine"
        )

        engine_layout = QFormLayout(
            engine_box
        )

        self.engine = QLabel(
            "Chưa chọn"
        )

        self.add_engine = QPushButton(
            "Thêm Engine..."
        )

        self.remove_engine = QPushButton(
            "Xóa Engine"
        )

        self.default_engine = QPushButton(
            "Đặt mặc định"
        )

        engine_layout.addRow(
            "Engine",
            self.engine
        )

        engine_layout.addRow(
            self.add_engine
        )

        engine_layout.addRow(
            self.remove_engine
        )

        engine_layout.addRow(
            self.default_engine
        )

        #
        # Workspace
        #

        workspace_box = QGroupBox(
            "Workspace"
        )

        workspace_layout = QFormLayout(
            workspace_box
        )

        self.workspace = QLabel(
            "workspace/"
        )

        self.change_workspace = QPushButton(
            "Đổi Workspace"
        )

        workspace_layout.addRow(
            "Folder",
            self.workspace
        )

        workspace_layout.addRow(
            self.change_workspace
        )

        #
        # Runtime & Training
        #

        training_box = QGroupBox(
            "Runtime & Training"
        )

        training_layout = QFormLayout(
            training_box
        )

        self.training_profile = QComboBox()

        self.training_profile.addItems(
            [
                "Tự động",
                "Tương thích",
                "Hiệu năng",
                "Tùy chỉnh",
            ]
        )

        self.auto_detect_hardware = QCheckBox(
            "Tự động phát hiện phần cứng"
        )

        self.auto_detect_hardware.setChecked(
            True
        )

        self.hardware_gpu = QLabel(
            "-"
        )

        self.hardware_vram = QLabel(
            "-"
        )

        self.hardware_cpu = QLabel(
            "-"
        )

        self.hardware_ram = QLabel(
            "-"
        )

        self.hardware_cuda = QLabel(
            "-"
        )

        self.runtime_profile = QLabel(
            "-"
        )

        self.runtime_python = QLabel(
            "-"
        )

        self.runtime_torch = QLabel(
            "-"
        )

        self.runtime_engine_version = QLabel(
            "-"
        )

        self.training_batch_size = QSpinBox()

        self.training_batch_size.setRange(
            1,
            64,
        )

        self.training_batch_size.setValue(
            1
        )

        self.training_workers = QSpinBox()

        self.training_workers.setRange(
            0,
            32,
        )

        self.training_workers.setValue(
            0
        )

        self.training_compute = QComboBox()

        self.training_compute.addItems(
            [
                "Tự động",
                "CUDA",
                "CPU",
            ]
        )

        self.training_gpt_epochs = QSpinBox()

        self.training_gpt_epochs.setRange(
            1,
            1000,
        )

        self.training_gpt_epochs.setValue(
            20
        )

        self.training_sovits_epochs = QSpinBox()

        self.training_sovits_epochs.setRange(
            1,
            1000,
        )

        self.training_sovits_epochs.setValue(
            50
        )

        self.training_save_interval = QSpinBox()

        self.training_save_interval.setRange(
            1,
            100,
        )

        self.training_save_interval.setValue(
            1
        )

        self.training_reason = QLabel(
            "Tự động sẽ chọn cấu hình an toàn dựa trên phần cứng và Runtime đã kiểm tra."
        )

        self.training_reason.setWordWrap(
            True
        )

        self.detect_again = QPushButton(
            "Phát hiện lại phần cứng"
        )

        self.validate_runtime = QPushButton(
            "Kiểm tra Runtime"
        )

        self.reset_recommended = QPushButton(
            "Khôi phục cấu hình khuyến nghị"
        )

        self.show_effective_config = QPushButton(
            "Xem cấu hình thực tế sẽ dùng"
        )

        self.copy_check_report = QPushButton(
            "Sao chép báo cáo kiểm tra"
        )

        self.open_training_guide = QPushButton(
            "Xem giải thích chi tiết"
        )

        self.training_short_help = QLabel(
            self.training_help_service.profile_help()[
                "auto"
            ][
                "short"
            ]
        )

        self.training_short_help.setWordWrap(
            True
        )

        self.training_short_help.setToolTip(
            self.training_help_service.profile_help()[
                "auto"
            ][
                "detail"
            ]
        )

        self.training_profile.currentTextChanged.connect(
            self.update_training_profile_mode
        )

        self.open_training_guide.clicked.connect(
            self.show_training_guide
        )

        self.copy_check_report.clicked.connect(
            self.copy_training_report
        )

        self.detect_again.clicked.connect(
            self.detect_training_hardware
        )

        self.validate_runtime.clicked.connect(
            self.validate_training_runtime
        )

        self.reset_recommended.clicked.connect(
            self.reset_training_recommended
        )

        self.show_effective_config.clicked.connect(
            self.show_training_effective_config
        )

        self.apply_training_tooltips()

        training_layout.addRow(
            "Chế độ",
            self.training_profile,
        )

        training_layout.addRow(
            self.auto_detect_hardware
        )

        training_layout.addRow(
            "Hướng dẫn sử dụng",
            self.training_short_help,
        )

        training_layout.addRow(
            "GPU",
            self.hardware_gpu,
        )

        training_layout.addRow(
            "VRAM",
            self.hardware_vram,
        )

        training_layout.addRow(
            "CPU",
            self.hardware_cpu,
        )

        training_layout.addRow(
            "RAM",
            self.hardware_ram,
        )

        training_layout.addRow(
            "CUDA",
            self.hardware_cuda,
        )

        training_layout.addRow(
            "Runtime đang chọn",
            self.runtime_profile,
        )

        training_layout.addRow(
            "Python",
            self.runtime_python,
        )

        training_layout.addRow(
            "Torch",
            self.runtime_torch,
        )

        training_layout.addRow(
            "Phiên bản Engine",
            self.runtime_engine_version,
        )

        training_layout.addRow(
            "Batch Size",
            self.training_batch_size,
        )

        training_layout.addRow(
            "Workers",
            self.training_workers,
        )

        training_layout.addRow(
            "Compute",
            self.training_compute,
        )

        training_layout.addRow(
            "GPT Epochs",
            self.training_gpt_epochs,
        )

        training_layout.addRow(
            "SoVITS Epochs",
            self.training_sovits_epochs,
        )

        training_layout.addRow(
            "Save Interval",
            self.training_save_interval,
        )

        training_layout.addRow(
            "Lý do",
            self.training_reason,
        )

        training_layout.addRow(
            self.detect_again
        )

        training_layout.addRow(
            self.validate_runtime
        )

        training_layout.addRow(
            self.reset_recommended
        )

        training_layout.addRow(
            self.show_effective_config
        )

        training_layout.addRow(
            self.copy_check_report
        )

        training_layout.addRow(
            self.open_training_guide
        )

        #
        # Dữ liệu tham chiếu giọng đọc
        #

        style_box = QGroupBox(
            "Dữ liệu tham chiếu giọng đọc"
        )

        style_layout = QFormLayout(
            style_box
        )

        style_profiles = self.style_profile_service.list_profiles()

        ready_profiles = [
            profile
            for profile in style_profiles
            if profile.status == "ready"
        ]

        self.style_profile_count = QLabel(
            str(
                len(
                    style_profiles
                )
            )
        )

        self.style_profile_ready = QLabel(
            str(
                len(
                    ready_profiles
                )
            )
        )

        self.style_profile_status = QLabel(
            "Schema đã sẵn sàng; extraction thật đang chờ analyzer."
        )

        self.style_profile_status.setWordWrap(
            True
        )

        self.open_style_profiles = QPushButton(
            "Mở trang Phong cách đọc"
        )

        self.style_profile_help = QLabel(
            "Style Profile lưu prosody/pacing/expression tách khỏi Voice model. Export mặc định không chứa MP3 gốc, checkpoint hoặc đường dẫn tuyệt đối."
        )

        self.style_profile_help.setWordWrap(
            True
        )

        style_layout.addRow(
            "Tổng Style Profile",
            self.style_profile_count,
        )

        style_layout.addRow(
            "Sẵn sàng",
            self.style_profile_ready,
        )

        style_layout.addRow(
            "Trạng thái",
            self.style_profile_status,
        )

        style_layout.addRow(
            self.open_style_profiles
        )

        style_layout.addRow(
            "Ghi chú",
            self.style_profile_help,
        )

        #
        # API & Integration
        #

        api_box = QGroupBox(
            "API & Tích hợp"
        )

        api_layout = QFormLayout(
            api_box
        )

        self.api_status = QLabel(
            "Chưa chạy"
        )

        self.api_enabled = QCheckBox(
            "Bật API nội bộ"
        )

        self.api_auto_start = QCheckBox(
            "Tự khởi động API cùng ứng dụng"
        )

        self.api_host = QLineEdit(
            self.local_api_service.config.local_api_host
        )

        self.api_port = QSpinBox()

        self.api_port.setRange(
            1,
            65535,
        )

        self.api_port.setValue(
            int(
                self.local_api_service.config.local_api_port
            )
        )

        self.api_token = QLineEdit(
            "••••••••"
        )

        self.api_token.setReadOnly(
            True
        )

        self.api_catalog_url = QLabel(
            f"{self.local_api_service.base_url()}/api/v1/voice-catalog"
        )

        self.api_openapi_url = QLabel(
            "MVP stdlib: xem docs/LOCAL_API_V1.md"
        )

        self.api_output_policy = QLabel(
            "Chỉ output do app quản lý"
        )

        self.api_running_jobs = QLabel(
            "0"
        )

        self.api_queued_jobs = QLabel(
            "0"
        )

        self.api_concurrency = QLabel(
            str(
                self.local_api_service.config.concurrency
            )
        )

        self.api_start = QPushButton(
            "Khởi động API"
        )

        self.api_stop = QPushButton(
            "Dừng API"
        )

        self.api_restart = QPushButton(
            "Khởi động lại"
        )

        self.api_check = QPushButton(
            "Kiểm tra kết nối"
        )

        self.api_copy_url = QPushButton(
            "Sao chép URL"
        )

        self.api_copy_token = QPushButton(
            "Sao chép Token"
        )

        self.api_regenerate_token = QPushButton(
            "Tạo Token mới"
        )

        self.api_docs = QPushButton(
            "Mở tài liệu API"
        )

        self.api_client_example = QPushButton(
            "Mở ví dụ app video"
        )

        self.api_help = QLabel(
            "API cho phép một ứng dụng khác, ví dụ phần mềm làm video, yêu cầu AI Voice Studio tạo giọng nói và nhận lại file âm thanh. API mặc định chỉ hoạt động trên máy này."
        )

        self.api_help.setWordWrap(
            True
        )

        self.api_enabled.setChecked(
            self.local_api_service.config.local_api_enabled
        )

        self.api_auto_start.setChecked(
            self.local_api_service.config.local_api_auto_start
        )

        self.api_start.clicked.connect(
            self.start_local_api
        )

        self.api_stop.clicked.connect(
            self.stop_local_api
        )

        self.api_restart.clicked.connect(
            self.restart_local_api
        )

        self.api_check.clicked.connect(
            self.check_local_api
        )

        self.api_copy_url.clicked.connect(
            self.copy_local_api_url
        )

        self.api_copy_token.clicked.connect(
            self.copy_local_api_token
        )

        self.api_regenerate_token.clicked.connect(
            self.regenerate_local_api_token
        )

        self.api_docs.clicked.connect(
            lambda: self.show_text_dialog(
                "Tài liệu API",
                "Xem docs/LOCAL_API_V1.md trong thư mục dự án.",
            )
        )

        self.api_client_example.clicked.connect(
            lambda: self.show_text_dialog(
                "Ví dụ app video",
                "Xem examples/video_app_client.py trong thư mục dự án.",
            )
        )

        api_layout.addRow(
            "Trạng thái API",
            self.api_status,
        )

        api_layout.addRow(
            self.api_enabled
        )

        api_layout.addRow(
            self.api_auto_start
        )

        api_layout.addRow(
            "Host",
            self.api_host,
        )

        api_layout.addRow(
            "Port",
            self.api_port,
        )

        api_layout.addRow(
            "Token",
            self.api_token,
        )

        api_layout.addRow(
            "Voice Catalog URL",
            self.api_catalog_url,
        )

        api_layout.addRow(
            "OpenAPI URL",
            self.api_openapi_url,
        )

        api_layout.addRow(
            "Output",
            self.api_output_policy,
        )

        api_layout.addRow(
            "Job đang chạy",
            self.api_running_jobs,
        )

        api_layout.addRow(
            "Job đang chờ",
            self.api_queued_jobs,
        )

        api_layout.addRow(
            "Concurrency",
            self.api_concurrency,
        )

        api_layout.addRow(
            self.api_start
        )

        api_layout.addRow(
            self.api_stop
        )

        api_layout.addRow(
            self.api_restart
        )

        api_layout.addRow(
            self.api_check
        )

        api_layout.addRow(
            self.api_copy_url
        )

        api_layout.addRow(
            self.api_copy_token
        )

        api_layout.addRow(
            self.api_regenerate_token
        )

        api_layout.addRow(
            self.api_docs
        )

        api_layout.addRow(
            self.api_client_example
        )

        api_layout.addRow(
            "Giải thích",
            self.api_help,
        )

        #
        # Text Processing
        #

        text_box = QGroupBox(
            "Text Processing"
        )

        text_layout = QFormLayout(
            text_box
        )

        self.edit_dictionary = QPushButton(
            "📖 Dictionary"
        )

        self.edit_pronunciation = QPushButton(
            "🔊 Pronunciation"
        )

        self.edit_ads = QPushButton(
            "🚫 Ads"
        )

        self.view_history = QPushButton(
            "📜 Lịch sử xử lý"
        )

        text_layout.addRow(
            self.edit_dictionary
        )

        text_layout.addRow(
            self.edit_pronunciation
        )

        text_layout.addRow(
            self.edit_ads
        )

        text_layout.addRow(
            self.view_history
        )

        #
        # Resource Manager
        #

        resource_box = QGroupBox(
            "Resource Manager"
        )

        resource_layout = QFormLayout(
            resource_box
        )

        resource_policy = self.resource_policy_service.load()

        self.resource_policy_name = QLabel(
            resource_policy.display_name
        )

        self.resource_max_jobs = QLabel(
            str(
                resource_policy.max_concurrent_jobs
            )
        )

        self.resource_max_gpu_jobs = QLabel(
            str(
                resource_policy.max_gpu_jobs
            )
        )

        self.resource_reserve_ram = QLabel(
            f"{resource_policy.reserve_ram_mb} MiB"
        )

        self.resource_reserve_vram = QLabel(
            f"{resource_policy.reserve_vram_mb} MiB"
        )

        self.resource_reserve_disk = QLabel(
            f"{resource_policy.reserve_disk_mb} MiB"
        )

        self.resource_help = QLabel(
            "Resource Manager điều phối Job Queue theo CPU/RAM/GPU/VRAM/Disk. Sprint này chỉ phát hiện, chờ tài nguyên và giữ lease an toàn."
        )

        self.resource_help.setWordWrap(
            True
        )

        resource_layout.addRow(
            "Policy",
            self.resource_policy_name,
        )

        resource_layout.addRow(
            "Max job đồng thời",
            self.resource_max_jobs,
        )

        resource_layout.addRow(
            "Max GPU job",
            self.resource_max_gpu_jobs,
        )

        resource_layout.addRow(
            "RAM dự phòng",
            self.resource_reserve_ram,
        )

        resource_layout.addRow(
            "VRAM dự phòng",
            self.resource_reserve_vram,
        )

        resource_layout.addRow(
            "Disk dự phòng",
            self.resource_reserve_disk,
        )

        resource_layout.addRow(
            "Ghi chú",
            self.resource_help,
        )

        #
        # Log
        #

        log_box = QGroupBox(
            "Log"
        )

        log_layout = QVBoxLayout(
            log_box
        )

        self.log = QTextEdit()

        self.log.setReadOnly(
            True
        )

        self.clear_log = QPushButton(
            "Xóa Log"
        )

        log_layout.addWidget(
            self.log
        )

        log_layout.addWidget(
            self.clear_log
        )

        root.addWidget(
            engine_box
        )

        root.addWidget(
            workspace_box
        )

        root.addWidget(
            training_box
        )

        root.addWidget(
            style_box
        )

        root.addWidget(
            api_box
        )

        root.addWidget(
            text_box
        )

        root.addWidget(
            resource_box
        )

        root.addWidget(
            log_box
        )

        root.addStretch()

        self.update_training_profile_mode(
            self.training_profile.currentText()
        )

        self.detect_training_hardware()

    def update_training_profile_mode(
        self,
        mode,
    ):

        new_key = self.profile_key(
            mode
        )

        if (
            self.current_training_profile_key == "custom"
            and new_key != "custom"
        ):

            self.custom_profile_backup = (
                self.current_training_profile(
                    mode="custom"
                ).to_dict()
            )

        editable = str(
            mode
        ).lower() in (
            "custom",
            "tùy chỉnh",
        )

        for widget in (
            self.training_batch_size,
            self.training_workers,
            self.training_compute,
            self.training_gpt_epochs,
            self.training_sovits_epochs,
            self.training_save_interval,
        ):

            widget.setEnabled(
                editable
            )

        help_item = self.training_help_service.profile_help().get(
            new_key,
            self.training_help_service.profile_help()[
                "auto"
            ],
        )

        self.training_short_help.setText(
            help_item[
                "short"
            ]
        )

        self.training_short_help.setToolTip(
            help_item[
                "detail"
            ]
        )

        self.training_reason.setText(
            help_item[
                "detail"
            ]
        )

        self.current_training_profile_key = new_key

        if (
            new_key == "custom"
            and self.custom_profile_backup
        ):

            self.apply_training_profile(
                RuntimeTrainingProfile.from_dict(
                    self.custom_profile_backup
                ),
                preserve_mode=True,
            )

            return

        if new_key != "custom":

            self.apply_recommended_training_profile(
                new_key
            )

    def profile_key(
        self,
        mode,
    ):

        value = str(
            mode
        ).lower()

        mapping = {
            "auto": "auto",
            "tự động": "auto",
            "compatibility": "compatibility",
            "tương thích": "compatibility",
            "performance": "performance",
            "hiệu năng": "performance",
            "custom": "custom",
            "tùy chỉnh": "custom",
        }

        return mapping.get(
            value,
            "auto",
        )

    def apply_training_tooltips(
        self,
    ):

        params = self.training_help_service.parameter_help()

        self.training_profile.setToolTip(
            "Chọn cách ứng dụng đề xuất hoặc áp dụng cấu hình train."
        )

        self.auto_detect_hardware.setToolTip(
            params[
                "Auto Detect Hardware"
            ]
        )

        self.runtime_profile.setToolTip(
            params[
                "Runtime"
            ]
        )

        self.training_compute.setToolTip(
            params[
                "Compute"
            ]
        )

        self.training_batch_size.setToolTip(
            params[
                "Batch Size"
            ]
        )

        self.training_workers.setToolTip(
            params[
                "Workers"
            ]
        )

        self.training_gpt_epochs.setToolTip(
            params[
                "GPT Epochs"
            ]
        )

        self.training_sovits_epochs.setToolTip(
            params[
                "SoVITS Epochs"
            ]
        )

        self.training_save_interval.setToolTip(
            params[
                "Save Interval"
            ]
        )

        self.detect_again.setToolTip(
            "Kiểm tra lại GPU, VRAM, CUDA, CPU, RAM và Runtime sau khi đổi máy hoặc nâng cấp phần cứng."
        )

        self.validate_runtime.setToolTip(
            "Kiểm tra Python, Torch, CUDA, script GPT-SoVITS và pretrained model trước khi Train."
        )

        self.reset_recommended.setToolTip(
            "Đưa cấu hình về mức khuyến nghị an toàn theo phần cứng và Runtime hiện tại."
        )

        self.show_effective_config.setToolTip(
            "Hiển thị cấu hình thực tế sẽ dùng nếu bắt đầu Train."
        )

        self.copy_check_report.setToolTip(
            "Sao chép báo cáo kiểm tra để lưu lại hoặc gửi khi cần hỗ trợ."
        )

        self.open_training_guide.setToolTip(
            "Mở hướng dẫn chi tiết bằng tiếng Việt cho Runtime & Training."
        )

    def show_training_guide(
        self,
    ):

        dialog = QDialog(
            self
        )

        dialog.setWindowTitle(
            "Hướng dẫn Runtime & Training"
        )

        layout = QVBoxLayout(
            dialog
        )

        content = QTextEdit()

        content.setReadOnly(
            True
        )

        content.setPlainText(
            self.training_help_service.full_guide()
        )

        copy_button = QPushButton(
            "Sao chép hướng dẫn"
        )

        close_button = QPushButton(
            "Đóng"
        )

        copy_button.clicked.connect(
            lambda: QApplication.clipboard().setText(
                content.toPlainText()
            )
        )

        close_button.clicked.connect(
            dialog.accept
        )

        layout.addWidget(
            content
        )

        layout.addWidget(
            copy_button
        )

        layout.addWidget(
            close_button
        )

        dialog.resize(
            720,
            560,
        )

        dialog.exec()

    def copy_training_guide(
        self,
    ):

        QApplication.clipboard().setText(
            self.training_help_service.full_guide()
        )

    def detect_training_hardware(
        self,
    ):

        try:

            self.last_training_detection = (
                self.training_profile_service.detect_hardware()
            )

            profile = self.apply_recommended_training_profile(
                self.profile_key(
                    self.training_profile.currentText()
                )
            )

            self.update_hardware_labels(
                self.last_training_detection,
                profile,
            )

            self.append_training_log(
                "Đã phát hiện lại phần cứng và cập nhật cấu hình khuyến nghị."
            )

        except Exception as e:

            self.append_training_log(
                f"Lỗi phát hiện phần cứng: {e}"
            )

    def validate_training_runtime(
        self,
    ):

        try:

            profile = self.current_training_profile()

            runtime_profile = (
                self.training_profile_service.select_runtime_profile(
                    profile.runtime_profile_id
                )
            )

            if runtime_profile is None:

                self.last_runtime_validation = {
                    "status": "runtime_missing",
                    "causes": [
                        {
                            "code": "runtime_missing",
                            "message": self.training_help_service.warning_message(
                                "runtime_missing"
                            ),
                        }
                    ],
                }

            else:

                self.last_runtime_validation = (
                    self.training_profile_service.runtime_profiles.validate(
                        runtime_profile,
                        smoke_test=False,
                    )
                )

            self.update_runtime_labels(
                self.last_runtime_validation
            )

            self.append_training_log(
                self.training_validation_message(
                    self.last_runtime_validation
                )
            )

        except Exception as e:

            self.append_training_log(
                f"Lỗi kiểm tra Runtime: {e}"
            )

    def reset_training_recommended(
        self,
    ):

        if self.profile_key(
            self.training_profile.currentText()
        ) == "custom":

            self.custom_profile_backup = (
                self.current_training_profile(
                    mode="custom"
                ).to_dict()
            )

        self.training_profile.setCurrentText(
            "Tá»± Ä‘á»™ng"
        )

        profile = self.apply_recommended_training_profile(
            "auto"
        )

        self.update_hardware_labels(
            self.last_training_detection,
            profile,
        )

        self.append_training_log(
            "Đã khôi phục cấu hình khuyến nghị theo phần cứng hiện tại."
        )

    def show_training_effective_config(
        self,
    ):

        profile = self.current_training_profile()

        self.last_effective_training_profile = profile

        self.show_text_dialog(
            "Cấu hình Runtime & Training sẽ dùng",
            self.training_effective_config_text(
                profile
            ),
        )

    def copy_training_report(
        self,
    ):

        QApplication.clipboard().setText(
            self.training_effective_config_text(
                self.current_training_profile()
            )
        )

        self.append_training_log(
            "Đã sao chép báo cáo kiểm tra Runtime & Training."
        )

    def apply_recommended_training_profile(
        self,
        mode,
    ):

        if not self.last_training_detection:

            self.last_training_detection = (
                self.training_profile_service.detect_hardware()
            )

        custom_config = (
            self.custom_profile_backup
            or self.current_training_profile(
                mode="custom"
            ).to_dict()
        )

        profile = self.training_profile_service.recommend(
            mode,
            custom_config=custom_config,
            hardware=self.last_training_detection,
        )

        self.last_effective_training_profile = profile

        if self.profile_key(
            mode
        ) != "custom":

            self.apply_training_profile(
                profile,
                preserve_mode=True,
            )

        return profile

    def apply_training_profile(
        self,
        profile,
        preserve_mode=False,
    ):

        profile = RuntimeTrainingProfile.from_dict(
            profile
        )

        if not preserve_mode:

            self.training_profile.setCurrentText(
                self.profile_label(
                    profile.mode
                )
            )

        self.auto_detect_hardware.setChecked(
            profile.auto_detect_hardware
        )

        self.training_compute.setCurrentText(
            self.compute_label(
                profile.compute_mode
            )
        )

        self.training_batch_size.setValue(
            int(
                profile.batch_size
            )
        )

        self.training_workers.setValue(
            int(
                profile.num_workers
            )
        )

        self.training_gpt_epochs.setValue(
            int(
                profile.gpt_epochs
            )
        )

        self.training_sovits_epochs.setValue(
            int(
                profile.sovits_epochs
            )
        )

        self.training_save_interval.setValue(
            int(
                profile.save_interval
            )
        )

        if profile.reason:

            self.training_reason.setText(
                profile.reason
            )

    def current_training_profile(
        self,
        mode=None,
    ):

        key = mode or self.profile_key(
            self.training_profile.currentText()
        )

        detection = self.last_training_detection or {}

        hardware = detection.get(
            "hardware",
            {},
        )

        runtime_profile_id = (
            hardware.get(
                "runtime_profile_id",
                "",
            )
            or getattr(
                self.last_effective_training_profile,
                "runtime_profile_id",
                "",
            )
        )

        return RuntimeTrainingProfile(
            mode=key,
            auto_detect_hardware=self.auto_detect_hardware.isChecked(),
            runtime_profile_id=runtime_profile_id,
            compute_mode=self.compute_value(
                self.training_compute.currentText()
            ),
            batch_size=self.training_batch_size.value(),
            num_workers=self.training_workers.value(),
            vram_profile=(
                "low_vram"
                if self.training_batch_size.value() <= 1
                else "custom"
            ),
            gpt_epochs=self.training_gpt_epochs.value(),
            sovits_epochs=self.training_sovits_epochs.value(),
            save_interval=self.training_save_interval.value(),
            resume_policy="manual",
            hardware=hardware,
        )

    def update_hardware_labels(
        self,
        detection,
        profile,
    ):

        hardware = detection.get(
            "hardware",
            {},
        )

        runtime_profile = detection.get(
            "runtime_profile",
            {},
        )

        self.hardware_gpu.setText(
            hardware.get(
                "gpu",
                "",
            )
            or "-"
        )

        vram = int(
            hardware.get(
                "vram_mb",
                0,
            )
            or 0
        )

        self.hardware_vram.setText(
            f"{vram} MiB"
            if vram
            else "-"
        )

        self.hardware_cpu.setText(
            hardware.get(
                "cpu",
                "",
            )
            or "-"
        )

        ram = int(
            hardware.get(
                "ram_mb",
                0,
            )
            or 0
        )

        self.hardware_ram.setText(
            f"{ram} MiB"
            if ram
            else "-"
        )

        self.hardware_cuda.setText(
            "Sẵn sàng"
            if hardware.get(
                "cuda_available",
                False,
            )
            else "Chưa khả dụng"
        )

        self.runtime_profile.setText(
            runtime_profile.get(
                "display_name",
                "",
            )
            or profile.runtime_profile_id
            or "-"
        )

        self.runtime_python.setText(
            hardware.get(
                "python",
                "",
            )
            or "-"
        )

        self.runtime_engine_version.setText(
            runtime_profile.get(
                "engine_version",
                "",
            )
            or "-"
        )

    def update_runtime_labels(
        self,
        validation,
    ):

        checks = validation.get(
            "checks",
            {},
        )

        python = checks.get(
            "python",
            {},
        )

        torch = checks.get(
            "torch",
            {},
        )

        self.runtime_python.setText(
            python.get(
                "stdout",
                "",
            )
            or "-"
        )

        self.runtime_torch.setText(
            torch.get(
                "stdout",
                "",
            )
            or "-"
        )

    def training_validation_message(
        self,
        validation,
    ):

        status = validation.get(
            "status",
            "unknown",
        )

        if status == "ready":

            return "Runtime sẵn sàng cho bước pre-flight. Chưa bắt đầu Train."

        causes = validation.get(
            "causes",
            [],
        )

        if not causes:

            return "Runtime chưa sẵn sàng. Hãy xem báo cáo kiểm tra."

        lines = [
            "Runtime chưa sẵn sàng:"
        ]

        for cause in causes:

            code = cause.get(
                "code",
                "",
            )

            lines.append(
                f"- {self.training_help_service.warning_message(code)}"
            )

        return "\n".join(
            lines
        )

    def training_effective_config_text(
        self,
        profile,
    ):

        profile = RuntimeTrainingProfile.from_dict(
            profile
        )

        hardware = (
            self.last_training_detection.get(
                "hardware",
                {},
            )
            if self.last_training_detection
            else {}
        )

        data = {
            "message": "Cấu hình này chỉ là preview, chưa bắt đầu Train.",
            "training_profile": profile.to_dict(),
            "hardware": hardware,
            "runtime_validation": self.last_runtime_validation or {},
        }

        return json.dumps(
            data,
            indent=4,
            ensure_ascii=False,
        )

    def show_text_dialog(
        self,
        title,
        text,
    ):

        dialog = QDialog(
            self
        )

        dialog.setWindowTitle(
            title
        )

        layout = QVBoxLayout(
            dialog
        )

        content = QTextEdit()

        content.setReadOnly(
            True
        )

        content.setPlainText(
            text
        )

        copy_button = QPushButton(
            "Sao chép"
        )

        close_button = QPushButton(
            "Đóng"
        )

        copy_button.clicked.connect(
            lambda: QApplication.clipboard().setText(
                content.toPlainText()
            )
        )

        close_button.clicked.connect(
            dialog.accept
        )

        layout.addWidget(
            content
        )

        layout.addWidget(
            copy_button
        )

        layout.addWidget(
            close_button
        )

        dialog.resize(
            760,
            560,
        )

        dialog.exec()

    def append_training_log(
        self,
        message,
    ):

        self.log.append(
            str(
                message
            )
        )

    def profile_label(
        self,
        mode,
    ):

        return {
            "auto": "Tá»± Ä‘á»™ng",
            "compatibility": "TÆ°Æ¡ng thĂ­ch",
            "performance": "Hiá»‡u nÄƒng",
            "custom": "TĂ¹y chá»‰nh",
        }.get(
            mode,
            "Tá»± Ä‘á»™ng",
        )

    def compute_label(
        self,
        value,
    ):

        return {
            "auto": "Tá»± Ä‘á»™ng",
            "cuda": "CUDA",
            "cpu": "CPU",
        }.get(
            str(
                value
            ).lower(),
            "Tá»± Ä‘á»™ng",
        )

    def compute_value(
        self,
        label,
    ):

        return {
            "tá»± Ä‘á»™ng": "auto",
            "auto": "auto",
            "cuda": "cuda",
            "cpu": "cpu",
        }.get(
            str(
                label
            ).lower(),
            "auto",
        )

    def sync_local_api_config_from_ui(
        self,
    ):

        self.local_api_service.config.local_api_enabled = (
            self.api_enabled.isChecked()
        )

        self.local_api_service.config.local_api_auto_start = (
            self.api_auto_start.isChecked()
        )

        self.local_api_service.config.local_api_host = (
            self.api_host.text().strip()
            or "127.0.0.1"
        )

        self.local_api_service.config.local_api_port = (
            self.api_port.value()
        )

        self.local_api_service.save_config()

    def update_local_api_status(
        self,
    ):

        status = self.local_api_service.status()

        self.api_status.setText(
            "Đang chạy"
            if status.get(
                "running",
                False,
            )
            else "Đã dừng"
        )

        self.api_catalog_url.setText(
            f"{self.local_api_service.base_url()}/api/v1/voice-catalog"
        )

        self.api_concurrency.setText(
            str(
                status.get(
                    "concurrency",
                    1,
                )
            )
        )

    def start_local_api(
        self,
    ):

        self.sync_local_api_config_from_ui()

        if not self.local_api_service.config.local_api_enabled:

            self.append_training_log(
                "API nội bộ đang tắt. Hãy bật API nội bộ trước khi khởi động."
            )

            self.update_local_api_status()

            return

        status = self.local_api_service.start()

        self.append_training_log(
            f"API nội bộ: {status.get('base_url', '')}"
        )

        self.update_local_api_status()

    def stop_local_api(
        self,
    ):

        self.local_api_service.stop()

        self.append_training_log(
            "Đã dừng API nội bộ."
        )

        self.update_local_api_status()

    def restart_local_api(
        self,
    ):

        self.sync_local_api_config_from_ui()

        status = self.local_api_service.restart()

        self.append_training_log(
            f"Đã khởi động lại API nội bộ: {status.get('base_url', '')}"
        )

        self.update_local_api_status()

    def check_local_api(
        self,
    ):

        status = self.local_api_service.status()

        self.append_training_log(
            "API đang chạy."
            if status.get(
                "running",
                False,
            )
            else "API chưa chạy."
        )

        self.update_local_api_status()

    def copy_local_api_url(
        self,
    ):

        QApplication.clipboard().setText(
            self.local_api_service.base_url()
        )

        self.append_training_log(
            "Đã sao chép URL API."
        )

    def copy_local_api_token(
        self,
    ):

        QApplication.clipboard().setText(
            self.local_api_service.ensure_token()
        )

        self.append_training_log(
            "Đã sao chép token API. Không chia sẻ token ra ngoài máy tin cậy."
        )

    def regenerate_local_api_token(
        self,
    ):

        self.local_api_service.regenerate_token()

        self.api_token.setText(
            "••••••••"
        )

        self.append_training_log(
            "Đã tạo token API mới."
        )

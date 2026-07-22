import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from services.runtime_training_help_service import RuntimeTrainingHelpService


def test_profile_help_is_vietnamese_and_complete():

    service = RuntimeTrainingHelpService()

    help_items = service.profile_help()

    assert help_items["auto"]["name"] == "Tự động"
    assert "khuyến nghị" in help_items["auto"]["detail"].lower()
    assert "phần cứng" in help_items["auto"]["detail"].lower()

    assert help_items["compatibility"]["name"] == "Tương thích"
    assert "vram" in help_items["compatibility"]["detail"].lower()
    assert "treo" in help_items["compatibility"]["detail"].lower()

    assert help_items["performance"]["name"] == "Hiệu năng"
    assert "nhanh hơn" in help_items["performance"]["detail"].lower()

    assert help_items["custom"]["name"] == "Tùy chỉnh"
    assert "hết vram" in help_items["custom"]["detail"].lower()


def test_parameter_help_contains_required_terms():

    service = RuntimeTrainingHelpService()

    params = service.parameter_help()

    for key in (
        "Runtime",
        "Compute",
        "Batch Size",
        "Workers",
        "VRAM Profile",
        "GPT Epochs",
        "SoVITS Epochs",
        "Save Interval",
        "Resume Policy",
        "Auto Detect Hardware",
    ):

        assert key in params
        assert len(
            params[key]
        ) > 40

    assert "không tự sửa Runtime gốc" in params["Runtime"]
    assert "GPU NVIDIA" in params["Compute"]
    assert "GPU 4 GB" in params["Batch Size"]
    assert "Windows" in params["Workers"]


def test_warning_messages_are_user_friendly_vietnamese():

    service = RuntimeTrainingHelpService()

    assert "GPU NVIDIA" in service.warning_message(
        "cuda_unavailable"
    )
    assert "GPT-SoVITS Runtime" in service.warning_message(
        "runtime_missing"
    )
    assert "Batch Size" in service.warning_message(
        "out_of_memory"
    )
    assert "pretrained_models" in service.warning_message(
        "pretrained_model_missing"
    )


def test_hardware_summary_uses_detection_data_not_hardcoded_gpu():

    service = RuntimeTrainingHelpService()

    summary = service.hardware_summary(
        {
            "gpu": "RTX 4090",
            "vram_mb": 24576,
            "cuda_available": True,
        },
        {
            "runtime_profile_id": "runtime-fast",
            "compatibility_mode": "performance",
            "batch_size": 4,
            "num_workers": 4,
            "compute_mode": "cuda",
        },
    )

    assert "RTX 4090" in summary
    assert "24.0 GB" in summary
    assert "runtime-fast" in summary
    assert "Quadro P1000" not in summary


def test_migration_guide_and_full_guide():

    service = RuntimeTrainingHelpService()

    guide = service.migration_guide()

    assert "Cài đặt → Runtime & Training" in guide
    assert "Phát hiện lại phần cứng" in guide
    assert "Kiểm tra Runtime" in guide

    full = service.full_guide()

    assert "Hướng dẫn sử dụng Runtime & Training" in full
    assert "Các chế độ cấu hình" in full
    assert "Giải thích tham số" in full
    assert "Hướng dẫn đổi máy" in full

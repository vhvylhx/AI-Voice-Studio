from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

SETTINGS_PAGE = ROOT / "src" / "pages" / "settings_page.py"


def read_settings_page():

    return SETTINGS_PAGE.read_text(
        encoding="utf-8"
    )


def test_runtime_training_buttons_have_handlers():

    text = read_settings_page()

    expected_connections = [
        "self.detect_again.clicked.connect(",
        "self.validate_runtime.clicked.connect(",
        "self.reset_recommended.clicked.connect(",
        "self.show_effective_config.clicked.connect(",
        "self.copy_check_report.clicked.connect(",
        "self.open_training_guide.clicked.connect(",
    ]

    for item in expected_connections:

        assert item in text

    expected_handlers = [
        "def detect_training_hardware(",
        "def validate_training_runtime(",
        "def reset_training_recommended(",
        "def show_training_effective_config(",
        "def copy_training_report(",
        "def show_training_guide(",
    ]

    for item in expected_handlers:

        assert item in text


def test_runtime_training_buttons_call_services():

    text = read_settings_page()

    assert "RuntimeTrainingProfileService" in text
    assert ".detect_hardware()" in text
    assert ".runtime_profiles.validate(" in text
    assert ".recommend(" in text
    assert "training_effective_config_text" in text
    assert "warning_message" in text
    assert "Chưa bắt đầu Train" in text


def test_runtime_training_preserves_custom_backup():

    text = read_settings_page()

    assert "custom_profile_backup" in text
    assert "current_training_profile_key" in text
    assert "new_key == \"custom\"" in text
    assert "new_key != \"custom\"" in text

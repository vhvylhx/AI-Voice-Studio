from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SETTINGS_PAGE = ROOT / "src" / "pages" / "settings_page.py"


def read_settings_page():

    return SETTINGS_PAGE.read_text(
        encoding="utf-8"
    )


def test_settings_has_api_integration_group():

    text = read_settings_page()

    assert "API & Tích hợp" in text
    assert "Bật API nội bộ" in text
    assert "Tự khởi động API cùng ứng dụng" in text
    assert "Voice Catalog URL" in text
    assert "Khởi động API" in text
    assert "Dừng API" in text
    assert "Tạo Token mới" in text


def test_settings_api_buttons_have_handlers():

    text = read_settings_page()

    expected = [
        "def start_local_api(",
        "def stop_local_api(",
        "def restart_local_api(",
        "def check_local_api(",
        "def copy_local_api_url(",
        "def copy_local_api_token(",
        "def regenerate_local_api_token(",
    ]

    for item in expected:

        assert item in text

    assert "LocalApiService" in text
    assert ".start()" in text
    assert ".stop()" in text
    assert ".regenerate_token()" in text


test_settings_has_api_integration_group()
test_settings_api_buttons_have_handlers()

print("SETTINGS_LOCAL_API_TEST_OK")

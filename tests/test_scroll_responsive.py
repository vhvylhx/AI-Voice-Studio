import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))


def test_training_page_uses_scroll_foundation():

    source = Path(
        "src/pages/training_page.py"
    ).read_text(
        encoding="utf-8"
    )

    assert "ScrollablePage" in source
    assert "Dữ liệu tham chiếu" in source
    assert "mode_panels" in source
    assert "Train thật đang bị khóa" in source


def test_ui_components_scroll_area_contract():

    source = Path(
        "src/widgets/ui_components.py"
    ).read_text(
        encoding="utf-8"
    )

    assert "ContentScrollArea" in source
    assert "setWidgetResizable" in source
    assert "ScrollBarAlwaysOff" in source

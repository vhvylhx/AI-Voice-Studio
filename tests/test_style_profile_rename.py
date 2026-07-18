import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from repositories.style_profile_repository import StyleProfileRepository  # noqa: E402
from services.style_profile_service import StyleProfileService  # noqa: E402


class DummyVoiceService:

    def list(
        self,
    ):

        return []


def test_style_profile_rename_keeps_id_and_state(tmp_path):

    repository = StyleProfileRepository(
        tmp_path / "style_profiles"
    )

    service = StyleProfileService(
        repository=repository,
        voice_service=DummyVoiceService(),
    )

    profile = service.create_profile(
        "Kể chuyện"
    )

    state_file = (
        repository.profile_dir(
            profile.style_profile_id
        )
        / "extraction_state.json"
    )

    before = state_file.read_text(
        encoding="utf-8"
    )

    renamed = service.rename(
        profile.style_profile_id,
        "Kể chuyện mới",
    )

    loaded = service.get_profile(
        profile.style_profile_id
    )

    assert renamed.style_profile_id == profile.style_profile_id
    assert loaded.display_name == "Kể chuyện mới"
    assert state_file.read_text(
        encoding="utf-8"
    ) == before


def test_style_profile_rename_rejects_invalid(tmp_path):

    service = StyleProfileService(
        repository=StyleProfileRepository(
            tmp_path / "style_profiles"
        ),
        voice_service=DummyVoiceService(),
    )

    profile = service.create_profile(
        "A"
    )

    try:

        service.rename(
            profile.style_profile_id,
            "",
        )

        assert False

    except ValueError as exc:

        assert "style_profile_name_required" in str(
            exc
        )

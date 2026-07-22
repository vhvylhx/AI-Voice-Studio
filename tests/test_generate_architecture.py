import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from models.generate_config import (  # noqa: E402
    GENERATE_MODE_AI_STYLE,
    GENERATE_MODE_STANDARD,
    TEMP_STATUS_CANCEL,
    TEMP_STATUS_ERROR,
    TEMP_STATUS_PAUSE,
    TEMP_STATUS_SUCCESS,
    GenerateSelectionConfig,
    SpeedProfile,
)
from models.voice_config import VoiceConfig  # noqa: E402
from services.generate_planning_service import (  # noqa: E402
    GeneratePlanningService,
)
from services.project_service import ProjectService  # noqa: E402
from services.temp_workspace_service import (  # noqa: E402
    TempWorkspaceService,
)


VARIANTS = [
    {
        "id": "default",
        "name": "Giọng mặc định",
    },
    {
        "id": "original",
        "name": "Giọng gốc",
    },
    {
        "id": "story",
        "name": "Kể chuyện",
    },
    {
        "id": "warm_male",
        "name": "Nam ấm áp",
    },
]

STYLES = [
    "natural",
    "story",
    "dramatic",
]


def clean_cache(name):

    root = ROOT / "cache" / name

    if root.exists():

        shutil.rmtree(
            root
        )

    root.mkdir(
        parents=True,
    )

    return root


def test_standard_mode_uses_selected_variant():

    service = GeneratePlanningService()

    config = GenerateSelectionConfig(
        mode=GENERATE_MODE_STANDARD,
        voice_id="0001",
        selected_variant_id="story",
    )

    result = service.validate_selection(
        config,
        VARIANTS,
        STYLES,
    )

    assert result.ok
    assert result.allowed_variant_ids == [
        "story"
    ]


def test_ai_style_only_uses_ticked_variants_and_styles():

    service = GeneratePlanningService()

    config = GenerateSelectionConfig(
        mode=GENERATE_MODE_AI_STYLE,
        voice_id="0001",
        allowed_variant_ids=[
            "story",
        ],
        allowed_style_ids=[
            "dramatic",
        ],
    )

    result = service.validate_selection(
        config,
        VARIANTS,
        STYLES,
    )

    assert result.ok
    assert result.allowed_variant_ids == [
        "story"
    ]
    assert result.allowed_style_ids == [
        "dramatic"
    ]


def test_all_variants_and_styles():

    service = GeneratePlanningService()

    config = GenerateSelectionConfig(
        mode=GENERATE_MODE_AI_STYLE,
        voice_id="0001",
        allow_all_variants=True,
        allow_all_styles=True,
    )

    result = service.validate_selection(
        config,
        VARIANTS,
        STYLES,
    )

    assert result.ok
    assert result.allowed_variant_ids == [
        "default",
        "original",
        "story",
        "warm_male",
    ]
    assert result.allowed_style_ids == STYLES


def test_no_variant_or_style_selected_blocks_ai_style():

    service = GeneratePlanningService()

    config = GenerateSelectionConfig(
        mode=GENERATE_MODE_AI_STYLE,
        voice_id="0001",
    )

    result = service.validate_selection(
        config,
        VARIANTS,
        STYLES,
    )

    assert not result.ok
    assert "no_variant_selected" in result.errors
    assert "no_style_selected" in result.errors


def test_fallback_stays_inside_allowed_scope():

    service = GeneratePlanningService()

    config = GenerateSelectionConfig(
        mode=GENERATE_MODE_AI_STYLE,
        voice_id="0001",
        default_variant_id="default",
        default_style_id="natural",
    )

    variant_id, _, variant_reason = service.choose_variant(
        config,
        [
            "story",
        ],
        candidate_id="warm_male",
    )

    style_id, _, style_reason = service.choose_style(
        config,
        [
            "dramatic",
        ],
        candidate_id="story",
    )

    assert variant_id == "story"
    assert variant_reason == "best_allowed_variant"
    assert style_id == "dramatic"
    assert style_reason == "best_allowed_style"


def test_timeline_does_not_change_mid_sentence():

    service = GeneratePlanningService()

    config = GenerateSelectionConfig(
        mode=GENERATE_MODE_AI_STYLE,
        voice_id="0001",
    )

    segments = [
        {
            "text": "Đây là nửa câu",
            "variant_id": "story",
            "mid_sentence": True,
            "boundary": "sentence",
        },
        {
            "text": "Đây là một câu đủ.",
            "variant_id": "story",
            "boundary": "sentence",
        },
        {
            "text": "Câu kế tiếp.",
            "variant_id": "story",
            "boundary": "sentence",
        },
    ]

    timeline = service.build_variant_timeline(
        segments,
        config,
        [
            "story",
        ],
    )

    assert len(
        timeline.items
    ) == 1
    assert timeline.items[0].segment_index == 1


def test_speed_validation():

    service = GeneratePlanningService()

    assert service.validate_speed(
        SpeedProfile(
            speed=1.2,
        )
    ) == []

    assert service.validate_speed(
        SpeedProfile(
            speed=1.19,
            allow_custom=True,
        )
    ) == []

    assert service.validate_speed(
        SpeedProfile(
            speed=1.21,
            allow_custom=True,
        )
    ) == [
        "custom_speed_out_of_range",
    ]

    assert service.validate_speed(
        SpeedProfile(
            speed=1.5,
            allow_custom=True,
        )
    ) == []


def test_best_confidence_fallback_within_allowed_scope():

    service = GeneratePlanningService()

    config = GenerateSelectionConfig(
        mode=GENERATE_MODE_AI_STYLE,
        voice_id="0001",
        default_variant_id="default",
        default_style_id="natural",
    )

    variant_id, confidence, reason = service.choose_variant(
        config,
        [
            "story",
            "warm_male",
        ],
        candidate_id="robot",
        candidates=[
            {
                "id": "story",
                "confidence": 0.7,
            },
            {
                "id": "warm_male",
                "confidence": 0.9,
            },
            {
                "id": "robot",
                "confidence": 1.0,
            },
        ],
    )

    assert variant_id == "warm_male"
    assert confidence == 0.9
    assert reason == "best_allowed_variant"


def test_temp_workspace_cleanup_and_output_clean():

    root = clean_cache(
        "test_temp_workspace"
    )

    output = root / "output"

    output.mkdir()

    service = TempWorkspaceService(
        root=root / "temp"
    )

    planner = GeneratePlanningService()

    workspace = service.create(
        kind="generate",
        job_id="job_success",
    )

    assert Path(
        workspace.work_dir
    ).exists()

    assert service.finish(
        workspace,
        TEMP_STATUS_SUCCESS,
    ) == "cleaned"

    assert not Path(
        workspace.work_dir
    ).exists()

    workspace = service.create(
        kind="generate",
        job_id="job_error",
    )

    assert service.finish(
        workspace,
        TEMP_STATUS_ERROR,
    ) == "kept"

    assert Path(
        workspace.work_dir
    ).exists()

    assert service.finish(
        workspace,
        TEMP_STATUS_PAUSE,
    ) == "kept"

    assert service.finish(
        workspace,
        TEMP_STATUS_CANCEL,
    ) == "needs_user_choice"

    planner.assert_output_clean(
        output
    )

    (output / "temp").mkdir()

    try:

        planner.assert_output_clean(
            output
        )

        assert False

    except ValueError as exc:

        assert str(exc) == "temp_file_in_output"


def test_project_remembers_generate_selection():

    root = clean_cache(
        "test_generate_selection_project"
    )

    service = ProjectService()

    service.root = root

    service.trash_root().mkdir(
        parents=True,
        exist_ok=True,
    )

    project = service.create(
        "Alpha"
    )

    selection = GenerateSelectionConfig(
        mode=GENERATE_MODE_AI_STYLE,
        voice_id="0001",
        allow_all_variants=False,
        allowed_variant_ids=[
            "story",
        ],
        allow_all_styles=False,
        allowed_style_ids=[
            "dramatic",
        ],
        preset_id="preset1",
        reference_style_id="ref1",
        text_profile_id="text1",
        input_path="input.txt",
        output_folder="out",
        output_name="demo",
        output_format="mp3",
        mp3_bitrate_kbps=192,
        speed=SpeedProfile(
            speed=1.2,
        ),
    )

    service.save_generate_selection(
        project,
        selection,
    )

    loaded = service.load(
        "Alpha"
    )

    assert loaded.config.last_generate_mode == GENERATE_MODE_AI_STYLE
    assert loaded.config.last_generate_voice_id == "0001"
    assert loaded.config.last_generate_variant_ids == [
        "story",
    ]
    assert loaded.config.last_generate_style_ids == [
        "dramatic",
    ]
    assert loaded.config.last_generate_speed == 1.2
    assert loaded.config.last_generate_preset_id == "preset1"
    assert loaded.config.last_generate_reference_style_id == "ref1"
    assert loaded.config.last_generate_text_profile_id == "text1"
    assert loaded.config.last_generate_input_path == "input.txt"
    assert loaded.config.last_generate_output_folder == "out"
    assert loaded.config.last_generate_output_name == "demo"
    assert loaded.config.last_generate_output_format == "mp3"
    assert loaded.config.last_generate_mp3_bitrate_kbps == 192


def test_voice_config_has_default_variant_contract():

    config = VoiceConfig()

    assert config.default_variant_id == "default"
    assert config.variants[0]["id"] == "default"

    migrated = VoiceConfig.from_dict(
        {
            "voice_id": "0001",
            "variants": [
                {
                    "id": "original",
                    "name": "Old",
                }
            ],
        }
    )

    assert migrated.default_variant_id == "default"
    assert migrated.variants[0]["id"] == "default"

from pathlib import Path

#
# Root
#

ROOT_DIR = Path(__file__).resolve().parents[2]

#
# App
#

APP_NAME = "AI Voice Studio"

VERSION = "0.1.0"

#
# Workspace
#

WORKSPACE_DIR = ROOT_DIR / "workspace"

PROJECTS_DIR = ROOT_DIR / "projects"

VOICES_DIR = ROOT_DIR / "voices"

OUTPUT_DIR = ROOT_DIR / "output"

LOGS_DIR = ROOT_DIR / "logs"

TEMP_DIR = ROOT_DIR / "temp"

CACHE_DIR = ROOT_DIR / "cache"

#
# Engine
#

DEFAULT_ENGINE = "gpt_sovits"

AUTO_START_ENGINE = True

AUTO_STOP_ENGINE = True

ENGINE_TIMEOUT = 30

#
# GPT-SoVITS
#

GPT_SOVITS_PATH = ""

GPT_SOVITS_HOST = "127.0.0.1"

GPT_SOVITS_PORT = 9880

#
# Dataset
#

DEFAULT_SAMPLE_RATE = 32000

DEFAULT_BATCH_SIZE = 4

DEFAULT_EPOCHS = 15

MIN_AUDIO_SECONDS = 2

MAX_AUDIO_SECONDS = 20

#
# Preview
#

DEFAULT_PREVIEW_TEXT = (
    "Xin chào, đây là giọng nói mẫu."
)

#
# Audio
#

OUTPUT_FORMAT = "wav"

OUTPUT_CHANNELS = 1

NORMALIZE_AUDIO = True

#
# Log
#

LOG_LEVEL = "INFO"

KEEP_LOG_DAYS = 30

#
# Tạo folder nếu chưa có
#

for folder in (

    WORKSPACE_DIR,

    PROJECTS_DIR,

    VOICES_DIR,

    OUTPUT_DIR,

    LOGS_DIR,

    TEMP_DIR,

    CACHE_DIR,

):

    folder.mkdir(

        parents=True,

        exist_ok=True,

    )
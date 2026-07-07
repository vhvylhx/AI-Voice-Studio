from pathlib import Path

# AI-Voice-Studio/
ROOT_DIR = Path(__file__).resolve().parents[2]

# Thư mục làm việc
WORKSPACE_DIR = ROOT_DIR / "workspace"
VOICES_DIR = ROOT_DIR / "voices"
OUTPUT_DIR = ROOT_DIR / "output"
PROJECTS_DIR = ROOT_DIR / "projects"
LOGS_DIR = ROOT_DIR / "logs"

APP_NAME = "AI Voice Studio"
VERSION = "0.1.0"
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from services import workspace_service

summary = workspace_service.scan()

print(summary)

assert "voices" in summary
assert "docx" in summary
assert "txt" in summary
assert "audio" in summary

workspace = Path(
    workspace_service.get_workspace()
)

cache = Path(
    workspace_service.get_cache()
)

print(cache)

assert workspace.exists()
assert cache.exists()

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from services import workspace_service

print(workspace_service.scan())

print(workspace_service.get_cache())
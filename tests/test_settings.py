import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from services import settings_service
from events import bus, Events


def on_change(key, value):
    print(f"{key} -> {value}")


bus.subscribe(Events.SETTINGS_CHANGED, on_change)

print(settings_service.get("language"))

settings_service.set("language", "vi")

print(settings_service.all())
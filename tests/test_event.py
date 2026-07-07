import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from events import bus, Events


def on_start():
    print("APP STARTED")


def on_queue():
    print("QUEUE UPDATED")


bus.subscribe(Events.APP_STARTED, on_start)
bus.subscribe(Events.QUEUE_CHANGED, on_queue)

bus.emit(Events.APP_STARTED)
bus.emit(Events.QUEUE_CHANGED)
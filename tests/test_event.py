import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(
    0,
    str(
        SRC
    ),
)

from events import bus, Events  # noqa: E402


def test_event_bus_emits_subscribed_callbacks():

    calls = []

    def on_start():

        calls.append(
            "started"
        )

    def on_queue():

        calls.append(
            "queue"
        )

    bus.subscribe(
        Events.APP_STARTED,
        on_start,
    )

    bus.subscribe(
        Events.QUEUE_CHANGED,
        on_queue,
    )

    bus.emit(
        Events.APP_STARTED
    )

    bus.emit(
        Events.QUEUE_CHANGED
    )

    assert calls == [
        "started",
        "queue",
    ]

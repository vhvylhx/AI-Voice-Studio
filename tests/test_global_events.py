import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from events import Events, bus
from services.app_events import AppEvents
from services.log_service import LogService


def test_job_progress_event_payload():

    bus.clear()

    received = []

    bus.subscribe(
        Events.JOB_PROGRESS,
        received.append,
    )

    payload = {
        "job": "alignment",
        "stage": "test",
        "current_file": "a.mp3",
        "current_item": 1,
        "total_items": 2,
        "percent": 50,
        "elapsed_seconds": 1,
        "estimated_remaining_seconds": 1,
        "message": "OK",
        "level": "info",
    }

    AppEvents.job_progress(
        payload
    )

    assert received == [
        payload
    ]


def test_log_service_emits_global_log_event():

    bus.clear()

    received = []

    bus.subscribe(
        Events.LOG_MESSAGE,
        received.append,
    )

    service = LogService()

    service.root = ROOT / "cache" / "test_global_log"

    service.info(
        "test",
        "Hello",
    )

    assert received
    assert received[-1]["category"] == "test"
    assert received[-1]["message"] == "Hello"
    assert received[-1]["level"] == "info"

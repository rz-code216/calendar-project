from datetime import time, timedelta

from io_comp.models.event import Event
from io_comp.repository.calendar_repository import CalendarRepository
from io_comp.services.availability_service import AvailabilityService

from pathlib import Path
import pytest
from io_comp.repository.errors import CalendarFileError


CALENDAR_CSV = Path(__file__).parent.parent / "resources" / "calendar.csv"

class FakeRepository:
    """A stand-in repository that returns the events given directly by the test.

    Because the service only needs get_all_events(), this fake can replace
    the real repository, and the tests do not depend on any file.
    """

    def __init__(self, events):
        self.events = events

    def get_all_events(self):
        return self.events


# ---------- Unit tests (service logic only, with a fake repository) ----------

def test_readme_example_returns_expected_slots():
    events = [
        Event("Alice", "Morning meeting", time(8, 0), time(9, 30)),
        Event("Alice", "Lunch with Jack", time(13, 0), time(14, 0)),
        Event("Alice", "Yoga", time(16, 0), time(17, 0)),
        Event("Jack", "Morning meeting", time(8, 0), time(8, 50)),
        Event("Jack", "Sales call", time(9, 0), time(9, 40)),
        Event("Jack", "Lunch with Alice", time(13, 0), time(14, 0)),
        Event("Jack", "Yoga", time(16, 0), time(17, 0)),
    ]
    service = AvailabilityService(FakeRepository(events))

    slots = service.find_available_slots(["Alice", "Jack"], timedelta(minutes=60))

    assert slots == [
        (time(7, 0), time(7, 0)),
        (time(9, 40), time(12, 0)),
        (time(14, 0), time(15, 0)),
        (time(17, 0), time(18, 0)),
    ]


def test_event_inside_another_event_does_not_shorten_busy_block():
    events = [
        Event("Alice", "Workshop", time(10, 0), time(12, 0)),
        Event("Jack", "Quick call", time(10, 30), time(11, 0)),
    ]
    service = AvailabilityService(FakeRepository(events))

    busy_blocks = service._merge_into_busy_blocks(events)

    # The block must stay 10:00-12:00 and not shrink to 11:00.
    assert busy_blocks == [(time(10, 0), time(12, 0))]


def test_meeting_longer_than_any_gap_returns_no_slots():
    events = [
        Event("Alice", "Morning", time(7, 0), time(12, 0)),
        Event("Alice", "Afternoon", time(12, 30), time(19, 0)),
    ]
    service = AvailabilityService(FakeRepository(events))

    slots = service.find_available_slots(["Alice"], timedelta(minutes=60))

    # The only free gap is 30 minutes, which is too short for 60 minutes.
    assert slots == []


# ---------- Integration tests (using the real CSV file) ----------
# Note: these use a relative path, so run pytest from the python-project folder.

def test_repository_reads_all_events_from_real_file():
    repository = CalendarRepository(CALENDAR_CSV)

    events = repository.get_all_events()

    assert len(events) == 12
    assert events[0].person == "Alice"
    assert events[0].subject == "Morning meeting"
    assert events[0].start == time(8, 0)
    assert events[0].end == time(9, 30)


def test_full_flow_with_real_file_matches_readme_example():
    service = AvailabilityService(CalendarRepository(CALENDAR_CSV))

    slots = service.find_available_slots(["Alice", "Jack"], timedelta(minutes=60))

    assert slots == [
        (time(7, 0), time(7, 0)),
        (time(9, 40), time(12, 0)),
        (time(14, 0), time(15, 0)),
        (time(17, 0), time(18, 0)),
    ]

def test_missing_file_raises_calendar_file_error():
    repository = CalendarRepository("no_such_file.csv")

    with pytest.raises(CalendarFileError):
        repository.get_all_events()
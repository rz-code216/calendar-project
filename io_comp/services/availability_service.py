from datetime import date, datetime, time, timedelta

from io_comp.models.event import Event
from io_comp.repository.event_repository import EventRepository

DAY_START = time(7, 0)
DAY_END = time(19, 0)

class AvailabilityService:
    """Finds time slots in which all requested people are free."""

    def __init__(self, repository: EventRepository):
        self.repository = repository

    def _get_events_of(self, person_names: list[str]) -> list[Event]:
        all_events = self.repository.get_all_events()
        return [event for event in all_events if event.person in person_names]
    
    def _merge_into_busy_blocks(self, events: list[Event]) -> list[tuple[time, time]]:
        sorted_events = sorted(events, key=lambda event: event.start)

        busy_blocks = []
        for event in sorted_events:
            if busy_blocks and event.start <= busy_blocks[-1][1]:
                last_start, last_end = busy_blocks[-1]
                busy_blocks[-1] = (last_start, max(last_end, event.end))
            else:
                busy_blocks.append((event.start, event.end))
        return busy_blocks

    def _find_free_gaps(self, busy_blocks: list[tuple[time, time]]) -> list[tuple[time, time]]:
        free_gaps = []
        current = DAY_START
        for block_start, block_end in busy_blocks:
            if current < block_start:
                free_gaps.append((current, block_start))
            current = max(current, block_end)
        if current < DAY_END:
            free_gaps.append((current, DAY_END))
        return free_gaps

    def _minutes_between(self, start: time, end: time) -> float:
        today = date.today()
        difference = datetime.combine(today, end) - datetime.combine(today, start)
        return difference.total_seconds() / 60
    
    def find_available_slots(
    self, person_list: list[str], event_duration: timedelta
    ) -> list[tuple[time, time]]:
        events = self._get_events_of(person_list)
        busy_blocks = self._merge_into_busy_blocks(events)
        free_gaps = self._find_free_gaps(busy_blocks)

        duration_minutes = event_duration.total_seconds() / 60
        slots = []
        for gap_start, gap_end in free_gaps:
            if self._minutes_between(gap_start, gap_end) >= duration_minutes:
                latest_start = (
                    datetime.combine(date.today(), gap_end) - event_duration
                ).time()
                slots.append((gap_start, latest_start))
        return slots
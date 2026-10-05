from typing import Protocol

from io_comp.models.event import Event


class EventRepository(Protocol):
    """Anything that can supply calendar events."""

    def get_all_events(self) -> list[Event]: ...
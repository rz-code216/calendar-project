from datetime import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    """A single calendar event that belongs to one person.

    This class only holds data. It is immutable: after an Event is created,
    its values cannot be changed.
    """

    person: str
    subject: str
    start: time
    end: time
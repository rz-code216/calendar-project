import csv
from datetime import datetime

from io_comp.models.event import Event
from io_comp.repository.errors import CalendarFileError

class CalendarRepository:
    """Reads calendar events from a CSV file."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_all_events(self) -> list[Event]:
        events = []
        try:
            with open(self.file_path, newline="") as file:
                for row in csv.reader(file):
                    person, subject, start_text, end_text = row
                    start = datetime.strptime(start_text, "%H:%M").time()
                    end = datetime.strptime(end_text, "%H:%M").time()
                    events.append(Event(person, subject, start, end))
        except FileNotFoundError as error:
            raise CalendarFileError(
                f"Calendar file not found: {self.file_path}"
            ) from error
        return events
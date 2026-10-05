from datetime import timedelta

from io_comp.repository.calendar_repository import CalendarRepository
from io_comp.services.availability_service import AvailabilityService


def format_slot(start, latest_start) -> str:
    if start == latest_start:
        return start.strftime("%H:%M")
    return f"{start.strftime('%H:%M')} - {latest_start.strftime('%H:%M')}"


def main():
    repository = CalendarRepository("resources/calendar.csv")
    service = AvailabilityService(repository)
    slots = service.find_available_slots(["Alice", "Jack"], timedelta(minutes=60))
    for start, latest_start in slots:
        print(f"Starting Time of available slots: {format_slot(start, latest_start)}")


if __name__ == "__main__":
    main()
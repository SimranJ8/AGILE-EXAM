import json
import sys
from collections.abc import Collection, Mapping
from datetime import date, time


_REQUIRED_FIELDS = (
    "patient_name",
    "doctor_name",
    "appointment_date",
    "appointment_time",
)


def _parse_time(value: object, field_name: str) -> time:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must use HH:MM format")

    try:
        parsed_time = time.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"{field_name} must use HH:MM format") from error

    if parsed_time.strftime("%H:%M") != value:
        raise ValueError(f"{field_name} must use HH:MM format")
    return parsed_time


def is_appointment_slot_available(
    appointment_time: str,
    booked_slots: Collection[str],
    opening_time: str = "09:00",
    closing_time: str = "17:00",
) -> bool:
    """Return whether a slot is unbooked and inside clinic hours [open, close)."""
    requested = _parse_time(appointment_time, "appointment_time")
    opening = _parse_time(opening_time, "opening_time")
    closing = _parse_time(closing_time, "closing_time")
    if opening >= closing:
        raise ValueError("opening_time must be earlier than closing_time")

    booked = {_parse_time(slot, "booked_slot") for slot in booked_slots}
    return opening <= requested < closing and requested not in booked


def clinic_appointment(appointment: Mapping[str, object]) -> dict[str, str]:
    """Validate and normalize the fields for a clinic appointment."""
    if not isinstance(appointment, Mapping):
        raise ValueError("appointment must be a JSON object")

    normalized: dict[str, str] = {}
    for field in _REQUIRED_FIELDS:
        value = appointment.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string")
        normalized[field] = value.strip()

    date_value = normalized["appointment_date"]
    try:
        appointment_date = date.fromisoformat(date_value)
    except ValueError as error:
        raise ValueError("appointment_date must use YYYY-MM-DD format") from error
    if appointment_date.isoformat() != date_value:
        raise ValueError("appointment_date must use YYYY-MM-DD format")

    _parse_time(normalized["appointment_time"], "appointment_time")

    return normalized


def main() -> int:
    try:
        appointment = json.load(sys.stdin)
        result = clinic_appointment(appointment)
    except (json.JSONDecodeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import json
import subprocess
import sys
from pathlib import Path

import pytest

from app import clinic_appointment, is_appointment_slot_available


@pytest.mark.parametrize("slot", ["09:30", "16:30"])
def test_available_slot(slot: str) -> None:
    assert is_appointment_slot_available(slot, booked_slots=[])


@pytest.mark.parametrize("slot", ["10:00", "15:30"])
def test_booked_slot_is_unavailable(slot: str) -> None:
    assert not is_appointment_slot_available(slot, booked_slots=[slot])


@pytest.mark.parametrize("slot", ["9:30", "25:00", "09:30:00"])
def test_invalid_time_is_rejected(slot: str) -> None:
    with pytest.raises(ValueError, match="HH:MM"):
        is_appointment_slot_available(slot, booked_slots=[])


@pytest.mark.parametrize(
    ("slot", "expected"),
    [("09:00", True), ("16:59", True), ("17:00", False)],
)
def test_clinic_hour_boundaries(slot: str, expected: bool) -> None:
    assert is_appointment_slot_available(slot, booked_slots=[]) is expected


def test_invalid_clinic_hours_are_rejected() -> None:
    with pytest.raises(ValueError, match="earlier"):
        is_appointment_slot_available(
            "10:00", booked_slots=[], opening_time="17:00", closing_time="09:00"
        )


def test_valid_appointment_is_normalized_without_mutating_input() -> None:
    appointment = {
        "patient_name": "  Alex Doe ",
        "doctor_name": "Dr. Smith",
        "appointment_date": "2026-11-06",
        "appointment_time": "09:30",
    }

    result = clinic_appointment(appointment)

    assert result["patient_name"] == "Alex Doe"
    assert result["appointment_date"] == "2026-11-06"
    assert result["appointment_time"] == "09:30"
    assert appointment["patient_name"] == "  Alex Doe "


@pytest.mark.parametrize(
    ("appointment", "message"),
    [
        ([], "JSON object"),
        ({"patient_name": "Alex"}, "doctor_name"),
        (
            {
                "patient_name": "Alex",
                "doctor_name": "Dr. Smith",
                "appointment_date": "2026-11-06",
                "appointment_time": "25:00",
            },
            "HH:MM",
        ),
    ],
)
def test_invalid_appointment_is_rejected(
    appointment: object, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        clinic_appointment(appointment)  # type: ignore[arg-type]


def test_cli_returns_normalized_json() -> None:
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    payload = {
        "patient_name": "Alex Doe",
        "doctor_name": "Dr. Smith",
        "appointment_date": "2026-11-06",
        "appointment_time": "09:30",
    }

    result = subprocess.run(
        [sys.executable, str(app_path)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert json.loads(result.stdout) == payload
    assert result.stderr == ""


def test_cli_reports_invalid_json() -> None:
    app_path = Path(__file__).resolve().parents[1] / "app.py"

    result = subprocess.run(
        [sys.executable, str(app_path)],
        input="{",
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert result.stderr.startswith("Error: ")

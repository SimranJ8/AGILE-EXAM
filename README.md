# Clinic Appointment App

A Python clinic appointment app with a dependency-free command-line interface
and a reusable appointment-slot availability check.

## Appointment format

The input must be a JSON object with all four fields:

```json
{
  "patient_name": "Alex Doe",
  "doctor_name": "Dr. Smith",
  "appointment_date": "2026-11-06",
  "appointment_time": "09:30"
}
```

Names must be non-empty strings, the date must use `YYYY-MM-DD`, and the time
must use `HH:MM`. `is_appointment_slot_available` checks a requested time
against booked slots during clinic hours (09:00 inclusive to 17:00 exclusive).
The command-line app writes the normalized appointment as JSON to standard
output; invalid input produces an error on standard error and exits with status
1.

## Run locally

```powershell
'{"patient_name":"Alex Doe","doctor_name":"Dr. Smith","appointment_date":"2026-11-06","appointment_time":"09:30"}' | python app.py
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Run in Docker

```powershell
docker build -t clinic-appointments .
'{"patient_name":"Alex Doe","doctor_name":"Dr. Smith","appointment_date":"2026-11-06","appointment_time":"09:30"}' | docker run --rm -i clinic-appointments
```

## Continuous integration

GitHub Actions runs the unit and command-line tests on pushes and pull requests
to `main`, using Python 3.12, 3.13, and 3.14.

## Selenium portal login tests

The Selenium tests in `tests/test_clinical_portal_login.py` verify successful
and unsuccessful logins with explicit waits. They use Chrome and are skipped
unless `PORTAL_URL`, `PORTAL_USERNAME`, and `PORTAL_PASSWORD` are set. Keep
credentials in environment variables or a secrets manager; do not commit them.

By default, the page uses `input[name='username']`,
`input[name='password']`, and `button[type='submit']`. Set
`PORTAL_USERNAME_SELECTOR`, `PORTAL_PASSWORD_SELECTOR`, and
`PORTAL_SUBMIT_SELECTOR` to CSS selectors matching the portal. The successful
login indicator defaults to `[data-testid='dashboard']`; the failed-login
message defaults to `[role='alert']`. Override those with
`PORTAL_SUCCESS_SELECTOR` and `PORTAL_ERROR_SELECTOR` when needed.

The failed-login case defaults to a deliberately invalid username and password.
Override them with `PORTAL_FAILURE_USERNAME` and `PORTAL_FAILURE_PASSWORD` if
the portal requires different test values. Set `PORTAL_HEADLESS=false` to show
the Chrome window. Run with:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q tests/test_clinical_portal_login.py
```

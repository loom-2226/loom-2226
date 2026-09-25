"""Canonical validation for v0.3-R1 knowledge-event times."""

from __future__ import annotations

from datetime import date, datetime
import re


DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
TIMESTAMP_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")


def validate_event_time(value: str) -> str:
    """Return DATE or SECOND precision, rejecting syntax and calendar errors."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("event_time must be a non-empty canonical ISO-8601 value")
    if DATE_RE.fullmatch(value):
        date.fromisoformat(value)
        return "DATE"
    if TIMESTAMP_RE.fullmatch(value):
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        return "SECOND"
    raise ValueError("event_time must be YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ")

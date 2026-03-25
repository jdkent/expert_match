from __future__ import annotations

import hashlib
from datetime import UTC, date, datetime, time, timedelta
from typing import Any
from uuid import uuid5, NAMESPACE_URL


EVENT_TIMEZONE = "Europe/Paris"
EVENT_DATES = [
    date(2026, 6, 14),
    date(2026, 6, 15),
    date(2026, 6, 16),
    date(2026, 6, 17),
    date(2026, 6, 18),
]
SLOT_START_HOUR = 8
SLOT_END_HOUR = 17
SLOT_INCREMENT_MINUTES = 15


def utcnow() -> datetime:
    return datetime.now(tz=UTC)


def normalize_email(email: str) -> str:
    return email.strip().lower()


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def canonical_slot_catalog() -> list[dict[str, Any]]:
    slots: list[dict[str, Any]] = []
    for current_date in EVENT_DATES:
        hour = SLOT_START_HOUR
        minute = 0
        while hour < SLOT_END_HOUR:
            if hour == SLOT_END_HOUR - 1 and minute > 45:
                break
            slot_start = datetime.combine(current_date, time(hour, minute))
            slot_end = slot_start + timedelta(minutes=SLOT_INCREMENT_MINUTES)
            if slot_end.time().hour > SLOT_END_HOUR or (
                slot_end.time().hour == SLOT_END_HOUR and slot_end.time().minute > 0
            ):
                break
            slot_key = uuid5(NAMESPACE_URL, f"expert-match:{slot_start.isoformat()}")
            slots.append(
                {
                    "slot_id": slot_key,
                    "slot_start": slot_start,
                    "slot_end": slot_end,
                    "local_date": current_date,
                    "local_start_time": slot_start.time(),
                }
            )
            minute += SLOT_INCREMENT_MINUTES
            if minute >= 60:
                hour += 1
                minute = 0
    return slots


SLOT_CATALOG = canonical_slot_catalog()
SLOT_ID_LOOKUP = {slot["slot_id"]: slot for slot in SLOT_CATALOG}

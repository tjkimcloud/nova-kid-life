"""
Optimal posting time calculator for NovaKidLife social posts.

Schedules posts at times when Northern Virginia parents are most active,
based on platform best practices and our target audience (working parents).
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

EASTERN = ZoneInfo("America/New_York")

# Optimal posting slots (Eastern time), ordered by priority within day
WEEKDAY_SLOTS: list[tuple[int, int]] = [
    (9,  0),   # Morning — school drop-off window
    (12, 0),   # Lunch
    (17, 0),   # After school / commute home
]

WEEKEND_SLOTS: list[tuple[int, int]] = [
    (10, 0),   # Weekend morning
    (14, 0),   # Weekend afternoon
]

# Quiet hours — never schedule posts in this window (Eastern)
QUIET_START = 22   # 10pm
QUIET_END   = 7    # 7am


def next_optimal_slot(after: datetime | None = None) -> datetime:
    """Return the next optimal posting slot in Eastern time.

    Args:
        after: Find the next slot after this datetime (default: now).

    Returns:
        A timezone-aware datetime in Eastern time.
    """
    now  = after or datetime.now(tz=EASTERN)
    # Advance at least 10 minutes from now to give Buffer time to process
    base = now + timedelta(minutes=10)

    # Search up to 7 days ahead
    for day_offset in range(7):
        candidate_day = base + timedelta(days=day_offset)
        is_weekend    = candidate_day.weekday() >= 5  # Sat=5, Sun=6
        slots         = WEEKEND_SLOTS if is_weekend else WEEKDAY_SLOTS

        for hour, minute in slots:
            slot_dt = candidate_day.replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )
            if slot_dt > base:
                logger.debug("Next optimal slot: %s", slot_dt.isoformat())
                return slot_dt

    # Fallback: 9am tomorrow (should never reach here)
    tomorrow = (base + timedelta(days=1)).replace(
        hour=9, minute=0, second=0, microsecond=0
    )
    return tomorrow


def slots_for_week(start: datetime | None = None) -> list[datetime]:
    """Return all optimal posting slots for the next 7 days.

    Useful for planning content calendars.
    """
    base   = start or datetime.now(tz=EASTERN)
    result = []
    for day_offset in range(7):
        day        = base + timedelta(days=day_offset)
        is_weekend = day.weekday() >= 5
        slots      = WEEKEND_SLOTS if is_weekend else WEEKDAY_SLOTS
        for hour, minute in slots:
            result.append(
                day.replace(hour=hour, minute=minute, second=0, microsecond=0)
            )
    return sorted(result)


def is_quiet_hours(dt: datetime | None = None) -> bool:
    """Return True if the given time falls in the quiet window (10pm–7am ET)."""
    eastern = (dt or datetime.now(tz=EASTERN)).astimezone(EASTERN)
    hour    = eastern.hour
    return hour >= QUIET_START or hour < QUIET_END

"""Tests for the optimal posting time scheduler."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime
from zoneinfo import ZoneInfo

from scheduler import next_optimal_slot, slots_for_week, is_quiet_hours, EASTERN


class TestNextOptimalSlot:
    def test_returns_future_datetime(self):
        slot = next_optimal_slot()
        assert slot > datetime.now(tz=EASTERN)

    def test_slot_is_timezone_aware(self):
        slot = next_optimal_slot()
        assert slot.tzinfo is not None

    def test_not_in_quiet_hours(self):
        slot = next_optimal_slot()
        assert not is_quiet_hours(slot)

    def test_slot_is_at_defined_hour(self):
        slot  = next_optimal_slot()
        valid = {9, 10, 12, 14, 17}
        assert slot.hour in valid

    def test_consecutive_slots_differ(self):
        slot1 = next_optimal_slot()
        # Request a slot after the first one
        slot2 = next_optimal_slot(after=slot1)
        assert slot2 > slot1

    def test_after_parameter_respected(self):
        # Request a slot after a future datetime
        future = datetime(2026, 6, 15, 15, 0, 0, tzinfo=EASTERN)  # 3pm Monday
        slot   = next_optimal_slot(after=future)
        assert slot > future

    def test_weekday_uses_weekday_slots(self):
        # Monday at 6am — should get 9am same day
        monday_6am = datetime(2026, 3, 23, 6, 0, 0, tzinfo=EASTERN)  # Monday
        slot       = next_optimal_slot(after=monday_6am)
        assert slot.weekday() == 0   # Monday
        assert slot.hour == 9

    def test_weekend_uses_weekend_slots(self):
        # Saturday at 6am — should get 10am same day
        saturday_6am = datetime(2026, 3, 21, 6, 0, 0, tzinfo=EASTERN)  # Saturday
        slot         = next_optimal_slot(after=saturday_6am)
        assert slot.weekday() == 5   # Saturday
        assert slot.hour == 10


class TestSlotsForWeek:
    def test_returns_list(self):
        slots = slots_for_week()
        assert isinstance(slots, list)

    def test_returns_multiple_slots(self):
        slots = slots_for_week()
        assert len(slots) >= 5

    def test_slots_are_sorted(self):
        slots = slots_for_week()
        assert slots == sorted(slots)

    def test_slots_span_seven_days(self):
        start = datetime(2026, 3, 23, 0, 0, 0, tzinfo=EASTERN)  # Monday
        slots = slots_for_week(start=start)
        days  = {s.date() for s in slots}
        assert len(days) == 7


class TestIsQuietHours:
    def test_midnight_is_quiet(self):
        midnight = datetime(2026, 3, 21, 0, 0, 0, tzinfo=EASTERN)
        assert is_quiet_hours(midnight)

    def test_6am_is_quiet(self):
        early = datetime(2026, 3, 21, 6, 0, 0, tzinfo=EASTERN)
        assert is_quiet_hours(early)

    def test_9am_is_not_quiet(self):
        morning = datetime(2026, 3, 21, 9, 0, 0, tzinfo=EASTERN)
        assert not is_quiet_hours(morning)

    def test_noon_is_not_quiet(self):
        noon = datetime(2026, 3, 21, 12, 0, 0, tzinfo=EASTERN)
        assert not is_quiet_hours(noon)

    def test_10pm_is_quiet(self):
        late = datetime(2026, 3, 21, 22, 0, 0, tzinfo=EASTERN)
        assert is_quiet_hours(late)

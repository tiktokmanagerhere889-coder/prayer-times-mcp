"""Tests for prayer times MCP server"""

import pytest
from datetime import datetime

from prayer_times_mcp.utils import (
    calculate_minutes_remaining,
    format_time_remaining,
    get_compass_direction,
    get_landmark_tip,
    get_next_prayer_name,
    get_plain_guide,
    parse_time,
)


class TestTimeUtils:
    """Tests for time parsing and formatting utilities."""

    def test_parse_time(self):
        """Test parsing HH:MM time string."""
        dt = parse_time("14:30")
        assert dt.hour == 14
        assert dt.minute == 30

    def test_format_time_remaining_minutes(self):
        """Test formatting minutes remaining."""
        assert format_time_remaining(30) == "30 minutes"
        assert format_time_remaining(5) == "5 minutes"

    def test_format_time_remaining_hours(self):
        """Test formatting hours and minutes remaining."""
        assert format_time_remaining(60) == "1 hour"
        assert format_time_remaining(90) == "1 hour 30 minutes"
        assert format_time_remaining(120) == "2 hours"

    def test_format_time_remaining_passed(self):
        """Test formatting negative minutes."""
        assert format_time_remaining(-10) == "Passed"

    def test_calculate_minutes_remaining_future(self):
        """Test calculating minutes to future time."""
        current = datetime(2026, 4, 25, 14, 0)
        target = datetime(2026, 4, 25, 16, 30)
        assert calculate_minutes_remaining(current, target) == 150

    def test_calculate_minutes_remaining_past(self):
        """Test calculating minutes to past time (next day)."""
        current = datetime(2026, 4, 25, 23, 0)
        target = datetime(2026, 4, 25, 5, 0)
        # When target is earlier, it means tomorrow - add 24 hours
        assert calculate_minutes_remaining(current, target) == 360  # 6 hours to 5am tomorrow


class TestDirectionUtils:
    """Tests for direction calculation utilities."""

    def test_compass_direction_north(self):
        """Test North direction."""
        assert get_compass_direction(0) == "N"
        assert get_compass_direction(10) == "N"
        assert get_compass_direction(22) == "N"

    def test_compass_direction_northeast(self):
        """Test Northeast direction."""
        assert get_compass_direction(45) == "NE"
        assert get_compass_direction(67) == "NE"

    def test_compass_direction_east(self):
        """Test East direction."""
        assert get_compass_direction(90) == "E"
        assert get_compass_direction(112) == "E"

    def test_compass_direction_southeast(self):
        """Test Southeast direction."""
        assert get_compass_direction(113) == "SE"
        assert get_compass_direction(157) == "SE"

    def test_compass_direction_south(self):
        """Test South direction."""
        assert get_compass_direction(180) == "S"
        assert get_compass_direction(202) == "S"

    def test_compass_direction_southwest(self):
        """Test Southwest direction."""
        assert get_compass_direction(203) == "SW"
        assert get_compass_direction(247) == "SW"

    def test_compass_direction_west(self):
        """Test West direction."""
        assert get_compass_direction(270) == "W"
        assert get_compass_direction(292) == "W"

    def test_compass_direction_northwest(self):
        """Test Northwest direction."""
        assert get_compass_direction(293) == "NW"
        assert get_compass_direction(337) == "NW"

    def test_plain_guide(self):
        """Test plain guide generation."""
        assert "North" in get_plain_guide(0)
        assert "East" in get_plain_guide(90)
        assert "Southeast" in get_plain_guide(135)

    def test_landmark_tip(self):
        """Test landmark tip generation."""
        tip = get_landmark_tip(90)
        assert "sunrise" in tip.lower() or "rising sun" in tip.lower()


class TestPrayerUtils:
    """Tests for prayer time utilities."""

    def test_get_next_prayer_before_fajr(self):
        """Test next prayer when before Fajr."""
        current = "03:00"
        prayers = {
            "Fajr": "04:30",
            "Sunrise": "06:00",
            "Dhuhr": "12:00",
            "Asr": "16:00",
            "Maghrib": "19:00",
            "Isha": "20:30",
        }
        next_prayer, next_time, is_tomorrow = get_next_prayer_name(current, prayers)
        assert next_prayer == "Fajr"
        assert next_time == "04:30"
        assert is_tomorrow is False

    def test_get_next_prayer_after_dhuhr(self):
        """Test next prayer when after Dhuhr."""
        current = "13:00"
        prayers = {
            "Fajr": "04:30",
            "Sunrise": "06:00",
            "Dhuhr": "12:00",
            "Asr": "16:00",
            "Maghrib": "19:00",
            "Isha": "20:30",
        }
        next_prayer, next_time, is_tomorrow = get_next_prayer_name(current, prayers)
        assert next_prayer == "Asr"
        assert next_time == "16:00"
        assert is_tomorrow is False

    def test_get_next_prayer_after_isha(self):
        """Test next prayer when after Isha (should be Fajr next day)."""
        current = "21:00"
        prayers = {
            "Fajr": "04:30",
            "Sunrise": "06:00",
            "Dhuhr": "12:00",
            "Asr": "16:00",
            "Maghrib": "19:00",
            "Isha": "20:30",
        }
        next_prayer, next_time, is_tomorrow = get_next_prayer_name(current, prayers)
        assert next_prayer == "Fajr"
        assert next_time == "04:30"
        assert is_tomorrow is True

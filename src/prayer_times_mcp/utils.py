"""Utilities for prayer times calculations"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple


def parse_time(time_str: str) -> datetime:
    """Parse HH:MM time string to datetime object (using today's date)."""
    return datetime.strptime(time_str, "%H:%M")


def format_time(dt: datetime) -> str:
    """Format datetime to HH:MM string."""
    return dt.strftime("%H:%M")


def calculate_minutes_remaining(current_time: datetime, target_time: datetime) -> int:
    """Calculate minutes between current time and target time.

    If target_time is earlier than current_time, it means the target is tomorrow.
    """
    diff = target_time - current_time
    minutes = int(diff.total_seconds() / 60)

    # If target is earlier (passed), add 24 hours to get tomorrow's time
    if minutes < 0:
        minutes += 24 * 60

    return minutes


def format_time_remaining(minutes: int, is_tomorrow: bool = False) -> str:
    """Format minutes remaining as human-readable string."""
    if minutes < 0:
        return "Passed"

    hours = minutes // 60
    mins = minutes % 60

    if hours == 0:
        result = f"{mins} minutes"
    elif hours == 1:
        if mins == 0:
            result = "1 hour"
        else:
            result = f"1 hour {mins} minutes"
    else:
        if mins == 0:
            result = f"{hours} hours"
        else:
            result = f"{hours} hours {mins} minutes"

    if is_tomorrow:
        result += " (tomorrow)"

    return result


def get_compass_direction(degrees: float) -> str:
    """Convert degrees to compass direction."""
    degrees = degrees % 360

    if degrees < 22.5:
        return "N"
    elif degrees < 67.5:
        return "NE"
    elif degrees < 112.5:
        return "E"
    elif degrees < 157.5:
        return "SE"
    elif degrees < 202.5:
        return "S"
    elif degrees < 247.5:
        return "SW"
    elif degrees < 292.5:
        return "W"
    else:
        return "NW"


def get_plain_guide(degrees: float) -> str:
    """Get human-readable direction guide."""
    direction = get_compass_direction(degrees)

    guides = {
        "N": "Face North",
        "NE": "Face Northeast",
        "E": "Face East",
        "SE": "Face Southeast",
        "S": "Face South",
        "SW": "Face Southwest",
        "W": "Face West",
        "NW": "Face Northwest",
    }

    return guides.get(direction, "Face unknown direction")


def get_landmark_tip(degrees: float) -> str:
    """Get landmark-based direction tip."""
    direction = get_compass_direction(degrees)

    tips = {
        "N": "Roughly towards the North Star at night",
        "NE": "Roughly towards sunrise direction",
        "E": "Roughly towards the rising sun",
        "SE": "Roughly towards the afternoon sun",
        "S": "Roughly towards the midday sun",
        "SW": "Roughly towards sunset direction",
        "W": "Roughly towards the setting sun",
        "NW": "Roughly towards the evening sky",
    }

    return tips.get(direction, "Face the general direction")


def get_prayer_order() -> List[str]:
    """Return prayers in order."""
    return ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]


def get_next_prayer_name(current_time: str, prayer_times: Dict[str, str]) -> Tuple[str, str, bool]:
    """
    Determine the next prayer based on current time.

    Returns:
        Tuple of (prayer_name, prayer_time, is_tomorrow)
    """
    prayers = get_prayer_order()
    current_dt = parse_time(current_time)

    for prayer in prayers:
        if prayer in prayer_times:
            prayer_dt = parse_time(prayer_times[prayer])
            if prayer_dt > current_dt:
                return (prayer, prayer_times[prayer], False)

    # If all prayers passed, next is Fajr (next day)
    return ("Fajr", prayer_times.get("Fajr", "00:00"), True)


def is_ramadan_month(month: int) -> bool:
    """Check if month is Ramadan (month 9 in Islamic calendar)."""
    return month == 9


def calculate_days_between(date1: datetime, date2: datetime) -> int:
    """Calculate days between two dates."""
    return abs((date2 - date1).days)

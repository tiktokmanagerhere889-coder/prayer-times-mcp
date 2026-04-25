"""Integration tests for prayer times MCP tools with real API calls"""

import pytest
import json
from datetime import datetime

from prayer_times_mcp.client import AladhanClient


@pytest.fixture
def client():
    """Create API client for tests."""
    return AladhanClient()


@pytest.mark.asyncio
async def test_get_prayer_times_london(client):
    """Test getting prayer times for London."""
    result = await client.get_prayer_times(
        city="London",
        country="UK",
        method=5,
    )

    assert result.get("code") == 200
    data = result.get("data", {})
    timings = data.get("timings", {})

    # Check required prayer times exist
    required_prayers = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
    for prayer in required_prayers:
        assert prayer in timings, f"Missing {prayer} time"
        assert timings[prayer] is not None, f"{prayer} time is None"

    # Check date info exists
    assert "date" in data
    assert "hijri" in data.get("date", {})


@pytest.mark.asyncio
async def test_get_prayer_times_different_methods(client):
    """Test prayer times with different calculation methods."""
    methods_to_test = [1, 2, 5, 12]  # MWL, ISNA, Karachi, Russia

    for method in methods_to_test:
        result = await client.get_prayer_times(
            city="London",
            country="UK",
            method=method,
        )

        assert result.get("code") == 200
        meta = result.get("data", {}).get("meta", {})
        assert meta.get("method", {}).get("id") == method


@pytest.mark.asyncio
async def test_get_hijri_date(client):
    """Test getting Hijri date."""
    result = await client.get_hijri_date(
        gregorian_date="2026-04-25",
        method=5,
    )

    assert result.get("code") == 200
    data = result.get("data", {})
    hijri = data.get("hijri", {})

    assert "day" in hijri
    assert "month" in hijri
    assert "year" in hijri
    assert "date" in hijri


@pytest.mark.asyncio
async def test_get_calendar(client):
    """Test getting monthly calendar."""
    result = await client.get_calendar(
        city="London",
        country="UK",
        month=4,
        year=2026,
        method=5,
    )

    assert result.get("code") == 200
    data = result.get("data", {})
    days = data.get("days", [])

    # Should have 30 or 31 days
    assert len(days) >= 29, "Calendar should have at least 29 days"

    # Check first day has required fields
    first_day = days[0]
    assert "timings" in first_day
    assert "date" in first_day


@pytest.mark.asyncio
async def test_get_qibla(client):
    """Test getting Qibla direction."""
    result = await client.get_qibla(
        city="London",
        country="UK",
    )

    assert result.get("code") == 200
    data = result.get("data", {})

    # API returns latitude/longitude directly, not coordinates object
    assert "latitude" in data
    assert "longitude" in data
    assert "angle" in data  # angle is the qibla direction
    assert "direction" in data  # direction is also present


@pytest.mark.asyncio
async def test_get_islamic_events(client):
    """Test getting Islamic events for a year."""
    result = await client.get_islamic_events(
        year=2026,
        method=5,
    )

    assert result.get("code") == 200
    data = result.get("data", {})
    events = data.get("events", [])

    # Should have multiple events
    assert len(events) >= 4, "Should have at least 4 major Islamic events"

    # Check event structure
    for event in events:
        assert "title" in event
        assert "date" in event
        assert "type" in event


@pytest.mark.asyncio
async def test_error_handling_invalid_city(client):
    """Test error handling for invalid city."""
    with pytest.raises(ValueError, match="Could not find coordinates"):
        await client.get_prayer_times(
            city="InvalidCityName12345",
            country="NonExistentCountry",
            method=5,
        )


@pytest.mark.asyncio
async def test_prayer_times_format(client):
    """Test that prayer times are in correct HH:MM format."""
    result = await client.get_prayer_times(
        city="Karachi",
        country="Pakistan",
        method=5,
    )

    assert result.get("code") == 200
    timings = result.get("data", {}).get("timings", {})

    time_format = "%H:%M"
    for prayer, time_str in timings.items():
        if time_str:
            # Strip any timezone suffix like (BST)
            clean_time = time_str.split(" ")[0]
            try:
                datetime.strptime(clean_time, time_format)
            except ValueError:
                pytest.fail(f"{prayer} time '{time_str}' is not in HH:MM format")


@pytest.mark.asyncio
async def test_geocoding_london(client):
    """Test geocoding for London."""
    result = await client.get_prayer_times(
        city="London",
        country="UK",
        method=5,
    )

    assert result.get("code") == 200
    data = result.get("data", {})
    location = data.get("location", {})

    # London coordinates should be around 51.5, -0.1
    lat = location.get("latitude", 0)
    lon = location.get("longitude", 0)

    assert 50 < lat < 52, f"London latitude {lat} out of expected range"
    assert -1 < lon < 0, f"London longitude {lon} out of expected range"


@pytest.mark.asyncio
async def test_geocoding_karachi(client):
    """Test geocoding for Karachi."""
    result = await client.get_prayer_times(
        city="Karachi",
        country="Pakistan",
        method=5,
    )

    assert result.get("code") == 200
    data = result.get("data", {})
    location = data.get("location", {})

    # Karachi coordinates should be around 24.8, 67.0
    lat = location.get("latitude", 0)
    lon = location.get("longitude", 0)

    assert 24 < lat < 25, f"Karachi latitude {lat} out of expected range"
    assert 66 < lon < 68, f"Karachi longitude {lon} out of expected range"

"""Tests for MCP tools using real API calls"""

import pytest
import json

from prayer_times_mcp.client import AladhanClient


@pytest.fixture
def client():
    """Create API client for tests."""
    return AladhanClient()


# Test get_prayer_times tool via client
@pytest.mark.asyncio
async def test_get_prayer_times_tool(client):
    """Test get_prayer_times tool via client."""
    result = await client.get_prayer_times(
        city="London",
        country="UK",
        method=5,
    )

    # Client returns dict directly, not JSON string
    data = result

    assert data.get("code") == 200
    assert "data" in data
    timings = data["data"].get("timings", {})
    assert "Fajr" in timings
    assert "Dhuhr" in timings


@pytest.mark.asyncio
async def test_get_next_prayer_tool(client):
    """Test get_next_prayer tool via client."""
    result = await client.get_prayer_times(
        city="London",
        country="UK",
        method=5,
    )

    data = result

    assert data.get("code") == 200
    assert "data" in data
    timings = data["data"].get("timings", {})
    assert "Fajr" in timings
    assert "Maghrib" in timings


@pytest.mark.asyncio
async def test_get_qibla_direction_tool(client):
    """Test get_qibla_direction tool via client."""
    result = await client.get_qibla(
        city="London",
        country="UK",
    )

    data = result

    assert data.get("code") == 200
    assert "data" in data
    assert "angle" in data["data"]
    assert "direction" in data["data"]


@pytest.mark.asyncio
async def test_get_hijri_date_tool(client):
    """Test get_hijri_date tool via client."""
    result = await client.get_hijri_date(
        gregorian_date="2026-04-25",
    )

    data = result

    assert data.get("code") == 200
    assert "data" in data
    hijri = data["data"].get("hijri", {})
    assert "day" in hijri
    assert "month" in hijri
    assert "year" in hijri


@pytest.mark.asyncio
async def test_get_monthly_calendar_tool(client):
    """Test get_monthly_calendar tool via client."""
    result = await client.get_calendar(
        city="London",
        country="UK",
        month=4,
        year=2026,
        method=5,
    )

    data = result

    assert data.get("code") == 200
    assert "data" in data
    days = data["data"].get("days", [])
    assert len(days) > 0
    assert "timings" in days[0]


@pytest.mark.asyncio
async def test_get_ramadan_times_tool(client):
    """Test get_ramadan_times tool via client."""
    result = await client.get_prayer_times(
        city="London",
        country="UK",
        method=5,
    )

    data = result

    assert data.get("code") == 200
    assert "data" in data


@pytest.mark.asyncio
async def test_get_islamic_events_tool(client):
    """Test get_islamic_events tool via client."""
    result = await client.get_islamic_events(
        year=2026,
    )

    data = result

    assert data.get("code") == 200
    assert "data" in data
    events = data["data"].get("events", [])
    assert len(events) >= 4


@pytest.mark.asyncio
async def test_compare_prayer_times_tool(client):
    """Test compare_prayer_times tool via client."""
    result1 = await client.get_prayer_times(
        city="London",
        country="UK",
        method=5,
    )

    result2 = await client.get_prayer_times(
        city="Manchester",
        country="UK",
        method=5,
    )

    assert result1.get("code") == 200
    assert result2.get("code") == 200


# Test error handling
@pytest.mark.asyncio
async def test_get_prayer_times_invalid_city(client):
    """Test get_prayer_times with invalid city."""
    with pytest.raises(ValueError, match="Could not find coordinates"):
        await client.get_prayer_times(
            city="InvalidCity12345",
            country="NonExistentCountry",
        )


@pytest.mark.asyncio
async def test_get_next_prayer_with_default_method(client):
    """Test get_next_prayer uses default method 5."""
    result = await client.get_prayer_times(
        city="Karachi",
        country="Pakistan",
    )

    data = result
    assert data.get("code") == 200
    meta = data["data"].get("meta", {})
    assert meta.get("method", {}).get("id") == 5  # Default method

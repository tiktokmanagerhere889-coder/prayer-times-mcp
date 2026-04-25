"""MCP tools for Islamic prayer times"""

import json
from datetime import datetime
from typing import Annotated, Optional

from mcp.server import Server
from mcp.types import Tool
from pydantic import BaseModel

from .client import AladhanClient
from .utils import (
    calculate_minutes_remaining,
    format_time_remaining,
    get_compass_direction,
    get_landmark_tip,
    get_next_prayer_name,
    get_plain_guide,
    parse_time,
)


class ToolResult(BaseModel):
    """Standard tool result format"""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


# Global server instance
server = Server("prayer-times-mcp")


def create_app() -> Server:
    """Create and configure the MCP server with all tools."""
    app = Server("prayer-times-mcp")

    # Initialize client
    client = AladhanClient()

    # Register all tool handlers
    @app.call_tool()
    async def get_prayer_times(tool_name: str, arguments: dict) -> str:
        """Get prayer times for a specific city and date."""
        try:
            city = arguments.get("city_name", arguments.get("city", ""))
            country = arguments.get("country", "")
            method = arguments.get("method", 5)

            result = await client.get_prayer_times(
                city=city,
                country=country,
                method=method,
            )

            if not result.get("code", 200) == 200:
                return json.dumps({
                    "success": False,
                    "error": result.get("message", "API error"),
                    "city": city,
                    "country": country,
                })

            data = result.get("data", {})
            timings = data.get("timings", {})

            # Get current time for next prayer calculation
            now = datetime.now()
            current_time = now.strftime("%H:%M")

            # Calculate next prayer
            next_prayer, next_time = get_next_prayer_name(current_time, timings)

            response = {
                "success": True,
                "date": data.get("date", {}).get("readable", now.strftime("%Y-%m-%d")),
                "hijri_date": data.get("date", {}).get("hijri", {}).get("date", "Unknown"),
                "city": city,
                "country": country,
                "method": method,
                "prayer_times": {
                    "Fajr": timings.get("Fajr", "Unknown"),
                    "Sunrise": timings.get("Sunrise", "Unknown"),
                    "Dhuhr": timings.get("Dhuhr", "Unknown"),
                    "Asr": timings.get("Asr", "Unknown"),
                    "Maghrib": timings.get("Maghrib", "Unknown"),
                    "Isha": timings.get("Isha", "Unknown"),
                },
                "next_prayer": next_prayer,
                "next_prayer_time": next_time,
            }

            return json.dumps(response, indent=2)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
                "city": arguments.get("city_name", arguments.get("city", "")),
                "country": arguments.get("country", ""),
            })

    @app.call_tool()
    async def get_next_prayer(tool_name: str, arguments: dict) -> str:
        """Get the next prayer time and countdown."""
        try:
            city = arguments.get("city_name", arguments.get("city", ""))
            country = arguments.get("country", "")
            method = arguments.get("method", 5)

            result = await client.get_prayer_times(
                city=city,
                country=country,
                method=method,
            )

            if not result.get("code", 200) == 200:
                return json.dumps({
                    "success": False,
                    "error": result.get("message", "API error"),
                })

            data = result.get("data", {})
            timings = data.get("timings", {})
            date_info = data.get("date", {})

            # Get current time
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            current_dt = parse_time(current_time)

            # Find next prayer
            next_prayer, next_time, is_tomorrow = get_next_prayer_name(current_time, timings)
            next_dt = parse_time(next_time)

            # Calculate minutes remaining
            minutes_remaining = calculate_minutes_remaining(current_dt, next_dt)

            # Format message
            time_str = format_time_remaining(minutes_remaining, is_tomorrow=is_tomorrow)

            response = {
                "success": True,
                "next_prayer": next_prayer,
                "next_prayer_time": next_time,
                "minutes_remaining": minutes_remaining,
                "hours_remaining": minutes_remaining // 60,
                "message": f"{next_prayer} in {time_str}",
                "date": date_info.get("readable", now.strftime("%Y-%m-%d")),
                "city": city,
                "country": country,
            }

            return json.dumps(response, indent=2)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
            })

    @app.call_tool()
    async def get_qibla_direction(tool_name: str, arguments: dict) -> str:
        """Get Qibla direction from a city."""
        try:
            city = arguments.get("city_name", arguments.get("city", ""))
            country = arguments.get("country", "")

            result = await client.get_qibla(
                city=city,
                country=country,
            )

            if not result.get("code", 200) == 200:
                return json.dumps({
                    "success": False,
                    "error": result.get("message", "API error"),
                })

            data = result.get("data", {})
            coordinates = data.get("coordinates", {})
            angle = data.get("angle", 0)

            degrees = float(angle)
            compass = get_compass_direction(degrees)
            plain_guide = get_plain_guide(degrees)
            landmark_tip = get_landmark_tip(degrees)

            response = {
                "success": True,
                "city": city,
                "country": country,
                "coordinates": {
                    "latitude": coordinates.get("latitude", 0),
                    "longitude": coordinates.get("longitude", 0),
                },
                "qibla": {
                    "degrees": round(degrees, 2),
                    "compass_direction": compass,
                    "plain_guide": plain_guide,
                    "landmark_tip": landmark_tip,
                },
            }

            return json.dumps(response, indent=2)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
            })

    @app.call_tool()
    async def get_hijri_date(tool_name: str, arguments: dict) -> str:
        """Get Hijri (Islamic) date for a Gregorian date."""
        try:
            gregorian_date = arguments.get("gregorian_date")
            city = arguments.get("city_name")
            country = arguments.get("country")
            method = arguments.get("method", 5)

            # Use today's date if not specified
            if not gregorian_date:
                gregorian_date = datetime.now().strftime("%Y-%m-%d")

            result = await client.get_hijri_date(
                gregorian_date=gregorian_date,
                method=method,
            )

            if not result.get("code", 200) == 200:
                return json.dumps({
                    "success": False,
                    "error": result.get("message", "API error"),
                })

            data = result.get("data", {})
            hijri = data.get("hijri", {})
            gregorian = data.get("gregorian", {})

            month_name = hijri.get("month", {}).get("en", "Unknown")
            month_num = hijri.get("month", {}).get("number", 0)

            # Check for special months
            special_note = None
            if month_num == 9:
                special_note = "This is Ramadan, the holy month of fasting"
            elif month_num == 12 and 9 <= hijri.get("day", 0) <= 13:
                special_note = "This is during Dhul-Hijjah, the month of Hajj"
            elif month_num == 1:
                special_note = "This is the start of the Islamic New Year"

            response = {
                "success": True,
                "gregorian_date": gregorian.get("date", gregorian_date),
                "hijri_date": {
                    "day": hijri.get("day", 0),
                    "month": month_num,
                    "month_name": month_name,
                    "year": hijri.get("year", 0),
                },
                "gregorian": {
                    "day": gregorian.get("day", 0),
                    "month": gregorian.get("month", {}).get("en", "Unknown"),
                    "year": gregorian.get("year", 0),
                },
                "special_note": special_note,
            }

            if city and country:
                response["city"] = city
                response["country"] = country

            return json.dumps(response, indent=2)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
            })

    @app.call_tool()
    async def get_monthly_calendar(tool_name: str, arguments: dict) -> str:
        """Get full month prayer schedule."""
        try:
            city = arguments.get("city_name", arguments.get("city", ""))
            country = arguments.get("country", "")
            month = arguments.get("month")
            year = arguments.get("year")
            method = arguments.get("method", 5)

            result = await client.get_calendar(
                city=city,
                country=country,
                month=month,
                year=year,
                method=method,
            )

            if not result.get("code", 200) == 200:
                return json.dumps({
                    "success": False,
                    "error": result.get("message", "API error"),
                })

            data = result.get("data", {})
            days = data.get("days", [])
            calendar = []

            for day_data in days:
                timings = day_data.get("timings", {})
                date_info = day_data.get("date", {})

                calendar.append({
                    "date": date_info.get("readable", "Unknown"),
                    "hijri_date": date_info.get("hijri", {}).get("date", "Unknown"),
                    "prayer_times": {
                        "Fajr": timings.get("Fajr", "Unknown"),
                        "Sunrise": timings.get("Sunrise", "Unknown"),
                        "Dhuhr": timings.get("Dhuhr", "Unknown"),
                        "Asr": timings.get("Asr", "Unknown"),
                        "Maghrib": timings.get("Maghrib", "Unknown"),
                        "Isha": timings.get("Isha", "Unknown"),
                    },
                })

            response = {
                "success": True,
                "city": city,
                "country": country,
                "month": month,
                "year": year,
                "method": method,
                "days": calendar,
            }

            return json.dumps(response, indent=2)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
            })

    @app.call_tool()
    async def get_ramadan_times(tool_name: str, arguments: dict) -> str:
        """Get Ramadan sehri and iftar times."""
        try:
            city = arguments.get("city_name", arguments.get("city", ""))
            country = arguments.get("country", "")
            year = arguments.get("year")
            method = arguments.get("method", 5)

            if not year:
                year = datetime.now().year

            # Get current date info
            now = datetime.now()
            current_month = now.month  # Gregorian month

            # Estimate Ramadan dates (month 9 in Islamic calendar)
            ramadan_start = datetime(year, 3, 10)  # Approximate start
            ramadan_end = datetime(year, 4, 9)  # Approximate end

            is_ramadan = ramadan_start <= now <= ramadan_end

            if is_ramadan:
                # Get today's prayer times for Ramadan
                result = await client.get_prayer_times(
                    city=city,
                    country=country,
                    method=method,
                )

                if not result.get("code", 200) == 200:
                    return json.dumps({
                        "success": False,
                        "error": result.get("message", "API error"),
                    })

                data = result.get("data", {})
                timings = data.get("timings", {})

                # Calculate days remaining
                days_elapsed = now.day
                total_days = 29  # Typical Ramadan length

                response = {
                    "success": True,
                    "is_ramadan": True,
                    "year": year,
                    "current_day": days_elapsed,
                    "total_days": total_days,
                    "days_remaining": total_days - days_elapsed,
                    "todays_sehri": timings.get("Fajr", "Unknown"),
                    "todays_iftar": timings.get("Maghrib", "Unknown"),
                    "city": city,
                    "country": country,
                }
            else:
                # Calculate days until next Ramadan
                next_ramadan = datetime(year + 1, 3, 10)  # Next year
                if now > ramadan_end:
                    next_ramadan = datetime(year + 1, 3, 10)
                else:
                    next_ramadan = datetime(year, 3, 10)

                days_until = (next_ramadan - now).days

                response = {
                    "success": True,
                    "is_ramadan": False,
                    "year": year,
                    "days_until_ramadan": days_until,
                    "estimated_start": next_ramadan.strftime("%Y-%m-%d"),
                    "estimated_end": (next_ramadan.replace(day=next_ramadan.day + 29)).strftime("%Y-%m-%d"),
                    "city": city,
                    "country": country,
                }

            return json.dumps(response, indent=2)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
            })

    @app.call_tool()
    async def get_islamic_events(tool_name: str, arguments: dict) -> str:
        """Get upcoming Islamic events."""
        try:
            year = arguments.get("year")
            if not year:
                year = datetime.now().year

            result = await client.get_islamic_events(
                year=year,
            )

            if not result.get("code", 200) == 200:
                return json.dumps({
                    "success": False,
                    "error": result.get("message", "API error"),
                })

            data = result.get("data", {})
            events = data.get("events", [])

            # Parse and format events
            formatted_events = []
            for event in events:
                event_date = event.get("date", {})
                formatted_events.append({
                    "name": event.get("title", "Unknown Event"),
                    "hijri_date": event.get("date", {}).get("hijri", {}).get("date", "Unknown"),
                    "gregorian_date": event_date.get("readable", "Unknown"),
                    "type": event.get("type", "Event"),
                    "description": event.get("description", ""),
                })

            response = {
                "success": True,
                "year": year,
                "events": formatted_events,
            }

            return json.dumps(response, indent=2)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
            })

    @app.call_tool()
    async def compare_prayer_times(tool_name: str, arguments: dict) -> str:
        """Compare prayer times between two cities."""
        try:
            city1 = arguments.get("city1", arguments.get("city_name", ""))
            country1 = arguments.get("country1", arguments.get("country", ""))
            city2 = arguments.get("city2", "")
            country2 = arguments.get("country2", "")
            method = arguments.get("method", 5)

            # Get prayer times for city 1
            result1 = await client.get_prayer_times(
                city=city1,
                country=country1,
                method=method,
            )

            if not result1.get("code", 200) == 200:
                return json.dumps({
                    "success": False,
                    "error": result1.get("message", "API error for city 1"),
                })

            # Get prayer times for city 2
            result2 = await client.get_prayer_times(
                city=city2,
                country=country2,
                method=method,
            )

            if not result2.get("code", 200) == 200:
                return json.dumps({
                    "success": False,
                    "error": result2.get("message", "API error for city 2"),
                })

            data1 = result1.get("data", {})
            data2 = result2.get("data", {})

            timings1 = data1.get("timings", {})
            timings2 = data2.get("timings", {})

            prayers = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
            comparison = {}

            for prayer in prayers:
                time1 = timings1.get(prayer, "00:00")
                time2 = timings2.get(prayer, "00:00")

                # Calculate difference
                diff = 0
                try:
                    from datetime import datetime
                    t1 = datetime.strptime(time1, "%H:%M")
                    t2 = datetime.strptime(time2, "%H:%M")
                    diff = int((t1 - t2).total_seconds() / 60)
                except:
                    pass

                comparison[prayer] = {
                    "city1": time1,
                    "city2": time2,
                    "difference_minutes": diff,
                }

            # Determine travel tip
            max_diff = max(abs(c["difference_minutes"]) for c in comparison.values())

            if max_diff > 30:
                travel_tip = f"Significant difference ({max_diff} minutes). Consider using local prayer times when traveling."
            elif max_diff > 10:
                travel_tip = f"Moderate difference ({max_diff} minutes). Adjust prayer times if traveling between these cities."
            else:
                travel_tip = f"Minor difference ({max_diff} minutes). Prayer times are very similar."

            response = {
                "success": True,
                "comparison": {
                    "city1": city1,
                    "country1": country1,
                    "city2": city2,
                    "country2": country2,
                    "method": method,
                },
                "prayer_times": comparison,
                "summary": {
                    "earliest_fajr": city1 if timings1.get("Fajr", "99:99") < timings2.get("Fajr", "99:99") else city2,
                    "latest_maghrib": city1 if timings1.get("Maghrib", "00:00") > timings2.get("Maghrib", "00:00") else city2,
                    "travel_tip": travel_tip,
                },
            }

            return json.dumps(response, indent=2)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
            })

    # Register tool definitions using list_tools decorator
    @app.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available tools."""
        return [
            Tool(
                name="get_prayer_times",
                description="Get prayer times for a specific city and date. Use this when user asks for prayer times for a city, Fajr/Dhuhr/Asr/Maghrib/Isha times, or today's prayer schedule.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "city_name": {"type": "string", "description": "City name (e.g., London, New York, Karachi)"},
                        "country": {"type": "string", "description": "Country name or code (e.g., UK, US, Pakistan)"},
                        "method": {"type": "integer", "description": "Calculation method (1-12). Default: 5 (Karachi)"}
                    },
                    "required": ["city_name", "country"]
                }
            ),
            Tool(
                name="get_next_prayer",
                description="Get the next prayer time and countdown. Use this when user asks 'what is the next prayer', 'when is the next prayer', 'countdown to prayer', or 'how long until next prayer'.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "city_name": {"type": "string", "description": "City name"},
                        "country": {"type": "string", "description": "Country name or code"},
                        "method": {"type": "integer", "description": "Calculation method. Default: 5"}
                    },
                    "required": ["city_name", "country"]
                }
            ),
            Tool(
                name="get_qibla_direction",
                description="Get Qibla direction from a city. Use this when user asks 'which way is Qibla', 'Qibla direction', 'where is Kaaba', or 'how to face Qibla'.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "city_name": {"type": "string", "description": "City name"},
                        "country": {"type": "string", "description": "Country name or code"}
                    },
                    "required": ["city_name", "country"]
                }
            ),
            Tool(
                name="get_hijri_date",
                description="Get Hijri (Islamic) date for a Gregorian date. Use this when user asks 'what is the Hijri date', 'Islamic date today', 'convert Gregorian to Hijri', or 'what date is [specific date] in Islamic calendar'.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "gregorian_date": {"type": "string", "description": "Gregorian date in YYYY-MM-DD format. Default: today"},
                        "city_name": {"type": "string", "description": "City name for location-based calculation"},
                        "country": {"type": "string", "description": "Country name"},
                        "method": {"type": "integer", "description": "Calculation method. Default: 5"}
                    },
                    "required": []
                }
            ),
            Tool(
                name="get_monthly_calendar",
                description="Get full month prayer schedule. Use this when user asks for 'monthly prayer schedule', 'prayer times for April', 'full month calendar', or 'all prayer times this month'.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "city_name": {"type": "string", "description": "City name"},
                        "country": {"type": "string", "description": "Country name or code"},
                        "month": {"type": "integer", "description": "Month (1-12)"},
                        "year": {"type": "integer", "description": "Year (e.g., 2026)"},
                        "method": {"type": "integer", "description": "Calculation method. Default: 5"}
                    },
                    "required": ["city_name", "country", "month", "year"]
                }
            ),
            Tool(
                name="get_ramadan_times",
                description="Get Ramadan sehri and iftar times. Use this when user asks about 'Ramadan times', 'Sehri and Iftar', 'days remaining in Ramadan', or 'Ramadan schedule'.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "city_name": {"type": "string", "description": "City name"},
                        "country": {"type": "string", "description": "Country name or code"},
                        "year": {"type": "integer", "description": "Year. Default: current year"},
                        "method": {"type": "integer", "description": "Calculation method. Default: 5"}
                    },
                    "required": ["city_name", "country"]
                }
            ),
            Tool(
                name="get_islamic_events",
                description="Get upcoming Islamic events. Use this when user asks about 'Islamic events', 'Eid dates', 'Shab-e-Qadr', 'Islamic holidays', or 'upcoming religious events'.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "year": {"type": "integer", "description": "Year. Default: current year"}
                    },
                    "required": []
                }
            ),
            Tool(
                name="compare_prayer_times",
                description="Compare prayer times between two cities. Use this when user asks to 'compare prayer times', 'London vs Manchester', 'side by side prayer times', or 'difference between cities'.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "city1": {"type": "string", "description": "First city name"},
                        "country1": {"type": "string", "description": "First country"},
                        "city2": {"type": "string", "description": "Second city name"},
                        "country2": {"type": "string", "description": "Second country"},
                        "method": {"type": "integer", "description": "Calculation method. Default: 5"}
                    },
                    "required": ["city1", "country1", "city2", "country2"]
                }
            ),
        ]

    return app

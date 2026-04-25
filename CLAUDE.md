# Prayer Times MCP Server

## Project
Production-ready Islamic prayer times MCP server.
Free API: aladhan.com — no key needed.
Transport: stdio (OpenClaw manages process).
Geocoding: Open-Meteo for city name to coordinates conversion.

## Rules
- Use the mcp-builder skill for all MCP work
- Use uv for Python projects
- Follow spec-first development: spec first, then build
- Use flat Annotated parameters, not Pydantic BaseModel
- Use stdio transport (NOT http)
- Use aladhan.com API — completely free, no auth
- Default calculation method: 5 (Karachi)

## Tools (8 total)

| Tool | Parameters | Description |
|------|------------|-------------|
| `get_prayer_times` | `city_name`, `country`, `method=5` | Get today's 5 daily prayer times |
| `get_next_prayer` | `city_name`, `country`, `method=5` | Get next prayer + countdown in minutes |
| `get_qibla_direction` | `city_name`, `country` | Get Qibla direction with compass |
| `get_hijri_date` | `gregorian_date`, `city_name`, `country`, `method=5` | Convert Gregorian to Hijri date |
| `get_monthly_calendar` | `city_name`, `country`, `month`, `year`, `method=5` | Get full month prayer schedule |
| `get_ramadan_times` | `city_name`, `country`, `year`, `method=5` | Get Sehri/Iftar + days remaining |
| `get_islamic_events` | `year` | Get upcoming Islamic events |
| `compare_prayer_times` | `city1`, `country1`, `city2`, `country2`, `method=5` | Compare 2 cities side by side |

## Calculation Methods
- 1 = Muslim World League (Global default)
- 2 = ISNA (North America)
- 3 = Egypt
- 4 = Makkah/Umm al-Qura (Saudi)
- 5 = Karachi (Pakistan/South Asia) ← default
- 6 = Gulf
- 7 = Kuwait
- 8 = Qatar
- 9 = Singapore
- 10 = France
- 11 = Turkey
- 12 = Russia

## After every build
1. Run tests — fix failures before continuing
2. Start server — confirm boots without errors
3. Make real API calls — verify end to end
4. Kill server
5. Report results

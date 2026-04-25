# Prayer Times MCP Server - Specification

## Overview
Production-ready Islamic prayer times MCP server using aladhan.com API with stdio transport.

## API Source
- **Provider**: aladhan.com
- **Cost**: Free, no authentication required
- **Endpoint**: `https://api.aladhan.com/v1/`

## Transport
- **Method**: stdio
- **Process Manager**: OpenClaw

---

## Tool Specifications

### 1. get_prayer_times

**When to use**: User asks for prayer times for a specific city/country. User wants to know all 5 daily prayer times (Fajr, Dhuhr, Asr, Maghrib, Isha).

**Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| city_name | string | Yes | City name (e.g., "London", "New York", "Karachi") |
| country | string | Yes | Country name or code (e.g., "UK", "US", "Pakistan") |
| method | integer | No | Calculation method (1-12). Default: 5 (Karachi) |

**Calculation Methods**:
- 1 = Muslim World League (Global default)
- 2 = ISNA (North America)
- 3 = Egypt
- 4 = Makkah/Umm al-Qura (Saudi)
- 5 = Karachi (Pakistan/South Asia) ← **default**
- 6 = Gulf
- 7 = Kuwait
- 8 = Qatar
- 9 = Singapore
- 10 = France
- 11 = Turkey
- 12 = Russia

**Returns**:
```json
{
  "date": "2026-04-26",
  "hijri_date": "1447-09-18",
  "city": "London",
  "country": "UK",
  "prayer_times": {
    "fajr": "04:32",
    "sunrise": "06:08",
    "dhuhr": "12:58",
    "asr": "16:47",
    "maghrib": "19:48",
    "isha": "21:24"
  },
  "method": 5,
  "next_prayer": "Maghrib"
}
```

---

### 2. get_next_prayer

**When to use**: User asks "what's the next prayer", "when is the next prayer", "countdown to prayer", or similar. User wants to know how long until the next prayer time.

**Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| city_name | string | Yes | City name |
| country | string | Yes | Country name or code |
| method | integer | No | Calculation method. Default: 5 |

**Returns**:
```json
{
  "next_prayer": "Maghrib",
  "next_prayer_time": "19:48",
  "minutes_remaining": 82,
  "hours_remaining": 1,
  "message": "Maghrib in 1 hour 22 minutes",
  "date": "2026-04-26",
  "city": "London",
  "country": "UK"
}
```

**Logic**:
- Compare current time with prayer times
- If after Isha, next prayer is Fajr (next day)
- Calculate minutes/hours remaining
- Format human-readable message

---

### 3. get_qibla_direction

**When to use**: User asks "which way is Qibla", "Qibla direction", "where is Kaaba", or "how to face Qibla".

**Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| city_name | string | Yes | City name |
| country | string | Yes | Country name or code |

**Returns**:
```json
{
  "city": "London",
  "country": "UK",
  "coordinates": {
    "latitude": 51.5074,
    "longitude": -0.1278
  },
  "qibla": {
    "degrees": 117.45,
    "compass_direction": "SE",
    "plain_guide": "Face Southeast",
    "landmark_tip": "Roughly towards sunrise direction"
  }
}
```

**Compass Directions**:
- N: 0-22.5, 337.5-360
- NE: 22.5-67.5
- E: 67.5-112.5
- SE: 112.5-157.5
- S: 157.5-202.5
- SW: 202.5-247.5
- W: 247.5-292.5
- NW: 292.5-337.5

---

### 4. get_hijri_date

**When to use**: User asks for Hijri date, Islamic date, or wants Gregorian to Hijri conversion. User may provide a specific date or want today's date.

**Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| gregorian_date | string | No | Date in YYYY-MM-DD format. Default: today |
| city_name | string | No | City for location-based calculation |

**Returns**:
```json
{
  "gregorian_date": "2026-04-26",
  "hijri_date": {
    "day": 18,
    "month": 9,
    "month_name": "Ramadan",
    "year": 1447
  },
  "city": "London",
  "country": "UK"
}
```

**Special handling**:
- If month = 9, note it's Ramadan
- If month = 12 and day = 9-13, note it's Dhul-Hijjah/Hajj
- If month = 1, note Islamic New Year

---

### 5. get_monthly_calendar

**When to use**: User asks for "monthly prayer schedule", "full month calendar", "prayer times for April", or similar. User wants to see all prayer times for an entire month.

**Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| city_name | string | Yes | City name |
| country | string | Yes | Country name or code |
| month | integer | Yes | Month (1-12) |
| year | integer | Yes | Year (e.g., 2026) |
| method | integer | No | Calculation method. Default: 5 |

**Returns**:
```json
{
  "city": "London",
  "country": "UK",
  "month": 4,
  "year": 2026,
  "method": 5,
  "days": [
    {
      "date": "2026-04-01",
      "hijri_date": "1447-09-12",
      "prayer_times": {
        "fajr": "05:12",
        "sunrise": "06:48",
        "dhuhr": "13:02",
        "asr": "17:01",
        "maghrib": "19:56",
        "isha": "21:32"
      }
    },
    // ... 29 more days
  ]
}
```

---

### 6. get_ramadan_times

**When to use**: User asks about Ramadan, sehri, iftar, or wants to know days remaining in Ramadan.

**Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| city_name | string | Yes | City name |
| country | string | Yes | Country name or code |
| year | integer | No | Year. Default: current year |
| method | integer | No | Calculation method. Default: 5 |

**Returns (during Ramadan)**:
```json
{
  "is_ramadan": true,
  "year": 2026,
  "current_day": 15,
  "total_days": 29,
  "days_remaining": 14,
  "todays_sehri": "04:32",
  "todays_iftar": "19:48",
  "next_sehri": "04:30",
  "next_iftar": "19:50",
  "city": "London",
  "country": "UK"
}
```

**Returns (outside Ramadan)**:
```json
{
  "is_ramadan": false,
  "year": 2026,
  "days_until_ramadan": 45,
  "estimated_start": "2026-03-12",
  "estimated_end": "2026-04-10",
  "city": "London",
  "country": "UK"
}
```

**Logic**:
- Check if current month is Ramadan (month 9)
- If yes, calculate days remaining and today's times
- If no, estimate next Ramadan start/end dates

---

### 7. get_islamic_events

**When to use**: User asks about Islamic holidays, Eid, Shab-e-Qadr, Islamic New Year, or Prophet's birthday.

**Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| year | integer | No | Year. Default: current year |

**Returns**:
```json
{
  "year": 2026,
  "events": [
    {
      "name": "Eid ul Fitr",
      "hijri_date": "1447-09-29",
      "gregorian_date": "2026-04-19",
      "type": "Festival",
      "description": "Celebration marking end of Ramadan"
    },
    {
      "name": "Shab-e-Qadr",
      "hijri_date": "1447-09-27",
      "gregorian_date": "2026-04-17",
      "type": "Night of Power",
      "description": "Night of Decree - most blessed night"
    },
    {
      "name": "Eid ul Adha",
      "hijri_date": "1447-12-10",
      "gregorian_date": "2026-06-27",
      "type": "Festival",
      "description": "Festival of Sacrifice"
    },
    {
      "name": "Islamic New Year",
      "hijri_date": "1448-01-01",
      "gregorian_date": "2026-09-16",
      "type": "New Year",
      "description": "Start of Islamic year 1448"
    },
    {
      "name": "Prophet Birthday (Mawlid)",
      "hijri_date": "1448-03-12",
      "gregorian_date": "2026-10-29",
      "type": "Mawlid",
      "description": "Birth anniversary of Prophet Muhammad (PBUH)"
    }
  ]
}
```

**Event Logic**:
- Calculate Islamic dates for key events
- Convert to Gregorian for current year
- Include both Hijri and Gregorian dates

---

### 8. compare_prayer_times

**When to use**: User asks to compare prayer times between two cities, "difference between London and Manchester", or "side by side prayer times".

**Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| city1 | string | Yes | First city name |
| country1 | string | Yes | First country |
| city2 | string | Yes | Second city name |
| country2 | string | Yes | Second country |
| method | integer | No | Calculation method. Default: 5 |

**Returns**:
```json
{
  "comparison": {
    "city1": "London",
    "country1": "UK",
    "city2": "Manchester",
    "country2": "UK",
    "method": 5
  },
  "prayer_times": {
    "fajr": {
      "city1": "04:32",
      "city2": "04:28",
      "difference_minutes": -4
    },
    "sunrise": {
      "city1": "06:08",
      "city2": "06:04",
      "difference_minutes": -4
    },
    "dhuhr": {
      "city1": "12:58",
      "city2": "12:58",
      "difference_minutes": 0
    },
    "asr": {
      "city1": "16:47",
      "city2": "16:45",
      "difference_minutes": -2
    },
    "maghrib": {
      "city1": "19:48",
      "city2": "19:44",
      "difference_minutes": -4
    },
    "isha": {
      "city1": "21:24",
      "city2": "21:20",
      "difference_minutes": -4
    }
  },
  "summary": {
    "earliest_fajr": "Manchester",
    "latest_maghrib": "London",
    "travel_tip": "Manchester prayers are 3-4 minutes earlier than London. For travel, use Manchester times."
  }
}
```

**Travel Tip Logic**:
- If cities in same country: note minor differences
- If cities in different countries: note timezone differences
- If cities far apart: suggest using local prayer times

---

## Error Handling

All tools should handle:
1. Invalid city/country names
2. API unavailability
3. Invalid date formats
4. Invalid method numbers
5. Missing parameters

**Error Response Format**:
```json
{
  "error": true,
  "message": "City 'Paris' not found. Please check the spelling.",
  "city": "Paris",
  "country": "France"
}
```

---

## Response Standards

1. **All responses include**:
   - `city` and `country` fields where applicable
   - `date` field for date-specific responses
   - Clear, consistent field names

2. **Time format**: HH:MM (24-hour format)

3. **Date format**: YYYY-MM-DD

4. **Human-readable messages**: Include when helpful (e.g., "Maghrib in 1 hour 22 minutes")

5. **No markdown in responses**: Plain text for stdio transport

---

## Testing Strategy

1. Test each tool with real API calls
2. Test error handling with invalid inputs
3. Test edge cases (midnight transitions, month boundaries)
4. Verify calculation methods produce expected results
5. Test timezone handling

---

## Implementation Order

1. **Core infrastructure**: Setup, base client, utilities
2. **get_prayer_times**: Foundation tool
3. **get_next_prayer**: Uses prayer times logic
4. **get_qibla_direction**: Independent calculation
5. **get_hijri_date**: Date conversion
6. **get_monthly_calendar**: Batch prayer times
7. **get_ramadan_times**: Special case handling
8. **get_islamic_events**: Event calendar
9. **compare_prayer_times**: Multi-city comparison

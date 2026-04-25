# 🕌 Prayer Times MCP Server

[![Free API](https://img.shields.io/badge/API-Free-green?style=flat-square)](https://aladhan.com/prayer-times-api)
[![No Auth](https://img.shields.io/badge/Auth-None-blue?style=flat-square)](#)
[![Transport](https://img.shields.io/badge/Transport-stdio-orange?style=flat-square)](#)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

Production-ready Islamic prayer times MCP server using the free [aladhan.com API](https://aladhan.com/prayer-times-api). No API key required.

## 📖 What is this?

This is a Model Context Protocol (MCP) server that provides 8 tools for retrieving Islamic prayer times, Qibla direction, Hijri dates, and Islamic events. It uses:

- **aladhan.com API** - Free, no authentication required
- **Open-Meteo Geocoding** - City name to coordinates conversion
- **stdio transport** - Works with OpenClaw and other MCP clients

## 🛠️ Available Tools

| Tool | Description | Example Query |
|------|-------------|---------------|
| `get_prayer_times` | Get today's 5 daily prayer times for a city | "What are the prayer times in London?" |
| `get_next_prayer` | Get the next prayer and countdown | "When is the next prayer?" |
| `get_qibla_direction` | Get Qibla direction with compass | "Which way is Qibla from Paris?" |
| `get_hijri_date` | Convert Gregorian to Hijri date | "What's the Islamic date today?" |
| `get_monthly_calendar` | Get full month prayer schedule | "Show me prayer times for April 2026" |
| `get_ramadan_times` | Get Sehri/Iftar times + days remaining | "What are today's Sehri and Iftar times?" |
| `get_islamic_events` | Get upcoming Islamic events | "When is Eid ul Fitr 2026?" |
| `compare_prayer_times` | Compare prayer times between two cities | "Compare London and Manchester prayer times" |

## 🚀 Installation

### Using uv (recommended)

```bash
uv add prayer-times-mcp
```

### Manual installation

```bash
git clone https://github.com/yourusername/prayer-times-mcp.git
cd prayer-times-mcp
uv sync
```

## ⚙️ OpenClaw Configuration

Add this to your OpenClaw configuration:

```json
{
  "mcpServers": {
    "prayer-times": {
      "command": "uv",
      "args": ["run", "python", "-m", "prayer_times_mcp.server"],
      "env": {}
    }
  }
}
```

## 🤖 Claude Desktop Configuration

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "prayer-times": {
      "command": "uv",
      "args": ["run", "python", "-m", "prayer_times_mcp.server"]
    }
  }
}
```

## 📊 Calculation Methods

| ID | Method | Name | Region |
|----|--------|------|--------|
| 1 | MWL | Muslim World League | Global default |
| 2 | ISNA | Islamic Society of North America | North America |
| 3 | Egypt | Egyptian General Authority of Survey | Egypt |
| 4 | Makkah | Umm al-Qura University | Saudi Arabia |
| 5 | Karachi | University of Islamic Sciences | Pakistan/South Asia |
| 6 | Gulf | Gulf Region | Gulf countries |
| 7 | Kuwait | Kuwait | Kuwait |
| 8 | Qatar | Qatar | Qatar |
| 9 | Singapore | MUIS Singapore | Singapore |
| 10 | France | France | France |
| 11 | Turkey | Diyanet Turkey | Turkey |
| 12 | Russia | Russian Muftis | Russia |

## 💡 Example Outputs

### get_prayer_times (Karachi, Pakistan)
```json
{
  "date": "26 Apr 2026",
  "hijri_date": "09-11-1447",
  "city": "Karachi",
  "prayer_times": {
    "Fajr": "04:33",
    "Sunrise": "06:01",
    "Dhuhr": "12:30",
    "Asr": "15:58",
    "Maghrib": "18:59",
    "Isha": "20:18"
  }
}
```

### get_next_prayer (Karachi, Pakistan)
```json
{
  "next_prayer": "Fajr",
  "next_prayer_time": "04:33",
  "minutes_remaining": 479,
  "message": "Fajr in 7 hours 59 minutes (tomorrow)"
}
```

### get_qibla_direction (London, UK)
```json
{
  "city": "London",
  "coordinates": {"latitude": 51.51, "longitude": -0.13},
  "qibla": {
    "degrees": 118.99,
    "compass_direction": "SE",
    "plain_guide": "Face Southeast",
    "landmark_tip": "Roughly towards the afternoon sun"
  }
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [aladhan.com](https://aladhan.com) for providing the free prayer times API
- [Open-Meteo](https://open-meteo.com) for geocoding services

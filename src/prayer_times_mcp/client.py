"""Core HTTP client for aladhan.com API with Open-Meteo geocoding"""

import httpx
from datetime import datetime
from typing import Optional, Dict, Any, Tuple


class AladhanClient:
    """Client for aladhan.com Islamic prayer times API with geocoding support"""

    BASE_URL = "https://api.aladhan.com/v1"
    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

    def __init__(self, timeout: float = 30.0):
        self._client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client"""
        await self._client.aclose()

    async def _get(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make GET request to aladhan.com API"""
        url = f"{self.BASE_URL}{endpoint}"
        response = await self._client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def _geocode_city(self, city: str, country: Optional[str] = None) -> Tuple[float, float, str, str]:
        """
        Geocode city name to latitude and longitude using Open-Meteo.

        Returns:
            Tuple of (latitude, longitude, city_name, country_name)
        """
        params = {
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json",
        }

        if country:
            params["country"] = country

        response = await self._client.get(self.GEOCODING_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if not data.get("results"):
            raise ValueError(f"Could not find coordinates for city: {city}")

        result = data["results"][0]
        latitude = result["latitude"]
        longitude = result["longitude"]
        city_name = result.get("name", city)
        country_name = result.get("country", country or "")

        return latitude, longitude, city_name, country_name

    async def get_prayer_times(
        self,
        city: str,
        country: str,
        method: int = 5,
    ) -> Dict[str, Any]:
        """
        Get prayer times for today for a city.

        Args:
            city: City name
            country: Country name or code
            method: Calculation method (1-12). Default: 5 (Karachi)

        Returns:
            API response with prayer times
        """
        # Geocode city to get coordinates
        latitude, longitude, city_name, country_name = await self._geocode_city(city, country)

        # Get today's date in format DD-MM-YYYY
        today = datetime.now().strftime("%d-%m-%Y")

        # Use timings endpoint with date in path and lat/long as query params
        url = f"{self.BASE_URL}/timings/{today}"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "method": method,
        }

        response = await self._client.get(url, params=params)
        response.raise_for_status()
        result = response.json()

        # Add location info to response
        if "data" in result:
            result["data"]["location"] = {
                "city": city_name,
                "country": country_name,
                "latitude": latitude,
                "longitude": longitude,
            }

        return result

    async def get_hijri_date(
        self,
        gregorian_date: str,
        method: int = 5,
    ) -> Dict[str, Any]:
        """
        Get Hijri date for a Gregorian date.

        Args:
            gregorian_date: Date in YYYY-MM-DD format
            method: Calculation method. Default: 5

        Returns:
            API response with Hijri date information
        """
        # Use timings endpoint with the given date to get hijri info
        # Parse the date and format for the URL
        try:
            dt = datetime.strptime(gregorian_date, "%Y-%m-%d")
            url_date = dt.strftime("%d-%m-%Y")
        except ValueError:
            # Use today's date if parsing fails
            url_date = datetime.now().strftime("%d-%m-%Y")

        # Use timings endpoint with the date - use London coordinates as fallback
        url = f"{self.BASE_URL}/timings/{url_date}?latitude=51.5074&longitude=-0.1278&method={method}"
        response = await self._client.get(url)
        response.raise_for_status()
        result = response.json()

        # Extract hijri info from the date object
        if "data" in result:
            date_info = result["data"].get("date", {})
            result["data"] = {
                "hijri": date_info.get("hijri", {}),
                "gregorian": date_info.get("gregorian", {}),
            }

        return result

    async def get_calendar(
        self,
        city: str,
        country: str,
        month: int,
        year: int,
        method: int = 5,
    ) -> Dict[str, Any]:
        """
        Get monthly prayer calendar.

        Args:
            city: City name
            country: Country name or code
            month: Month (1-12)
            year: Year (e.g., 2026)
            method: Calculation method. Default: 5

        Returns:
            API response with monthly calendar
        """
        # Geocode city to get coordinates
        latitude, longitude, city_name, country_name = await self._geocode_city(city, country)

        # Use calendar endpoint with date in path and lat/long as query params
        url = f"{self.BASE_URL}/calendar/{year}/{month:02d}"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "method": method,
        }

        response = await self._client.get(url, params=params)
        response.raise_for_status()
        result = response.json()

        # Calendar returns data directly as a list - wrap it properly
        if "data" in result and isinstance(result["data"], list):
            result["data"] = {
                "location": {
                    "city": city_name,
                    "country": country_name,
                    "latitude": latitude,
                    "longitude": longitude,
                },
                "days": result["data"]
            }

        return result

    async def get_qibla(
        self,
        city: str,
        country: str,
    ) -> Dict[str, Any]:
        """
        Get Qibla direction from a city.

        Args:
            city: City name
            country: Country name or code

        Returns:
            API response with Qibla direction
        """
        # Geocode city to get coordinates
        latitude, longitude, city_name, country_name = await self._geocode_city(city, country)

        # Use qibla endpoint with coordinates in path
        url = f"{self.BASE_URL}/qibla/{latitude}/{longitude}"

        response = await self._client.get(url)
        response.raise_for_status()
        result = response.json()

        # Add location info to response
        if "data" in result:
            result["data"]["location"] = {
                "city": city_name,
                "country": country_name,
                "latitude": latitude,
                "longitude": longitude,
            }
            # Map direction to angle for consistency
            if "direction" in result["data"]:
                result["data"]["angle"] = result["data"]["direction"]
            # Add coordinates object for backward compatibility
            result["data"]["coordinates"] = {
                "latitude": result["data"]["latitude"],
                "longitude": result["data"]["longitude"],
            }

        return result

    async def get_islamic_events(
        self,
        year: int,
        method: int = 5,
    ) -> Dict[str, Any]:
        """
        Get Islamic events for a year.

        Args:
            year: Year (e.g., 2026)
            method: Calculation method. Default: 5

        Returns:
            API response with Islamic events
        """
        # The aladhan.com API doesn't have an Islamic events endpoint
        # Return a placeholder response with estimated dates
        # This can be enhanced with actual Islamic calendar calculations

        # Estimate Islamic events based on known patterns
        # These are approximate dates and would need proper Islamic calendar calculation
        events = self._estimate_islamic_events(year)

        return {
            "code": 200,
            "status": "OK",
            "data": {
                "events": events
            }
        }

    def _estimate_islamic_events(self, year: int) -> list:
        """
        Estimate Islamic events for a year.
        Note: These are approximate dates. For production use, implement
        proper Islamic calendar calculations or use a dedicated library.
        """
        # These are approximate dates based on typical Islamic calendar patterns
        # In production, use a proper Hijri calendar library for accurate dates

        events = [
            {
                "title": "Islamic New Year",
                "date": {"readable": f"1 Muharram {year}"},
                "type": "New Year",
                "description": "Start of the Islamic new year",
            },
            {
                "title": "Prophet's Birthday (Mawlid)",
                "date": {"readable": f"12 Rabi' al-awwal {year}"},
                "type": "Mawlid",
                "description": "Birth anniversary of Prophet Muhammad (PBUH)",
            },
            {
                "title": "Shab-e-Barat",
                "date": {"readable": f"15 Sha'ban {year}"},
                "type": "Night of Forgiveness",
                "description": "Night of Forgiveness and mercy",
            },
            {
                "title": "Ramadan",
                "date": {"readable": f"1 Ramadan {year}"},
                "type": "Holy Month",
                "description": "The holy month of fasting",
            },
            {
                "title": "Eid ul Fitr",
                "date": {"readable": f"1 Shawwal {year}"},
                "type": "Festival",
                "description": "Celebration marking end of Ramadan",
            },
            {
                "title": "Hajj begins",
                "date": {"readable": f"8 Dhul-Hijjah {year}"},
                "type": "Pilgrimage",
                "description": "Start of the Hajj pilgrimage",
            },
            {
                "title": "Eid ul Adha",
                "date": {"readable": f"10 Dhul-Hijjah {year}"},
                "type": "Festival",
                "description": "Festival of Sacrifice",
            },
        ]

        return events

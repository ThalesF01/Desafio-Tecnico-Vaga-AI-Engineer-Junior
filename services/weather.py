# services/weather.py
from __future__ import annotations
import requests
from dataclasses import dataclass
from typing import Optional, Dict, Any
import re

class WeatherError(Exception):
    pass

@dataclass
class Location:
    name: str
    country: Optional[str]
    latitude: float
    longitude: float

# Minimal mapping of Open-Meteo weather codes
WEATHER_CODE_MAP: Dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    80: "Rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

class WeatherClient:
    def __init__(self, geocoding_url: str, forecast_url: str, timeout_seconds: int = 10):
        self.geocoding_url = geocoding_url.rstrip("/")
        self.forecast_url = forecast_url.rstrip("/")
        self.timeout = timeout_seconds
        self.headers = {"User-Agent": "AI-Assistant/1.0 (contact@example.com)"}

    def is_weather_query(self, text: str) -> bool:
        if not text:
            return False
        t = text.lower()
        return any(k in t for k in ["weather", "forecast", "temperature", "tempo", "clima", "pronóstico", "pronostico"])

    def extract_location(self, text: str) -> Optional[str]:
        if not text:
            return None
        t = text.strip()
        m = re.search(r"\b(?:in|em|en)\s+([A-Za-zÀ-ÿ0-9\.\-\,\s]+)\??$", t, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip()
        for lead in ["weather in", "weather at", "tempo em", "clima em", "pronóstico en", "pronostico en", "forecast in"]:
            if t.lower().startswith(lead):
                return t[len(lead):].strip(" ?")
        return None

    def geocode(self, location_name: str) -> Location:
        params = {
            "q": location_name,
            "format": "json",
            "limit": 1,
            "addressdetails": 1,
        }
        try:
            resp = requests.get(self.geocoding_url, params=params, headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            if not data:
                raise WeatherError(f"No results for location '{location_name}'.")
            loc_data = data[0]
            return Location(
                name=loc_data.get("display_name", location_name),
                country=loc_data.get("address", {}).get("country"),
                latitude=float(loc_data["lat"]),
                longitude=float(loc_data["lon"]),
            )
        except requests.Timeout:
            raise WeatherError(f"Geocoding request timed out for '{location_name}'.")
        except requests.RequestException as e:
            raise WeatherError(f"Geocoding request failed: {e}")

    def current_weather(self, loc: Location) -> str:
        params = {
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "current_weather": True,
        }
        try:
            r = requests.get(self.forecast_url, params=params, timeout=self.timeout)
            r.raise_for_status()
            data: Dict[str, Any] = r.json()
        except requests.RequestException as e:
            raise WeatherError(f"Forecast request failed: {e}")

        current = data.get("current_weather")
        if not current:
            raise WeatherError("Weather data unavailable.")
        temp = current.get("temperature")
        wind = current.get("windspeed")
        code = int(current.get("weathercode", 0))
        desc = WEATHER_CODE_MAP.get(code, f"Code {code}")

        place = loc.name + (f", {loc.country}" if loc.country else "")
        return f"Weather in {place}: {desc}, {temp}°C, wind {wind} m/s."

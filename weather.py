"""
Author: Adam Cottam
Purpose: CSE 310 Module 2 - Trail Log Tracker
Description: Weather lookup for national park locations using Open-Meteo API.
"""

# Imports
from __future__ import annotations
import requests
from datetime import datetime, timezone
from typing import Optional


# National Park Coordinates (lat, lon)
PARK_COORDS = {
    "Zion National Park": (37.2982, -113.0263),
    "Yellowstone National Park": (44.4280, -110.5885),
    "Grand Canyon National Park": (36.1069, -112.1129),
    "Glacier National Park": (48.7596, -113.7870),
    "Bryce Canyon National Park": (37.5930, -112.1871),
    "Rocky Mountain National Park": (40.3428, -105.6836),
    "Yosemite National Park": (37.8651, -119.5383),
    "Grand Teton National Park": (43.7904, -110.6818),
    "Arches National Park": (38.7331, -109.5925),
    "Canyonlands National Park": (38.2136, -109.9025),
}


def calculate_wind_chill(temp_f: float, wind_mph: float) -> Optional[float]:
    """
    Calculate Wind Chill using NWS formula.
    Parameters: temp_f (float), wind_mph (float)
    Return: wind chill (°F) if valid (temp<=50F and wind>3mph), else None.
    """
    # If 50°F and 3 mph winds
    if temp_f <= 50 and wind_mph > 3:
        # Calculate and return Wind Chill
        return 35.74 + 0.6215 * temp_f - 35.75 * (wind_mph**0.16) + 0.4275 * temp_f * (wind_mph**0.16)

    # Returns None above 50°F and less than 3 mph winds
    return None


def calculate_heat_index(temp_f: float, humidity: float) -> Optional[float]:
    """
    Calculate Heat Index using simplified Rothfusz regression.
    Parameters: temp_f (float), humidity (float)
    Return: heat index (°F) if valid (temp>=80F), else None.
    """
    # Heat index only applies at 80°F+
    if temp_f < 80:
        return None

    # Rothfusz regression
    hi = (
        -42.379
        + 2.04901523 * temp_f
        + 10.14333127 * humidity
        - 0.22475541 * temp_f * humidity
        - 0.00683783 * temp_f**2
        - 0.05481717 * humidity**2
        + 0.00122874 * temp_f**2 * humidity
        + 0.00085282 * temp_f * humidity**2
        - 0.00000199 * temp_f**2 * humidity**2
    )

    return hi


def get_weather(park_name: str) -> dict:
    """
    Fetch current weather for a park from Open-Meteo (no API key required).
    Parameters: park_name (str) - The park to fetch weather for.
    Returns: dictionary - The weather data.
    """
    # Check if park is in coordinates list
    if park_name not in PARK_COORDS:
        raise ValueError(f"Unknown park '{park_name}'. Add it to PARK_COORDS in weather.py.")

    # Lat and Long Coordinates
    lat, lon = PARK_COORDS[park_name]

    # URL for API
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code"
        "&temperature_unit=fahrenheit&wind_speed_unit=mph"
    )

    # Response
    resp = requests.get(url, timeout=10)

    # Response Status
    resp.raise_for_status()

    # Convert to JSON format
    data = resp.json()

    # Get Current Data
    current = data.get("current", {})

    # Get Values
    temp_f = float(current.get("temperature_2m", 0))
    humidity = float(current.get("relative_humidity_2m", 0))
    wind_mph = float(current.get("wind_speed_10m", 0))
    weather_code = int(current.get("weather_code", 0))

    # Calculate Wind Chill
    wc = calculate_wind_chill(temp_f, wind_mph)

    # Calculate Heat Index
    hi = calculate_heat_index(temp_f, humidity)

    # Get Weather Description
    description = _weather_code_to_description(weather_code)

    # Return Dictionary
    return {
        "park_name": park_name,
        "lat": lat,
        "lon": lon,
        "temp_f": temp_f,
        "humidity": humidity,
        "wind_mph": wind_mph,
        "wind_chill_f": wc,
        "heat_index_f": hi,
        "description": description,
        "weather_code": weather_code,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def _weather_code_to_description(code: int) -> str:
    """
    Convert WMO weather code to human-readable description.
    Parameters: code (int)
    Return: str
    """
    # WMO Weather Codes
    codes = {
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
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }

    return codes.get(code, f"Unknown ({code})")

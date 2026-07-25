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
    "Acadia National Park": (44.34815, -68.20223),
    "Arches National Park": (38.61587, -109.61999),
    "Badlands National Park": (43.7613, -101.92792),
    "Big Bend National Park": (29.41042, -103.20765),
    "Biscayne National Park": (25.53849, -80.33091),
    "Black Canyon of the Gunnison National Park": (38.57637, -107.7206),
    "Bryce Canyon National Park": (37.50369, -112.26266),
    "Canyonlands National Park": (38.4231, -109.90878),
    "Capitol Reef National Park": (37.71796, -110.9301),
    "Carlsbad Caverns National Park": (32.17496, -104.37547),
    "Channel Islands National Park": (33.48062, -119.02959),
    "Congaree National Park": (33.82994, -80.8225),
    "Congaree National Park Wilderness": (33.81969, -80.7879),
    "Crater Lake National Park": (42.86542, -122.16247),
    "Cuyahoga Valley National Park": (41.25634, -81.57266),
    "Death Valley National Park": (36.33218, -116.80642),
    "Denali National Park": (63.80507, -148.95336),
    "Dry Tortugas National Park": (24.62723, -82.87242),
    "Everglades National Park": (25.38252, -80.60978),
    "Fort Hunt National Park": (38.71518, -77.05732),
    "Fort Pickens National Park": (30.31943, -87.26118),
    "Gateway Arch National Park": (38.62327, -90.18743),
    "Glacier Bay National Park": (58.46205, -135.77323),
    "Glacier National Park": (48.82859, -114.20173),
    "Grand Canyon National Park": (36.05706, -112.14428),
    "Grand Teton National Park": (43.69978, -110.61533),
    "Great Basin National Park": (39.00984, -114.30709),
    "Great Sand Dunes National Park and Preserve": (37.75804, -105.50116),
    "Great Smoky Mountains National Park": (35.59137, -83.85285),
    "Guadalupe Mountains National Park": (31.89674, -104.8286),
    "Haleakala National Park": (20.71417, -156.25093),
    "Hawaii Volcanoes National Park": (19.43001, -155.25985),
    "Hot Springs National Park": (34.51359, -93.05238),
    "Indiana Dunes National Park": (41.62953, -87.09132),
    "Isle Royale National Park": (47.91214, -89.15641),
    "Joshua Tree National Park": (33.98986, -116.02328),
    "Katmai National Park": (58.55986, -155.77752),
    "Kenai Fjords National Park": (60.18879, -149.631),
    "Kings Canyon National Park": (36.7947, -118.58295),
    "Lassen Volcanic National Park": (40.5652, -121.30133),
    "Mammoth Cave National Park": (37.2057, -86.13904),
    "Mesa Verde National Park": (37.19574, -108.53807),
    "Mount Rainier National Park": (46.78386, -121.74238),
    "North Cascades National Park": (48.51941, -120.67423),
    "Olympic National Park": (48.0644, -123.99621),
    "Petrified Forest National Park": (34.94323, -109.77762),
    "Pinnacles National Park": (36.49191, -121.20958),
    "Redwood National Park": (41.45094, -124.03803),
    "Rocky Mountain National Park": (40.31226, -105.64641),
    "Saguaro National Park": (32.06403, -110.62252),
    "Sequoia National Park": (36.02707, -118.51524),
    "Shenandoah National Park": (38.4511, -78.48581),
    "Theodore Roosevelt National Park": (47.59297, -103.33894),
    "Voyageurs National Park": (48.42288, -92.84588),
    "Wind Cave National Park": (43.59131, -103.38165),
    "Wolf Trap National Park for the Performing Arts": (38.93672, -77.26292),
    "Yellowstone National Park": (44.91214, -110.38741),
    "Yosemite National Park": (37.57543, -119.68064),
    "Zion National Park": (37.21752, -112.92365),
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
        # Returns None below 80°F
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

    # Adjustments for low humidity
    if humidity < 13 and temp_f > 80:
        hi -= ((13 - humidity) / 4) * ((85 - temp_f) / 4)

    # Adjustments for high humidity
    return hi


def get_weather(park_name: str) -> dict:
    """
    Fetch current weather for a park from Open-Meteo (no API key required).
    Parameters: park_name (str) - The park to fetch weather for.
    Returns: dictionary - The weather data.
    """
    # Check if park is in coordinates list
    if park_name not in PARK_COORDS:
        # Raise ValueError if park is not found
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

    # Return Description or Unknown 
    return codes.get(code, f"Unknown ({code})")

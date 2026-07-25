"""
Author: Adam Cottam
Purpose: CSE 310 Module 2 - Trail Log Tracker
"""
from weather import calculate_wind_chill, calculate_heat_index, get_weather, PARK_COORDS
import pytest
from pytest import approx


def test_calculate_wind_chill_valid():
    """
    Test Wind Chill calculation with valid inputs.
    Parameters: none
    Return: none
    """
    assert calculate_wind_chill(40, 10) == approx(33.642, abs=0.001)
    assert calculate_wind_chill(50, 5) == approx(48.218, abs=0.001)
    assert calculate_wind_chill(0, 10) == approx(-15.934, abs=0.001)
    assert calculate_wind_chill(32, 100) == approx(9.5172, abs=0.001)


def test_calculate_wind_chill_none():
    """
    Test Wind Chill returns None when conditions don't apply.
    Parameters: none
    Return: none
    """
    # Above 50°F
    assert calculate_wind_chill(60, 10) is None
    assert calculate_wind_chill(51, 10) is None

    # Wind <= 3 mph
    assert calculate_wind_chill(40, 3) is None
    assert calculate_wind_chill(40, 0) is None
    assert calculate_wind_chill(50, 3) is None


def test_calculate_heat_index_valid():
    """
    Test Heat Index calculation with valid inputs.
    Parameters: none
    Return: none
    """
    # 90°F and 50% humidity
    result = calculate_heat_index(90, 50)
    assert result is not None
    assert result > 90  # Heat index should be higher than actual temp

    # 100°F and 70% humidity
    result = calculate_heat_index(100, 70)
    assert result is not None
    assert result > 100


def test_calculate_heat_index_none():
    """
    Test Heat Index returns None when temp is below 80°F.
    Parameters: none
    Return: none
    """
    assert calculate_heat_index(79, 50) is None
    assert calculate_heat_index(70, 80) is None
    assert calculate_heat_index(32, 90) is None


def test_get_weather_zion():
    """
    Test Weather lookup for Zion National Park.
    Parameters: none
    Return: none
    """
    weather = get_weather("Zion National Park")
    assert "park_name" in weather
    assert "lat" in weather
    assert "lon" in weather
    assert "temp_f" in weather
    assert "humidity" in weather
    assert "wind_mph" in weather
    assert "wind_chill_f" in weather
    assert "heat_index_f" in weather
    assert "description" in weather
    assert "timestamp_utc" in weather
    assert weather["park_name"] == "Zion National Park"


def test_get_weather_yellowstone():
    """
    Test Weather lookup for Yellowstone National Park.
    Parameters: none
    Return: none
    """
    weather = get_weather("Yellowstone National Park")
    assert weather["park_name"] == "Yellowstone National Park"
    assert isinstance(weather["temp_f"], float)
    assert isinstance(weather["wind_mph"], float)


def test_get_weather_invalid_park():
    """
    Test Weather lookup with unknown park raises ValueError.
    Parameters: none
    Return: none
    """
    with pytest.raises(ValueError):
        get_weather("Fake National Park")


def test_park_coords_coverage():
    """
    Test that PARK_COORDS has reasonable number of parks.
    Parameters: none
    Return: none
    """
    assert len(PARK_COORDS) >= 50
    assert "Zion National Park" in PARK_COORDS
    assert "Yellowstone National Park" in PARK_COORDS
    assert "Grand Canyon National Park" in PARK_COORDS


def test_park_coords_valid_values():
    """
    Test that coordinates are valid lat/lon ranges.
    Parameters: none
    Return: none
    """
    for park_name, (lat, lon) in PARK_COORDS.items():
        assert -90 <= lat <= 90, f"Invalid latitude for {park_name}: {lat}"
        assert -180 <= lon <= 180, f"Invalid longitude for {park_name}: {lon}"


# Call the main function that is part of pytest so that the
# computer will execute the test functions in this file.
pytest.main(["-v", "--tb=line", "-rN", __file__])

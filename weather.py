import requests
from datetime import datetime


def get_temperature(lat: float, lon: float) -> str:
    """
    Fetch the current temperature for the given coordinates.

    Calls the Open-Meteo API (free, no API key required).
    Returns a string like "18.5°C", or an error message on failure.
    """
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}&current_weather=true"
    )
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        temp = data["current_weather"]["temperature"]
        return f"{temp}°C"
    except (requests.exceptions.RequestException, KeyError, ValueError):
        return "Could not retrieve weather data. Please try again."


def get_forecast(lat: float, lon: float) -> list[dict] | str:
    """
    Fetch the 7-day weather forecast for the given coordinates.

    Returns a list of 7 dicts with keys: date (str), min (float), max (float).
    Returns an error string on failure.
    """
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min"
        "&forecast_days=7"
        "&timezone=auto"
    )
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        days = data["daily"]
        return [
            {
                "date": days["time"][i],
                "min": days["temperature_2m_min"][i],
                "max": days["temperature_2m_max"][i],
            }
            for i in range(len(days["time"]))
        ]
    except (requests.exceptions.RequestException, KeyError, ValueError):
        return "Could not retrieve forecast data. Please try again."

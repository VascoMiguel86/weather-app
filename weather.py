import requests


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

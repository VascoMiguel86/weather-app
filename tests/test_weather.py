from unittest.mock import patch, MagicMock
import requests
from weather import get_temperature


def test_get_temperature_returns_celsius_string():
    """Happy path: API returns valid data."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "current_weather": {"temperature": 18.5}
    }
    mock_response.raise_for_status.return_value = None

    with patch("weather.requests.get", return_value=mock_response):
        result = get_temperature(52.37, 4.89)

    assert result == "18.5°C"


def test_get_temperature_returns_error_on_network_failure():
    """Network is down — should return a friendly error string."""
    with patch("weather.requests.get", side_effect=requests.exceptions.ConnectionError):
        result = get_temperature(52.37, 4.89)

    assert result == "Could not retrieve weather data. Please try again."


def test_get_temperature_returns_error_on_malformed_response():
    """API responds but JSON is missing the expected key."""
    mock_response = MagicMock()
    mock_response.json.return_value = {}  # missing "current_weather"
    mock_response.raise_for_status.return_value = None

    with patch("weather.requests.get", return_value=mock_response):
        result = get_temperature(52.37, 4.89)

    assert result == "Could not retrieve weather data. Please try again."

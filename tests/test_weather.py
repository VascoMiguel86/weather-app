from unittest.mock import patch, MagicMock
import requests
from weather import get_temperature, get_forecast


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


def test_get_forecast_returns_list_of_7_days():
    """Happy path: API returns 7 days of forecast data."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "daily": {
            "time": [
                "2026-05-27", "2026-05-28", "2026-05-29",
                "2026-05-30", "2026-05-31", "2026-06-01", "2026-06-02",
            ],
            "temperature_2m_max": [18.0, 19.5, 17.0, 20.0, 21.0, 16.5, 18.5],
            "temperature_2m_min": [10.0, 11.5,  9.0, 12.0, 13.0,  8.5, 10.5],
        }
    }
    mock_response.raise_for_status.return_value = None

    with patch("weather.requests.get", return_value=mock_response):
        result = get_forecast(52.37, 4.89)

    assert isinstance(result, list)
    assert len(result) == 7
    assert result[0] == {"date": "2026-05-27", "min": 10.0, "max": 18.0}
    assert result[6] == {"date": "2026-06-02", "min": 10.5, "max": 18.5}


def test_get_forecast_returns_error_on_network_failure():
    """Network is down — should return a friendly error string."""
    with patch("weather.requests.get", side_effect=requests.exceptions.ConnectionError):
        result = get_forecast(52.37, 4.89)

    assert result == "Could not retrieve forecast data. Please try again."


def test_get_forecast_returns_error_on_malformed_response():
    """API responds but JSON is missing the expected key."""
    mock_response = MagicMock()
    mock_response.json.return_value = {}  # missing "daily"
    mock_response.raise_for_status.return_value = None

    with patch("weather.requests.get", return_value=mock_response):
        result = get_forecast(52.37, 4.89)

    assert result == "Could not retrieve forecast data. Please try again."

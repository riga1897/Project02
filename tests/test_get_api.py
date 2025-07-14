import pytest
from unittest.mock import patch, Mock
from src.api_modules.get_api import APIConnector
import requests


class TestAPIConnector:
    @patch('requests.get')
    def test_successful_connection(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'key': 'value'}
        mock_get.return_value = mock_response

        connector = APIConnector()
        result = connector.connect("http://test.com", {"param": "value"})
        assert result == {'key': 'value'}

    @patch('requests.get')
    def test_rate_limit_handling(self, mock_get):
        mock_response1 = Mock()
        mock_response1.status_code = 429
        mock_response1.headers = {'Retry-After': '1'}

        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {'key': 'value'}

        mock_get.side_effect = [mock_response1, mock_response2]

        connector = APIConnector()
        result = connector.connect("http://test.com", {"param": "value"})
        assert result == {'key': 'value'}

    @patch('requests.get')
    def test_connection_error_handling(self, mock_get):
        mock_get.side_effect = requests.ConnectionError("Connection failed")

        connector = APIConnector()
        with pytest.raises(ConnectionError) as excinfo:
            connector.connect("http://test.com", {"param": "value"})
        assert "Connection error" in str(excinfo.value)

    @patch('requests.get')
    def test_timeout_handling(self, mock_get):
        mock_get.side_effect = requests.Timeout("Request timed out")

        connector = APIConnector()
        with pytest.raises(ConnectionError) as excinfo:
            connector.connect("http://test.com", {"param": "value"})
        assert "Timeout error" in str(excinfo.value)

    @patch('requests.get')
    def test_http_error_handling(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"

        http_error = requests.HTTPError("404 Not Found", response=mock_response)
        mock_response.raise_for_status.side_effect = http_error

        mock_get.return_value = mock_response

        connector = APIConnector()
        with pytest.raises(ConnectionError) as excinfo:
            connector.connect("http://test.com", {"param": "value"})
        assert "HTTP error 404" in str(excinfo.value)

    @patch('requests.get')
    def test_request_exception_handling(self, mock_get):
        mock_get.side_effect = requests.RequestException("Some request error")

        connector = APIConnector()
        with pytest.raises(ConnectionError) as excinfo:
            connector.connect("http://test.com", {"param": "value"})
        assert "Connection error: Some request error" in str(excinfo.value)

    @patch('requests.get')
    def test_json_decode_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        connector = APIConnector()
        with pytest.raises(ConnectionError) as excinfo:
            connector.connect("http://test.com", {"param": "value"})
        assert "JSON decode error" in str(excinfo.value)

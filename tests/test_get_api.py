import pytest
import requests
from src.api_modules.get_api import APIConnector
from src.config.api_config import APIConfig


def test_success(mocker):
    """Тест успешного запроса"""
    mock_get = mocker.patch('requests.get')
    mock_get.return_value.json.return_value = {'data': 'success'}
    mock_get.return_value.status_code = 200

    connector = APIConnector(APIConfig())
    result = connector.connect("http://test.com", {})
    assert result == {'data': 'success'}


def test_retry(mocker):
    """Тест повторного запроса после 429"""
    mock_get = mocker.patch('requests.get')
    mock_get.side_effect = [
        mocker.Mock(status_code=429, headers={'Retry-After': '1'}),
        mocker.Mock(status_code=200, json=lambda: {'data': 'retry'})
    ]
    mocker.patch('time.sleep')

    connector = APIConnector(APIConfig())
    result = connector.connect("http://test.com", {})
    assert result == {'data': 'retry'}


def test_timeout(mocker):
    """Тест таймаута"""
    mocker.patch('requests.get', side_effect=requests.Timeout())

    connector = APIConnector(APIConfig())
    with pytest.raises(ConnectionError) as e:
        connector.connect("http://test.com", {})
    assert "Timeout error" in str(e.value)


def test_http_error(mocker):
    """Тест HTTP ошибки"""
    mock_resp = mocker.Mock(status_code=500, text="Server Error")
    mock_resp.raise_for_status.side_effect = requests.HTTPError(response=mock_resp)
    mocker.patch('requests.get', return_value=mock_resp)

    connector = APIConnector(APIConfig())
    with pytest.raises(ConnectionError) as e:
        connector.connect("http://test.com", {})
    assert "HTTP error 500" in str(e.value)
    assert "Server Error" in str(e.value)

def test_http_error_with_and_without_text(mocker):
    """Тест обработки HTTP ошибок с текстом и без текста ответа"""
    # Случай 1: Ошибка с текстом ответа
    mock_response_with_text = mocker.Mock()
    mock_response_with_text.status_code = 404
    mock_response_with_text.text = "Resource not found"
    http_error_with_text = requests.HTTPError()
    http_error_with_text.response = mock_response_with_text
    mock_response_with_text.raise_for_status.side_effect = http_error_with_text

    mocker.patch('requests.get', return_value=mock_response_with_text)

    connector = APIConnector(APIConfig())
    with pytest.raises(ConnectionError) as excinfo:
        connector.connect("http://test.com", {})
    assert "HTTP error 404" in str(excinfo.value)
    assert "Resource not found" in str(excinfo.value)

    # Случай 2: Ошибка без текста ответа
    mock_response_no_text = mocker.Mock()
    mock_response_no_text.status_code = 500
    mock_response_no_text.text = ""
    http_error_no_text = requests.HTTPError()
    http_error_no_text.response = mock_response_no_text
    mock_response_no_text.raise_for_status.side_effect = http_error_no_text

    mocker.patch('requests.get', return_value=mock_response_no_text)

    with pytest.raises(ConnectionError) as excinfo:
        connector.connect("http://test.com", {})
    assert "HTTP error 500" in str(excinfo.value)
    assert ":" not in str(excinfo.value)  # Не должно быть двоеточия, если нет текста


def test_http_error_no_text(mocker):
    """Тест HTTP ошибки без текста"""
    mock_response = mocker.Mock()
    mock_response.status_code = 500
    mock_response.text = ""
    mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)
    mocker.patch('requests.get', return_value=mock_response)

    with pytest.raises(ConnectionError) as e:
        APIConnector(APIConfig()).connect("http://test.com", {})

    assert "HTTP error 500" in str(e.value)
    assert ":" not in str(e.value)  # Проверяем что нет двоеточия если нет текста


def test_http_error_without_response(mocker):
    """Тест HTTP ошибки без response"""
    # Создаем HTTPError без response
    http_error = requests.HTTPError()
    http_error.response = None

    mock_get = mocker.patch('requests.get')
    mock_response = mocker.Mock()
    mock_response.raise_for_status.side_effect = http_error
    mock_get.return_value = mock_response

    with pytest.raises(ConnectionError) as e:
        APIConnector(APIConfig()).connect("http://test.com", {})

    assert "HTTP error (no response details)" in str(e.value)


def test_request_exception(mocker):
    """Тест общего исключения запроса"""
    mock_get = mocker.patch('requests.get')
    mock_get.side_effect = requests.RequestException("Test request error")

    with pytest.raises(ConnectionError) as e:
        APIConnector(APIConfig()).connect("http://test.com", {})

    assert "Connection error: Test request error" in str(e.value)


def test_json_decode_error(mocker):
    """Тест ошибки декодирования JSON"""
    mock_get = mocker.patch('requests.get')
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_get.return_value = mock_response

    with pytest.raises(ConnectionError) as e:
        APIConnector(APIConfig()).connect("http://test.com", {})

    assert "JSON decode error: Invalid JSON" in str(e.value)
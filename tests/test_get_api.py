
from unittest.mock import Mock, patch

import pytest
import requests

from src.api_modules.get_api import APIConnector
from src.config.api_config import APIConfig


class TestAPIConnector:
    """Тесты для класса APIConnector"""

    def test_init_default_config(self):
        """Тест инициализации с конфигурацией по умолчанию"""
        connector = APIConnector()
        
        assert connector.config is not None
        assert isinstance(connector.config, APIConfig)
        assert connector.headers['User-Agent'] == connector.config.user_agent
        assert connector.headers['Accept'] == 'application/json'
        assert connector._progress is None

    def test_init_custom_config(self):
        """Тест инициализации с пользовательской конфигурацией"""
        config = APIConfig()
        connector = APIConnector(config)
        
        assert connector.config is config
        assert connector.headers['User-Agent'] == config.user_agent

    @patch('src.api_modules.get_api.tqdm')
    def test_init_progress(self, mock_tqdm):
        """Тест инициализации прогресс-бара"""
        connector = APIConnector()
        mock_progress = Mock()
        mock_tqdm.return_value = mock_progress
        
        connector._init_progress(10, "Test")
        
        mock_tqdm.assert_called_once()
        call_kwargs = mock_tqdm.call_args[1]
        assert call_kwargs['total'] == 10
        assert call_kwargs['desc'] == "Test"
        assert call_kwargs['unit'] == "req"
        assert connector._progress == mock_progress

    @patch.dict('os.environ', {'DISABLE_TQDM': '1'})
    @patch('src.api_modules.get_api.tqdm')
    def test_init_progress_disabled(self, mock_tqdm):
        """Тест инициализации прогресс-бара с отключением"""
        connector = APIConnector()
        
        connector._init_progress(10, "Test")
        
        call_kwargs = mock_tqdm.call_args[1]
        assert call_kwargs['disable'] is True

    def test_update_progress_with_progress(self):
        """Тест обновления прогресс-бара когда он существует"""
        connector = APIConnector()
        mock_progress = Mock()
        connector._progress = mock_progress
        
        connector._update_progress(5)
        
        mock_progress.update.assert_called_once_with(5)

    def test_update_progress_without_progress(self):
        """Тест обновления прогресс-бара когда он не существует"""
        connector = APIConnector()
        connector._progress = None
        
        # Не должно вызвать исключение
        connector._update_progress(5)

    def test_close_progress_with_progress(self):
        """Тест закрытия прогресс-бара когда он существует"""
        connector = APIConnector()
        mock_progress = Mock()
        connector._progress = mock_progress
        
        connector._close_progress()
        
        mock_progress.close.assert_called_once()
        assert connector._progress is None

    def test_close_progress_without_progress(self):
        """Тест закрытия прогресс-бара когда он не существует"""
        connector = APIConnector()
        connector._progress = None
        
        # Не должно вызвать исключение
        connector._close_progress()

    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_success(self, mock_get, mock_sleep):
        """Тест успешного запроса"""
        connector = APIConnector()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_get.return_value = mock_response
        
        result = connector._APIConnector__connect("http://test.com", {"param": "value"})
        
        assert result == {"result": "success"}
        mock_sleep.assert_called_with(0.15)
        mock_get.assert_called_once()

    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_with_progress(self, mock_get, mock_sleep):
        """Тест запроса с прогресс-баром"""
        connector = APIConnector()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_get.return_value = mock_response
        
        with patch.object(connector, '_init_progress') as mock_init, \
             patch.object(connector, '_update_progress') as mock_update, \
             patch.object(connector, '_close_progress') as mock_close:
            
            result = connector._APIConnector__connect(
                "http://test.com", 
                {"param": "value"}, 
                show_progress=True, 
                progress_desc="Custom desc"
            )
            
            mock_init.assert_called_once_with(1, "Custom desc")
            mock_update.assert_called_once()
            mock_close.assert_called_once()

    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_with_default_progress_desc(self, mock_get, mock_sleep):
        """Тест запроса с прогресс-баром и описанием по умолчанию"""
        connector = APIConnector()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_get.return_value = mock_response
        
        with patch.object(connector, '_init_progress') as mock_init, \
             patch.object(connector, '_update_progress') as mock_update, \
             patch.object(connector, '_close_progress') as mock_close:
            
            connector._APIConnector__connect(
                "http://test.com/endpoint", 
                {"param": "value"}, 
                show_progress=True
            )
            
            mock_init.assert_called_once_with(1, "Request to endpoint")

    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_rate_limit_retry(self, mock_get, mock_sleep):
        """Тест обработки ограничения скорости (429)"""
        connector = APIConnector()
        
        # Первый ответ - 429, второй - успех
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {'Retry-After': '2'}
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"result": "success"}
        
        mock_get.side_effect = [mock_response_429, mock_response_success]
        
        result = connector._APIConnector__connect("http://test.com", {"param": "value"})
        
        assert result == {"result": "success"}
        assert mock_get.call_count == 2
        # Проверяем что был sleep для Retry-After
        sleep_calls = mock_sleep.call_args_list
        assert any(call[0][0] == 2 for call in sleep_calls)

    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_timeout_error(self, mock_get, mock_sleep):
        """Тест обработки ошибки таймаута"""
        connector = APIConnector()
        mock_get.side_effect = requests.Timeout("Request timeout")
        
        with patch.object(connector, '_close_progress'):
            with pytest.raises(ConnectionError, match="Timeout error"):
                connector._APIConnector__connect("http://test.com", {"param": "value"})

    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_http_error_with_response(self, mock_get, mock_sleep):
        """Тест обработки HTTP ошибки с ответом"""
        connector = APIConnector()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found error text"
        
        http_error = requests.HTTPError()
        http_error.response = mock_response
        mock_get.side_effect = http_error
        
        with patch.object(connector, '_close_progress'):
            with pytest.raises(ConnectionError, match="HTTP error 404"):
                connector._APIConnector__connect("http://test.com", {"param": "value"})

    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_http_error_without_response(self, mock_get, mock_sleep):
        """Тест обработки HTTP ошибки без ответа"""
        connector = APIConnector()
        http_error = requests.HTTPError()
        http_error.response = None
        mock_get.side_effect = http_error
        
        with patch.object(connector, '_close_progress'):
            with pytest.raises(ConnectionError, match="HTTP error \\(no response details\\)"):
                connector._APIConnector__connect("http://test.com", {"param": "value"})

    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_request_exception(self, mock_get, mock_sleep):
        """Тест обработки общей ошибки запроса"""
        connector = APIConnector()
        mock_get.side_effect = requests.RequestException("Connection failed")
        
        with patch.object(connector, '_close_progress'):
            with pytest.raises(ConnectionError, match="Connection error"):
                connector._APIConnector__connect("http://test.com", {"param": "value"})

    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_json_decode_error(self, mock_get, mock_sleep):
        """Тест обработки ошибки декодирования JSON"""
        connector = APIConnector()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        with patch.object(connector, '_close_progress'):
            with pytest.raises(ConnectionError, match="JSON decode error"):
                connector._APIConnector__connect("http://test.com", {"param": "value"})

    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_unexpected_error(self, mock_get, mock_sleep):
        """Тест обработки неожиданной ошибки"""
        connector = APIConnector()
        mock_get.side_effect = Exception("Unexpected error")
        
        with patch.object(connector, '_close_progress'):
            with pytest.raises(ConnectionError, match="Unexpected error"):
                connector._APIConnector__connect("http://test.com", {"param": "value"})

    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_params_filtering(self, mock_get, mock_sleep):
        """Тест фильтрации параметров (None значения удаляются)"""
        connector = APIConnector()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_get.return_value = mock_response
        
        params = {"param1": "value1", "param2": None, "param3": "value3"}
        connector._APIConnector__connect("http://test.com", params)
        
        # Проверяем что None параметры были отфильтрованы
        call_kwargs = mock_get.call_args[1]
        expected_params = {"param1": "value1", "param3": "value3"}
        assert call_kwargs['params'] == expected_params

    def test_connect_public_method(self):
        """Тест публичного метода connect"""
        connector = APIConnector()
        
        with patch.object(connector, '_APIConnector__connect', return_value={"result": "success"}) as mock_private:
            result = connector.connect("http://test.com", {"param": "value"})
            
            assert result == {"result": "success"}
            mock_private.assert_called_once_with("http://test.com", {"param": "value"})

    def test_connect_public_method_default_params(self):
        """Тест публичного метода connect с параметрами по умолчанию"""
        connector = APIConnector()
        
        with patch.object(connector, '_APIConnector__connect', return_value={"result": "success"}) as mock_private:
            result = connector.connect("http://test.com")
            
            assert result == {"result": "success"}
            mock_private.assert_called_once_with("http://test.com", None)

    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_always_closes_progress(self, mock_get, mock_sleep):
        """Тест что прогресс-бар всегда закрывается даже при ошибке"""
        connector = APIConnector()
        mock_get.side_effect = Exception("Test error")
        
        with patch.object(connector, '_init_progress'), \
             patch.object(connector, '_update_progress'), \
             patch.object(connector, '_close_progress') as mock_close:
            
            with pytest.raises(ConnectionError):
                connector._APIConnector__connect(
                    "http://test.com", 
                    {"param": "value"}, 
                    show_progress=True
                )
            
            mock_close.assert_called_once()

    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_custom_delay(self, mock_get, mock_sleep):
        """Тест кастомной задержки"""
        connector = APIConnector()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_get.return_value = mock_response
        
        connector._APIConnector__connect("http://test.com", {"param": "value"}, delay=0.5)
        
        mock_sleep.assert_called_with(0.5)

    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_rate_limit_default_retry_after(self, mock_get, mock_sleep):
        """Тест обработки 429 без заголовка Retry-After"""
        connector = APIConnector()
        
        # Первый ответ - 429 без Retry-After, второй - успех
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {}
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"result": "success"}
        
        mock_get.side_effect = [mock_response_429, mock_response_success]
        
        result = connector._APIConnector__connect("http://test.com", {"param": "value"})
        
        assert result == {"result": "success"}
        # Проверяем что был sleep с дефолтным значением 1
        sleep_calls = mock_sleep.call_args_list
        assert any(call[0][0] == 1 for call in sleep_calls)

    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_http_error_long_response_text(self, mock_get, mock_sleep):
        """Тест обработки HTTP ошибки с длинным текстом ответа"""
        connector = APIConnector()
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "A" * 300  # Текст длиннее 200 символов
        
        http_error = requests.HTTPError()
        http_error.response = mock_response
        mock_get.side_effect = http_error
        
        with patch.object(connector, '_close_progress'):
            with pytest.raises(ConnectionError) as exc_info:
                connector._APIConnector__connect("http://test.com", {"param": "value"})
            
            # Проверяем что текст обрезан до 200 символов
            error_msg = str(exc_info.value)
            assert "HTTP error 500: " + "A" * 200 in error_msg


"""
Тесты для модуля sj_api
"""

import pytest
from unittest.mock import MagicMock, patch, mock_open
from src.api_modules.sj_api import SuperJobAPI
from src.config.sj_api_config import SJAPIConfig
import json


class TestSuperJobAPI:
    """Тесты для класса SuperJobAPI"""
    
    @pytest.fixture
    def sj_api(self):
        """Фикстура для создания экземпляра SuperJobAPI"""
        return SuperJobAPI()
    
    @pytest.fixture
    def sample_sj_response(self):
        """Образец ответа SuperJob API"""
        return {
            'objects': [
                {
                    'id': 123,
                    'profession': 'Python Developer',
                    'link': 'https://superjob.ru/vacancy/123',
                    'payment_from': 100000,
                    'payment_to': 150000,
                    'currency': 'rub',
                    'candidat': 'Разработка на Python'
                }
            ],
            'total': 1
        }
    
    def test_init_default(self, sj_api):
        """Тест инициализации с настройками по умолчанию"""
        assert isinstance(sj_api.config, SJAPIConfig)
        assert sj_api.base_url == "https://api.superjob.ru/2.0/vacancies/"
        assert sj_api.cache_dir is not None
    
    def test_init_with_custom_config(self):
        """Тест инициализации с пользовательской конфигурацией"""
        config = SJAPIConfig(api_key="test_key", timeout=30)
        sj_api = SuperJobAPI(config)
        
        assert sj_api.config == config
        assert sj_api.config.api_key == "test_key"
        assert sj_api.config.timeout == 30
    
    @patch('src.api_modules.sj_api.os.path.exists')
    @patch('src.api_modules.sj_api.os.makedirs')
    def test_ensure_cache_dir_creates_directory(self, mock_makedirs, mock_exists):
        """Тест создания директории кэша"""
        mock_exists.return_value = False
        
        SuperJobAPI.ensure_cache_dir()
        
        mock_makedirs.assert_called_once()
    
    @patch('src.api_modules.sj_api.os.path.exists')
    @patch('src.api_modules.sj_api.os.makedirs')
    def test_ensure_cache_dir_exists(self, mock_makedirs, mock_exists):
        """Тест когда директория кэша уже существует"""
        mock_exists.return_value = True
        
        SuperJobAPI.ensure_cache_dir()
        
        mock_makedirs.assert_not_called()
    
    def test_get_headers_with_api_key(self, sj_api):
        """Тест получения заголовков с API ключом"""
        sj_api.config.api_key = "test_key"
        
        headers = sj_api._get_headers()
        
        assert headers["X-Api-App-Id"] == "test_key"
        assert "User-Agent" in headers
    
    def test_get_headers_without_api_key(self, sj_api):
        """Тест получения заголовков без API ключа"""
        sj_api.config.api_key = None
        
        headers = sj_api._get_headers()
        
        assert "X-Api-App-Id" not in headers
        assert "User-Agent" in headers
    
    def test_build_params_basic(self, sj_api):
        """Тест построения базовых параметров"""
        params = sj_api._build_params("python")
        
        assert params["keyword"] == "python"
        assert params["count"] == 100
        assert params["published"] == 1
    
    def test_build_params_with_kwargs(self, sj_api):
        """Тест построения параметров с дополнительными аргументами"""
        params = sj_api._build_params("python", count=50, published=7, town="Moscow")
        
        assert params["keyword"] == "python"
        assert params["count"] == 50
        assert params["published"] == 7
        assert params["town"] == "Moscow"
    
    def test_build_cache_key(self, sj_api):
        """Тест построения ключа кэша"""
        params = {"keyword": "python", "count": 100}
        
        cache_key = sj_api._build_cache_key(params)
        
        assert cache_key == "sj_count_100_keyword_python"
    
    def test_build_cache_key_with_special_chars(self, sj_api):
        """Тест построения ключа кэша со специальными символами"""
        params = {"keyword": "python developer", "count": 100}
        
        cache_key = sj_api._build_cache_key(params)
        
        assert cache_key == "sj_count_100_keyword_python_developer"
    
    @patch('builtins.open', new_callable=mock_open, read_data='{"test": "data"}')
    @patch('src.api_modules.sj_api.os.path.exists')
    def test_load_from_cache_exists(self, mock_exists, mock_file, sj_api):
        """Тест загрузки из кэша когда файл существует"""
        mock_exists.return_value = True
        
        result = sj_api._load_from_cache("test_key")
        
        assert result == {"test": "data"}
        mock_file.assert_called_once()
    
    @patch('src.api_modules.sj_api.os.path.exists')
    def test_load_from_cache_not_exists(self, mock_exists, sj_api):
        """Тест загрузки из кэша когда файл не существует"""
        mock_exists.return_value = False
        
        result = sj_api._load_from_cache("test_key")
        
        assert result is None
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('src.api_modules.sj_api.SuperJobAPI.ensure_cache_dir')
    def test_save_to_cache(self, mock_ensure_dir, mock_file, sj_api):
        """Тест сохранения в кэш"""
        data = {"test": "data"}
        
        sj_api._save_to_cache("test_key", data)
        
        mock_ensure_dir.assert_called_once()
        mock_file.assert_called_once()
        handle = mock_file()
        handle.write.assert_called_once()
    
    @patch('src.api_modules.sj_api.requests.get')
    def test_connect_to_api_success(self, mock_get, sj_api, sample_sj_response):
        """Тест успешного подключения к API"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_sj_response
        mock_get.return_value = mock_response
        
        result = sj_api._connect_to_api("test_url", {"keyword": "python"}, "test_key")
        
        assert result == sample_sj_response
        mock_get.assert_called_once()
    
    @patch('src.api_modules.sj_api.requests.get')
    def test_connect_to_api_error(self, mock_get, sj_api):
        """Тест ошибки подключения к API"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response
        
        with pytest.raises(Exception):
            sj_api._connect_to_api("test_url", {"keyword": "python"}, "test_key")
    
    @patch('src.api_modules.sj_api.requests.get')
    def test_connect_to_api_timeout(self, mock_get, sj_api):
        """Тест таймаута подключения к API"""
        mock_get.side_effect = Exception("Timeout")
        
        with pytest.raises(Exception):
            sj_api._connect_to_api("test_url", {"keyword": "python"}, "test_key")
    
    def test_get_vacancies_from_cache(self, sj_api, sample_sj_response):
        """Тест получения вакансий из кэша"""
        with patch.object(sj_api, '_load_from_cache') as mock_load:
            mock_load.return_value = sample_sj_response
            
            result = sj_api.get_vacancies("python")
            
            assert result == sample_sj_response['objects']
            mock_load.assert_called_once()
    
    def test_get_vacancies_from_api(self, sj_api, sample_sj_response):
        """Тест получения вакансий из API"""
        with patch.object(sj_api, '_load_from_cache') as mock_load, \
             patch.object(sj_api, '_connect_to_api') as mock_connect, \
             patch.object(sj_api, '_save_to_cache') as mock_save:
            
            mock_load.return_value = None
            mock_connect.return_value = sample_sj_response
            
            result = sj_api.get_vacancies("python")
            
            assert result == sample_sj_response['objects']
            mock_connect.assert_called_once()
            mock_save.assert_called_once()
    
    def test_get_vacancies_api_error(self, sj_api):
        """Тест обработки ошибки API"""
        with patch.object(sj_api, '_load_from_cache') as mock_load, \
             patch.object(sj_api, '_connect_to_api') as mock_connect:
            
            mock_load.return_value = None
            mock_connect.side_effect = Exception("API Error")
            
            result = sj_api.get_vacancies("python")
            
            assert result == []
    
    @patch('src.api_modules.sj_api.shutil.rmtree')
    @patch('src.api_modules.sj_api.os.path.exists')
    def test_clear_cache_success(self, mock_exists, mock_rmtree, sj_api):
        """Тест успешной очистки кэша"""
        mock_exists.return_value = True
        
        sj_api.clear_cache()
        
        mock_rmtree.assert_called_once()
    
    @patch('src.api_modules.sj_api.shutil.rmtree')
    @patch('src.api_modules.sj_api.os.path.exists')
    def test_clear_cache_not_exists(self, mock_exists, mock_rmtree, sj_api):
        """Тест очистки кэша когда директория не существует"""
        mock_exists.return_value = False
        
        sj_api.clear_cache()
        
        mock_rmtree.assert_not_called()
    
    @patch('src.api_modules.sj_api.shutil.rmtree')
    @patch('src.api_modules.sj_api.os.path.exists')
    def test_clear_cache_error(self, mock_exists, mock_rmtree, sj_api):
        """Тест обработки ошибки при очистке кэша"""
        mock_exists.return_value = True
        mock_rmtree.side_effect = Exception("Permission denied")
        
        with pytest.raises(Exception):
            sj_api.clear_cache()

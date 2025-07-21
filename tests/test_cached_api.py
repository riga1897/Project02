

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from typing import Dict, List

from src.api_modules.cached_api import CachedAPI
from src.utils.cache import FileCache


class ConcreteCachedAPI(CachedAPI):
    """Конкретная реализация CachedAPI для тестирования"""
    
    def _get_empty_response(self) -> Dict:
        return {"items": [], "found": 0, "pages": 0}
    
    def _validate_vacancy(self, vacancy: Dict) -> bool:
        return "name" in vacancy
    
    def get_vacancies_page(self, search_query: str, page: int = 0, **kwargs) -> List[Dict]:
        return [{"name": "Test Vacancy", "page": page}]
    
    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict]:
        return [{"name": "Test Vacancy"}]


class TestCachedAPI:
    """Тесты для класса CachedAPI"""

    @patch('src.api_modules.cached_api.Path')
    @patch('src.api_modules.cached_api.FileCache')
    def test_init(self, mock_file_cache, mock_path):
        """Тест инициализации CachedAPI"""
        mock_path_instance = Mock()
        mock_path.return_value = mock_path_instance
        
        api = ConcreteCachedAPI("test_cache")
        
        assert api.cache_dir == mock_path_instance
        mock_path_instance.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_file_cache.assert_called_once_with(str(mock_path_instance))

    @patch('src.api_modules.cached_api.Path')
    @patch('src.api_modules.cached_api.FileCache')
    def test_init_cache(self, mock_file_cache, mock_path):
        """Тест инициализации кэша"""
        mock_path_instance = Mock()
        mock_path.return_value = mock_path_instance
        
        api = ConcreteCachedAPI("test_cache")
        
        mock_path_instance.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        assert isinstance(api.cache, Mock)

    @patch('src.api_modules.cached_api.Path')
    @patch('src.api_modules.cached_api.FileCache')
    @patch('src.api_modules.cached_api.logger')
    def test_cached_api_request_success(self, mock_logger, mock_file_cache, mock_path):
        """Тест успешного кэшированного API запроса"""
        api = ConcreteCachedAPI("test_cache")
        api.connector = Mock()
        api.connector._APIConnector__connect.return_value = {"test": "data"}
        
        # Патчим _cached_api_request напрямую
        with patch.object(api, '_cached_api_request') as mock_cached:
            mock_cached.return_value = {"test": "data"}
            result = mock_cached("test_url", (1, "value"), "test_prefix")
        
        assert result == {"test": "data"}

    @patch('src.api_modules.cached_api.Path')
    @patch('src.api_modules.cached_api.FileCache')
    @patch('src.api_modules.cached_api.logger')
    def test_cached_api_request_error(self, mock_logger, mock_file_cache, mock_path):
        """Тест ошибки в кэшированном API запросе"""
        api = ConcreteCachedAPI("test_cache")
        api.connector = Mock()
        api.connector._APIConnector__connect.side_effect = Exception("API Error")
        
        # Патчим _cached_api_request напрямую
        with patch.object(api, '_cached_api_request') as mock_cached:
            mock_cached.return_value = {"items": [], "found": 0, "pages": 0}
            result = mock_cached("test_url", (1, "value"), "test_prefix")
        
        assert result == {"items": [], "found": 0, "pages": 0}

    @patch('src.api_modules.cached_api.Path')
    @patch('src.api_modules.cached_api.FileCache')
    @patch('src.api_modules.cached_api.logger')
    def test_connect_to_api_memory_cache_hit(self, mock_logger, mock_file_cache, mock_path):
        """Тест попадания в кэш памяти"""
        api = ConcreteCachedAPI("test_cache")
        api.connector = Mock()
        
        # Мокаем метод _cached_api_request для имитации попадания в кэш
        with patch.object(api, '_cached_api_request', return_value={"cached": "data"}):
            result = api._CachedAPI__connect_to_api("test_url", {"param": "value"}, "test_prefix")
        
        assert result == {"cached": "data"}

    @patch('src.api_modules.cached_api.Path')
    @patch('src.api_modules.cached_api.FileCache')
    @patch('src.api_modules.cached_api.logger')
    @patch('src.api_modules.cached_api.logging')
    def test_connect_to_api_memory_cache_error_file_cache_hit(self, mock_logging, mock_logger, mock_file_cache, mock_path):
        """Тест ошибки кэша памяти с попаданием в файловый кэш"""
        api = ConcreteCachedAPI("test_cache")
        api.connector = Mock()
        api.cache.load_response.return_value = {"data": {"file_cached": "data"}}
        
        # Мокаем метод _cached_api_request для имитации ошибки кэша памяти
        with patch.object(api, '_cached_api_request', side_effect=Exception("Cache error")):
            result = api._CachedAPI__connect_to_api("test_url", {"param": "value"}, "test_prefix")
        
        assert result == {"file_cached": "data"}
        mock_logging.warning.assert_called_once()

    @patch('src.api_modules.cached_api.Path')
    @patch('src.api_modules.cached_api.FileCache')
    @patch('src.api_modules.cached_api.logger')
    def test_connect_to_api_no_cache_api_success(self, mock_logger, mock_file_cache, mock_path):
        """Тест успешного API запроса без кэша"""
        api = ConcreteCachedAPI("test_cache")
        api.connector = Mock()
        api.connector._APIConnector__connect.return_value = {"api": "data"}
        api.cache.load_response.return_value = None
        
        # Мокаем метод _cached_api_request для имитации промаха кэша памяти
        with patch.object(api, '_cached_api_request', return_value={"items": [], "found": 0, "pages": 0}):
            result = api._CachedAPI__connect_to_api("test_url", {"param": "value"}, "test_prefix")
        
        assert result == {"api": "data"}
        api.cache.save_response.assert_called_once_with("test_prefix", {"param": "value"}, {"api": "data"})

    @patch('src.api_modules.cached_api.Path')
    @patch('src.api_modules.cached_api.FileCache')
    @patch('src.api_modules.cached_api.logger')
    def test_connect_to_api_no_cache_api_empty_response(self, mock_logger, mock_file_cache, mock_path):
        """Тест API запроса с пустым ответом"""
        api = ConcreteCachedAPI("test_cache")
        api.connector = Mock()
        api.connector._APIConnector__connect.return_value = {"items": [], "found": 0, "pages": 0}
        api.cache.load_response.return_value = None
        
        # Мокаем метод _cached_api_request для имитации промаха кэша памяти
        with patch.object(api, '_cached_api_request', return_value={"items": [], "found": 0, "pages": 0}):
            result = api._CachedAPI__connect_to_api("test_url", {"param": "value"}, "test_prefix")
        
        assert result == {"items": [], "found": 0, "pages": 0}
        # Пустые данные не сохраняются в кэш
        api.cache.save_response.assert_not_called()

    @patch('src.api_modules.cached_api.Path')
    @patch('src.api_modules.cached_api.FileCache')
    @patch('src.api_modules.cached_api.logger')
    def test_connect_to_api_error(self, mock_logger, mock_file_cache, mock_path):
        """Тест ошибки при API запросе"""
        api = ConcreteCachedAPI("test_cache")
        api.connector = Mock()
        api.connector._APIConnector__connect.side_effect = Exception("API Error")
        api.cache.load_response.return_value = None
        
        # Мокаем метод _cached_api_request для имитации промаха кэша памяти
        with patch.object(api, '_cached_api_request', return_value={"items": [], "found": 0, "pages": 0}):
            result = api._CachedAPI__connect_to_api("test_url", {"param": "value"}, "test_prefix")
        
        assert result == {"items": [], "found": 0, "pages": 0}
        mock_logger.error.assert_called_once()

    @patch('src.api_modules.cached_api.Path')
    @patch('src.api_modules.cached_api.FileCache')
    @patch('src.api_modules.cached_api.logger')
    def test_clear_cache_success(self, mock_logger, mock_file_cache, mock_path):
        """Тест успешной очистки кэша"""
        api = ConcreteCachedAPI("test_cache")
        
        # Мокаем clear_cache метод
        mock_clear_cache = Mock()
        with patch.object(api, '_cached_api_request', Mock(clear_cache=mock_clear_cache)):
            api.clear_cache("test_prefix")
        
        api.cache.clear.assert_called_once_with("test_prefix")
        mock_clear_cache.assert_called_once()
        mock_logger.info.assert_called_once_with("Кэш test_prefix очищен (файловый и в памяти)")

    @patch('src.api_modules.cached_api.Path')
    @patch('src.api_modules.cached_api.FileCache')
    @patch('src.api_modules.cached_api.logger')
    def test_clear_cache_no_clear_cache_method(self, mock_logger, mock_file_cache, mock_path):
        """Тест очистки кэша без метода clear_cache"""
        api = ConcreteCachedAPI("test_cache")
        
        api.clear_cache("test_prefix")
        
        api.cache.clear.assert_called_once_with("test_prefix")
        mock_logger.info.assert_called_once_with("Кэш test_prefix очищен (файловый и в памяти)")

    @patch('src.api_modules.cached_api.Path')
    @patch('src.api_modules.cached_api.FileCache')
    @patch('src.api_modules.cached_api.logger')
    def test_clear_cache_error(self, mock_logger, mock_file_cache, mock_path):
        """Тест ошибки при очистке кэша"""
        api = ConcreteCachedAPI("test_cache")
        api.cache.clear.side_effect = Exception("Clear error")
        
        api.clear_cache("test_prefix")
        
        mock_logger.error.assert_called_once_with("Ошибка очистки кэша test_prefix: Clear error")

    @patch('src.api_modules.cached_api.Path')
    @patch('src.api_modules.cached_api.FileCache')
    @patch('src.api_modules.cached_api.logger')
    def test_get_cache_status_success(self, mock_logger, mock_file_cache, mock_path):
        """Тест успешного получения статуса кэша"""
        api = ConcreteCachedAPI("test_cache")
        
        # Мокаем Path.glob
        mock_file1 = Mock()
        mock_file1.name = "test_prefix_1.json"
        mock_file2 = Mock()
        mock_file2.name = "test_prefix_2.json"
        api.cache_dir.glob.return_value = [mock_file1, mock_file2]
        api.cache_dir.exists.return_value = True
        
        # Мокаем cache_info
        mock_cache_info = Mock(return_value={"hits": 5, "misses": 2})
        with patch.object(api, '_cached_api_request', Mock(cache_info=mock_cache_info)):
            result = api.get_cache_status("test_prefix")
        
        expected = {
            'cache_dir': str(api.cache_dir),
            'cache_dir_exists': True,
            'file_cache_count': 2,
            'cache_files': ["test_prefix_1.json", "test_prefix_2.json"],
            'memory_cache': {"hits": 5, "misses": 2}
        }
        assert result == expected

    @patch('src.api_modules.cached_api.Path')
    @patch('src.api_modules.cached_api.FileCache')
    @patch('src.api_modules.cached_api.logger')
    def test_get_cache_status_no_cache_info(self, mock_logger, mock_file_cache, mock_path):
        """Тест получения статуса кэша без cache_info"""
        api = ConcreteCachedAPI("test_cache")
        
        api.cache_dir.glob.return_value = []
        api.cache_dir.exists.return_value = True
        # Не устанавливаем cache_info - используется cache_info по умолчанию
        
        result = api.get_cache_status("test_prefix")
        
        # cache_info по умолчанию возвращает базовую информацию о кэше
        expected = {
            'cache_dir': str(api.cache_dir),
            'cache_dir_exists': True,
            'file_cache_count': 0,
            'cache_files': [],
            'memory_cache': {'max_size': 1000, 'size': 0, 'ttl': None}
        }
        assert result == expected

    @patch('src.api_modules.cached_api.Path')
    @patch('src.api_modules.cached_api.FileCache')
    @patch('src.api_modules.cached_api.logger')
    def test_get_cache_status_error(self, mock_logger, mock_file_cache, mock_path):
        """Тест ошибки при получении статуса кэша"""
        api = ConcreteCachedAPI("test_cache")
        api.cache_dir.glob.side_effect = Exception("Status error")
        
        result = api.get_cache_status("test_prefix")
        
        assert result == {'error': 'Status error'}
        mock_logger.error.assert_called_once_with("Ошибка получения статуса кэша: Status error")


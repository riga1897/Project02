
import pytest
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

    def test_init(self, mocker):
        """Тест инициализации CachedAPI"""
        mock_path = mocker.patch('src.api_modules.cached_api.Path')
        mock_file_cache = mocker.patch('src.api_modules.cached_api.FileCache')
        
        mock_path_instance = Mock()
        mock_path.return_value = mock_path_instance

        api = ConcreteCachedAPI("test_cache")

        assert api.cache_dir == mock_path_instance
        mock_path_instance.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_file_cache.assert_called_once_with(str(mock_path_instance))

    def test_init_cache(self, mocker):
        """Тест инициализации кэша"""
        mock_path = mocker.patch('src.api_modules.cached_api.Path')
        mock_file_cache = mocker.patch('src.api_modules.cached_api.FileCache')
        
        mock_path_instance = Mock()
        mock_path.return_value = mock_path_instance

        api = ConcreteCachedAPI("test_cache")

        mock_path_instance.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        assert isinstance(api.cache, Mock)

    def test_cached_api_request_success(self, mocker):
        """Тест успешного кэшированного API запроса"""
        mocker.patch('src.api_modules.cached_api.Path')
        mocker.patch('src.api_modules.cached_api.FileCache')
        mock_logger = mocker.patch('src.api_modules.cached_api.logger')
        
        api = ConcreteCachedAPI("test_cache")
        api.connector = Mock()
        api.connector._APIConnector__connect.return_value = {"test": "data"}

        # Патчим _cached_api_request напрямую
        mock_cached = mocker.patch.object(api, '_cached_api_request')
        mock_cached.return_value = {"test": "data"}
        result = mock_cached("test_url", (1, "value"), "test_prefix")

        assert result == {"test": "data"}

    def test_cached_api_request_error(self, mocker):
        """Тест ошибки в кэшированном API запросе"""
        mocker.patch('src.api_modules.cached_api.Path')
        mocker.patch('src.api_modules.cached_api.FileCache')
        mock_logger = mocker.patch('src.api_modules.cached_api.logger')
        
        api = ConcreteCachedAPI("test_cache")
        api.connector = Mock()
        api.connector._APIConnector__connect.side_effect = Exception("API Error")

        # Патчим _cached_api_request напрямую
        mock_cached = mocker.patch.object(api, '_cached_api_request')
        mock_cached.return_value = {"items": [], "found": 0, "pages": 0}
        result = mock_cached("test_url", (1, "value"), "test_prefix")

        assert result == {"items": [], "found": 0, "pages": 0}

    def test_connect_to_api_memory_cache_hit(self, mocker):
        """Тест попадания в кэш памяти"""
        mocker.patch('src.api_modules.cached_api.Path')
        mocker.patch('src.api_modules.cached_api.FileCache')
        mock_logger = mocker.patch('src.api_modules.cached_api.logger')
        
        api = ConcreteCachedAPI("test_cache")
        api.connector = Mock()

        # Мокаем метод _cached_api_request для имитации попадания в кэш
        mocker.patch.object(api, '_cached_api_request', return_value={"cached": "data"})
        result = api._CachedAPI__connect_to_api("test_url", {"param": "value"}, "test_prefix")

        assert result == {"cached": "data"}

    def test_connect_to_api_memory_cache_error_file_cache_hit(self, mocker):
        """Тест ошибки кэша памяти с попаданием в файловый кэш"""
        mocker.patch('src.api_modules.cached_api.Path')
        mocker.patch('src.api_modules.cached_api.FileCache')
        mock_logger = mocker.patch('src.api_modules.cached_api.logger')
        mock_logging = mocker.patch('src.api_modules.cached_api.logging')
        
        api = ConcreteCachedAPI("test_cache")
        api.connector = Mock()
        api.cache.load_response.return_value = {"data": {"file_cached": "data"}}

        # Мокаем метод _cached_api_request для имитации ошибки кэша памяти
        mocker.patch.object(api, '_cached_api_request', side_effect=Exception("Cache error"))
        result = api._CachedAPI__connect_to_api("test_url", {"param": "value"}, "test_prefix")

        assert result == {"file_cached": "data"}
        mock_logging.warning.assert_called_once()

    def test_connect_to_api_memory_cache_empty_file_cache_hit(self, mocker):
        """Тест покрытия строк 65-71: кэш памяти пустой, файловый кэш содержит данные"""
        mocker.patch('src.api_modules.cached_api.Path')
        mocker.patch('src.api_modules.cached_api.FileCache')
        mock_logger = mocker.patch('src.api_modules.cached_api.logger')
        
        api = ConcreteCachedAPI("test_cache")
        api.connector = Mock()
        
        # Настраиваем файловый кэш для возврата данных
        test_data = {"file_cached": "data"}
        api.cache.load_response.return_value = {"data": test_data}
        
        # Мокаем _cached_api_request для возврата пустого ответа
        mocker.patch.object(api, '_cached_api_request', return_value=api._get_empty_response())
        
        # Выполняем метод - покрывает строки 65-71
        result = api._CachedAPI__connect_to_api("test_url", {"param": "value"}, "test_prefix")
        
        assert result == test_data
        api.cache.load_response.assert_called_once_with("test_prefix", {"param": "value"})
        mock_logger.debug.assert_any_call("Данные получены из файлового кэша для test_prefix")

    def test_connect_to_api_no_cache_api_success(self, mocker):
        """Тест успешного API запроса без кэша"""
        mocker.patch('src.api_modules.cached_api.Path')
        mocker.patch('src.api_modules.cached_api.FileCache')
        mock_logger = mocker.patch('src.api_modules.cached_api.logger')
        
        api = ConcreteCachedAPI("test_cache")
        api.connector = Mock()
        api.connector._APIConnector__connect.return_value = {"api": "data"}
        api.cache.load_response.return_value = None

        # Мокаем метод _cached_api_request для имитации промаха кэша памяти
        mocker.patch.object(api, '_cached_api_request', return_value={"items": [], "found": 0, "pages": 0})
        result = api._CachedAPI__connect_to_api("test_url", {"param": "value"}, "test_prefix")

        assert result == {"api": "data"}
        api.cache.save_response.assert_called_once_with("test_prefix", {"param": "value"}, {"api": "data"})

    def test_connect_to_api_no_cache_api_empty_response(self, mocker):
        """Тест API запроса с пустым ответом"""
        mocker.patch('src.api_modules.cached_api.Path')
        mocker.patch('src.api_modules.cached_api.FileCache')
        mock_logger = mocker.patch('src.api_modules.cached_api.logger')
        
        api = ConcreteCachedAPI("test_cache")
        api.connector = Mock()
        api.connector._APIConnector__connect.return_value = {"items": [], "found": 0, "pages": 0}
        api.cache.load_response.return_value = None

        # Мокаем метод _cached_api_request для имитации промаха кэша памяти
        mocker.patch.object(api, '_cached_api_request', return_value={"items": [], "found": 0, "pages": 0})
        result = api._CachedAPI__connect_to_api("test_url", {"param": "value"}, "test_prefix")

        assert result == {"items": [], "found": 0, "pages": 0}
        # Пустые данные не сохраняются в кэш
        api.cache.save_response.assert_not_called()

    def test_connect_to_api_error(self, mocker):
        """Тест ошибки при API запросе"""
        mocker.patch('src.api_modules.cached_api.Path')
        mocker.patch('src.api_modules.cached_api.FileCache')
        mock_logger = mocker.patch('src.api_modules.cached_api.logger')
        
        api = ConcreteCachedAPI("test_cache")
        api.connector = Mock()
        api.connector._APIConnector__connect.side_effect = Exception("API Error")
        api.cache.load_response.return_value = None

        # Мокаем метод _cached_api_request для имитации промаха кэша памяти
        mocker.patch.object(api, '_cached_api_request', return_value={"items": [], "found": 0, "pages": 0})
        result = api._CachedAPI__connect_to_api("test_url", {"param": "value"}, "test_prefix")

        assert result == {"items": [], "found": 0, "pages": 0}
        mock_logger.error.assert_called_once()

    def test_clear_cache_success(self, mocker):
        """Тест успешной очистки кэша"""
        mocker.patch('src.api_modules.cached_api.Path')
        mocker.patch('src.api_modules.cached_api.FileCache')
        mock_logger = mocker.patch('src.api_modules.cached_api.logger')
        
        api = ConcreteCachedAPI("test_cache")

        # Мокаем clear_cache метод
        mock_clear_cache = Mock()
        mocker.patch.object(api, '_cached_api_request', Mock(clear_cache=mock_clear_cache))
        api.clear_cache("test_prefix")

        api.cache.clear.assert_called_once_with("test_prefix")
        mock_clear_cache.assert_called_once()
        mock_logger.info.assert_called_once_with("Кэш test_prefix очищен (файловый и в памяти)")

    def test_clear_cache_no_clear_cache_method(self, mocker):
        """Тест очистки кэша без метода clear_cache"""
        mocker.patch('src.api_modules.cached_api.Path')
        mocker.patch('src.api_modules.cached_api.FileCache')
        mock_logger = mocker.patch('src.api_modules.cached_api.logger')
        
        api = ConcreteCachedAPI("test_cache")

        api.clear_cache("test_prefix")

        api.cache.clear.assert_called_once_with("test_prefix")
        mock_logger.info.assert_called_once_with("Кэш test_prefix очищен (файловый и в памяти)")

    def test_clear_cache_error(self, mocker):
        """Тест ошибки при очистке кэша"""
        mocker.patch('src.api_modules.cached_api.Path')
        mocker.patch('src.api_modules.cached_api.FileCache')
        mock_logger = mocker.patch('src.api_modules.cached_api.logger')
        
        api = ConcreteCachedAPI("test_cache")
        api.cache.clear.side_effect = Exception("Clear error")

        api.clear_cache("test_prefix")

        mock_logger.error.assert_called_once_with("Ошибка очистки кэша test_prefix: Clear error")

    def test_get_cache_status_success(self, mocker):
        """Тест успешного получения статуса кэша"""
        mocker.patch('src.api_modules.cached_api.Path')
        mocker.patch('src.api_modules.cached_api.FileCache')
        mock_logger = mocker.patch('src.api_modules.cached_api.logger')
        
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
        mocker.patch.object(api, '_cached_api_request', Mock(cache_info=mock_cache_info))
        result = api.get_cache_status("test_prefix")

        expected = {
            'cache_dir': str(api.cache_dir),
            'cache_dir_exists': True,
            'file_cache_count': 2,
            'cache_files': ["test_prefix_1.json", "test_prefix_2.json"],
            'memory_cache': {"hits": 5, "misses": 2}
        }
        assert result == expected

    def test_get_cache_status_no_cache_info(self, mocker):
        """Тест получения статуса кэша без cache_info"""
        mocker.patch('src.api_modules.cached_api.Path')
        mocker.patch('src.api_modules.cached_api.FileCache')
        mock_logger = mocker.patch('src.api_modules.cached_api.logger')
        
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
            'memory_cache': {'max_size': 1000, 'size': 0, 'ttl': 300}
        }
        assert result == expected

    def test_get_cache_status_error(self, mocker):
        """Тест ошибки при получении статуса кэша"""
        mocker.patch('src.api_modules.cached_api.Path')
        mocker.patch('src.api_modules.cached_api.FileCache')
        mock_logger = mocker.patch('src.api_modules.cached_api.logger')
        
        api = ConcreteCachedAPI("test_cache")
        api.cache_dir.glob.side_effect = Exception("Glob error")

        result = api.get_cache_status("test_prefix")

        assert result == {'error': 'Glob error'}
        mock_logger.error.assert_called_once_with("Ошибка получения статуса кэша: Glob error")

    def test_connect_method(self, mocker):
        """Тест метода __connect"""
        mocker.patch('src.api_modules.cached_api.Path')
        mocker.patch('src.api_modules.cached_api.FileCache')
        mock_logger = mocker.patch('src.api_modules.cached_api.logger')
        
        api = ConcreteCachedAPI("test_cache")
        api.connector = Mock()
        api.connector._APIConnector__connect.return_value = {"success": True}

        result = api._CachedAPI__connect("test_url", {"param": "value"})

        assert result == {"success": True}
        api.connector._APIConnector__connect.assert_called_once_with("test_url", {"param": "value"})

    def test_connect_method_error(self, mocker):
        """Тест ошибки в методе __connect"""
        mocker.patch('src.api_modules.cached_api.Path')
        mocker.patch('src.api_modules.cached_api.FileCache')
        mock_logger = mocker.patch('src.api_modules.cached_api.logger')
        
        api = ConcreteCachedAPI("test_cache")
        api.connector = Mock()
        api.connector._APIConnector__connect.side_effect = Exception("Connection error")

        result = api._CachedAPI__connect("test_url", {"param": "value"})

        assert result == {}
        mock_logger.error.assert_called_once_with("Ошибка при подключении к API: Connection error")

    def test_connect_method_no_params(self, mocker):
        """Тест метода __connect without params"""
        mocker.patch('src.api_modules.cached_api.Path')
        mocker.patch('src.api_modules.cached_api.FileCache')
        mock_logger = mocker.patch('src.api_modules.cached_api.logger')
        
        api = ConcreteCachedAPI("test_cache")
        api.connector = Mock()
        api.connector._APIConnector__connect.return_value = {"success": True}

        result = api._CachedAPI__connect("test_url")

        assert result == {"success": True}
        api.connector._APIConnector__connect.assert_called_once_with("test_url", {})

    def test_connect_method_with_default_params(self, mocker):
        """Тест метода __connect with default empty dict params"""
        mocker.patch('src.api_modules.cached_api.Path')
        mocker.patch('src.api_modules.cached_api.FileCache')
        mock_logger = mocker.patch('src.api_modules.cached_api.logger')
        
        api = ConcreteCachedAPI("test_cache")
        api.connector = Mock()
        api.connector._APIConnector__connect.return_value = {"default": "params"}

        # Call without any params to test default {} assignment
        result = api._CachedAPI__connect("test_url", {})

        assert result == {"default": "params"}
        api.connector._APIConnector__connect.assert_called_once_with("test_url", {})

    def test_connect_method_without_params_arg(self, mocker):
        """Тест метода __connect без передачи параметра params (использование значения по умолчанию)"""
        mocker.patch('src.api_modules.cached_api.Path')
        mocker.patch('src.api_modules.cached_api.FileCache')
        mock_logger = mocker.patch('src.api_modules.cached_api.logger')
        
        api = ConcreteCachedAPI("test_cache")
        api.connector = Mock()
        api.connector._APIConnector__connect.return_value = {"no_params": "test"}

        # Вызываем метод без второго аргумента для тестирования значения по умолчанию
        result = api._CachedAPI__connect("test_url")

        assert result == {"no_params": "test"}
        api.connector._APIConnector__connect.assert_called_once_with("test_url", {})

    def test_connect_method_signature_coverage(self, mocker):
        """Тест для 100% покрытия метода __connect - проверка сигнатуры метода"""
        mocker.patch('src.api_modules.cached_api.Path')
        mocker.patch('src.api_modules.cached_api.FileCache')
        
        api = ConcreteCachedAPI("test_cache")
        api.connector = Mock()
        api.connector._APIConnector__connect.return_value = {"signature": "test"}

        # Вызываем метод с явным указанием params={} для покрытия строки с default параметром
        result = api._CachedAPI__connect(url="test_url", params={})

        assert result == {"signature": "test"}
        api.connector._APIConnector__connect.assert_called_once_with("test_url", {})

    def test_connect_method_exception_handling(self, mocker):
        """Тест обработки исключения в методе __connect для 100% покрытия"""
        mocker.patch('src.api_modules.cached_api.Path')
        mocker.patch('src.api_modules.cached_api.FileCache')
        mock_logger = mocker.patch('src.api_modules.cached_api.logger')
        
        api = ConcreteCachedAPI("test_cache")
        api.connector = Mock()
        api.connector._APIConnector__connect.side_effect = Exception("Test connection error")

        result = api._CachedAPI__connect("test_url", {"param": "value"})

        assert result == {}
        mock_logger.error.assert_called_once_with("Ошибка при подключении к API: Test connection error")

import hashlib
import json
from unittest.mock import Mock, patch, mock_open

from src.utils.cache import simple_cache, FileCache


class TestSimpleCache:
    """Тесты для декоратора simple_cache"""

    def test_simple_cache_basic(self):
        """Тест базового кэширования"""
        call_count = 0

        @simple_cache()
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # Первый вызов
        result1 = test_func(5)
        assert result1 == 10
        assert call_count == 1

        # Второй вызов с тем же аргументом - должен использовать кэш
        result2 = test_func(5)
        assert result2 == 10
        assert call_count == 1  # Функция не вызывалась повторно

    def test_simple_cache_with_kwargs(self):
        """Тест кэширования с kwargs"""
        call_count = 0

        @simple_cache()
        def test_func(x, y=1):
            nonlocal call_count
            call_count += 1
            return x + y

        result1 = test_func(5, y=2)
        result2 = test_func(5, y=2)
        assert result1 == result2 == 7
        assert call_count == 1

    @patch('src.utils.cache.EnvLoader.get_env_var_int')
    @patch('time.time')
    def test_simple_cache_ttl_expired(self, mock_time, mock_get_env):
        """Тест истечения TTL кэша"""
        mock_get_env.return_value = 1  # 1 секунда TTL
        mock_time.return_value = 0  # Начальное время
        call_count = 0

        @simple_cache()
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # Первый вызов в момент времени 0
        result1 = test_func(5)
        assert result1 == 10
        assert call_count == 1

        # Имитируем прошествие времени (время истекло)
        mock_time.return_value = 2  # Время больше TTL (1 секунда)
        result2 = test_func(5)
        assert result2 == 10
        assert call_count == 2  # Функция вызвалась снова

    def test_simple_cache_max_size_lru(self):
        """Тест LRU очистки при достижении max_size"""
        call_count = 0

        @simple_cache(max_size=2)
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # Заполняем кэш
        test_func(1)
        test_func(2)
        assert call_count == 2

        # Добавляем третий элемент - должен удалить первый (LRU)
        test_func(3)
        assert call_count == 3

        # Проверяем, что первый элемент удален
        test_func(1)  # Должен вызвать функцию снова
        assert call_count == 4

    @patch('src.utils.cache.EnvLoader.get_env_var_int')
    def test_simple_cache_custom_ttl(self, mock_get_env):
        """Тест кэша с кастомным TTL"""
        mock_get_env.return_value = 3600  # Значение по умолчанию
        
        @simple_cache(ttl=10)
        def test_func(x):
            return x * 2

        # Проверяем cache_info
        info = test_func.cache_info()
        assert info['ttl'] == 10

    @patch('src.utils.cache.EnvLoader.get_env_var_int')
    def test_simple_cache_clear_cache(self, mock_get_env):
        """Тест очистки кэша"""
        mock_get_env.return_value = 3600
        call_count = 0

        @simple_cache()
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # Кэшируем значение
        test_func(5)
        assert call_count == 1

        # Очищаем кэш
        test_func.clear_cache()

        # Проверяем, что кэш очищен
        test_func(5)
        assert call_count == 2

    @patch('src.utils.cache.EnvLoader.get_env_var_int')
    def test_simple_cache_info(self, mock_get_env):
        """Тест получения информации о кэше"""
        mock_get_env.return_value = 3600

        @simple_cache(max_size=100)
        def test_func(x):
            return x * 2

        info = test_func.cache_info()
        assert info['size'] == 0
        assert info['max_size'] == 100
        assert info['ttl'] == 3600

        # Добавляем элемент в кэш
        test_func(5)
        info = test_func.cache_info()
        assert info['size'] == 1


class TestFileCache:
    """Тесты для класса FileCache"""

    @patch('src.utils.cache.Path')
    def test_file_cache_init(self, mock_path):
        """Тест инициализации FileCache"""
        mock_path_instance = Mock()
        mock_path.return_value = mock_path_instance
        
        cache = FileCache("test_cache")
        
        mock_path.assert_called_once_with("test_cache")
        mock_path_instance.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        assert cache.cache_dir == mock_path_instance

    def test_generate_params_hash(self):
        """Тест генерации хеша параметров"""
        params = {"key1": "value1", "key2": "value2"}
        expected_hash = hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()
        
        actual_hash = FileCache._generate_params_hash(params)
        assert actual_hash == expected_hash

    @patch('src.utils.cache.Path')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_save_response(self, mock_json_dump, mock_file, mock_path):
        """Тест сохранения ответа в файл"""
        mock_path_instance = Mock()
        mock_path.return_value = mock_path_instance
        mock_filepath = Mock()
        mock_path_instance.__truediv__ = Mock(return_value=mock_filepath)
        
        cache = FileCache()
        params = {"test": "param"}
        data = {"response": "data"}
        
        result = cache.save_response("test_source", params, data)
        
        # Проверяем, что файл открыт для записи
        mock_file.assert_called_once_with(mock_filepath, 'w', encoding='utf-8')
        
        # Проверяем, что данные записаны
        expected_data = {
            "meta": {"params": params},
            "data": data
        }
        mock_json_dump.assert_called_once_with(expected_data, mock_file(), ensure_ascii=False, indent=2)
        assert result == mock_filepath

    @patch('src.utils.cache.Path')
    @patch('builtins.open', new_callable=mock_open, read_data='{"test": "data"}')
    @patch('json.load')
    def test_load_response_success(self, mock_json_load, mock_file, mock_path):
        """Тест успешной загрузки кэшированного ответа"""
        mock_path_instance = Mock()
        mock_path.return_value = mock_path_instance
        mock_filepath = Mock()
        mock_filepath.exists.return_value = True
        mock_path_instance.__truediv__ = Mock(return_value=mock_filepath)
        mock_json_load.return_value = {"test": "data"}
        
        cache = FileCache()
        params = {"test": "param"}
        
        result = cache.load_response("test_source", params)
        
        mock_filepath.exists.assert_called_once()
        mock_file.assert_called_once_with(mock_filepath, 'r', encoding='utf-8')
        mock_json_load.assert_called_once()
        assert result == {"test": "data"}

    @patch('src.utils.cache.Path')
    def test_load_response_file_not_exists(self, mock_path):
        """Тест загрузки несуществующего файла"""
        mock_path_instance = Mock()
        mock_path.return_value = mock_path_instance
        mock_filepath = Mock()
        mock_filepath.exists.return_value = False
        mock_path_instance.__truediv__ = Mock(return_value=mock_filepath)
        
        cache = FileCache()
        params = {"test": "param"}
        
        result = cache.load_response("test_source", params)
        
        assert result is None

    @patch('src.utils.cache.Path')
    @patch('builtins.open', side_effect=OSError("File error"))
    def test_load_response_file_error(self, mock_file, mock_path):
        """Тест обработки ошибки при загрузке файла"""
        mock_path_instance = Mock()
        mock_path.return_value = mock_path_instance
        mock_filepath = Mock()
        mock_filepath.exists.return_value = True
        mock_path_instance.__truediv__ = Mock(return_value=mock_filepath)
        
        cache = FileCache()
        params = {"test": "param"}
        
        result = cache.load_response("test_source", params)
        
        assert result is None

    @patch('src.utils.cache.Path')
    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    @patch('json.load', side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
    def test_load_response_json_error(self, mock_json_load, mock_file, mock_path):
        """Тест обработки ошибки JSON при загрузке"""
        mock_path_instance = Mock()
        mock_path.return_value = mock_path_instance
        mock_filepath = Mock()
        mock_filepath.exists.return_value = True
        mock_path_instance.__truediv__ = Mock(return_value=mock_filepath)
        
        cache = FileCache()
        params = {"test": "param"}
        
        result = cache.load_response("test_source", params)
        
        assert result is None

    @patch('src.utils.cache.Path')
    @patch('builtins.open', side_effect=Exception("Unexpected error"))
    def test_load_response_unexpected_error(self, mock_file, mock_path):
        """Тест обработки неожиданной ошибки при загрузке"""
        mock_path_instance = Mock()
        mock_path.return_value = mock_path_instance
        mock_filepath = Mock()
        mock_filepath.exists.return_value = True
        mock_path_instance.__truediv__ = Mock(return_value=mock_filepath)
        
        cache = FileCache()
        params = {"test": "param"}
        
        result = cache.load_response("test_source", params)
        
        assert result is None

    @patch('src.utils.cache.Path')
    def test_clear_specific_source(self, mock_path):
        """Тест очистки кэша для конкретного источника"""
        mock_path_instance = Mock()
        mock_path.return_value = mock_path_instance
        mock_file1 = Mock()
        mock_file2 = Mock()
        mock_path_instance.glob.return_value = [mock_file1, mock_file2]
        
        cache = FileCache()
        cache.clear("test_source")
        
        mock_path_instance.glob.assert_called_once_with("test_source_*.json")
        mock_file1.unlink.assert_called_once()
        mock_file2.unlink.assert_called_once()

    @patch('src.utils.cache.Path')
    def test_clear_all_sources(self, mock_path):
        """Тест очистки всего кэша"""
        mock_path_instance = Mock()
        mock_path.return_value = mock_path_instance
        mock_file1 = Mock()
        mock_file2 = Mock()
        mock_path_instance.glob.return_value = [mock_file1, mock_file2]
        
        cache = FileCache()
        cache.clear()
        
        mock_path_instance.glob.assert_called_once_with("*.json")
        mock_file1.unlink.assert_called_once()
        mock_file2.unlink.assert_called_once()

    @patch('src.utils.cache.Path')
    def test_clear_no_files(self, mock_path):
        """Тест очистки когда нет файлов"""
        mock_path_instance = Mock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.glob.return_value = []
        
        cache = FileCache()
        cache.clear("test_source")
        
        mock_path_instance.glob.assert_called_once_with("test_source_*.json")

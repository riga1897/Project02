import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# Добавляем путь к исходному коду
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.cache import FileCache
from src.utils.env_loader import EnvLoader
from src.utils.paginator import Paginator


class TestFileCache:

    @pytest.fixture
    def cache(self):
        return FileCache("test_cache")

    def test_init(self, cache):
        assert cache is not None
        assert cache.cache_dir == Path("test_cache")

    @patch('builtins.open', new_callable=mock_open, read_data='{"data": "test"}')
    @patch('src.utils.cache.Path.exists')
    def test_load_response_exists(self, mock_exists, mock_file, cache):
        mock_exists.return_value = True

        result = cache.load_response("api", {"param": "value"})
        assert result == {"data": "test"}

    @patch('src.utils.cache.Path.exists')
    def test_load_response_not_exists(self, mock_exists, cache):
        mock_exists.return_value = False

        result = cache.load_response("api", {"param": "value"})
        assert result is None

    @patch('src.utils.cache.Path.exists')
    @patch('src.utils.cache.Path.read_text')
    def test_load_response_json_error(self, mock_read_text, mock_exists, cache):
        mock_exists.return_value = True
        mock_read_text.return_value = 'invalid json'

        result = cache.load_response("api", {"param": "value"})
        assert result is None

    @patch('builtins.open', new_callable=mock_open)
    @patch('src.utils.cache.Path.mkdir')
    def test_save_response(self, mock_mkdir, mock_file, cache):
        cache.save_response("api", {"param": "value"}, {"data": "test"})

        mock_file.assert_called_once()

    @patch('src.utils.cache.Path.write_text')
    @patch('src.utils.cache.Path.mkdir')
    def test_save_response_error(self, mock_mkdir, mock_write_text, cache):
        mock_write_text.side_effect = Exception("Write error")

        # Should not raise exception
        cache.save_response("api", {"param": "value"}, {"data": "test"})

    @patch('src.utils.cache.Path.glob')
    def test_clear(self, mock_glob, cache):
        mock_file = Mock()
        mock_file.unlink = Mock()
        mock_glob.return_value = [mock_file]

        cache.clear("api")
        mock_file.unlink.assert_called()

    @patch('src.utils.cache.Path.exists')
    def test_clear_not_exists(self, mock_exists, cache):
        mock_exists.return_value = False

        # Should not raise exception
        cache.clear("api")


class TestEnvLoader:

    @patch('src.utils.env_loader.os.getenv')
    def test_get_env_var_exists(self, mock_getenv):
        mock_getenv.return_value = "test_value"

        result = EnvLoader.get_env_var("TEST_VAR")
        assert result == "test_value"

    @patch('src.utils.env_loader.os.getenv')
    def test_get_env_var_not_exists(self, mock_getenv):
        # Мокаем os.getenv так, чтобы он возвращал второй аргумент (default) когда переменная не найдена
        def mock_getenv_func(key, default=None):
            return default
        mock_getenv.side_effect = mock_getenv_func

        result = EnvLoader.get_env_var("TEST_VAR", "default")
        assert result == "default"

    @patch('src.utils.env_loader.os.getenv')
    def test_get_env_var_no_default(self, mock_getenv):
        # Мокаем os.getenv так, чтобы он возвращал второй аргумент (None по умолчанию)
        def mock_getenv_func(key, default=None):
            return default
        mock_getenv.side_effect = mock_getenv_func

        result = EnvLoader.get_env_var("TEST_VAR")
        assert result is None

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='TEST_VAR=test_value\n')
    def test_load_env_file_exists(self, mock_file, mock_exists):
        mock_exists.return_value = True

        # Сбрасываем состояние загрузки для корректного тестирования
        EnvLoader._loaded = False

        EnvLoader.load_env_file()
        mock_file.assert_called_once()

    @patch('os.path.exists')
    def test_load_env_file_not_exists(self, mock_exists):
        mock_exists.return_value = False

        # Сбрасываем состояние загрузки для корректного тестирования
        EnvLoader._loaded = False

        # Should not raise exception
        EnvLoader.load_env_file()


class TestPaginator:

    @pytest.fixture
    def paginator(self):
        return Paginator()

    def test_init(self, paginator):
        assert paginator is not None

    def test_paginate_success(self, paginator):
        def mock_fetch(page):
            return [f"item_{page}"]

        result = paginator.paginate(mock_fetch, 3)
        assert len(result) == 3
        assert result == ["item_0", "item_1", "item_2"]

    def test_paginate_with_error(self, paginator):
        def mock_fetch(page):
            if page == 1:
                raise Exception("Test error")
            return [f"item_{page}"]

        result = paginator.paginate(mock_fetch, 3)
        assert len(result) == 2  # Should skip page 1 due to error
        assert result == ["item_0", "item_2"]

    def test_paginate_keyboard_interrupt(self, paginator):
        def mock_fetch(page):
            if page == 1:
                raise KeyboardInterrupt()
            return [f"item_{page}"]

        # Тест перехватывает KeyboardInterrupt как обычное исключение
        with pytest.raises(KeyboardInterrupt):
            paginator.paginate(mock_fetch, 3)
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, Mock

# Добавляем путь к исходному коду
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.cache import FileCache
from src.utils.env_loader import EnvLoader
from src.utils.salary import SalaryFormatter, SalaryFilter
from src.utils.paginator import Paginator


class TestFileCache:
    
    @pytest.fixture
    def cache(self, tmp_path):
        return FileCache(str(tmp_path))
    
    def test_init(self, cache, tmp_path):
        assert cache.cache_dir == Path(tmp_path)
        assert cache.cache_dir.exists()
    
    def test_save_and_load_response(self, cache):
        api_prefix = "test_api"
        params = {"query": "python", "page": 1}
        data = {"items": [{"id": 1, "name": "Test"}]}
        
        # Сохраняем данные
        cache.save_response(api_prefix, params, data)
        
        # Загружаем данные
        result = cache.load_response(api_prefix, params)
        
        assert result is not None
        assert result["data"] == data
    
    def test_load_nonexistent(self, cache):
        result = cache.load_response("nonexistent", {"test": "value"})
        assert result is None
    
    def test_clear(self, cache):
        # Создаем файл кэша
        cache.save_response("test", {"param": "value"}, {"data": "test"})
        
        # Очищаем кэш
        cache.clear("test")
        
        # Проверяем что данные удалены
        result = cache.load_response("test", {"param": "value"})
        assert result is None


class TestEnvLoader:
    
    def test_get_env_var_existing(self):
        with patch.dict('os.environ', {'TEST_VAR': 'test_value'}):
            result = EnvLoader.get_env_var('TEST_VAR')
            assert result == 'test_value'
    
    def test_get_env_var_with_default(self):
        result = EnvLoader.get_env_var('NONEXISTENT_VAR', 'default_value')
        assert result == 'default_value'
    
    def test_get_env_var_required_missing(self):
        with pytest.raises(ValueError):
            EnvLoader.get_env_var('NONEXISTENT_VAR', required=True)


class TestSalaryFormatter:
    
    def test_format_salary_range(self):
        salary_data = {"from": 100000, "to": 150000, "currency": "RUR"}
        result = SalaryFormatter.format_salary(salary_data)
        assert "100 000" in result
        assert "150 000" in result
    
    def test_format_salary_from_only(self):
        salary_data = {"from": 100000, "currency": "RUR"}
        result = SalaryFormatter.format_salary(salary_data)
        assert "от 100 000" in result
    
    def test_format_salary_none(self):
        result = SalaryFormatter.format_salary(None)
        assert result == "Не указана"
    
    def test_format_number(self):
        result = SalaryFormatter.format_number(1000000)
        assert result == "1 000 000"


class TestSalaryFilter:
    
    def test_filter_by_salary_range(self):
        vacancies = [
            {"salary": {"from": 50000, "to": 100000}},
            {"salary": {"from": 150000, "to": 200000}},
            {"salary": None}
        ]
        
        result = SalaryFilter.filter_by_salary_range(vacancies, min_salary=80000, max_salary=180000)
        assert len(result) == 1
        assert result[0]["salary"]["from"] == 150000
    
    def test_has_salary(self):
        vacancy_with_salary = {"salary": {"from": 100000}}
        vacancy_without_salary = {"salary": None}
        
        assert SalaryFilter.has_salary(vacancy_with_salary) is True
        assert SalaryFilter.has_salary(vacancy_without_salary) is False


class TestPaginator:
    
    def test_paginate_basic(self):
        items = list(range(25))  # 0-24
        paginator = Paginator(items, per_page=10)
        
        assert paginator.total_items == 25
        assert paginator.total_pages == 3
        assert paginator.current_page == 1
    
    def test_get_page_items(self):
        items = list(range(25))
        paginator = Paginator(items, per_page=10)
        
        page_1 = paginator.get_page_items()
        assert len(page_1) == 10
        assert page_1[0] == 0
        assert page_1[9] == 9
    
    def test_next_page(self):
        items = list(range(25))
        paginator = Paginator(items, per_page=10)
        
        assert paginator.has_next() is True
        paginator.next_page()
        assert paginator.current_page == 2
    
    def test_previous_page(self):
        items = list(range(25))
        paginator = Paginator(items, per_page=10)
        
        paginator.next_page()  # Переходим на страницу 2
        assert paginator.has_previous() is True
        paginator.previous_page()
        assert paginator.current_page == 1


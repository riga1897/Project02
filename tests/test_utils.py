
import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
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
    
    @patch('src.utils.cache.Path.exists')
    @patch('src.utils.cache.Path.read_text')
    def test_load_response_exists(self, mock_read_text, mock_exists, cache):
        mock_exists.return_value = True
        mock_read_text.return_value = '{"data": "test"}'
        
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
    
    @patch('src.utils.cache.Path.write_text')
    @patch('src.utils.cache.Path.mkdir')
    def test_save_response(self, mock_mkdir, mock_write_text, cache):
        cache.save_response("api", {"param": "value"}, {"data": "test"})
        
        mock_mkdir.assert_called_once()
        mock_write_text.assert_called_once()
    
    @patch('src.utils.cache.Path.write_text')
    @patch('src.utils.cache.Path.mkdir')
    def test_save_response_error(self, mock_mkdir, mock_write_text, cache):
        mock_write_text.side_effect = Exception("Write error")
        
        # Should not raise exception
        cache.save_response("api", {"param": "value"}, {"data": "test"})
    
    @patch('src.utils.cache.Path.exists')
    @patch('src.utils.cache.Path.iterdir')
    @patch('src.utils.cache.Path.unlink')
    def test_clear(self, mock_unlink, mock_iterdir, mock_exists, cache):
        mock_exists.return_value = True
        mock_file = Mock()
        mock_file.is_file.return_value = True
        mock_iterdir.return_value = [mock_file]
        
        cache.clear("api")
        mock_unlink.assert_called()
    
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
        mock_getenv.return_value = None
        
        result = EnvLoader.get_env_var("TEST_VAR", "default")
        assert result == "default"
    
    @patch('src.utils.env_loader.os.getenv')
    def test_get_env_var_no_default(self, mock_getenv):
        mock_getenv.return_value = None
        
        result = EnvLoader.get_env_var("TEST_VAR")
        assert result is None
    
    @patch('src.utils.env_loader.Path.exists')
    @patch('src.utils.env_loader.load_dotenv')
    def test_load_env_file_exists(self, mock_load_dotenv, mock_exists):
        mock_exists.return_value = True
        
        result = EnvLoader.load_env()
        assert result is True
        mock_load_dotenv.assert_called_once()
    
    @patch('src.utils.env_loader.Path.exists')
    def test_load_env_file_not_exists(self, mock_exists):
        mock_exists.return_value = False
        
        result = EnvLoader.load_env()
        assert result is False


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
        
        result = paginator.paginate(mock_fetch, 3)
        assert len(result) == 1  # Should stop at page 1
        assert result == ["item_0"]


class TestSalaryUtils:
    
    def test_normalize_currency_rub(self):
        result = SalaryUtils.normalize_currency("rub")
        assert result == "RUB"
    
    def test_normalize_currency_rur(self):
        result = SalaryUtils.normalize_currency("rur")
        assert result == "RUB"
    
    def test_normalize_currency_usd(self):
        result = SalaryUtils.normalize_currency("usd")
        assert result == "USD"
    
    def test_normalize_currency_eur(self):
        result = SalaryUtils.normalize_currency("eur")
        assert result == "EUR"
    
    def test_normalize_currency_unknown(self):
        result = SalaryUtils.normalize_currency("unknown")
        assert result == "UNKNOWN"
    
    def test_normalize_currency_none(self):
        result = SalaryUtils.normalize_currency(None)
        assert result == "RUB"
    
    def test_format_salary_both(self):
        result = SalaryUtils.format_salary(50000, 80000, "RUB")
        assert result == "50000 - 80000 RUB"
    
    def test_format_salary_from_only(self):
        result = SalaryUtils.format_salary(50000, None, "RUB")
        assert result == "от 50000 RUB"
    
    def test_format_salary_to_only(self):
        result = SalaryUtils.format_salary(None, 80000, "RUB")
        assert result == "до 80000 RUB"
    
    def test_format_salary_none(self):
        result = SalaryUtils.format_salary(None, None, "RUB")
        assert result == "Не указана"
    
    def test_parse_salary_from_string(self):
        from_sal, to_sal = SalaryUtils.parse_salary_from_string("50000 - 80000")
        assert from_sal == 50000
        assert to_sal == 80000
    
    def test_parse_salary_from_string_from_only(self):
        from_sal, to_sal = SalaryUtils.parse_salary_from_string("от 50000")
        assert from_sal == 50000
        assert to_sal is None
    
    def test_parse_salary_from_string_to_only(self):
        from_sal, to_sal = SalaryUtils.parse_salary_from_string("до 80000")
        assert from_sal is None
        assert to_sal == 80000
    
    def test_parse_salary_from_string_invalid(self):
        from_sal, to_sal = SalaryUtils.parse_salary_from_string("invalid")
        assert from_sal is None
        assert to_sal is None

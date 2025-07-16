import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import pytest
from src.api_modules.hh_api import HeadHunterAPI
from src.utils.cache import FileCache


def test_cache_dir_initialization_failure():
    """Тест ошибки инициализации кэша (строка 24)"""
    # 1. Создаем мок для FileCache, который имитирует ошибку при создании директории
    mock_filecache = MagicMock()
    mock_filecache.return_value._ensure_dir_exists.side_effect = OSError("Cannot create dir")

    # 2. Мокируем Path.exists чтобы эмулировать отсутствие директории
    with patch('pathlib.Path.exists', return_value=False), \
            patch('src.api_modules.hh_api.FileCache', mock_filecache), \
            patch('builtins.print') as mock_print:
        # 3. Проверяем что инициализация API выбрасывает RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            HeadHunterAPI(MagicMock())

        # 4. Проверяем сообщение об ошибке
        assert "Cache directory not found" in str(exc_info.value)
        assert "data/cache/hh" in str(exc_info.value)

        # 5. Убеждаемся что прогресс-бар не вызывался
        mock_print.assert_not_called()


def test_ensure_cache_dir_success():
    """Тест успешного создания директории кэша (строка 34)"""
    with patch('pathlib.Path.mkdir') as mock_mkdir, \
            patch('builtins.print') as mock_print:  # Мокируем print

        HeadHunterAPI.ensure_cache_dir("test_dir")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_print.assert_not_called()  # Прогресс-бар не должен вызываться


def test_ensure_cache_dir_failure():
    """Тест ошибки при создании директории кэша"""
    with patch('pathlib.Path.mkdir', side_effect=OSError("Cannot create dir")), \
            patch('builtins.print') as mock_print:
        with pytest.raises(OSError, match="Cannot create dir"):
            HeadHunterAPI.ensure_cache_dir("test_dir")
        mock_print.assert_not_called()  # Проверяем что прогресс-бар не вызывался


@pytest.fixture
def api_instance():
    """Фикстура с моками для тестирования"""
    with patch('pathlib.Path.exists', return_value=True), \
            patch('src.api_modules.hh_api.FileCache') as mock_cache, \
            patch('src.api_modules.hh_api.APIConfig') as mock_config:
        # Настраиваем моки
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.hh_config.get_params.return_value = {}
        mock_config_instance.get_pagination_params.return_value = {'max_pages': 10}

        api = HeadHunterAPI(mock_config_instance)
        api.connector = MagicMock()
        mock_cache.return_value.load_response.return_value = None
        yield api


def test_connect_to_api_cache_hit(api_instance):
    """Тест _connect_to_api с попаданием в кэш (строки 33-38)"""
    # Настраиваем мок кэша
    test_data = {'data': {'items': [{'id': 'cached'}]}}
    api_instance.cache.load_response.return_value = test_data

    result = api_instance._connect_to_api("test_url", {})
    assert result == test_data['data']
    api_instance.connector.connect.assert_not_called()


def test_connect_to_api_cache_miss(api_instance):
    """Тест _connect_to_api с промахом кэша (строки 33-38)"""
    test_data = {'items': [{'id': 'new'}]}
    api_instance.connector.connect.return_value = test_data

    result = api_instance._connect_to_api("test_url", {})
    assert result == test_data
    api_instance.cache.save_response.assert_called_once_with("hh", {}, test_data)


def test_get_vacancies_page(api_instance):
    """Тест get_vacancies_page (строки 42-48)"""
    test_data = {'items': [{'id': '1'}]}
    api_instance._connect_to_api = MagicMock(return_value=test_data)

    result = api_instance.get_vacancies_page("Python", 0)
    assert result == test_data['items']
    api_instance._connect_to_api.assert_called_once()


def test_clear_cache(api_instance):
    """Тест clear_cache (строка 78)"""
    api_instance.clear_cache()
    api_instance.cache.clear.assert_called_once_with("hh")


def test_get_vacancies_simplified():
    """Упрощенный тест с моком пагинатора"""
    api = HeadHunterAPI()
    api._connect_to_api = MagicMock(return_value={
        'items': [{"id": "1"}],
        'pages': 1,
        'found': 1
    })
    api.paginator.paginate = MagicMock(return_value=[{"id": "1"}])

    results = api.get_vacancies(search_query="Python")
    assert len(results) == 1
    assert results[0]['id'] == "1"


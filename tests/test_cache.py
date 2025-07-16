
import time
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import pytest
from src.utils.cache import simple_cache, FileCache


def test_simple_cache_basic_functionality():
    """Test that cache stores and returns results correctly."""
    call_count = 0

    @simple_cache()
    def test_func(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    # Первый вызов - должен выполниться функция
    assert test_func(2) == 4
    assert call_count == 1

    # Повторный вызов с теми же аргументами - должен вернуть из кэша
    assert test_func(2) == 4
    assert call_count == 1  # Счетчик не увеличился


def test_simple_cache_with_different_args():
    """Test cache works with different arguments."""
    call_count = 0

    @simple_cache()
    def test_func(x):
        nonlocal call_count
        call_count += 1
        return x ** 2

    assert test_func(3) == 9
    assert test_func(4) == 16
    assert call_count == 2  # Должны быть два вызова


def test_simple_cache_ttl_expiration(monkeypatch):
    """Test that cache expires after TTL."""
    call_count = 0
    fake_time = 0

    def mock_time():
        return fake_time

    monkeypatch.setattr(time, 'time', mock_time)

    @simple_cache(ttl=3600)
    def test_func(x):
        nonlocal call_count
        call_count += 1
        return x + 1

    # Первый вызов
    assert test_func(5) == 6
    assert call_count == 1

    # Вызов до истечения TTL
    fake_time = 3599  # Меньше 1 часа
    assert test_func(5) == 6
    assert call_count == 1  # Из кэша

    # Вызов после истечения TTL
    fake_time = 3601  # Больше 1 часа
    assert test_func(5) == 6
    assert call_count == 2  # Снова выполнилась функция


def test_cache_decorator_with_ttl():
    """Тест кэширования с истечением TTL"""
    @simple_cache(ttl=1)
    def slow_function(x):
        time.sleep(0.1)
        return x * 2

    # Первый вызов - функция выполняется
    start_time = time.time()
    result = slow_function(5)
    first_call_time = time.time() - start_time
    assert result == 10
    assert first_call_time >= 0.1

    # Второй вызов - берется из кэша
    start_time = time.time()
    result = slow_function(5)
    second_call_time = time.time() - start_time
    assert result == 10
    assert second_call_time < 0.05  # Значительно быстрее

    # Ждем истечения TTL
    time.sleep(1.1)

    # Третий вызов - функция выполняется снова
    start_time = time.time()
    result = slow_function(5)
    third_call_time = time.time() - start_time
    assert result == 10
    assert third_call_time >= 0.1


@pytest.fixture
def temp_cache_dir():
    """Фикстура для создания временной директории кэша"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def test_file_cache_initialization_with_default_dir():
    """Тест инициализации FileCache с директорией по умолчанию"""
    cache = FileCache()
    assert cache.cache_dir == Path("data/cache/hh")


def test_file_cache_write_error_handling(temp_cache_dir):
    """Тест обработки ошибок записи"""
    cache = FileCache(temp_cache_dir)
    
    with patch('builtins.open', side_effect=OSError("Write error")):
        with pytest.raises(OSError):
            cache.save_response("test", {"param": "value"}, {"data": "test"})


def test_file_cache_read_error_handling(temp_cache_dir):
    """Тест обработки ошибок чтения"""
    cache = FileCache(temp_cache_dir)
    
    # Создаем файл с невалидным JSON
    test_file = Path(temp_cache_dir) / "test_invalid.json"
    test_file.write_text("invalid json content")
    
    with patch.object(cache, '_generate_params_hash', return_value='invalid'):
        result = cache.load_response("test", {"param": "value"})
        # Должен вернуть None при ошибке чтения
        assert result is None


def test_file_cache_json_encoding_error(temp_cache_dir):
    """Тест обработки ошибок кодирования JSON"""
    cache = FileCache(temp_cache_dir)
    
    # Создаем объект, который нельзя сериализовать в JSON
    class NonSerializable:
        pass
    
    with pytest.raises(TypeError):
        cache.save_response("test", {"param": "value"}, NonSerializable())


def test_file_cache_file_operations_coverage(temp_cache_dir):
    """Тест покрытия файловых операций"""
    cache = FileCache(temp_cache_dir)
    
    # Тестируем сохранение с различными типами данных
    test_data = {
        "string": "test",
        "number": 123,
        "boolean": True,
        "null": None,
        "list": [1, 2, 3],
        "dict": {"nested": "value"}
    }
    
    params = {"test": "complex_data"}
    filepath = cache.save_response("complex", params, test_data)
    
    # Проверяем что файл создан
    assert filepath.exists()
    
    # Проверяем содержимое файла напрямую
    with open(filepath, 'r', encoding='utf-8') as f:
        saved_content = json.load(f)
    
    assert saved_content["meta"]["params"] == params
    assert saved_content["data"] == test_data
    
    # Тестируем загрузку
    loaded = cache.load_response("complex", params)
    assert loaded["data"] == test_data


def test_file_cache_save_and_load_response(temp_cache_dir):
    """Тест сохранения и загрузки ответа"""
    cache = FileCache(temp_cache_dir)

    # Сохраняем ответ
    params = {"text": "python", "area": 1}
    data = {"items": [{"title": "Python Developer"}]}

    filepath = cache.save_response("hh", params, data)
    assert filepath.exists()

    # Загружаем ответ
    loaded = cache.load_response("hh", params)
    assert loaded is not None
    assert loaded["meta"]["params"] == params
    assert loaded["data"] == data


def test_file_cache_load_nonexistent_response(temp_cache_dir):
    """Тест загрузки несуществующего ответа"""
    cache = FileCache(temp_cache_dir)

    params = {"text": "nonexistent", "area": 1}
    loaded = cache.load_response("hh", params)
    assert loaded is None


def test_file_cache_clear_all(temp_cache_dir):
    """Тест очистки всего кэша"""
    cache = FileCache(temp_cache_dir)

    # Создаем несколько файлов кэша
    cache.save_response("hh", {"text": "python"}, {"data": 1})
    cache.save_response("sj", {"text": "java"}, {"data": 2})

    # Проверяем что файлы созданы
    files_before = list(cache.cache_dir.glob("*.json"))
    assert len(files_before) == 2

    # Очищаем весь кэш
    cache.clear()

    # Проверяем что все файлы удалены
    files_after = list(cache.cache_dir.glob("*.json"))
    assert len(files_after) == 0


def test_file_cache_clear_specific_source(temp_cache_dir):
    """Тест очистки кэша для конкретного источника"""
    cache = FileCache(temp_cache_dir)

    # Создаем файлы для разных источников
    cache.save_response("hh", {"text": "python"}, {"data": 1})
    cache.save_response("sj", {"text": "java"}, {"data": 2})

    # Очищаем кэш только для HH
    cache.clear("hh")

    # Проверяем что остался только файл SJ
    remaining_files = list(cache.cache_dir.glob("*.json"))
    assert len(remaining_files) == 1
    assert "sj_" in remaining_files[0].name


def test_file_cache_generate_params_hash():
    """Тест генерации хеша параметров"""
    # Одинаковые параметры должны давать одинаковый хеш
    params1 = {"text": "python", "area": 1}
    params2 = {"area": 1, "text": "python"}  # Порядок не важен

    hash1 = FileCache._generate_params_hash(params1)
    hash2 = FileCache._generate_params_hash(params2)
    assert hash1 == hash2

    # Разные параметры должны давать разные хеши
    params3 = {"text": "java", "area": 1}
    hash3 = FileCache._generate_params_hash(params3)
    assert hash1 != hash3


def test_file_cache_ensure_dir_exists(tmp_path):
    """Тест создания директорий"""
    cache_dir = tmp_path / "deep" / "nested" / "cache"
    cache = FileCache(str(cache_dir))

    assert cache_dir.exists()
    assert cache_dir.is_dir()


def test_file_cache_save_response_creates_file(temp_cache_dir):
    """Тест создания файла при сохранении ответа"""
    cache = FileCache(temp_cache_dir)
    
    params = {"text": "python", "area": 1}
    data = {"items": [{"title": "Python Developer"}]}
    
    filepath = cache.save_response("hh", params, data)
    
    assert filepath.exists()
    assert filepath.is_file()
    assert "hh_" in filepath.name
    assert filepath.suffix == ".json"


def test_file_cache_load_response_file_not_found(temp_cache_dir):
    """Тест загрузки несуществующего файла"""
    cache = FileCache(temp_cache_dir)
    
    result = cache.load_response("nonexistent", {"param": "value"})
    assert result is None


def test_file_cache_save_and_load_cycle(temp_cache_dir):
    """Тест полного цикла сохранения и загрузки"""
    cache = FileCache(temp_cache_dir)
    
    # Тестируем различные типы данных
    test_cases = [
        {"params": {"text": "python"}, "data": {"items": []}},
        {"params": {"area": 1, "per_page": 50}, "data": {"total": 100}},
        {"params": {"salary": 100000}, "data": {"vacancies": ["job1", "job2"]}}
    ]
    
    for case in test_cases:
        # Сохраняем
        filepath = cache.save_response("test_source", case["params"], case["data"])
        assert filepath.exists()
        
        # Загружаем
        loaded = cache.load_response("test_source", case["params"])
        assert loaded is not None
        assert loaded["meta"]["params"] == case["params"]
        assert loaded["data"] == case["data"]

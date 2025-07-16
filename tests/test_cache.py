import time
from src.utils.cache import simple_cache


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

    def test_cache_decorator_with_ttl(self):
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

    def test_file_cache_save_and_load_response(self, temp_cache_dir):
        """Тест сохранения и загрузки ответа"""
        from src.utils.file_handlers import FileCache # Import FileCache here to avoid circular dependency

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

    def test_file_cache_load_nonexistent_response(self, temp_cache_dir):
        """Тест загрузки несуществующего ответа"""
        from src.utils.file_handlers import FileCache # Import FileCache here to avoid circular dependency
        cache = FileCache(temp_cache_dir)

        params = {"text": "nonexistent", "area": 1}
        loaded = cache.load_response("hh", params)
        assert loaded is None

    def test_file_cache_clear_all(self, temp_cache_dir):
        """Тест очистки всего кэша"""
        from src.utils.file_handlers import FileCache # Import FileCache here to avoid circular dependency
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

    def test_file_cache_clear_specific_source(self, temp_cache_dir):
        """Тест очистки кэша для конкретного источника"""
        from src.utils.file_handlers import FileCache # Import FileCache here to avoid circular dependency
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

    def test_file_cache_generate_params_hash(self):
        """Тест генерации хеша параметров"""
        from src.utils.file_handlers import FileCache # Import FileCache here to avoid circular dependency
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

    def test_file_cache_ensure_dir_exists(self, tmp_path):
        """Тест создания директорий"""
        from src.utils.file_handlers import FileCache # Import FileCache here to avoid circular dependency
        cache_dir = tmp_path / "deep" / "nested" / "cache"
        cache = FileCache(str(cache_dir))

        assert cache_dir.exists()
        assert cache_dir.is_dir()
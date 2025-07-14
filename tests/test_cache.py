import time
from src.decorators.cache import simple_cache


def test_simple_cache_basic_functionality():
    """Test that cache stores and returns results correctly."""
    call_count = 0

    @simple_cache
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

    @simple_cache
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

    @simple_cache
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

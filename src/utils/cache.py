import hashlib
import json
import time
from functools import wraps
from pathlib import Path
from typing import Any, Dict, Optional, Callable, Tuple

from .env_loader import EnvLoader


def simple_cache(ttl: Optional[int] = None, max_size: int = 1000) -> Callable:
    """
    Декоратор для кэширования результатов функций в памяти с ограничением размера
    :param ttl: Время жизни кэша в секундах (по умолчанию 1 час)
    :param max_size: Максимальный размер кэша (по умолчанию 1000 элементов)
    :return: Декорированная функция
    """

    def decorator(func: Callable) -> Callable:
        cache: Dict[Tuple, Tuple[float, Any]] = {}
        access_times: Dict[Tuple, float] = {}  # Для LRU очистки

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Получаем TTL из переменных окружения или используем переданное значение
            actual_ttl = ttl if ttl is not None else EnvLoader.get_env_var_int('CACHE_TTL', 3600)
            current_time = time.time()

            cache_key = (args, frozenset(kwargs.items()))

            # Проверяем существующий кэш
            if cache_key in cache:
                timestamp, result = cache[cache_key]
                if current_time - timestamp < actual_ttl:
                    access_times[cache_key] = current_time  # Обновляем время доступа
                    return result
                else:
                    # Удаляем устаревший элемент
                    del cache[cache_key]
                    if cache_key in access_times:
                        del access_times[cache_key]

            # Проверяем размер кэша
            if len(cache) >= max_size:
                # Удаляем самый старый элемент (LRU)
                oldest_key = min(access_times.keys(), key=lambda k: access_times[k])
                del cache[oldest_key]
                del access_times[oldest_key]

            # Выполняем функцию и кэшируем результат
            result = func(*args, **kwargs)
            cache[cache_key] = (current_time, result)
            access_times[cache_key] = current_time
            return result

        def clear_cache() -> None:
            """Очистка кэша функции"""
            cache.clear()
            access_times.clear()

        def cache_info(actual_ttl=None) -> Dict[str, Any]:
            """Информация о состоянии кэша"""
            return {
                'size': len(cache),
                'max_size': max_size,
                'ttl': ttl if ttl is not None else EnvLoader.get_env_var_int('CACHE_TTL', 3600)
            }

        wrapper.clear_cache = clear_cache
        wrapper.cache_info = cache_info
        return wrapper

    return decorator


class FileCache:
    """Класс для файлового кэширования API-ответов"""

    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self._ensure_dir_exists()

    def _ensure_dir_exists(self) -> None:
        """Создает все необходимые директории"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _generate_params_hash(params: Dict[str, Any]) -> str:
        """
        Генерация хеша параметров
        :param params: Словарь параметров запроса
        :return: Строка с hex-представлением MD5 хеша
        """
        params_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(params_str.encode()).hexdigest()

    def save_response(self, source: str, params: Dict[str, Any], data: Any) -> Path:
        """Сохранение сырого ответа API в файл"""
        params_hash = self._generate_params_hash(params)
        filename = f"{source}_{params_hash}.json"
        filepath = self.cache_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "meta": {"params": params},
                "data": data
            }, f, ensure_ascii=False, indent=2)

        return filepath

    def load_response(self, source: str, params: Dict[str, Any]) -> Optional[Dict]:
        """Загрузка кэшированного ответа"""
        try:
            params_hash = self._generate_params_hash(params)
            filename = f"{source}_{params_hash}.json"
            filepath = self.cache_dir / filename

            if not filepath.exists():
                return None

            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError, Exception):
            return None

    def clear(self, source: Optional[str] = None) -> None:
        """Очистка кэша"""
        pattern = f"{source}_*.json" if source else "*.json"
        for file in self.cache_dir.glob(pattern):
            file.unlink()
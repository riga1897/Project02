import json
import time
from functools import wraps
from pathlib import Path
from typing import Any, Dict, Optional, Callable, Tuple
import hashlib


def simple_cache(ttl: int = 3600) -> Callable:
    """
    Декоратор для кэширования результатов функций в памяти
    :param ttl: Время жизни кэша в секундах (по умолчанию 1 час)
    :return: Декорированная функция
    """

    def decorator(func: Callable) -> Callable:
        cache: Dict[Tuple, Tuple[float, Any]] = {}

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache_key = (args, frozenset(kwargs.items()))

            if cache_key in cache:
                timestamp, result = cache[cache_key]
                if time.time() - timestamp < ttl:
                    return result

            result = func(*args, **kwargs)
            cache[cache_key] = (time.time(), result)
            return result

        def clear_cache() -> None:
            """Очистка кэша функции"""
            cache.clear()

        wrapper.clear_cache = clear_cache
        return wrapper

    return decorator


class FileCache:
    """Класс для файлового кэширования API-ответов"""

    def __init__(self, cache_dir: str = "data/cache/hh"):
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
        params_hash = self._generate_params_hash(params)
        filename = f"{source}_{params_hash}.json"
        filepath = self.cache_dir / filename

        if not filepath.exists():
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    def clear(self, source: Optional[str] = None) -> None:
        """Очистка кэша"""
        pattern = f"{source}_*.json" if source else "*.json"
        for file in self.cache_dir.glob(pattern):
            file.unlink()

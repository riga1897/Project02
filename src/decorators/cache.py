from functools import wraps
from typing import Any, Dict, Tuple
import time


def simple_cache(func):
    """Simple caching decorator with time-based expiration."""
    cache: Dict[Tuple, Tuple[float, Any]] = {}
    ttl: float = 3600  # 1 hour in seconds

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        cache_key = (args, frozenset(kwargs.items()))

        if cache_key in cache:
            cached_time, result = cache[cache_key]
            if time.time() - cached_time < ttl:
                return result

        result = func(*args, **kwargs)
        cache[cache_key] = (time.time(), result)
        return result

    return wrapper

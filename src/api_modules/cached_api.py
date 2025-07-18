
import logging
from pathlib import Path
from typing import Dict, Union
from abc import ABC

from .base_api import BaseAPI
from src.utils.cache import FileCache

logger = logging.getLogger(__name__)


class CachedAPI(BaseAPI, ABC):
    """Base class with shared caching logic for API modules"""
    
    DEFAULT_CACHE_DIR = None  # To be overridden by subclasses
    
    def __init__(self, cache_dir: str = None):
        """Initialize with caching support"""
        if cache_dir is None and self.DEFAULT_CACHE_DIR is None:
            raise ValueError("cache_dir must be provided or DEFAULT_CACHE_DIR must be set")
        
        cache_directory = cache_dir or self.DEFAULT_CACHE_DIR
        self.cache = FileCache(cache_directory)
        self._init_cache(cache_directory)
    
    def _init_cache(self, cache_dir: str) -> None:
        """Initialize cache directory with validation"""
        try:
            Path(cache_dir).mkdir(parents=True, exist_ok=True)
            logger.info(f"Cache directory initialized: {cache_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize cache: {e}")
            raise

    def _connect_to_api(self, url: str, params: Dict, source_name: str) -> Dict:
        """Execute API request with caching and enhanced error handling"""
        cache_key = self._generate_cache_key(params)

        try:
            # Проверяем кэш
            cached = self.cache.load_response(source_name, cache_key)
            if cached and self.validate_response(cached.get("data")):
                logger.debug(f"Cache hit for {source_name} params: {params}")
                return cached["data"]

            # Делаем реальный API запрос если кэш отсутствует
            logger.info(f"Making API request to {url} with params: {params}")
            response = self.connector.connect(url, params)

            if not self.validate_response(response):
                logger.error(f"Invalid API response structure: {response}")
                return self._get_empty_response()

            # Сохраняем в кэш
            self.cache.save_response(source_name, cache_key, response)
            logger.info(f"Response cached for {source_name} params: {params}")
            return response

        except Exception as e:
            logger.error(f"API connection failed: {e}")
            # Попробуем сделать запрос без кэша
            try:
                logger.info("Attempting direct API call without cache...")
                response = self.connector.connect(url, params)
                if self.validate_response(response):
                    return response
            except Exception as e2:
                logger.error(f"Direct API call also failed: {e2}")
            return self._get_empty_response()

    def _generate_cache_key(self, params: Dict) -> str:
        """Generate consistent cache key from params"""
        return str(sorted(params.items()))

    def _get_empty_response(self) -> Dict:
        """Get empty response structure - to be overridden by subclasses"""
        return {'items': []}
    
    def clear_cache(self, source_name: str) -> None:
        """
        Очищает кэш API

        Удаляет все сохраненные ответы API из кэша для освобождения места
        и обеспечения получения актуальных данных при следующих запросах.
        """
        try:
            from src.utils.cache_manager import cache_manager
            cache_manager.clear_cache_for_source(source_name)
            logger.info(f"Кэш {source_name} очищен")
        except Exception as e:
            logger.error(f"Ошибка очистки кэша {source_name}: {e}")

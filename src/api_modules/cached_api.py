
import logging
from pathlib import Path
from typing import Dict, Union, List, Optional
from abc import ABC, abstractmethod

from .base_api import BaseAPI
from src.utils.cache import FileCache

logger = logging.getLogger(__name__)


class CachedAPI(BaseAPI, ABC):
    """Абстрактный базовый класс для API с кэшированием"""

    def __init__(self, cache_dir: str):
        """
        Инициализация базового API с кэшем

        Args:
            cache_dir: Директория для кэша
        """
        super().__init__()
        self.cache_dir = Path(cache_dir)
        self._init_cache()

    def _init_cache(self) -> None:
        """Инициализация кэша"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache = FileCache(str(self.cache_dir))

    def _generate_cache_key(self, url: str, params: Dict, api_prefix: str) -> str:
        """
        Генерация ключа кэша на основе URL и параметров

        Args:
            url: URL запроса
            params: Параметры запроса
            api_prefix: Префикс API (hh, sj)

        Returns:
            str: Ключ кэша
        """
        import hashlib
        
        # Сортируем параметры для консистентности
        sorted_params = sorted(params.items())
        cache_string = f"{url}_{sorted_params}"
        
        # Создаем хэш
        hash_object = hashlib.md5(cache_string.encode())
        hash_hex = hash_object.hexdigest()
        
        return f"{api_prefix}_{hash_hex}"

    def _connect_to_api(self, url: str, params: Dict, api_prefix: str) -> Dict:
        """
        Подключение к API с использованием кэша

        Args:
            url: URL для запроса
            params: Параметры запроса
            api_prefix: Префикс для кэша

        Returns:
            Dict: Ответ API
        """
        # Генерируем ключ кэша
        cache_key = self._generate_cache_key(url, params, api_prefix)
        
        # Проверяем кэш
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            logger.debug(f"Данные получены из кэша: {cache_key}")
            return cached_data
        
        # Если кэш пуст, делаем запрос
        try:
            data = self.connector.connect(url, params)
            
            # Сохраняем в кэш
            self.cache.set(cache_key, data)
            logger.debug(f"Данные сохранены в кэш: {cache_key}")
            
            return data
            
        except Exception as e:
            logger.error(f"Ошибка API запроса: {e}")
            # Возвращаем пустой ответ соответствующей структуры
            return self._get_empty_response()

    def clear_cache(self, api_prefix: str) -> None:
        """
        Очистка кэша для конкретного API

        Args:
            api_prefix: Префикс API (hh, sj)
        """
        try:
            if self.cache_dir.exists():
                for cache_file in self.cache_dir.glob(f"{api_prefix}_*.json"):
                    cache_file.unlink()
                logger.info(f"Кэш {api_prefix} очищен")
        except Exception as e:
            logger.error(f"Ошибка очистки кэша {api_prefix}: {e}")

    @abstractmethod
    def _get_empty_response(self) -> Dict:
        """Получить пустую структуру ответа для конкретного API"""
        pass

    @abstractmethod
    def _validate_vacancy(self, vacancy: Dict) -> bool:
        """Валидация структуры вакансии для конкретного API"""
        pass

    @abstractmethod
    def get_vacancies_page(self, search_query: str, page: int = 0, **kwargs) -> List[Dict]:
        """Получить одну страницу вакансий"""
        pass

    @abstractmethod
    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict]:
        """Получить все вакансии с пагинацией"""
        pass

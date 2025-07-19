
import logging
from pathlib import Path
from typing import Dict, Union, List, Optional
from abc import ABC, abstractmethod

from .base_api import BaseAPI
from src.utils.cache import FileCache, simple_cache

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

    

    @simple_cache(ttl=300)  # Кэш в памяти на 5 минут
    def _cached_api_request(self, url: str, params_hash: str, api_prefix: str) -> Dict:
        """
        Кэшированный API запрос в памяти
        
        Args:
            url: URL для запроса
            params_hash: Хеш параметров для уникальности
            api_prefix: Префикс для логирования
            
        Returns:
            Dict: Ответ API
        """
        # Восстанавливаем параметры из оригинального вызова
        params = getattr(self, '_current_params', {})
        
        try:
            data = self.connector.connect(url, params)
            logger.debug(f"Данные получены из API для {api_prefix}")
            return data
        except Exception as e:
            logger.error(f"Ошибка API запроса: {e}")
            return self._get_empty_response()

    def __connect_to_api(self, url: str, params: Dict, api_prefix: str) -> Dict:
        """
        Подключение к API с многоуровневым кэшированием

        Args:
            url: URL для запроса
            params: Параметры запроса
            api_prefix: Префикс для кэша

        Returns:
            Dict: Ответ API
        """
        # Сохраняем параметры для кэшированного метода
        self._current_params = params
        
        # Создаем хеш параметров для уникальности кэша в памяти
        params_hash = self.cache._generate_params_hash(params)
        
        # 1. Проверяем кэш в памяти (быстрее всего)
        try:
            memory_result = self._cached_api_request(url, params_hash, api_prefix)
            if memory_result != self._get_empty_response():
                logger.debug(f"Данные получены из кэша в памяти для {api_prefix}")
                return memory_result
        except Exception:
            pass
        
        # 2. Проверяем файловый кэш
        cached_response = self.cache.load_response(api_prefix, params)
        if cached_response is not None:
            logger.debug(f"Данные получены из файлового кэша для {api_prefix}")
            data = cached_response.get('data', self._get_empty_response())
            # Также кэшируем в памяти для следующих запросов
            self._cached_api_request(url, params_hash, api_prefix)
            return data
        
        # 3. Делаем реальный запрос к API
        try:
            data = self._cached_api_request(url, params_hash, api_prefix)
            
            # Сохраняем в файловый кэш
            if data != self._get_empty_response():
                self.cache.save_response(api_prefix, params, data)
                logger.debug(f"Данные сохранены в файловый кэш для {api_prefix}")
            
            return data
            
        except Exception as e:
            logger.error(f"Ошибка многоуровневого кэширования: {e}")
            return self._get_empty_response()

    def clear_cache(self, api_prefix: str) -> None:
        """
        Очистка кэша для конкретного API

        Args:
            api_prefix: Префикс API (hh, sj)
        """
        try:
            # Очищаем файловый кэш
            self.cache.clear(api_prefix)
            
            # Очищаем кэш в памяти
            if hasattr(self._cached_api_request, 'clear_cache'):
                self._cached_api_request.clear_cache()
                
            logger.info(f"Кэш {api_prefix} очищен (файловый и в памяти)")
        except Exception as e:
            logger.error(f"Ошибка очистки кэша {api_prefix}: {e}")

    @abstractmethod
    def _get_empty_response(self) -> Dict:
        """Получить пустую структуру ответа для конкретного API"""

    @abstractmethod
    def _validate_vacancy(self, vacancy: Dict) -> bool:
        """Валидация структуры вакансии для конкретного API"""

    @abstractmethod
    def get_vacancies_page(self, search_query: str, page: int = 0, **kwargs) -> List[Dict]:
        """Получить одну страницу вакансий"""

    @abstractmethod
    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict]:
        """Получить все вакансии с пагинацией"""


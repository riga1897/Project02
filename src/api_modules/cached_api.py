"""
Модуль для работы с кэшированными API запросами.

Реализует многоуровневое кэширование для оптимизации работы с внешними API:
- Кэш в памяти для быстрого доступа к недавним запросам
- Файловый кэш для долгосрочного хранения данных
- Автоматическое управление временем жизни кэша
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List

from src.utils.cache import FileCache, simple_cache
from .base_api import BaseJobAPI

logger = logging.getLogger(__name__)


class CachedAPI(BaseJobAPI, ABC):
    """
    Абстрактный базовый класс для API с кэшированием

    Расширяет BaseJobAPI функциональностью многоуровневого кэширования:
    - Кэш в памяти для быстрого доступа
    - Файловый кэш для долгосрочного хранения
    """

    def __init__(self, cache_dir: str):
        """
        Инициализация базового API с кэшем

        Args:
            cache_dir: Директория для хранения файлового кэша
        """
        super().__init__()
        self.cache_dir = Path(cache_dir)
        self._init_cache()

    def _init_cache(self) -> None:
        """
        Инициализация кэша

        Создает директорию для кэша и инициализирует файловый кэш.
        """
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache = FileCache(str(self.cache_dir))



    @simple_cache(ttl=300)  # Кэш в памяти на 5 минут
    def _cached_api_request(self, url: str, params: Dict, api_prefix: str) -> Dict:
        """
        Кэшированный API запрос в памяти

        Args:
            url: URL для запроса
            params: Параметры запроса
            api_prefix: Префикс для логирования

        Returns:
            Dict: Ответ API
        """
        try:
            data = self.connector._APIConnector__connect(url, params)
            logger.debug(f"Данные получены из API для {api_prefix} (кэш в памяти)")
            return data
        except Exception as e:
            logger.error(f"Ошибка API запроса: {e}")
            return self._get_empty_response()

    def __connect_to_api(self, url: str, params: Dict, api_prefix: str) -> Dict:
        """
        Подключение к API с многоуровневым кэшированием

        Реализует стратегию кэширования в три уровня:
        1. Проверка кэша в памяти (самый быстрый)
        2. Проверка файлового кэша (средний по скорости)
        3. Реальный запрос к API с параллельным сохранением в память и на диск

        Args:
            url: URL для запроса
            params: Параметры запроса
            api_prefix: Префикс для кэша (hh, sj и т.д.)

        Returns:
            Dict: Ответ API или пустая структура при ошибке
        """
        # 1. Проверяем кэш в памяти (быстрее всего)
        try:
            memory_result = self._cached_api_request(url, params, api_prefix)
            if memory_result != self._get_empty_response():
                logger.debug(f"Данные получены из кэша в памяти для {api_prefix}")
                return memory_result
        except Exception as e:
            # Игнорируем ошибки кэша в памяти, переходим к файловому кэшу
            logging.warning(f"Ошибка кэша памяти: {str(e)}. Переключаемся на файловый кэш")

        # 2. Проверяем файловый кэш
        cached_response = self.cache.load_response(api_prefix, params)
        if cached_response is not None:
            logger.debug(f"Данные получены из файлового кэша для {api_prefix}")
            data = cached_response.get('data', self._get_empty_response())
            return data

        # 3. Делаем реальный запрос к API с параллельным кэшированием
        try:
            # Делаем прямой запрос к API
            data = self.connector._APIConnector__connect(url, params)
            logger.debug(f"Данные получены из API для {api_prefix}")

            # Параллельно сохраняем в файловый кэш только валидные данные
            if data and data != self._get_empty_response():
                # Сохраняем в файловый кэш в data/cache/
                self.cache.save_response(api_prefix, params, data)
                logger.debug(f"Данные сохранены в файловый кэш data/cache/ для {api_prefix}")

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

    def get_cache_status(self, api_prefix: str) -> Dict:
        """
        Получение статуса кэша для диагностики

        Args:
            api_prefix: Префикс API (hh, sj)

        Returns:
            Dict: Информация о состоянии кэша
        """
        try:
            cache_files = list(self.cache_dir.glob(f"{api_prefix}_*.json"))
            memory_info = {}
            if hasattr(self._cached_api_request, 'cache_info'):
                memory_info = self._cached_api_request.cache_info()

            return {
                'cache_dir': str(self.cache_dir),
                'cache_dir_exists': self.cache_dir.exists(),
                'file_cache_count': len(cache_files),
                'cache_files': [f.name for f in cache_files],
                'memory_cache': memory_info
            }
        except Exception as e:
            logger.error(f"Ошибка получения статуса кэша: {e}")
            return {'error': str(e)}

    def __connect(self, url: str, params: Dict = {}) -> Dict:
        """
        Выполнение HTTP-запроса к API HeadHunter

        Args:
            url: URL для запроса
            params: Параметры запроса

        Returns:
            Dict: Ответ API
        """
        try:
            # Делаем запрос к HH API через connector
            data = self.connector._APIConnector__connect(url, params)
            return data
        except Exception as e:
            logger.error(f"Ошибка при подключении к API: {e}")
            return {}

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
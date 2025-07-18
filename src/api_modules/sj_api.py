import requests
import time
import logging
import os
from typing import Dict, List, Union, Optional
from .base_api import BaseAPI
from src.config.sj_api_config import SJAPIConfig
from src.utils.cache import simple_cache, FileCache
from src.utils.env_loader import EnvLoader
from src.utils.paginator import Paginator

logger = logging.getLogger(__name__)


class SuperJobAPI(BaseAPI):
    """SuperJob API для поиска вакансий"""

    def __init__(self, config: Optional[SJAPIConfig] = None):
        """
        Инициализация SuperJob API

        Args:
            config: Конфигурация SuperJob API
        """
        self.base_url = "https://api.superjob.ru/2.0"
        self.config = config or SJAPIConfig()

        # Получаем API ключ из переменных окружения (включая .env файл)
        api_key = EnvLoader.get_env_var('SUPERJOB_API_KEY', 'v3.r.137440105.example.test_tool')

        self.headers = {
            "X-Api-App-Id": api_key,
            "User-Agent": "VacancySearchApp/1.0"
        }
        self.request_delay = 0.5

        # Инициализируем файловый кэш для SuperJob
        self.file_cache = FileCache("data/cache/sj")

        # Логируем, какой ключ используется (скрываем реальный ключ)
        if api_key == 'v3.r.137440105.example.test_tool':
            logger.warning("Используется тестовый API ключ SuperJob. Для полной функциональности добавьте реальный ключ в переменную окружения SUPERJOB_API_KEY")
        else:
            logger.info("Используется пользовательский API ключ SuperJob")

        self.paginator = Paginator()

    def _connect_to_api(self, url: str, params: Dict, max_retries: int = 3) -> Union[Dict, str]:
        """
        Подключение к API SuperJob с обработкой ошибок и повторными попытками

        Args:
            url: URL для запроса
            params: Параметры запроса
            max_retries: Максимальное количество повторных попыток

        Returns:
            Dict: Ответ API в виде словаря
            str: Сообщение об ошибке
        """
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    wait_time = 2 ** attempt  # Экспоненциальная задержка
                    logger.info(f"Повторная попытка {attempt}/{max_retries} через {wait_time} сек...")
                    time.sleep(wait_time)

                logger.debug(f"Making request to: {url} (attempt {attempt + 1})")
                logger.debug(f"Request params: {params}")
                logger.debug(f"Request headers: {self.headers}")

                time.sleep(self.request_delay)

                response = requests.get(
                    url, 
                    params=params, 
                    headers=self.headers, 
                    timeout=30  # Увеличиваем timeout
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    logger.warning("Rate limit exceeded, waiting...")
                    time.sleep(5)
                    if attempt < max_retries:
                        continue
                    return "Rate limit exceeded"
                elif response.status_code == 403:
                    logger.error("Access forbidden - check API key")
                    return "Access forbidden"
                else:
                    logger.error(f"HTTP {response.status_code}: {response.text}")
                    if attempt < max_retries:
                        continue
                    return f"HTTP error: {response.status_code}"

            except requests.exceptions.Timeout:
                logger.error(f"Request timeout (attempt {attempt + 1})")
                if attempt < max_retries:
                    continue
                return "Request timeout"
            except requests.exceptions.ConnectionError:
                logger.error(f"Connection error (attempt {attempt + 1})")
                if attempt < max_retries:
                    continue
                return "Connection error"
            except Exception as e:
                logger.error(f"Unexpected error (attempt {attempt + 1}): {e}")
                if attempt < max_retries:
                    continue
                return f"Unexpected error: {e}"

        return "Max retries exceeded"

    def get_vacancies_page(self, search_query: str, page: int = 0, **kwargs) -> List[Dict]:
        """Get and validate single page of vacancies"""
        try:
            params = self.config.get_params(
                keyword=search_query,
                page=page,
                **kwargs
            )

            url = f"{self.base_url}/vacancies/"
            data = self._connect_to_api(url, params)

            if not data or not isinstance(data, dict):
                logger.error(f"Invalid response on page {page}")
                return []

            items = data.get('objects', [])
            for item in items:
                item["source"] = "superjob.ru"
            return items

        except Exception as e:
            logger.error(f"Failed to get vacancies page {page}: {e}")
            return []

    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict]:
        """Get all vacancies with pagination and validation"""
        try:
            # Initial request to get metadata
            initial_params = self.config.get_params(
                keyword=search_query,
                count=1,  # Get minimal data first
                **kwargs
            )
            url = f"{self.base_url}/vacancies/"

            logger.debug(f"SuperJob API URL: {url}")
            logger.debug(f"SuperJob API params: {initial_params}")
            logger.debug(f"SuperJob API headers: {self.headers}")

            initial_data = self._connect_to_api(url, initial_params)

            if not initial_data or not isinstance(initial_data, dict):
                logger.error("Invalid initial response format")
                return []

            total_found = initial_data.get('total', 0)
            more_available = initial_data.get('more', False)

            logger.debug(f"Total found: {total_found}")
            logger.debug(f"More available: {more_available}")

            if total_found == 0:
                logger.info("No vacancies found for query")
                return []

            # Calculate pages needed
            per_page = kwargs.get('count', 100)
            max_pages = kwargs.get('max_pages', 20)
            total_pages = min(
                max_pages,
                (total_found + per_page - 1) // per_page if total_found > 0 else 1
            )

            logger.info(f"Found {total_found} vacancies ({total_pages} pages to process)")

            # Process all pages using unified paginator with progress bar
            results = self.paginator.paginate(
                fetch_func=lambda p: self.get_vacancies_page(search_query, p, **kwargs),
                total_pages=total_pages
            )

            logger.info(f"Successfully processed {len(results)} vacancies")
            return results

        except KeyboardInterrupt:
            logger.info("Получение вакансий прервано пользователем")
            print("\nПолучение вакансий остановлено.")
            return []
        except Exception as e:
            logger.error(f"Failed to get vacancies: {e}")
            return []

    def clear_cache(self) -> None:
        """Очистка кэша SuperJob API"""
        try:
            # Очищаем файловый кэш
            self.file_cache.clear("sj")
            # Очищаем через менеджер кэша
            from src.utils.cache_manager import cache_manager
            cache_manager.clear_cache_for_source("sj")
            logger.info("Кэш SuperJob очищен")
        except Exception as e:
            logger.error(f"Ошибка очистки кэша SuperJob: {e}")
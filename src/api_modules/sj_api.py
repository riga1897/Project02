import requests
import time
import logging
import os
from typing import Dict, List, Union, Optional
from .base_api import BaseAPI
from src.config.sj_api_config import SJAPIConfig
from src.utils.cache import simple_cache, FileCache
from src.utils.env_loader import EnvLoader

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

    def _connect_to_api(self, url: str, params: Dict) -> Union[Dict, str]:
        """
        Подключение к API SuperJob с обработкой ошибок

        Args:
            url: URL для запроса
            params: Параметры запроса

        Returns:
            Dict: Ответ API в виде словаря
            str: Сообщение об ошибке
        """
        try:
            logger.debug(f"Making request to: {url}")
            logger.debug(f"Request params: {params}")
            logger.debug(f"Request headers: {self.headers}")

            time.sleep(self.request_delay)

            response = requests.get(
                url, 
                params=params, 
                headers=self.headers, 
                timeout=15
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logger.warning("Rate limit exceeded, waiting...")
                time.sleep(2)
                return "Rate limit exceeded"
            elif response.status_code == 403:
                logger.error("Access forbidden - check API key")
                return "Access forbidden"
            else:
                logger.error(f"HTTP {response.status_code}: {response.text}")
                return f"HTTP error: {response.status_code}"

        except requests.exceptions.Timeout:
            logger.error("Request timeout")
            return "Request timeout"
        except requests.exceptions.ConnectionError:
            logger.error("Connection error")
            return "Connection error"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return f"Unexpected error: {e}"

    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict]:
        """
        Получение вакансий по поисковому запросу

        Args:
            search_query: Поисковый запрос
            **kwargs: Дополнительные параметры поиска

        Returns:
            List[Dict]: Список вакансий
        """
        url = f"{self.base_url}/vacancies/"

        # Базовые параметры из конфигурации
        params = self.config.get_params(**kwargs)
        params["keyword"] = search_query

        # Проверяем кэш
        cache_key_params = {
            "query": search_query,
            "params": params
        }
        
        cached_data = self.file_cache.load_response("sj", cache_key_params)
        if cached_data:
            logger.info(f"Found cached data for SuperJob query: '{search_query}'")
            return cached_data.get("data", [])

        logger.info(f"Searching SuperJob vacancies for: '{search_query}'")
        logger.info(f"Request parameters: {params}")

        all_vacancies = []
        page = 0
        max_pages = kwargs.get('max_pages', 100)  # Еще больше увеличиваем количество страниц
        consecutive_empty_pages = 0
        max_empty_pages = 3  # Останавливаемся после 3 пустых страниц подряд

        while page < max_pages and consecutive_empty_pages < max_empty_pages:
            params["page"] = page

            logger.debug(f"Requesting page {page + 1}")

            response = self._connect_to_api(url, params)

            # Если получили строку - это ошибка
            if isinstance(response, str):
                logger.error(f"API error on page {page + 1}: {response}")
                break

            # Проверяем, что ответ является словарем и содержит данные
            if not isinstance(response, dict):
                logger.error(f"Invalid response type on page {page + 1}: {type(response)}")
                break

            if not response.get("objects") and page == 0:
                logger.warning(f"No 'objects' key in response on page {page + 1}")
                logger.debug(f"Response keys: {list(response.keys())}")
                break

            vacancies = response.get("objects", [])

            if not vacancies:
                consecutive_empty_pages += 1
                logger.info(f"Empty page {page + 1}, consecutive empty: {consecutive_empty_pages}")
                if consecutive_empty_pages >= max_empty_pages:
                    logger.info(f"Stopping after {consecutive_empty_pages} consecutive empty pages")
                    break
            else:
                consecutive_empty_pages = 0  # Сбрасываем счетчик пустых страниц
                
                # Добавляем источник к каждой вакансии
                for vacancy in vacancies:
                    vacancy["source"] = "superjob.ru"

                all_vacancies.extend(vacancies)
                logger.info(f"Page {page + 1}: found {len(vacancies)} vacancies")

            # Проверяем, есть ли еще страницы
            if not response.get("more", False) and not vacancies:
                logger.info("API indicates no more pages available")
                break

            page += 1

        logger.info(f"Total SuperJob vacancies found: {len(all_vacancies)}")
        
        # Сохраняем результаты в кэш
        if all_vacancies:
            self.file_cache.save_response("sj", cache_key_params, all_vacancies)
            logger.debug(f"Saved {len(all_vacancies)} SuperJob vacancies to cache")
        
        return all_vacancies

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
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
        
        # Используем более безопасный размер страницы
        params["count"] = min(params.get("count", 100), 100)

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
        
        # Добавляем отладочную информацию
        print(f"DEBUG: SuperJob API URL: {url}")
        print(f"DEBUG: SuperJob API params: {params}")
        print(f"DEBUG: SuperJob API headers: {self.headers}")

        all_vacancies = []
        page = 0
        max_pages = kwargs.get('max_pages', 20)  # Увеличиваем количество страниц
        consecutive_empty_pages = 0
        max_empty_pages = 3  # Увеличиваем терпимость к пустым страницам
        total_found = 0

        while page < max_pages and consecutive_empty_pages < max_empty_pages:
            params["page"] = page

            logger.debug(f"Requesting page {page + 1}")
            
            # Показываем прогресс
            if page == 0:
                print(f"🔍 Загружаем вакансии SuperJob...")
            else:
                print(f"📄 Загружаем страницу {page + 1}... (найдено: {len(all_vacancies)})")

            response = self._connect_to_api(url, params)
            
            # Добавляем отладочную информацию о ответе
            print(f"DEBUG: Response type: {type(response)}")
            if isinstance(response, dict):
                print(f"DEBUG: Response keys: {list(response.keys())}")
                print(f"DEBUG: Total found: {response.get('total', 'N/A')}")
                print(f"DEBUG: More available: {response.get('more', 'N/A')}")
                if response.get('objects'):
                    print(f"DEBUG: Objects count: {len(response.get('objects', []))}")
                else:
                    print("DEBUG: No 'objects' key or empty objects")

            # Если получили строку - это ошибка
            if isinstance(response, str):
                logger.error(f"API error on page {page + 1}: {response}")
                print(f"⚠️  Ошибка на странице {page + 1}: {response}")
                
                # Если это первая страница и есть ошибка - прерываем
                if page == 0:
                    break
                
                # Для последующих страниц - пытаемся продолжить с разными стратегиями
                if "Connection error" in response and page > 0:
                    logger.warning(f"Connection error on page {page + 1}, trying recovery strategies")
                    
                    # Стратегия 1: Уменьшаем размер страницы
                    if params.get("count", 100) > 20:
                        params["count"] = 20
                        print(f"🔄 Уменьшаем размер страницы до {params['count']} и повторяем...")
                        continue
                    
                    # Стратегия 2: Увеличиваем задержку
                    print(f"⏳ Увеличиваем задержку и повторяем...")
                    time.sleep(2)
                    
                    # Стратегия 3: Пропускаем эту страницу
                    if consecutive_empty_pages < max_empty_pages - 1:
                        consecutive_empty_pages += 1
                        page += 1
                        print(f"⏭️  Пропускаем страницу {page}, переходим к следующей...")
                        continue
                
                # Если ошибка критическая - останавливаемся
                break

            # Проверяем, что ответ является словарем и содержит данные
            if not isinstance(response, dict):
                logger.error(f"Invalid response type on page {page + 1}: {type(response)}")
                break

            if not response.get("objects") and page == 0:
                logger.warning(f"No 'objects' key in response on page {page + 1}")
                logger.debug(f"Response keys: {list(response.keys())}")
                print(f"DEBUG: Full response: {response}")
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
            has_more = response.get("more", False)
            if page == 0:  # Сохраняем общее количество с первой страницы
                total_found = response.get("total", 0)
            
            logger.debug(f"Page {page + 1}: has_more={has_more}, total_found={total_found}, current_total={len(all_vacancies)}")
            
            # Показываем прогресс
            if total_found > 0:
                progress = min(100, (len(all_vacancies) / total_found) * 100)
                print(f"📊 Прогресс: {len(all_vacancies)}/{total_found} ({progress:.1f}%)")
            
            # Останавливаемся если API сообщает что больше нет данных
            if not has_more:
                logger.info(f"API indicates no more pages available. Total processed: {len(all_vacancies)}")
                print(f"✅ Загрузка завершена - больше страниц нет")
                break

            page += 1

        logger.info(f"Total SuperJob vacancies found: {len(all_vacancies)}")
        
        # Финальная статистика
        if total_found > 0:
            coverage = (len(all_vacancies) / total_found) * 100
            print(f"📈 Итого загружено: {len(all_vacancies)} из {total_found} ({coverage:.1f}%)")
        else:
            print(f"📈 Итого загружено: {len(all_vacancies)} вакансий")

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
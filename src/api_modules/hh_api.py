# Adding docstrings to the clear_cache method in the HeadHunterAPI class.
from pathlib import Path
from typing import List, Dict, Optional, Union
import logging
from src.api_modules.cached_api import CachedAPI
from src.api_modules.get_api import APIConnector
from src.utils.paginator import Paginator
from src.config.api_config import APIConfig

logger = logging.getLogger(__name__)


class HeadHunterAPI(CachedAPI):
    """Enhanced HH API client with robust error handling and caching"""

    BASE_URL = "https://api.hh.ru/vacancies"
    DEFAULT_CACHE_DIR = "data/cache/hh"
    REQUIRED_VACANCY_FIELDS = {'name', 'alternate_url', 'salary'}

    def __init__(self, config: Optional[APIConfig] = None):
        super().__init__(self.DEFAULT_CACHE_DIR)  # Инициализируем кэш через родительский класс
        self.config = config or APIConfig()
        self.connector = APIConnector(self.config)
        self.paginator = Paginator()

    def _get_empty_response(self) -> Dict:
        """Get empty response structure for HH API"""
        return {'items': []}

    def _validate_vacancy(self, vacancy: Dict) -> bool:
        """Validate vacancy structure"""
        return (
            isinstance(vacancy, dict) and 
            all(field in vacancy for field in self.REQUIRED_VACANCY_FIELDS)
        )

    def get_vacancies_page(self, search_query: str, page: int = 0, **kwargs) -> List[Dict]:
        """Get and validate single page of vacancies"""
        try:
            params = {
                "text": search_query,
                "page": page,
                **self.config.hh_config.get_params(**kwargs)
            }

            data = self._connect_to_api(self.BASE_URL, params, "hh")
            items = data.get('items', [])

            return [item for item in items if self._validate_vacancy(item)]

        except Exception as e:
            logger.error(f"Failed to get vacancies page {page}: {e}")
            return []

    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict]:
        """Get all vacancies with pagination and validation"""
        try:
            # Initial request for metadata
            initial_data = self._connect_to_api(
                self.BASE_URL,
                self.config.hh_config.get_params(
                    text=search_query,
                    page=0,
                    per_page=1,
                    **kwargs
                ),
                "hh"
            )

            if not initial_data.get('found', 0):
                logger.info("No vacancies found for query")
                return []

            total_pages = min(
                initial_data.get('pages', 1),
                self.config.get_pagination_params(**kwargs)["max_pages"]
            )

            logger.info(
                f"Found {initial_data.get('found')} vacancies "
                f"({total_pages} pages to process)"
            )

            # Process all pages
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
        """
        Очищает кэш API

        Удаляет все сохраненные ответы API из кэша для освобождения места
        и обеспечения получения актуальных данных при следующих запросах.
        """
        super().clear_cache("hh")
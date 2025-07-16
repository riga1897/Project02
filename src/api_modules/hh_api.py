from pathlib import Path
from typing import List, Dict, Optional, Union
import logging
from src.api_modules.base_api import BaseAPI
from src.api_modules.get_api import APIConnector
from src.utils.paginator import Paginator
from src.config.api_config import APIConfig
from src.utils.cache import FileCache

logger = logging.getLogger(__name__)


class HeadHunterAPI(BaseAPI):
    """Enhanced HH API client with robust error handling and caching"""

    BASE_URL = "https://api.hh.ru/vacancies"
    DEFAULT_CACHE_DIR = "data/cache/hh"
    REQUIRED_VACANCY_FIELDS = {'name', 'alternate_url', 'salary'}

    def __init__(self, config: Optional[APIConfig] = None):
        self.config = config or APIConfig()
        self.connector = APIConnector(self.config)
        self.paginator = Paginator()
        self.cache = FileCache(self.DEFAULT_CACHE_DIR)
        self._init_cache()

    def _init_cache(self) -> None:
        """Initialize cache directory with validation"""
        try:
            Path(self.DEFAULT_CACHE_DIR).mkdir(parents=True, exist_ok=True)
            logger.info(f"Cache directory initialized: {self.DEFAULT_CACHE_DIR}")
        except Exception as e:
            logger.error(f"Failed to initialize cache: {e}")
            raise

    def _connect_to_api(self, url: str, params: Dict) -> Dict:
        """Execute API request with caching and enhanced error handling"""
        cache_key = self._generate_cache_key(params)

        try:
            if cached := self.cache.load_response("hh", cache_key):
                if self.validate_response(cached["data"]):
                    return cached["data"]

            response = self.connector.connect(url, params)

            if not self.validate_response(response):
                logger.error(f"Invalid API response structure: {response}")
                return {'items': []}

            self.cache.save_response("hh", cache_key, response)
            return response

        except Exception as e:
            logger.error(f"API connection failed: {e}")
            return {'items': []}

    def _generate_cache_key(self, params: Dict) -> str:
        """Generate consistent cache key from params"""
        return str(sorted(params.items()))

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

            data = self._connect_to_api(self.BASE_URL, params)
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
                )
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

        except Exception as e:
            logger.error(f"Failed to get vacancies: {e}")
            return []

    def clear_cache(self) -> None:
        """Clear cache with confirmation"""
        try:
            self.cache.clear("hh")
            logger.info("Cache cleared successfully")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            
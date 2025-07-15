from typing import List, Dict, Optional
from src.api_modules.base_api import BaseAPI
from src.api_modules.get_api import APIConnector
from src.decorators.cache import simple_cache
from src.utils.paginator import Paginator
from src.config.api_config import APIConfig


class HeadHunterAPI(BaseAPI):
    """HH.ru API implementation."""

    def __init__(self, config: Optional[APIConfig] = None):
        self.config = config or APIConfig()
        self.connector = APIConnector(self.config)
        self.base_url = "https://api.hh.ru/vacancies"
        self.paginator = Paginator()

    def _connect_to_api(self, url: str, params: dict) -> Dict:
        """Implementation of abstract connection method."""
        return self.connector.connect(url, params, self.config.request_delay)

    @simple_cache
    def get_vacancies_page(self, search_query: str, page: int = 0, **kwargs) -> List[Dict]:
        """Get one page of results with caching."""
        params = {
            "text": search_query,
            "search_field": "name",
            "page": max(page, 0),
            **self.config.hh_config.get_hh_params(**kwargs)
        }
        data = self._connect_to_api(self.base_url, params)
        return data.get('items', [])

    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict]:
        """Main method to get vacancies."""
        return Paginator.paginate(
            fetch_func=lambda page: self.get_vacancies_page(search_query, page, **kwargs),
            **self.config.get_pagination_params(**kwargs)
        )
        

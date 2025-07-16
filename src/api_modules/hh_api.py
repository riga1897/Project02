from pathlib import Path
from typing import List, Dict, Optional
from src.api_modules.base_api import BaseAPI
from src.api_modules.get_api import APIConnector
from src.utils.paginator import Paginator
from src.config.api_config import APIConfig
from src.utils.cache import FileCache


class HeadHunterAPI(BaseAPI):
    """API клиент с оптимизированной инициализацией кэша"""

    BASE_URL = "https://api.hh.ru/vacancies"
    DEFAULT_CACHE_DIR = "data/cache/hh"

    def __init__(self, config: Optional[APIConfig] = None):
        self.config = config or APIConfig()
        self.connector = APIConnector(self.config)
        self.paginator = Paginator()
        self.cache = FileCache(self.DEFAULT_CACHE_DIR)

        # Проверка инициализации кэша
        if not Path(self.DEFAULT_CACHE_DIR).exists():
            raise RuntimeError(f"Cache directory not found: {self.DEFAULT_CACHE_DIR}")

    @staticmethod
    def ensure_cache_dir(cache_dir: str = DEFAULT_CACHE_DIR) -> None:
        """Статический метод для создания директории кэша"""
        Path(cache_dir).mkdir(parents=True, exist_ok=True)

    def _connect_to_api(self, url: str, params: Dict) -> Dict:
        """Выполнение запроса с кэшированием"""
        if cached := self.cache.load_response("hh", params):
            return cached["data"]

        data = self.connector.connect(url, params)
        self.cache.save_response("hh", params, data)
        return data

    def get_vacancies_page(self, search_query: str, page: int = 0, **kwargs) -> List[Dict]:
        """Получение одной страницы вакансий"""
        base_params = {
            "text": search_query,
            "page": page
        }
        params = {**base_params, **self.config.hh_config.get_params(**kwargs)}
        data = self._connect_to_api(self.BASE_URL, params)
        return data.get('items', [])

    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict]:
        """Получение всех вакансий с пагинацией"""
        # Первый запрос для получения метаданных
        initial_data = self._connect_to_api(
            self.BASE_URL,
            self.config.hh_config.get_params(
                text=search_query,
                page=0,
                per_page=1,
                **kwargs
            )
        )

        total_pages = min(
            initial_data.get('pages', 1),
            self.config.get_pagination_params(**kwargs)["max_pages"]
        )
        total_items = initial_data.get('found', 0)

        print(f"Найдено вакансий: {total_items} (будет обработано {total_pages} страниц)")

        return self.paginator.paginate(
            fetch_func=lambda p: self.get_vacancies_page(search_query, p, **kwargs),
            total_pages=total_pages
        )

    def clear_cache(self) -> None:
        """Очистка кэша"""
        self.cache.clear("hh")

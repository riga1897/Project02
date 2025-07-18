import logging
from pathlib import Path
from typing import Dict, List, Union, Optional
from .cached_api import CachedAPI
from .get_api import APIConnector
from src.config.sj_api_config import SJAPIConfig
from src.config.api_config import APIConfig
from src.utils.paginator import Paginator
from src.utils.env_loader import EnvLoader

logger = logging.getLogger(__name__)


class SuperJobAPI(CachedAPI):
    """SuperJob API для поиска вакансий с использованием общих механизмов"""

    BASE_URL = "https://api.superjob.ru/2.0/vacancies"
    DEFAULT_CACHE_DIR = "data/cache/sj"
    REQUIRED_VACANCY_FIELDS = {'profession', 'link'}

    def __init__(self, config: Optional[SJAPIConfig] = None):
        """
        Инициализация SuperJob API

        Args:
            config: Конфигурация SuperJob API
        """
        super().__init__(self.DEFAULT_CACHE_DIR)  # Инициализируем кэш через родительский класс
        self.config = config or SJAPIConfig()
        
        # Используем общий APIConnector как в HH API
        api_config = APIConfig()
        self.connector = APIConnector(api_config)
        
        # Настраиваем специфичные для SJ заголовки
        api_key = EnvLoader.get_env_var('SUPERJOB_API_KEY', 'v3.r.137440105.example.test_tool')
        self.connector.headers.update({
            "X-Api-App-Id": api_key,
            "User-Agent": "VacancySearchApp/1.0"
        })

        # Инициализируем общие компоненты как в HH API
        self.paginator = Paginator()

        # Логируем, какой ключ используется
        if api_key == 'v3.r.137440105.example.test_tool':
            logger.warning("Используется тестовый API ключ SuperJob. Для полной функциональности добавьте реальный ключ в переменную окружения SUPERJOB_API_KEY")
        else:
            logger.info("Используется пользовательский API ключ SuperJob")

    def _get_empty_response(self) -> Dict:
        """Get empty response structure for SJ API"""
        return {'objects': []}

    def _validate_vacancy(self, vacancy: Dict) -> bool:
        """Validate vacancy structure (как в HH API)"""
        return (
            isinstance(vacancy, dict) and 
            all(field in vacancy for field in self.REQUIRED_VACANCY_FIELDS)
        )

    def get_vacancies_page(self, search_query: str, page: int = 0, **kwargs) -> List[Dict]:
        """Get and validate single page of vacancies (как в HH API)"""
        try:
            params = self.config.get_params(
                keyword=search_query,
                page=page,
                **kwargs
            )

            data = self._CachedAPI__connect_to_api(self.BASE_URL, params, "sj")
            items = data.get('objects', [])

            # Добавляем источник и валидируем как в HH API
            validated_items = []
            for item in items:
                item["source"] = "superjob.ru"
                if self._validate_vacancy(item):
                    validated_items.append(item)

            return validated_items

        except Exception as e:
            logger.error(f"Failed to get vacancies page {page}: {e}")
            return []

    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict]:
        """Get all vacancies with pagination and validation (адаптировано под паттерн HH API)"""
        try:
            # Initial request for metadata (как в HH API)
            initial_data = self._connect_to_api(
                self.BASE_URL,
                self.config.get_params(
                    keyword=search_query,
                    count=1,  # Минимальные данные сначала
                    **kwargs
                ),
                "sj"
            )

            if not initial_data.get('total', 0):
                logger.info("No vacancies found for query")
                return []

            total_found = initial_data.get('total', 0)
            
            # Используем общую логику пагинации как в HH API
            per_page = kwargs.get('count', 100)
            max_pages = kwargs.get('max_pages', 20)
            total_pages = min(
                max_pages,
                (total_found + per_page - 1) // per_page if total_found > 0 else 1
            )

            logger.info(
                f"Found {total_found} vacancies "
                f"({total_pages} pages to process)"
            )

            # Process all pages using unified paginator (как в HH API)
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
        Очищает кэш API (используя общий механизм как в HH API)

        Удаляет все сохраненные ответы API из кэша для освобождения места
        и обеспечения получения актуальных данных при следующих запросах.
        """
        super().clear_cache("sj")
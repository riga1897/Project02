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
    """
    API SuperJob для поиска вакансий с использованием общих механизмов

    Предоставляет полный набор функций для работы с API superjob.ru:
    - Поиск вакансий с пагинацией
    - Многоуровневое кэширование
    - Дедупликация результатов
    - Автоматическая обработка API ключей
    """

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
        """
        Получить пустую структуру ответа для SJ API

        Returns:
            Dict: Пустая структура ответа с полем 'objects'
        """
        return {'objects': []}

    def _validate_vacancy(self, vacancy: Dict) -> bool:
        """
        Валидация структуры вакансии (аналогично HH API)

        Args:
            vacancy: Словарь с данными вакансии

        Returns:
            bool: True если структура валидна, False иначе
        """
        return (
            isinstance(vacancy, dict) and 
            all(field in vacancy and vacancy[field] is not None and vacancy[field] != '' 
                for field in self.REQUIRED_VACANCY_FIELDS)
        )

    def get_vacancies_page(self, search_query: str, page: int = 0, **kwargs) -> List[Dict]:
        """
        Получение и валидация одной страницы вакансий (аналогично HH API)

        Args:
            search_query: Поисковый запрос
            page: Номер страницы (начиная с 0)
            **kwargs: Дополнительные параметры поиска

        Returns:
            List[Dict]: Список валидных вакансий со страницы
        """
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
        """
        Получение всех вакансий с пагинацией и валидацией (адаптировано под паттерн HH API)

        Выполняет полный цикл получения вакансий:
        1. Получает метаданные о количестве результатов
        2. Рассчитывает необходимое количество страниц
        3. Обрабатывает все страницы с помощью унифицированного пагинатора
        4. Валидирует каждую вакансию

        Args:
            search_query: Поисковый запрос
            **kwargs: Дополнительные параметры поиска

        Returns:
            List[Dict]: Список всех найденных и валидных вакансий
        """
        try:
            # Initial request for metadata (как в HH API)
            initial_data = self._CachedAPI__connect_to_api(
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

    @staticmethod
    def _deduplicate_vacancies(vacancies: List[Dict]) -> List[Dict]:
        """
        Удаление дублирующихся вакансий SuperJob по названию и компании

        Args:
            vacancies: Список вакансий с SuperJob

        Returns:
            List[Dict]: Список уникальных вакансий
        """
        seen = set()
        unique_vacancies = []

        for vacancy in vacancies:
            # Создаем ключ для дедупликации SJ вакансий
            title = vacancy.get('profession', '').lower().strip()
            company = vacancy.get('firm_name', '').lower().strip()

            # Нормализуем зарплату для сравнения
            salary_key = f"{vacancy.get('payment_from', 0)}-{vacancy.get('payment_to', 0)}"

            dedup_key = (title, company, salary_key)

            if dedup_key not in seen:
                seen.add(dedup_key)
                unique_vacancies.append(vacancy)
            else:
                logger.debug(f"Дублирующаяся SJ вакансия отфильтрована: {title} в {company}")

        logger.info(f"SJ дедупликация: {len(vacancies)} -> {len(unique_vacancies)} вакансий")
        return unique_vacancies

    def get_vacancies_with_deduplication(self, search_query: str, **kwargs) -> List[Dict]:
        """
        Получение вакансий с SuperJob с дедупликацией

        Args:
            search_query: Поисковый запрос
            **kwargs: Дополнительные параметры

        Returns:
            List[Dict]: Список уникальных вакансий
        """
        vacancies = self.get_vacancies(search_query, **kwargs)
        return self._deduplicate_vacancies(vacancies)

    def clear_cache(self, api_prefix: str) -> None:
        """
        Очищает кэш API (используя общий механизм как в HH API)

        Удаляет все сохраненные ответы API из кэша для освобождения места
        и обеспечения получения актуальных данных при следующих запросах.
        """
        super().clear_cache("sj")
import logging
from typing import List, Dict, Any, Optional, Set
from .hh_api import HeadHunterAPI
from .sj_api import SuperJobAPI
from src.vacancies.models import Vacancy
from src.vacancies.parsers.sj_parser import SuperJobParser
from src.utils.source_manager import source_manager

logger = logging.getLogger(__name__)


class UnifiedVacancyAPI:
    """Унифицированный API для работы с несколькими источниками вакансий"""

    def __init__(self):
        """Инициализация унифицированного API"""
        self.hh_api = HeadHunterAPI()
        self.sj_api = SuperJobAPI()
        self.sj_parser = SuperJobParser()

    def get_vacancies(
        self, 
        search_query: str, 
        sources: Optional[Set[str]] = None,
        **kwargs
    ) -> List[Vacancy]:
        """
        Получение вакансий из выбранных источников

        Args:
            search_query: Поисковый запрос
            sources: Множество источников ('hh', 'sj'). Если None - все источники
            **kwargs: Дополнительные параметры поиска

        Returns:
            List[Vacancy]: Список унифицированных вакансий
        """
        
        sources = source_manager.validate_sources(sources)

        all_vacancies = []

        # Получение вакансий с HH.ru
        if 'hh' in sources:
            try:
                logger.info(f"Поиск вакансий на HH.ru по запросу: '{search_query}'")
                hh_vacancies_data = self.hh_api.get_vacancies(search_query, **kwargs)
                hh_vacancies = Vacancy.cast_to_object_list(hh_vacancies_data)

                # Устанавливаем источник для HH вакансий
                for vacancy in hh_vacancies:
                    vacancy.source = "hh.ru"

                all_vacancies.extend(hh_vacancies)
                logger.info(f"Найдено {len(hh_vacancies)} вакансий на HH.ru")

            except Exception as e:
                logger.error(f"Ошибка при получении вакансий с HH.ru: {e}")

        # Получение вакансий с SuperJob
        if 'sj' in sources:
            try:
                logger.info(f"Поиск вакансий на SuperJob по запросу: '{search_query}'")
                sj_vacancies_data = self.sj_api.get_vacancies(search_query, **kwargs)

                # Парсим SuperJob вакансии
                sj_vacancies_objects = self.sj_parser.parse_vacancies(sj_vacancies_data)

                # Конвертируем в унифицированный формат и создаем объекты Vacancy
                for sj_vacancy in sj_vacancies_objects:
                    unified_data = self.sj_parser.convert_to_unified_format(sj_vacancy)
                    try:
                        vacancy = Vacancy.from_dict(unified_data)
                        all_vacancies.append(vacancy)
                    except Exception as e:
                        logger.warning(f"Ошибка конвертации SuperJob вакансии: {e}")

                logger.info(f"Найдено {len(sj_vacancies_objects)} вакансий на SuperJob")

            except Exception as e:
                logger.error(f"Ошибка при получении вакансий с SuperJob: {e}")

        # Удаление дубликатов по URL
        unique_vacancies = self._remove_duplicates(all_vacancies)

        logger.info(f"Всего найдено {len(unique_vacancies)} уникальных вакансий из {len(all_vacancies)}")
        return unique_vacancies

    def _remove_duplicates(self, vacancies: List[Vacancy]) -> List[Vacancy]:
        """
        Удаление дубликатов вакансий по URL

        Args:
            vacancies: Список вакансий

        Returns:
            List[Vacancy]: Список уникальных вакансий
        """
        seen_urls = set()
        unique_vacancies = []

        for vacancy in vacancies:
            if vacancy.url not in seen_urls:
                seen_urls.add(vacancy.url)
                unique_vacancies.append(vacancy)
            else:
                logger.debug(f"Дубликат найден: {vacancy.url}")

        return unique_vacancies

    def clear_cache(self, sources: Optional[Set[str]] = None) -> None:
        """
        Очистка кэша выбранных источников

        Args:
            sources: Множество источников для очистки кэша
        """
        if sources is None:
            sources = {'hh', 'sj'}

        if 'hh' in sources:
            try:
                self.hh_api.clear_cache()
                logger.info("Кэш HH.ru очищен")
            except Exception as e:
                logger.error(f"Ошибка очистки кэша HH.ru: {e}")

        if 'sj' in sources:
            try:
                self.sj_api.clear_cache()
                logger.info("Кэш SuperJob очищен")
            except Exception as e:
                logger.error(f"Ошибка очистки кэша SuperJob: {e}")

    def get_available_sources(self) -> List[str]:
        """
        Получение списка доступных источников

        Returns:
            List[str]: Список доступных источников
        """
        return ['hh', 'sj']
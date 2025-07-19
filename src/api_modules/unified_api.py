import logging
from typing import List, Dict, Any, Optional, Set
from .hh_api import HeadHunterAPI
from .sj_api import SuperJobAPI
from src.vacancies.models import Vacancy
from src.vacancies.parsers.sj_parser import SuperJobParser
from src.storage.json_saver import JSONSaver

logger = logging.getLogger(__name__)


class UnifiedAPI:
    """Унифицированный API для работы с несколькими источниками вакансий"""

    def __init__(self):
        self.hh_api = HeadHunterAPI()
        self.sj_api = SuperJobAPI()
        self.parser = SuperJobParser()

    def _deduplicate_vacancies(self, vacancies: List[Dict]) -> List[Dict]:
        """
        Удаление дублирующихся вакансий по названию и компании

        Args:
            vacancies: Список вакансий

        Returns:
            List[Dict]: Список уникальных вакансий
        """
        seen = set()
        unique_vacancies = []

        for vacancy in vacancies:
            # Создаем ключ для дедупликации
            title = vacancy.get('name', vacancy.get('profession', '')).lower().strip()
            company = vacancy.get('employer', {}).get('name', 
                     vacancy.get('firm_name', '')).lower().strip()

            # Нормализуем зарплату для сравнения
            salary_key = ''
            if 'salary' in vacancy and vacancy['salary']:
                salary = vacancy['salary']
                salary_from = salary.get('from', 0) or 0
                salary_to = salary.get('to', 0) or 0
                salary_key = f"{salary_from}-{salary_to}"
            elif 'payment_from' in vacancy:
                salary_key = f"{vacancy.get('payment_from', 0)}-{vacancy.get('payment_to', 0)}"

            dedup_key = (title, company, salary_key)

            if dedup_key not in seen:
                seen.add(dedup_key)
                unique_vacancies.append(vacancy)
            else:
                logger.debug(f"Дублирующаяся вакансия отфильтрована: {title} в {company}")

        logger.info(f"Дедупликация: {len(vacancies)} -> {len(unique_vacancies)} вакансий")
        return unique_vacancies

    def get_vacancies_from_sources(self, search_query: str, sources: List[str] = None, **kwargs) -> List[Dict]:
        """
        Получение вакансий из выбранных источников с дедупликацией

        Args:
            search_query: Поисковый запрос
            sources: Список источников ['hh', 'sj']
            **kwargs: Дополнительные параметры для API

        Returns:
            List[Dict]: Список всех уникальных вакансий
        """
        if sources is None:
            sources = self.get_available_sources()
        else:
            sources = self.validate_sources(sources)

        all_vacancies = []

        # Получение из HeadHunter
        if 'hh' in sources:
            try:
                logger.info(f"Получение вакансий с HH.ru по запросу: '{search_query}'")
                hh_data = self.hh_api.get_vacancies(search_query, **kwargs)
                hh_vacancies = [Vacancy.from_dict(item).to_dict() for item in hh_data]

                if hh_vacancies:
                    logger.info(f"Найдено {len(hh_vacancies)} вакансий с HH.ru")
                    all_vacancies.extend(hh_vacancies)

            except Exception as e:
                logger.error(f"Ошибка получения вакансий с HH.ru: {e}")

        # Получение из SuperJob
        if 'sj' in sources:
            try:
                logger.info(f"Получение вакансий с SuperJob по запросу: '{search_query}'")
                # Синхронизируем параметры периода между API
                sj_kwargs = kwargs.copy()
                if 'period' in kwargs:
                    # HH использует 'period', SuperJob использует 'published'
                    sj_kwargs['published'] = kwargs['period']
                sj_data = self.sj_api.get_vacancies(search_query, **sj_kwargs)

                if sj_data:
                    # Парсим данные SuperJob в объекты SuperJobVacancy
                    sj_vacancies_raw = self.parser.parse_vacancies(sj_data)

                    # Конвертируем SuperJobVacancy в унифицированный формат
                    sj_vacancies = []
                    for sj_vac in sj_vacancies_raw:
                        try:
                            # Конвертируем SuperJobVacancy в унифицированный формат
                            unified_data = self.parser.convert_to_unified_format(sj_vac)
                            vacancy = Vacancy.from_dict(unified_data)
                            sj_vacancies.append(vacancy.to_dict())
                        except Exception as e:
                            logger.warning(f"Ошибка конвертации вакансии SuperJob: {e}")

                    if sj_vacancies:
                        logger.info(f"Найдено {len(sj_vacancies)} вакансий с SuperJob")
                        all_vacancies.extend(sj_vacancies)
                    else:
                        logger.warning("SuperJob API не вернул вакансий")

            except Exception as e:
                logger.error(f"Ошибка получения вакансий из SJ: {e}")

        # Применяем дедупликацию к общему списку вакансий
        return self._deduplicate_vacancies(all_vacancies)

    def get_hh_vacancies(self, query: str, **kwargs) -> List[Vacancy]:
        """Получение вакансий только с HH.ru"""
        hh_vacancies = self.get_vacancies_from_sources(query, sources=['hh'], **kwargs)
        return [Vacancy.from_dict(item) for item in hh_vacancies]

    def get_sj_vacancies(self, query: str, **kwargs) -> List[Vacancy]:
        """Получение вакансий только с SuperJob"""
        # Синхронизируем параметры периода
        sj_kwargs = kwargs.copy()
        if 'period' in kwargs:
            # HH использует 'period', SuperJob использует 'published'
            sj_kwargs['published'] = kwargs['period']
        sj_vacancies = self.get_vacancies_from_sources(query, sources=['sj'], **sj_kwargs)
        return [Vacancy.from_dict(item) for item in sj_vacancies]

    def clear_cache(self, sources: Dict[str, bool]) -> None:
        """
        Очистка кэша выбранных источников

        Args:
            sources: Словарь источников {'hh': bool, 'sj': bool}
        """
        try:
            if sources.get('hh', False):
                self.hh_api.clear_cache()
                logger.info("Кэш HH.ru очищен")

            if sources.get('sj', False):
                self.sj_api.clear_cache()
                logger.info("Кэш SuperJob очищен")

        except Exception as e:
            logger.error(f"Ошибка очистки кэша: {e}")

    def clear_all_cache(self) -> None:
        """Очистка кэша всех API"""
        # Очищаем кэш каждого API отдельно, чтобы ошибка в одном не влияла на другой
        try:
            self.hh_api.clear_cache()
            logger.info("Кэш HH.ru очищен")
        except Exception as e:
            logger.error(f"Ошибка очистки кэша HH.ru: {e}")

        try:
            self.sj_api.clear_cache()
            logger.info("Кэш SuperJob очищен")
        except Exception as e:
            logger.error(f"Ошибка очистки кэша SuperJob: {e}")

    def get_available_sources(self) -> List[str]:
        """Получение списка доступных источников"""
        return ['hh', 'sj']

    def validate_sources(self, sources: List[str]) -> List[str]:
        """Валидация списка источников"""
        available = self.get_available_sources()
        valid_sources = [s for s in sources if s in available]

        if not valid_sources:
            logger.warning(f"Нет валидных источников в {sources}, используем все доступные")
            return available

        return valid_sources
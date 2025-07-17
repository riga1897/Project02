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

    def get_vacancies_from_sources(self, query: str, sources: List[str] = None, **kwargs) -> List[Vacancy]:
        """
        Получение вакансий из выбранных источников (только кэш, без автосохранения)

        Args:
            query: Поисковый запрос
            sources: Список источников ('hh', 'sj'). Если None - используются все
            **kwargs: Дополнительные параметры

        Returns:
            List[Vacancy]: Объединенный список вакансий
        """
        if sources is None:
            sources = ['hh', 'sj']

        all_vacancies = []

        # Получение из HeadHunter
        if 'hh' in sources:
            try:
                logger.info(f"Получение вакансий с HH.ru по запросу: '{query}'")
                hh_data = self.hh_api.get_vacancies(query, **kwargs)
                hh_vacancies = [Vacancy.from_dict(item) for item in hh_data]

                if hh_vacancies:
                    logger.info(f"Найдено {len(hh_vacancies)} вакансий с HH.ru")
                    all_vacancies.extend(hh_vacancies)

            except Exception as e:
                logger.error(f"Ошибка получения вакансий с HH.ru: {e}")

        # Получение из SuperJob
        if 'sj' in sources:
            try:
                logger.info(f"Получение вакансий с SuperJob по запросу: '{query}'")
                # Синхронизируем параметры периода между API
                sj_kwargs = kwargs.copy()
                if 'period' in kwargs:
                    # HH использует 'period', SuperJob использует 'published'
                    sj_kwargs['published'] = kwargs['period']
                sj_data = self.sj_api.get_vacancies(query, **sj_kwargs)

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
                            sj_vacancies.append(vacancy)
                        except Exception as e:
                            logger.warning(f"Ошибка конвертации вакансии SuperJob: {e}")

                    if sj_vacancies:
                        logger.info(f"Найдено {len(sj_vacancies)} вакансий с SuperJob")
                        all_vacancies.extend(sj_vacancies)
                    else:
                        logger.warning("SuperJob API не вернул вакансий")

            except Exception as e:
                logger.error(f"Ошибка получения вакансий с SuperJob: {e}")
                # Продолжаем работу, даже если SuperJob недоступен

        logger.info(f"Всего получено {len(all_vacancies)} вакансий (сохранено в кэш)")
        return all_vacancies

    def get_hh_vacancies(self, query: str, **kwargs) -> List[Vacancy]:
        """Получение вакансий только с HH.ru"""
        return self.get_vacancies_from_sources(query, sources=['hh'], **kwargs)

    def get_sj_vacancies(self, query: str, **kwargs) -> List[Vacancy]:
        """Получение вакансий только с SuperJob"""
        # Синхронизируем параметры периода
        sj_kwargs = kwargs.copy()
        if 'period' in kwargs:
            # HH использует 'period', SuperJob использует 'published'
            sj_kwargs['published'] = kwargs['period']
        return self.get_vacancies_from_sources(query, sources=['sj'], **sj_kwargs)

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
        try:
            self.hh_api.clear_cache()
            self.sj_api.clear_cache()
            logger.info("Кэш всех API очищен")
        except Exception as e:
            logger.error(f"Ошибка очистки кэша: {e}")

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
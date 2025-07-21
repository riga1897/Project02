import logging
from typing import Any, Dict, List

from src.utils.cache import FileCache

from ..models import Vacancy

logger = logging.getLogger(__name__)


class HHParser:
    """Парсер вакансий с HeadHunter API"""

    requirements = None
    responsibilities = None

    def __init__(self, cache_dir: str = "data/cache/hh"):
        self.cache = FileCache(cache_dir)
        self.base_url = "https://api.hh.ru/vacancies"

    def parse_vacancies(self, search_params: Dict[str, Any]) -> List[Vacancy]:
        """Парсинг вакансий по параметрам поиска"""
        # Проверка кэша
        cached = self.cache.load_response("hh", search_params)
        if cached:
            return self._parse_items(cached.get("data", []))

        # Запрос к API (заглушка для примера)
        # В реальной реализации здесь будет запрос к API
        vacancies_data = self._fetch_from_api()

        # Сохранение в кэш
        self.cache.save_response("hh", search_params, vacancies_data)
        return self._parse_items(vacancies_data)

    @staticmethod
    def _fetch_from_api() -> List[Dict[str, Any]]:
        """Заглушка для реального запроса к API"""
        # В реальной реализации здесь будет код для работы с API
        return []

    def _parse_items(self, raw_data: List[Dict[str, Any]]) -> List[Vacancy]:
        """Преобразование сырых данных HH в объекты Vacancy"""
        vacancies = []

        for item in raw_data:
            try:
                # Сначала создаем HH-специфичную модель
                hh_vacancy = Vacancy.from_dict(item)
                # Устанавливаем raw_data для доступа к исходным данным
                hh_vacancy.raw_data = item
                # Обработка snippet (специфично для HH)
                snippet = item.get("snippet", {})

                if isinstance(snippet, dict):
                    requirements = snippet.get("requirement")
                    responsibilities = snippet.get("responsibility")

                    # Отладочная информация для определенных вакансий
                    vacancy_id = str(item.get("id", ""))
                    if vacancy_id in ["122732917", "122993500", "122509873", "122991966", "122865078"]:
                        print(f"DEBUG HH Parser ID {vacancy_id}:")
                        print(f"  raw item keys = {list(item.keys())}")
                        print(f"  snippet = {snippet}")
                        print(f"  requirements = {requirements}")
                        print(f"  responsibilities = {responsibilities}")
                        # Проверим, что передается в HHVacancy
                        print(f"  hh_vacancy.requirements = {hh_vacancy.requirements}")
                        print(f"  hh_vacancy.responsibilities = {hh_vacancy.responsibilities}")
                # Затем конвертируем в унифицированный формат
                unified_vacancy = self.convert_to_unified_format(hh_vacancy)
                vacancies.append(unified_vacancy)
            except Exception as e:
                logger.warning(f"Ошибка парсинга HH вакансии: {e}")
                continue
        return vacancies

    @staticmethod
    def convert_to_unified_format(hh_vacancy: Vacancy) -> Vacancy:
        """Конвертация HH вакансии в унифицированный формат"""
        # Для HH: обязанности = responsibility, требования = requirement
        return Vacancy(
            vacancy_id=hh_vacancy.vacancy_id,
            title=hh_vacancy.title,
            url=(
                (hh_vacancy.raw_data.get("alternate_url") if hh_vacancy.raw_data else "")
                or (hh_vacancy.raw_data.get("url") if hh_vacancy.raw_data else "")
                or ""
            ),
            salary=hh_vacancy.salary.to_dict() if hh_vacancy.salary else None,
            description=hh_vacancy.description,
            requirements=hh_vacancy.requirements,  # requirement из snippet
            responsibilities=hh_vacancy.responsibilities,  # responsibility из snippet
            employer=hh_vacancy.employer,
            experience=hh_vacancy.experience,
            employment=hh_vacancy.employment,
            schedule=hh_vacancy.schedule,
            published_at=hh_vacancy.published_at.isoformat() if hh_vacancy.published_at else None,
            skills=hh_vacancy.skills,
            detailed_description=hh_vacancy.detailed_description,
            benefits=hh_vacancy.benefits,
            source=hh_vacancy.source,
        )

from typing import List, Dict, Any, Optional
from src.vacancies.models import Vacancy
from src.utils.cache import FileCache

class HHParser:
    """Парсер вакансий с HeadHunter API"""

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
        """Преобразование сырых данных в объекты Vacancy"""
        vacancies = []
        for item in raw_data:
            vacancy = self._parse_item(item)
            if vacancy:
                vacancies.append(vacancy)
        return vacancies

    def _parse_item(self, item: Dict[str, Any]) -> Optional[Vacancy]:
        """Парсинг одного элемента вакансии"""
        try:
            return Vacancy(
                title=item.get("name", ""),
                url=item.get("alternate_url", ""),
                salary=item.get("salary"),
                description=self._get_description(item),
            )
        except (KeyError, TypeError):
            return None

    @staticmethod
    def _get_description(item: Dict[str, Any]) -> str:
        """Извлечение описания вакансии"""
        snippet = item.get("snippet", {})
        return (
            f"Требования: {snippet.get('requirement', '')}\n"
            f"Обязанности: {snippet.get('responsibility', '')}"
        )
        
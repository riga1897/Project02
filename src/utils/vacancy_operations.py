"""
Модуль для операций с вакансиями
"""

from typing import List, Dict, Any, Optional
import logging
from src.vacancies.models import Vacancy
from src.utils.ui_helpers import filter_vacancies_by_keyword

logger = logging.getLogger(__name__)


class VacancyOperations:
    """Класс для операций с вакансиями"""

    @staticmethod
    def get_vacancies_with_salary(vacancies: List[Vacancy]) -> List[Vacancy]:
        """
        Фильтрация вакансий, у которых указана зарплата

        Args:
            vacancies: Список вакансий для фильтрации

        Returns:
            List[Vacancy]: Список вакансий с указанной зарплатой
        """
        return [
            v for v in vacancies 
            if v.salary and (v.salary.salary_from or v.salary.salary_to)
        ]

    @staticmethod
    def sort_vacancies_by_salary(vacancies: List[Vacancy], reverse: bool = True) -> List[Vacancy]:
        """
        Сортировка вакансий по зарплате

        Args:
            vacancies: Список вакансий для сортировки
            reverse: Сортировка по убыванию (True) или возрастанию (False)

        Returns:
            List[Vacancy]: Отсортированный список вакансий
        """
        return sorted(
            vacancies,
            key=lambda x: x.salary.get_max_salary() if x.salary else 0,
            reverse=reverse
        )

    @staticmethod
    def filter_vacancies_by_min_salary(vacancies: List[Vacancy], min_salary: int) -> List[Vacancy]:
        """
        Фильтрация вакансий по минимальной зарплате

        Args:
            vacancies: Список вакансий для фильтрации
            min_salary: Минимальная зарплата

        Returns:
            List[Vacancy]: Список отфильтрованных вакансий
        """
        return [
            v for v in vacancies 
            if v.salary and v.salary.get_max_salary() and v.salary.get_max_salary() >= min_salary
        ]

    @staticmethod
    def filter_vacancies_by_max_salary(vacancies: List[Vacancy], max_salary: int) -> List[Vacancy]:
        """
        Фильтрация вакансий по максимальной зарплате

        Args:
            vacancies: Список вакансий для фильтрации
            max_salary: Максимальная зарплата

        Returns:
            List[Vacancy]: Список отфильтрованных вакансий
        """
        return [
            v for v in vacancies 
            if v.salary and (
                (v.salary.salary_from and v.salary.salary_from <= max_salary) or
                (v.salary.salary_to and v.salary.salary_to <= max_salary)
            )
        ]

    @staticmethod
    def filter_vacancies_by_salary_range(vacancies: List[Vacancy], min_salary: int, max_salary: int) -> List[Vacancy]:
        """
        Фильтрация вакансий по диапазону зарплат

        Args:
            vacancies: Список вакансий для фильтрации
            min_salary: Минимальная зарплата диапазона
            max_salary: Максимальная зарплата диапазона

        Returns:
            List[Vacancy]: Список отфильтрованных вакансий
        """
        return [
            v for v in vacancies 
            if v.salary and (
                (v.salary.salary_from and min_salary <= v.salary.salary_from <= max_salary) or
                (v.salary.salary_to and min_salary <= v.salary.salary_to <= max_salary) or
                (v.salary.salary_from and v.salary.salary_to and 
                 v.salary.salary_from <= max_salary and v.salary.salary_to >= min_salary)
            )
        ]

    @staticmethod
    def filter_vacancies_by_multiple_keywords(vacancies: List[Vacancy], keywords: List[str]) -> List[Vacancy]:
        """
        Фильтрация вакансий по нескольким ключевым словам

        Args:
            vacancies: Список вакансий для фильтрации
            keywords: Список ключевых слов для поиска

        Returns:
            List[Vacancy]: Список отфильтрованных вакансий
        """
        if not keywords:
            return vacancies

        filtered_vacancies = []

        for vacancy in vacancies:
            matches = 0
            for keyword in keywords:
                if filter_vacancies_by_keyword([vacancy], keyword):
                    matches += 1

            # Включаем вакансию, если найдено хотя бы одно совпадение
            if matches > 0:
                vacancy._keyword_matches = matches
                filtered_vacancies.append(vacancy)

        # Сортируем по количеству совпадений
        filtered_vacancies.sort(key=lambda x: getattr(x, '_keyword_matches', 0), reverse=True)

        return filtered_vacancies

    @staticmethod
    def search_vacancies_advanced(vacancies: List[Vacancy], query: str) -> List[Vacancy]:
        """
        Продвинутый поиск по вакансиям с поддержкой операторов

        Args:
            vacancies: Список вакансий для поиска
            query: Поисковый запрос (может содержать операторы AND, OR)

        Returns:
            List[Vacancy]: Список найденных вакансий
        """
        # Простая обработка AND/OR операторов
        if ' AND ' in query.upper():
            keywords = [kw.strip() for kw in query.upper().split(' AND ')]
            result = vacancies
            for keyword in keywords:
                result = filter_vacancies_by_keyword(result, keyword)
            return result

        elif ' OR ' in query.upper():
            keywords = [kw.strip() for kw in query.upper().split(' OR ')]
            return VacancyOperations.filter_vacancies_by_multiple_keywords(vacancies, keywords)
        elif ',' in query:
            # Поиск с запятой как разделителем (OR)
            keywords = [kw.strip().upper() for kw in query.split(',') if kw.strip()]
            return VacancyOperations.filter_vacancies_by_multiple_keywords(vacancies, keywords)
        elif ' ' in query.strip() and not any(op in query.upper() for op in [' AND ', ' OR ']):
            # Поиск с пробелами как разделителем (OR по умолчанию)
            keywords = [kw.strip().upper() for kw in query.split() if kw.strip()]
            return VacancyOperations.filter_vacancies_by_multiple_keywords(vacancies, keywords)
        else:
            # Простой поиск по одному ключевому слову
            return filter_vacancies_by_keyword(vacancies, query)

    @staticmethod
    def get_vacancy_keywords_summary(vacancies: List[Vacancy]) -> Dict[str, int]:
        """
        Получение сводки по ключевым словам в вакансиях

        Args:
            vacancies: Список вакансий

        Returns:
            Dict[str, int]: Словарь {ключевое_слово: количество_вакансий}
        """
        keyword_count = {}

        for vacancy in vacancies:
            if vacancy.keywords:
                for keyword in vacancy.keywords:
                    keyword_count[keyword] = keyword_count.get(keyword, 0) + 1

        # Сортируем по популярности
        return dict(sorted(keyword_count.items(), key=lambda x: x[1], reverse=True))
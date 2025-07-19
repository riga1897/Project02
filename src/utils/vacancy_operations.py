import logging
from typing import List

from src.utils.search_utils import filter_vacancies_by_keyword, vacancy_contains_keyword
from src.vacancies.models import Vacancy

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
            if v.salary and (
                # Если есть только нижняя граница - она должна быть >= min_salary
                (v.salary.salary_from and not v.salary.salary_to and v.salary.salary_from >= min_salary) or
                # Если есть только верхняя граница - она должна быть >= min_salary
                (not v.salary.salary_from and v.salary.salary_to and v.salary.salary_to >= min_salary) or
                # Если есть обе границы - нижняя граница должна быть >= min_salary
                (v.salary.salary_from and v.salary.salary_to and v.salary.salary_from >= min_salary)
            )
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
                # Если есть только нижняя граница - она должна быть <= max_salary
                (v.salary.salary_from and not v.salary.salary_to and v.salary.salary_from <= max_salary) or
                # Если есть только верхняя граница - она должна быть <= max_salary
                (not v.salary.salary_from and v.salary.salary_to and v.salary.salary_to <= max_salary) or
                # Если есть обе границы - ОБЕ границы должны быть <= max_salary
                (v.salary.salary_from and v.salary.salary_to and 
                 v.salary.salary_from <= max_salary and v.salary.salary_to <= max_salary)
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
            # Разбираем более аккуратно, сохраняя регистр
            parts = query.split()
            keywords = []
            current_keyword = []
            for part in parts:
                if part.upper() == 'AND':
                    if current_keyword:
                        keywords.append(' '.join(current_keyword))
                        current_keyword = []
                else:
                    current_keyword.append(part)
            if current_keyword:
                keywords.append(' '.join(current_keyword))

            # Для AND ищем вакансии, которые содержат ВСЕ ключевые слова
            result = []
            for vacancy in vacancies:
                found_all = True
                for keyword in keywords:
                    # Проверяем наличие каждого ключевого слова в вакансии
                    if not vacancy_contains_keyword(vacancy, keyword.strip()):
                        found_all = False
                        break
                if found_all:
                    result.append(vacancy)
            return result

        elif ' OR ' in query.upper():
            # Аналогично для OR
            parts = query.split()
            keywords = []
            current_keyword = []
            for part in parts:
                if part.upper() == 'OR':
                    if current_keyword:
                        keywords.append(' '.join(current_keyword))
                        current_keyword = []
                else:
                    current_keyword.append(part)
            if current_keyword:
                keywords.append(' '.join(current_keyword))

            return VacancyOperations.filter_vacancies_by_multiple_keywords(vacancies, [kw.strip() for kw in keywords])
        elif ',' in query:
            # Поиск с запятой как разделителем (OR)
            keywords = [kw.strip() for kw in query.split(',') if kw.strip()]
            return VacancyOperations.filter_vacancies_by_multiple_keywords(vacancies, keywords)
        elif ' ' in query.strip() and not any(op in query.upper() for op in [' AND ', ' OR ']):
            # Поиск с пробелами как разделителем (OR по умолчанию)
            keywords = [kw.strip() for kw in query.split() if kw.strip()]
            return VacancyOperations.filter_vacancies_by_multiple_keywords(vacancies, keywords)
        else:
            # Простой поиск по одному ключевому слову
            return filter_vacancies_by_keyword(vacancies, query)

    

    

    @staticmethod
    def debug_vacancy_search(vacancy: Vacancy, keyword: str) -> None:
        """
        Отладочная функция для проверки содержимого вакансии при поиске

        Выводит подробную информацию о вакансии и показывает, в каких полях
        найдено ключевое слово.
        """
        print(f"\n=== ОТЛАДКА ПОИСКА: '{keyword}' ===")
        print(f"Вакансия: {vacancy.title}")
        print(f"Компания: {vacancy.employer}")
        # print(f"Ключевые слова: {vacancy.keywords}")
        print(f"URL: {vacancy.url}")

        # Проверяем каждое поле
        fields_to_check = [
            ('Название', vacancy.title),
            ('Описание', vacancy.description),
            ('Требования', vacancy.requirements),
            ('Обязанности', vacancy.responsibilities),
            ('Компания', vacancy.employer),
        ]

        for field_name, field_value in fields_to_check:
            if field_value and keyword.lower() in str(field_value).lower():
                print(f"  ✓ Найдено в поле '{field_name}': ...{str(field_value)[:100]}...")

        print("=" * 50)

    @staticmethod
    def debug_vacancy_keywords(vacancy: Vacancy) -> None:
        """
        Отладочная функция для проверки извлечения ключевых слов
        """
        print(f"\n=== ОТЛАДКА КЛЮЧЕВЫХ СЛОВ ===")
        print(f"Вакансия: {vacancy.title}")
        print(f"URL: {vacancy.url}")
        # print(f"Автоматически извлеченные ключевые слова: {vacancy.keywords}")

        # Показываем текст, из которого извлекались ключевые слова
        full_text = ' '.join([
            vacancy.description or '',
            vacancy.requirements or '',
            vacancy.responsibilities or ''
        ]).lower()

        print(f"Полный текст для анализа (первые 200 символов): {full_text[:200]}...")

        # Проверяем конкретные ключевые слова
        test_keywords = ['excel', '1c', '1с', 'r']
        for keyword in test_keywords:
            import re
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = re.findall(pattern, full_text)
            if matches:
                print(f"  ✓ Найдено '{keyword}': {matches}")
            else:
                print(f"  ✗ НЕ найдено '{keyword}'")

        print("=" * 50)
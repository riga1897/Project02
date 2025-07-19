import logging
from typing import List, Optional

from src.vacancies.models import Vacancy

logger = logging.getLogger(__name__)


def get_user_input(prompt: str, required: bool = True) -> Optional[str]:
    """
    Получение ввода от пользователя с валидацией

    Args:
        prompt: Текст приглашения для ввода
        required: Обязательно ли поле для заполнения

    Returns:
        Введенная строка или None если поле не обязательное и пустое
    """
    while True:
        user_input = input(prompt).strip()

        if user_input or not required:
            return user_input if user_input else None

        print("Поле не может быть пустым!")


def get_positive_integer(prompt: str) -> Optional[int]:
    """
    Получение положительного целого числа от пользователя

    Args:
        prompt: Текст приглашения для ввода

    Returns:
        Положительное целое число или None при ошибке
    """
    try:
        value = int(input(prompt))
        if value <= 0:
            print("Число должно быть положительным!")
            return None
        return value
    except ValueError:
        print("Введите корректное число!")
        return None


def parse_salary_range(salary_range: str) -> Optional[tuple[int, int]]:
    """
    Парсинг диапазона зарплат из строки

    Args:
        salary_range: Строка с диапазоном зарплат (например: "100000 - 150000")

    Returns:
        Кортеж (min_salary, max_salary) или None при ошибке
    """
    try:
        # Парсим диапазон
        if " - " in salary_range:
            min_sal, max_sal = salary_range.split(" - ")
        elif "-" in salary_range:
            min_sal, max_sal = salary_range.split("-")
        else:
            print("Неверный формат диапазона. Используйте формат: 100000 - 150000")
            return None

        min_salary = int(min_sal.strip())
        max_salary = int(max_sal.strip())

        if min_salary > max_salary:
            min_salary, max_salary = max_salary, min_salary

        return min_salary, max_salary

    except ValueError:
        print("Введите корректные числа!")
        return None


def confirm_action(prompt: str) -> bool:
    """
    Получение подтверждения действия от пользователя

    Args:
        prompt: Текст приглашения для подтверждения

    Returns:
        True если пользователь подтвердил, False иначе
    """
    while True:
        answer = input(f"{prompt} (y/n): ").strip().lower()
        if answer in ['y', 'yes', 'д', 'да']:
            return True
        elif answer in ['n', 'no', 'н', 'нет']:
            return False
        else:
            print("Введите 'y' для да или 'n' для нет.")


def filter_vacancies_by_keyword(vacancies: List[Vacancy], keyword: str) -> List[Vacancy]:
    """
    Расширенная фильтрация вакансий по ключевому слову

    Args:
        vacancies: Список вакансий для фильтрации
        keyword: Ключевое слово для поиска

    Returns:
        Список отфильтрованных вакансий с оценкой релевантности
    """
    filtered_vacancies = []
    keyword_lower = keyword.lower()

    for vacancy in vacancies:
        relevance_score = 0

        # Проверяем по ID вакансии (очень высокий приоритет)
        if vacancy.vacancy_id and keyword_lower in vacancy.vacancy_id.lower():
            relevance_score += 15

        # Проверяем в заголовке (высокий приоритет)
        if vacancy.title and keyword_lower in vacancy.title.lower():
            relevance_score += 10

        

        # Проверяем в требованиях (средний приоритет)
        if vacancy.requirements and keyword_lower in vacancy.requirements.lower():
            relevance_score += 5

        # Проверяем в обязанностях (средний приоритет)  
        if vacancy.responsibilities and keyword_lower in vacancy.responsibilities.lower():
            relevance_score += 5

        # Проверяем в описании (низкий приоритет)
        if vacancy.description and keyword_lower in vacancy.description.lower():
            relevance_score += 3

        # Проверяем в детальном описании
        if vacancy.detailed_description and keyword_lower in vacancy.detailed_description.lower():
            relevance_score += 2

        # Проверяем в навыках
        if vacancy.skills:
            for skill in vacancy.skills:
                if isinstance(skill, dict) and 'name' in skill:
                    if keyword_lower in skill['name'].lower():
                        relevance_score += 6
                elif isinstance(skill, str) and keyword_lower in skill.lower():
                    relevance_score += 6

        # Дополнительные проверки для улучшения поиска
        # Проверяем в информации о работодателе
        if vacancy.employer and isinstance(vacancy.employer, dict):
            employer_name = vacancy.employer.get('name', '')
            if employer_name and keyword_lower in employer_name.lower():
                relevance_score += 4

        # Проверяем в типе занятости
        if vacancy.employment and keyword_lower in vacancy.employment.lower():
            relevance_score += 3

        # Проверяем в графике работы
        if vacancy.schedule and keyword_lower in vacancy.schedule.lower():
            relevance_score += 3

        # Проверяем в опыте работы
        if vacancy.experience and keyword_lower in vacancy.experience.lower():
            relevance_score += 3

        # Проверяем в бонусах/льготах
        if vacancy.benefits and keyword_lower in vacancy.benefits.lower():
            relevance_score += 2

        if relevance_score > 0:
            # Добавляем временный атрибут для сортировки
            vacancy._relevance_score = relevance_score
            filtered_vacancies.append(vacancy)

    # Сортируем по релевантности
    filtered_vacancies.sort(key=lambda x: getattr(x, '_relevance_score', 0), reverse=True)

    return filtered_vacancies


# Эти функции перенесены в src/utils/vacancy_operations.py
# Импортируем их оттуда для обратной совместимости
from src.utils.vacancy_operations import VacancyOperations

def filter_vacancies_by_min_salary(vacancies: List[Vacancy], min_salary: int) -> List[Vacancy]:
    """Устаревшая функция - используйте VacancyOperations.filter_vacancies_by_min_salary"""
    return VacancyOperations.filter_vacancies_by_min_salary(vacancies, min_salary)

def filter_vacancies_by_max_salary(vacancies: List[Vacancy], max_salary: int) -> List[Vacancy]:
    """Устаревшая функция - используйте VacancyOperations.filter_vacancies_by_max_salary"""
    return VacancyOperations.filter_vacancies_by_max_salary(vacancies, max_salary)

def filter_vacancies_by_salary_range(vacancies: List[Vacancy], min_salary: int, max_salary: int) -> List[Vacancy]:
    """Устаревшая функция - используйте VacancyOperations.filter_vacancies_by_salary_range"""
    return VacancyOperations.filter_vacancies_by_salary_range(vacancies, min_salary, max_salary)

def get_vacancies_with_salary(vacancies: List[Vacancy]) -> List[Vacancy]:
    """Устаревшая функция - используйте VacancyOperations.get_vacancies_with_salary"""
    return VacancyOperations.get_vacancies_with_salary(vacancies)

def sort_vacancies_by_salary(vacancies: List[Vacancy], reverse: bool = True) -> List[Vacancy]:
    """Устаревшая функция - используйте VacancyOperations.sort_vacancies_by_salary"""
    return VacancyOperations.sort_vacancies_by_salary(vacancies, reverse)

def filter_vacancies_by_multiple_keywords(vacancies: List[Vacancy], keywords: List[str]) -> List[Vacancy]:
    """Устаревшая функция - используйте VacancyOperations.filter_vacancies_by_multiple_keywords"""
    return VacancyOperations.filter_vacancies_by_multiple_keywords(vacancies, keywords)

def search_vacancies_advanced(vacancies: List[Vacancy], query: str) -> List[Vacancy]:
    """Устаревшая функция - используйте VacancyOperations.search_vacancies_advanced"""
    return VacancyOperations.search_vacancies_advanced(vacancies, query)







def debug_vacancy_search(vacancy: Vacancy, keyword: str) -> None:
    """
    Отладочная функция для проверки содержимого вакансии при поиске

    Выводит подробную информацию о вакансии и показывает, в каких полях
    найдено искомое ключевое слово. Используется для отладки алгоритма поиска.

    Args:
        vacancy: Вакансия для отладки
        keyword: Ключевое слово для поиска
    """
    print(f"\n=== Отладка вакансии: {vacancy.title} ===")
    print(f"ID: {vacancy.vacancy_id}")
    print(f"Заголовок: {vacancy.title}")
    print(f"Описание: {vacancy.description[:200] if vacancy.description else 'Нет'}...")
    print(f"Требования: {vacancy.requirements[:200] if vacancy.requirements else 'Нет'}...")
    print(f"Обязанности: {vacancy.responsibilities[:200] if vacancy.responsibilities else 'Нет'}...")
    # print(f"Ключевые слова: {vacancy.keywords}")
    print(f"Навыки: {vacancy.skills}")
    print(f"Работодатель: {vacancy.employer}")
    print(f"Опыт: {vacancy.experience}")
    print(f"Занятость: {vacancy.employment}")
    print(f"График: {vacancy.schedule}")
    print(f"Бонусы: {vacancy.benefits}")

    # Проверяем наличие ключевого слова
    keyword_lower = keyword.lower()
    found_in = []

    if vacancy.title and keyword_lower in vacancy.title.lower():
        found_in.append("заголовок")
    if vacancy.description and keyword_lower in vacancy.description.lower():
        found_in.append("описание")
    if vacancy.requirements and keyword_lower in vacancy.requirements.lower():
        found_in.append("требования")
    if vacancy.responsibilities and keyword_lower in vacancy.responsibilities.lower():
        found_in.append("обязанности")
    # if vacancy.keywords and any(keyword_lower in kw.lower() for kw in vacancy.keywords):
    #     found_in.append("ключевые слова")

    print(f"Ключевое слово '{keyword}' найдено в: {', '.join(found_in) if found_in else 'НИГДЕ'}")
    print("=" * 50)


def debug_search_vacancies(vacancies: List[Vacancy], keyword: str) -> None:
    """
    Отладочная функция для анализа всех сохраненных вакансий

    Выводит сводную информацию о поиске по всем вакансиям и показывает
    первые 5 вакансий с подробным анализом. Используется для отладки
    алгоритма поиска на больших наборах данных.

    Args:
        vacancies: Список вакансий для анализа
        keyword: Ключевое слово для поиска
    """
    print(f"\n=== Отладка поиска по слову '{keyword}' ===")
    print(f"Всего вакансий: {len(vacancies)}")

    for i, vacancy in enumerate(vacancies[:5]):  # Показываем первые 5
        print(f"\nВакансия {i+1}:")
        debug_vacancy_search(vacancy, keyword)


# Импорт унифицированного форматтера
from src.utils.vacancy_formatter import vacancy_formatter

def display_vacancy_info(vacancy: 'Vacancy', number: int = None) -> None:
    """
    Отображение информации о вакансии
    
    Args:
        vacancy: Объект вакансии
        number: Порядковый номер (опционально)
    """
    vacancy_formatter.display_vacancy_info(vacancy, number)
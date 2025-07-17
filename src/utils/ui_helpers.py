
"""
Вспомогательные функции для пользовательского интерфейса
"""

from typing import List, Optional
import logging
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
    Фильтрация вакансий по ключевому слову в описании
    
    Args:
        vacancies: Список вакансий для фильтрации
        keyword: Ключевое слово для поиска
        
    Returns:
        Список отфильтрованных вакансий
    """
    filtered_vacancies = []
    keyword_lower = keyword.lower()
    
    for vacancy in vacancies:
        description_text = ""
        if vacancy.title:
            description_text += vacancy.title.lower()
        if vacancy.description:
            description_text += " " + vacancy.description.lower()
        if vacancy.requirements:
            description_text += " " + vacancy.requirements.lower()
        if vacancy.responsibilities:
            description_text += " " + vacancy.responsibilities.lower()
        
        if keyword_lower in description_text:
            filtered_vacancies.append(vacancy)
    
    return filtered_vacancies


def filter_vacancies_by_min_salary(vacancies: List[Vacancy], min_salary: int) -> List[Vacancy]:
    """
    Фильтрация вакансий по минимальной зарплате
    
    Args:
        vacancies: Список вакансий для фильтрации
        min_salary: Минимальная зарплата
        
    Returns:
        Список отфильтрованных вакансий
    """
    return [
        v for v in vacancies 
        if v.salary and v.salary.get_max_salary() and v.salary.get_max_salary() >= min_salary
    ]


def filter_vacancies_by_max_salary(vacancies: List[Vacancy], max_salary: int) -> List[Vacancy]:
    """
    Фильтрация вакансий по максимальной зарплате
    
    Args:
        vacancies: Список вакансий для фильтрации
        max_salary: Максимальная зарплата
        
    Returns:
        Список отфильтрованных вакансий
    """
    return [
        v for v in vacancies 
        if v.salary and (
            (v.salary.salary_from and v.salary.salary_from <= max_salary) or
            (v.salary.salary_to and v.salary.salary_to <= max_salary)
        )
    ]


def filter_vacancies_by_salary_range(vacancies: List[Vacancy], min_salary: int, max_salary: int) -> List[Vacancy]:
    """
    Фильтрация вакансий по диапазону зарплат
    
    Args:
        vacancies: Список вакансий для фильтрации
        min_salary: Минимальная зарплата диапазона
        max_salary: Максимальная зарплата диапазона
        
    Returns:
        Список отфильтрованных вакансий
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


def get_vacancies_with_salary(vacancies: List[Vacancy]) -> List[Vacancy]:
    """
    Фильтрация вакансий, у которых указана зарплата
    
    Args:
        vacancies: Список вакансий для фильтрации
        
    Returns:
        Список вакансий с указанной зарплатой
    """
    return [
        v for v in vacancies 
        if v.salary and (v.salary.salary_from or v.salary.salary_to)
    ]


def sort_vacancies_by_salary(vacancies: List[Vacancy], reverse: bool = True) -> List[Vacancy]:
    """
    Сортировка вакансий по зарплате
    
    Args:
        vacancies: Список вакансий для сортировки
        reverse: Сортировка по убыванию (True) или возрастанию (False)
        
    Returns:
        Отсортированный список вакансий
    """
    return sorted(
        vacancies,
        key=lambda x: x.salary.get_max_salary() if x.salary else 0,
        reverse=reverse
    )


def display_vacancy_info(vacancy: Vacancy, number: int) -> None:
    """
    Отображение информации об одной вакансии
    
    Args:
        vacancy: Вакансия для отображения
        number: Номер вакансии в списке
    """
    print(f"\n{number}. {vacancy.title}")
    
    if vacancy.employer:
        company = vacancy.employer.get('name', 'Не указана')
        print(f"   Компания: {company}")
    
    if vacancy.salary:
        print(f"   Зарплата: {vacancy.salary}")
    else:
        print("   Зарплата: Не указана")
    
    if vacancy.experience:
        print(f"   Опыт: {vacancy.experience}")
    
    if vacancy.url:
        print(f"   Ссылка: {vacancy.url}")
    
    print("-" * 80)


def print_section_header(title: str, width: int = 50) -> None:
    """
    Печать заголовка секции с декоративным оформлением
    
    Args:
        title: Текст заголовка
        width: Ширина декоративной линии
    """
    print("=" * width)
    print(title)
    print("=" * width)


def print_menu_separator(width: int = 40) -> None:
    """
    Печать разделителя меню
    
    Args:
        width: Ширина разделителя
    """
    print("-" * width)

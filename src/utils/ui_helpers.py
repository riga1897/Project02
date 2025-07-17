
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
        
        # Проверяем в заголовке (высокий приоритет)
        if vacancy.title and keyword_lower in vacancy.title.lower():
            relevance_score += 10
        
        # Проверяем в ключевых словах (высокий приоритет)
        if vacancy.keywords and any(keyword_lower in kw.lower() for kw in vacancy.keywords):
            relevance_score += 8
        
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
        
        if relevance_score > 0:
            # Добавляем временный атрибут для сортировки
            vacancy._relevance_score = relevance_score
            filtered_vacancies.append(vacancy)
    
    # Сортируем по релевантности
    filtered_vacancies.sort(key=lambda x: getattr(x, '_relevance_score', 0), reverse=True)
    
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


def filter_vacancies_by_multiple_keywords(vacancies: List[Vacancy], keywords: List[str]) -> List[Vacancy]:
    """
    Фильтрация вакансий по нескольким ключевым словам
    
    Args:
        vacancies: Список вакансий для фильтрации
        keywords: Список ключевых слов для поиска
        
    Returns:
        Список отфильтрованных вакансий
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


def search_vacancies_advanced(vacancies: List[Vacancy], query: str) -> List[Vacancy]:
    """
    Продвинутый поиск по вакансиям с поддержкой операторов
    
    Args:
        vacancies: Список вакансий для поиска
        query: Поисковый запрос (может содержать операторы AND, OR)
        
    Returns:
        Список найденных вакансий
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
        return filter_vacancies_by_multiple_keywords(vacancies, keywords)
    
    else:
        return filter_vacancies_by_keyword(vacancies, query)


def get_vacancy_keywords_summary(vacancies: List[Vacancy]) -> Dict[str, int]:
    """
    Получение сводки по ключевым словам в вакансиях
    
    Args:
        vacancies: Список вакансий
        
    Returns:
        Словарь {ключевое_слово: количество_вакансий}
    """
    keyword_count = {}
    
    for vacancy in vacancies:
        if vacancy.keywords:
            for keyword in vacancy.keywords:
                keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
    
    # Сортируем по популярности
    return dict(sorted(keyword_count.items(), key=lambda x: x[1], reverse=True))


def display_vacancy_info(vacancy: Vacancy, number: int) -> None:
    """
    Отображение расширенной информации об одной вакансии
    
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
    
    # Показываем ключевые слова
    if vacancy.keywords:
        keywords_str = ", ".join(vacancy.keywords[:10])  # Показываем первые 10
        if len(vacancy.keywords) > 10:
            keywords_str += f" и еще {len(vacancy.keywords) - 10}"
        print(f"   Ключевые слова: {keywords_str}")
    
    # Показываем навыки
    if vacancy.skills:
        skills_list = []
        for skill in vacancy.skills[:5]:  # Показываем первые 5 навыков
            if isinstance(skill, dict) and 'name' in skill:
                skills_list.append(skill['name'])
            elif isinstance(skill, str):
                skills_list.append(skill)
        if skills_list:
            skills_str = ", ".join(skills_list)
            if len(vacancy.skills) > 5:
                skills_str += f" и еще {len(vacancy.skills) - 5}"
            print(f"   Навыки: {skills_str}")
    
    # Показываем краткое описание требований
    if vacancy.requirements:
        requirements_short = vacancy.requirements[:150] + "..." if len(vacancy.requirements) > 150 else vacancy.requirements
        print(f"   Требования: {requirements_short}")
    
    if vacancy.url:
        print(f"   Ссылка: {vacancy.url}")
    
    # Показываем оценку релевантности, если есть
    if hasattr(vacancy, '_relevance_score'):
        print(f"   Релевантность: {vacancy._relevance_score}")
    
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

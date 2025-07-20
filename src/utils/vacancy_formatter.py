from typing import Optional, List
from ..vacancies.models import Vacancy
from .base_formatter import BaseFormatter
import logging

logger = logging.getLogger(__name__)


class VacancyFormatter(BaseFormatter):
    """Класс для форматирования и отображения вакансий с поддержкой маппинга полей"""

    @staticmethod
    def _extract_responsibilities(vacancy) -> Optional[str]:
        """Извлечение обязанностей с учетом источника"""
        source = getattr(vacancy, 'source', '')

        if source == 'hh.ru':
            # Для HH обязанности в поле responsibilities
            return getattr(vacancy, 'responsibilities', None)
        elif source == 'superjob.ru':
            # Для SJ обязанности в поле description (vacancyRichText)  
            return getattr(vacancy, 'description', None)
        else:
            # Универсальная проверка
            return getattr(vacancy, 'responsibilities', None) or getattr(vacancy, 'description', None)

    @staticmethod
    def _extract_requirements(vacancy) -> Optional[str]:
        """Извлечение требований с учетом источника"""
        source = getattr(vacancy, 'source', '')

        if source == 'hh.ru':
            # Для HH требования в поле requirements
            return getattr(vacancy, 'requirements', None)
        elif source == 'superjob.ru':
            # Для SJ требования в поле requirements (candidat)
            return getattr(vacancy, 'requirements', None)
        else:
            # Универсальная проверка
            return getattr(vacancy, 'requirements', None)

    @staticmethod
    def _extract_conditions(vacancy) -> Optional[str]:
        """Извлечение условий с учетом источника"""
        conditions_parts = []

        # График работы
        schedule = getattr(vacancy, 'schedule', None)
        if schedule:
            conditions_parts.append(f"График: {schedule}")

        # Можно добавить другие условия специфичные для разных источников
        source = getattr(vacancy, 'source', '')

        if source == 'hh.ru':
            # Специфичные для HH условия
            pass
        elif source == 'superjob.ru':
            # Специфичные для SJ условия
            pass

        return "; ".join(conditions_parts) if conditions_parts else None

    @staticmethod
    def format_vacancy_info(vacancy: Vacancy, number: Optional[int] = None) -> str:
        """
        Форматирование информации о вакансии в строку

        Args:
            vacancy: Объект вакансии
            number: Порядковый номер (опционально)

        Returns:
            Отформатированная строка с информацией о вакансии
        """
        lines = VacancyFormatter._build_vacancy_lines(vacancy, number)
        return "\n".join(lines) + "\n"

    @staticmethod
    def display_vacancy_info(vacancy: Vacancy, number: Optional[int] = None) -> None:
        """
        Отображение информации о вакансии

        Args:
            vacancy: Объект вакансии
            number: Порядковый номер (опционально)
        """
        lines = VacancyFormatter._build_vacancy_lines(vacancy, number)

        for line in lines:
            print(line)

        print()  # Один перевод строки между вакансиями

    @staticmethod
    def format_salary(salary_info) -> str:
        """
        Форматирование информации о зарплате

        Args:
            salary_info: Информация о зарплате

        Returns:
            Отформатированная строка с зарплатой
        """
        if not salary_info:
            return "Зарплата не указана"

        if isinstance(salary_info, dict):
            return VacancyFormatter._format_salary_dict(salary_info)

        return str(salary_info)
    
    @staticmethod
    def _build_vacancy_lines(vacancy: Vacancy, number: Optional[int] = None) -> List[str]:
        """
        Формирование списка строк с информацией о вакансии

        Args:
            vacancy: Объект вакансии
            number: Порядковый номер (опционально)

        Returns:
            Список строк с информацией о вакансии
            :type vacancy: Vacancy
        """
        lines = []

        # Добавляем номер отдельной строкой
        if number:
            lines.append(f"{number}.")

        # Добавляем название
        title = vacancy.title or getattr(vacancy, 'name', None) or 'Не указано'
        lines.append(f"Название: {title}")

        # Источник
        lines.append(f"Источник: {getattr(vacancy, 'source', 'Не указан')}")

        # Компания
        company_name = 'Не указана'
        if vacancy.employer:
            if isinstance(vacancy.employer, dict):
                company_name = vacancy.employer.get('name', 'Не указана')
            else:
                company_name = str(vacancy.employer)
        lines.append(f"Компания: {company_name}")

        # ID
        lines.append(f"ID: {vacancy.vacancy_id}")

        # Зарплата
        if vacancy.salary:
            lines.append(f"Зарплата: {vacancy.salary}")
        else:
            lines.append("Зарплата: Не указана")

        # Опыт
        if vacancy.experience:
            lines.append(f"Опыт: {vacancy.experience}")

        # Занятость
        if vacancy.employment:
            lines.append(f"Занятость: {vacancy.employment}")

        # График (moved to conditions)

        # Навыки
        if vacancy.skills:
            skills_list = []
            for skill in vacancy.skills[:5]:
                if isinstance(skill, dict) and 'name' in skill:
                    skills_list.append(skill['name'])
                elif isinstance(skill, str):
                    skills_list.append(skill)

            if skills_list:
                skills_str = ", ".join(skills_list)
                if len(vacancy.skills) > 5:
                    skills_str += f" и еще {len(vacancy.skills) - 5}"
                lines.append(f"Навыки: {skills_str}")

        # Требования
        requirements = VacancyFormatter._extract_requirements(vacancy)
        if requirements:
            requirements_short = requirements[:150] + "..." if len(requirements) > 150 else requirements
            lines.append(f"Требования: {requirements_short}")
            
        # Обязанности
        responsibilities = VacancyFormatter._extract_responsibilities(vacancy)
        if responsibilities:
            responsibilities_short = responsibilities[:150] + "..." if len(responsibilities) > 150 else responsibilities
            lines.append(f"Обязанности: {responsibilities_short}")

        # Условия
        conditions = VacancyFormatter._extract_conditions(vacancy)
        if conditions:
            lines.append(f"Условия: {conditions}")

        # Оценка релевантности
        if hasattr(vacancy, '_relevance_score'):
            lines.append(f"Релевантность: {vacancy._relevance_score}")

        # Ссылка
        lines.append(f"Ссылка: {vacancy.url}")

        return lines
    
    @staticmethod
    def format_company_info(employer_info) -> str:
        """
        Форматирование информации о компании
        Args:
            employer_info: Информация о работодателе
        Returns:
            Отформатированная строка с информацией о компании
        """
        if not employer_info:
            return "Не указана"

        if isinstance(employer_info, dict):
            return employer_info.get('name', 'Не указана')

        return str(employer_info)

    @staticmethod
    def _format_salary_dict(salary_info: dict) -> str:
        """
        Форматирование информации о зарплате из словаря
        """
        salary_str = ""
        from_value = salary_info.get('from')
        to_value = salary_info.get('to')
        currency = salary_info.get('currency')

        if from_value:
            salary_str += f"от {from_value} "
        if to_value:
            salary_str += f"до {to_value} "
        if currency:
            salary_str += currency

        return salary_str.strip() if salary_str else "Зарплата не указана"

# Глобальный экземпляр форматтера
vacancy_formatter = VacancyFormatter()
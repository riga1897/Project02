"""
Унифицированный форматтер для отображения вакансий
"""

from typing import Optional, List
from src.vacancies.models import Vacancy


class VacancyFormatter:
    """Класс для форматирования и отображения вакансий"""

    @staticmethod
    def _build_vacancy_lines(vacancy: Vacancy, number: Optional[int] = None) -> List[str]:
        """
        Формирование списка строк с информацией о вакансии

        Args:
            vacancy: Объект вакансии
            number: Порядковый номер (опционально)

        Returns:
            Список строк с информацией о вакансии
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

        # График
        if vacancy.schedule:
            lines.append(f"График: {vacancy.schedule}")

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
        if vacancy.requirements:
            requirements_short = vacancy.requirements[:150] + "..." if len(vacancy.requirements) > 150 else vacancy.requirements
            lines.append(f"Требования: {requirements_short}")

        # Оценка релевантности
        if hasattr(vacancy, '_relevance_score'):
            lines.append(f"Релевантность: {vacancy._relevance_score}")

        # Ссылка
        lines.append(f"Ссылка: {vacancy.url}")

        return lines

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
        return "\n".join(lines) + "\n" + "-" * 50

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

        print("-" * 80)

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

        if hasattr(salary_info, '__str__'):
            return str(salary_info)

        return "Зарплата не указана"

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


# Глобальный экземпляр форматтера
vacancy_formatter = VacancyFormatter()

"""
Унифицированный форматтер для отображения вакансий
"""

from typing import Optional
from src.vacancies.models import Vacancy


class VacancyFormatter:
    """Класс для форматирования и отображения вакансий"""
    
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
        lines = []
        
        # Добавляем номер отдельной строкой
        if number:
            lines.append(f"{number}.")
        
        # Добавляем название
        title = vacancy.title or getattr(vacancy, 'name', None) or 'Не указано'
        lines.append(f"Название: {title}")
        
        lines.append(f"Источник: {getattr(vacancy, 'source', 'Не указан')}")
        lines.append(f"Компания: {vacancy.employer.get('name') if vacancy.employer else 'Не указана'}")
        lines.append(f"ID: {vacancy.vacancy_id}")
        
        if vacancy.salary:
            lines.append(f"Зарплата: {vacancy.salary}")
        else:
            lines.append("Зарплата: Не указана")
        
        if vacancy.experience:
            lines.append(f"Опыт: {vacancy.experience}")
        
        if vacancy.employment:
            lines.append(f"Занятость: {vacancy.employment}")
        
        if vacancy.schedule:
            lines.append(f"График: {vacancy.schedule}")
        
        # Показываем ключевые слова
        if vacancy.keywords:
            keywords_str = ", ".join(vacancy.keywords[:10])
            if len(vacancy.keywords) > 10:
                keywords_str += f" и еще {len(vacancy.keywords) - 10}"
            lines.append(f"Ключевые слова: {keywords_str}")
        
        # Показываем навыки
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
        
        # Показываем краткое описание требований
        if vacancy.requirements:
            requirements_short = vacancy.requirements[:150] + "..." if len(vacancy.requirements) > 150 else vacancy.requirements
            lines.append(f"Требования: {requirements_short}")
        
        # Показываем оценку релевантности, если есть
        if hasattr(vacancy, '_relevance_score'):
            lines.append(f"Релевантность: {vacancy._relevance_score}")
        
        lines.append(f"Ссылка: {vacancy.url}")
        
        return "\n".join(lines)
    
    @staticmethod
    def display_vacancy_info(vacancy: Vacancy, number: Optional[int] = None) -> None:
        """
        Отображение информации о вакансии
        
        Args:
            vacancy: Объект вакансии
            number: Порядковый номер (опционально)
        """
        # Печатаем номер отдельно
        if number:
            print(f"{number}.")
        
        # Печатаем название
        title = vacancy.title or getattr(vacancy, 'name', None) or 'Не указано'
        print(f"Название: {title}")
        
        print(f"Источник: {getattr(vacancy, 'source', 'Не указан')}")
        print(f"Компания: {vacancy.employer.get('name') if vacancy.employer else 'Не указана'}")
        print(f"ID: {vacancy.vacancy_id}")
        
        if vacancy.salary:
            print(f"Зарплата: {vacancy.salary}")
        else:
            print("Зарплата: Не указана")
        
        if vacancy.experience:
            print(f"Опыт: {vacancy.experience}")
        
        if vacancy.employment:
            print(f"Занятость: {vacancy.employment}")
        
        if vacancy.schedule:
            print(f"График: {vacancy.schedule}")
        
        # Показываем ключевые слова
        if vacancy.keywords:
            keywords_str = ", ".join(vacancy.keywords[:10])
            if len(vacancy.keywords) > 10:
                keywords_str += f" и еще {len(vacancy.keywords) - 10}"
            print(f"Ключевые слова: {keywords_str}")
        
        # Показываем навыки
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
                print(f"Навыки: {skills_str}")
        
        # Показываем краткое описание требований
        if vacancy.requirements:
            requirements_short = vacancy.requirements[:150] + "..." if len(vacancy.requirements) > 150 else vacancy.requirements
            print(f"Требования: {requirements_short}")
        
        # Показываем оценку релевантности, если есть
        if hasattr(vacancy, '_relevance_score'):
            print(f"Релевантность: {vacancy._relevance_score}")
        
        print(f"Ссылка: {vacancy.url}")
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

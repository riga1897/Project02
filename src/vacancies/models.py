from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import logging
from .abstract import AbstractVacancy
from src.utils.salary import Salary
logging.basicConfig(level=logging.ERROR)
class Vacancy(AbstractVacancy):
    """Класс для представления вакансии с полной структурой HH.ru"""
    __slots__ = (
        'vacancy_id', 'title', 'url', 'salary', 'description', 
        'requirements', 'responsibilities', 'employer', 'experience',
        'employment', 'schedule', 'published_at', 'skills',
        'detailed_description', 'benefits', 'source'
    )
    def __init__(
        self,
        title: str,
        url: str,
        salary: Optional[Dict[str, Any]],
        description: str,
        requirements: Optional[str] = None,
        responsibilities: Optional[str] = None,
        employer: Optional[Dict[str, Any]] = None,
        experience: Optional[str] = None,
        employment: Optional[str] = None,
        schedule: Optional[str] = None,
        published_at: Optional[str] = None,
        skills: Optional[List[Dict[str, str]]] = None,
        
        detailed_description: Optional[str] = None,
        benefits: Optional[str] = None,
        vacancy_id: Optional[str] = None,
        source: str = "hh.ru"
    ):
        self.vacancy_id = vacancy_id or str(uuid.uuid4())
        self.title = title
        self.url = url
        self.salary = self._validate_salary(salary)
        self.description = description
        self.requirements = self._clean_html(requirements) if requirements else None
        self.responsibilities = self._clean_html(responsibilities) if responsibilities else None
        self.employer = employer
        self.experience = experience
        self.employment = employment
        self.schedule = schedule
        self.published_at = self._parse_datetime(published_at) if published_at else None
        self.skills = skills or []
        self.detailed_description = detailed_description or description
        self.benefits = benefits
        self.source = source
    def _validate_salary(self, salary_data: Optional[Dict[str, Any]]) -> Salary:
        """Приватный метод валидации данных о зарплате"""
        return Salary(salary_data) if salary_data else Salary()
    @staticmethod
    def _clean_html(text: str) -> str:
        """Очистка HTML-тегов из текста"""
        import re
        return re.sub(r'<[^>]+>', '', text)
    def _parse_datetime(self, published_at_str: str) -> datetime:
        """Парсинг строки с датой и временем в объект datetime"""
        if not published_at_str:
            return datetime.now()

        try:
            # Попробуем разные форматы даты
            formats = [
                '%Y-%m-%dT%H:%M:%S%z',  # '2024-01-15T10:30:45+0300'
                '%Y-%m-%dT%H:%M:%S',    # '2024-01-15T10:30:45'
                '%Y-%m-%d %H:%M:%S',    # '2024-01-15 10:30:45'
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(published_at_str, fmt)
                except ValueError:
                    continue

            # Если ни один формат не подошел
            logging.warning(f"Не удалось распарсить дату '{published_at_str}', используем текущее время")
            return datetime.now()

        except Exception as e:
            logging.error(f"Ошибка парсинга даты '{published_at_str}': {e}")
            return datetime.now()

    
    @classmethod
    def cast_to_object_list(cls, data):
        vacancies = []
        for item in data:
            try:
                vacancy = cls.from_dict(item)
                vacancies.append(vacancy)
            except ValueError as e:
                print(f"Skipping item due to validation error: {e}")
                continue
        return vacancies
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Vacancy':
        """Создает объект Vacancy из словаря с защитой от ошибок структуры"""
        try:
            if not isinstance(data, dict):
                raise ValueError("Данные должны быть словарем")

            # Обработка опыта работы (может быть как строкой, так и словарем)
            experience = None
            experience_data = data.get('experience')
            if isinstance(experience_data, dict):
                experience = experience_data.get('name')
            elif isinstance(experience_data, str):
                experience = experience_data

            # Безопасная обработка зарплаты
            salary = None
            salary_data = data.get('salary')
            if isinstance(salary_data, dict):
                salary = salary_data

            # Безопасная обработка работодателя
            employer = None
            employer_data = data.get('employer')
            if isinstance(employer_data, dict):
                employer = employer_data

            return cls(
                vacancy_id=str(data.get('id', '')),
                title=data.get('title', '') or data.get('name', ''),  # Приоритет title, fallback на name
                url=data.get('url', '') or data.get('alternate_url', ''),  # Приоритет url, fallback на alternate_url
                salary=salary,
                description=data.get('description', ''),
                requirements=data.get('snippet', {}).get('requirement') if isinstance(data.get('snippet'), dict) else None,
                responsibilities=data.get('snippet', {}).get('responsibility') if isinstance(data.get('snippet'), dict) else None,
                employer=employer,
                experience=experience,
                employment=data.get('employment', {}).get('name') if isinstance(data.get('employment'), dict) else None,
                schedule=data.get('schedule', {}).get('name') if isinstance(data.get('schedule'), dict) else None,
                published_at=data.get('published_at'),
                
                detailed_description=data.get('detailed_description'),
                benefits=data.get('benefits'),
                source=data.get('source', 'hh.ru'))

        except Exception as e:
            logging.error(f"Ошибка создания вакансии из данных: {data}\nОшибка: {e}")
            raise ValueError(f"Невозможно создать вакансию: {e}")
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'id': self.vacancy_id,
            'title': self.title,
            'url': self.url,
            'salary': self.salary.to_dict() if self.salary else None,
            'description': self.description,
            'requirements': self.requirements,
            'responsibilities': self.responsibilities,
            'employer': self.employer,
            'experience': self.experience,
            'employment': self.employment,
            'schedule': self.schedule,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'skills': self.skills,
            'detailed_description': self.detailed_description,
            'benefits': self.benefits,
            'source': self.source
        }
    def __str__(self) -> str:
        """Строковое представление вакансии"""
        parts = [
            f"Должность: {self.title}",
            f"Компания: {self.employer.get('name') if self.employer else 'Не указана'}",
            f"Источник: {self.source}",
            f"Зарплата: {self.salary}",
            f"Требования: {self.requirements[:100] + '...' if self.requirements else 'Не указаны'}",
            f"Ссылка: {self.url}"
        ]
        return "\n".join(parts)

    def __eq__(self, other) -> bool:
        """Сравнение вакансий по ID"""
        if not isinstance(other, Vacancy):
            return False
        return self.vacancy_id == other.vacancy_id

    def __lt__(self, other) -> bool:
        """Сравнение по зарплате для сортировки"""
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.salary.average < other.salary.average

    def __le__(self, other) -> bool:
        """Сравнение по зарплате (меньше или равно)"""
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.salary.average <= other.salary.average

    def __gt__(self, other) -> bool:
        """Сравнение по зарплате (больше)"""
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.salary.average > other.salary.average

    def __ge__(self, other) -> bool:
        """Сравнение по зарплате (больше или равно)"""
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.salary.average >= other.salary.average

    def __hash__(self) -> int:
        """Хеш для использования в множествах и словарях"""
        return hash(self.vacancy_id)
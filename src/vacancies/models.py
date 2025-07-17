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
        'employment', 'schedule', 'published_at', 'skills'
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
        vacancy_id: Optional[str] = None
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
        self.skills = skills
    def _validate_salary(self, salary_data: Optional[Dict[str, Any]]) -> Salary:
        """Приватный метод валидации данных о зарплате"""
        return Salary(salary_data) if salary_data else Salary()
    @staticmethod
    def _clean_html(text: str) -> str:
        """Очистка HTML-тегов из текста"""
        import re
        return re.sub(r'<[^>]+>', '', text)
    @staticmethod
    def _parse_datetime(dt_str: str) -> datetime:
        """Парсинг даты из строки"""
        return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S%z")
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
                title=data.get('title', ''),
                url=data.get('url', ''),
                salary=salary,
                description=data.get('description', ''),
                requirements=data.get('snippet', {}).get('requirement') if isinstance(data.get('snippet'), dict) else None,
                responsibilities=data.get('snippet', {}).get('responsibility') if isinstance(data.get('snippet'), dict) else None,
                employer=employer,
                experience=experience,
                employment=data.get('employment', {}).get('name') if isinstance(data.get('employment'), dict) else None,
                schedule=data.get('schedule', {}).get('name') if isinstance(data.get('schedule'), dict) else None,
                published_at=data.get('published_at'))

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
            'skills': self.skills
        }
    def __str__(self) -> str:
        """Строковое представление вакансии"""
        parts = [
            f"Должность: {self.title}",
            f"Компания: {self.employer.get('name') if self.employer else 'Не указана'}",
            f"Зарплата: {self.salary}",
            f"Требования: {self.requirements[:100] + '...' if self.requirements else 'Не указаны'}",
            f"Ссылка: {self.url}"
        ]
        return "\n".join(parts)
```
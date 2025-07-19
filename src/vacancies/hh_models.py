from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import logging
from .abstract import AbstractVacancy
from src.utils.salary import Salary

logger = logging.getLogger(__name__)


class HHVacancy(AbstractVacancy):
    """Класс для представления вакансии с HH.ru со специфичными для HH полями"""
    
    __slots__ = (
        'vacancy_id', 'title', 'url', 'salary', 'description', 
        'requirements', 'responsibilities', 'employer', 'experience',
        'employment', 'schedule', 'published_at', 'skills',
        'detailed_description', 'benefits', 'source', 'area', 'snippet'
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
        source: str = "hh.ru",
        area: Optional[Dict[str, Any]] = None,
        snippet: Optional[Dict[str, Any]] = None
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
        self.area = area  # Специфично для HH - информация о регионе
        self.snippet = snippet  # Специфично для HH - краткие выдержки из описания

    @staticmethod
    def _validate_salary(salary_data: Optional[Dict[str, Any]]) -> Salary:
        """Приватный метод валидации данных о зарплате для HH"""
        return Salary(salary_data) if salary_data else Salary()

    @staticmethod
    def _clean_html(text: str) -> str:
        """Очистка HTML-тегов из текста"""
        import re
        return re.sub(r'<[^>]+>', '', text)

    @staticmethod
    def _parse_datetime(published_at_str: str) -> datetime:
        """Парсинг строки с датой и временем в объект datetime для HH формата"""
        if not published_at_str:
            return datetime.now()

        try:
            # HH использует ISO формат с timezone
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

            logger.warning(f"Не удалось распарсить дату '{published_at_str}', используем текущее время")
            return datetime.now()

        except Exception as e:
            logger.error(f"Ошибка парсинга даты '{published_at_str}': {e}")
            return datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HHVacancy':
        """Создает объект HHVacancy из данных HH API"""
        try:
            if not isinstance(data, dict):
                raise ValueError("Данные должны быть словарем")

            # Обработка опыта работы (HH специфичная структура)
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

            # Обработка snippet (специфично для HH)
            snippet = data.get('snippet', {})
            requirements = None
            responsibilities = None
            if isinstance(snippet, dict):
                requirements = snippet.get('requirement')
                responsibilities = snippet.get('responsibility')

            return cls(
                vacancy_id=str(data.get('id', '')),
                title=data.get('name', ''),  # HH использует 'name' для названия
                url=data.get('alternate_url', ''),  # HH использует 'alternate_url'
                salary=salary,
                description=data.get('description', ''),
                requirements=requirements,
                responsibilities=responsibilities,
                employer=employer,
                experience=experience,
                employment=data.get('employment', {}).get('name') if isinstance(data.get('employment'), dict) else None,
                schedule=data.get('schedule', {}).get('name') if isinstance(data.get('schedule'), dict) else None,
                published_at=data.get('published_at'),
                detailed_description=data.get('detailed_description'),
                benefits=data.get('benefits'),
                source="hh.ru",
                area=data.get('area'),  # Специфично для HH
                snippet=snippet  # Специфично для HH
            )

        except Exception as e:
            logger.error(f"Ошибка создания HH вакансии из данных: {data}\nОшибка: {e}")
            raise ValueError(f"Невозможно создать HH вакансию: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь в формате HH API"""
        return {
            'id': self.vacancy_id,
            'name': self.title,
            'alternate_url': self.url,
            'salary': self.salary.to_dict() if self.salary else None,
            'description': self.description,
            'snippet': {
                'requirement': self.requirements,
                'responsibility': self.responsibilities
            },
            'employer': self.employer,
            'experience': {'name': self.experience} if self.experience else None,
            'employment': {'name': self.employment} if self.employment else None,
            'schedule': {'name': self.schedule} if self.schedule else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'skills': self.skills,
            'detailed_description': self.detailed_description,
            'benefits': self.benefits,
            'source': self.source,
            'area': self.area
        }

    def __str__(self) -> str:
        """Строковое представление HH вакансии"""
        parts = [
            f"[HH] Должность: {self.title}",
            f"Компания: {self.employer.get('name') if self.employer else 'Не указана'}",
            f"Регион: {self.area.get('name') if self.area else 'Не указан'}",
            f"Зарплата: {self.salary}",
            f"Требования: {self.requirements[:100] + '...' if self.requirements else 'Не указаны'}",
            f"Ссылка: {self.url}"
        ]
        return "\n".join(parts)

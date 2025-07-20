from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import logging
from .abstract import AbstractVacancy
from src.utils.salary import Salary
from typing import Union

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class Vacancy(AbstractVacancy):
    """
    Модуль моделей данных для работы с вакансиями.

    Содержит основную модель Vacancy и вспомогательные классы для представления
    структурированных данных о вакансиях из различных источников (HH.ru, SuperJob).
    Обеспечивает унификацию данных и их валидацию.
    """

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
        salary: Optional[Dict[str, Any]] = None,
        description: str = "",
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
        source: str = "unknown"
    ):
        self.raw_data = None
        self.profession = None
        self.area = None
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

    @staticmethod
    def _validate_salary(salary_data: Optional[Dict[str, Any]]) -> Salary:
        """Приватный метод валидации данных о зарплате"""
        return Salary(salary_data) if salary_data else Salary()

    @staticmethod
    def _clean_html(text: str) -> str:
        """Очистка HTML-тегов из текста"""
        import re
        return re.sub(r'<[^>]+>', '', text)

    @staticmethod
    def _parse_datetime(date_str: Union[str, int, None]) -> Optional[datetime]:
        """
        Универсальный парсер дат для разных форматов API

        Args:
            date_str: Строка с датой в различных форматах или timestamp

        Returns:
            datetime object или None при ошибке
        """
        if not date_str:
            return None

        try:
            # Если это timestamp (для SuperJob)
            if isinstance(date_str, (int, float)):
                return datetime.fromtimestamp(date_str)

            # Если это строка
            if isinstance(date_str, str):
                # Сначала попробуем как timestamp
                try:
                    timestamp = float(date_str)
                    return datetime.fromtimestamp(timestamp)
                except (ValueError, TypeError):
                    pass

                # Попробуем разные форматы строк
                formats = [
                    '%Y-%m-%dT%H:%M:%S%z',      # ISO with timezone
                    '%Y-%m-%dT%H:%M:%S',        # ISO without timezone  
                    '%Y-%m-%d %H:%M:%S',        # Standard format
                    '%Y-%m-%d',                 # Date only
                ]

                for fmt in formats:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue

        except Exception as e:
            logger.error(f"Ошибка парсинга даты '{date_str}': {e}")

        return None

    @classmethod
    def cast_to_object_list(cls, data):
        """Преобразование списка словарей в список объектов Vacancy"""
        vacancies = []
        for item in data:
            try:
                vacancy = cls.from_dict(item)
                vacancies.append(vacancy)
            except ValueError as e:
                logging.warning(f"Пропуск элемента из-за ошибки валидации: {e}")
                continue
        return vacancies

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Vacancy':
        """Создает унифицированный объект Vacancy из словаря"""
        try:
            if not isinstance(data, dict):
                raise ValueError("Данные должны быть словарем")

            # Универсальная обработка полей из разных источников
            title = (
                data.get('title') or 
                data.get('name') or 
                data.get('profession') or 
                'Без названия'
            )

            url = (
                data.get('alternate_url') or  # Веб-версия для HH
                data.get('link') or           # Веб-версия для SuperJob
                data.get('url') or            # Fallback на API-ссылку
                ''
            )

            vacancy_id = str(data.get('id', ''))

            # Обработка зарплаты (универсальная для всех источников)
            salary = data.get('salary')

            # Обработка работодателя
            employer = data.get('employer')
            if not employer and data.get('firm_name'):
                employer = {"name": data.get('firm_name')}

            # Обработка опыта работы
            experience = None
            experience_data = data.get('experience')
            if isinstance(experience_data, dict):
                experience = experience_data.get('name') or experience_data.get('title')
            elif isinstance(experience_data, str):
                experience = experience_data

            # Обработка типа занятости
            employment = None
            employment_data = data.get('employment') or data.get('type_of_work')
            if isinstance(employment_data, dict):
                employment = employment_data.get('name') or employment_data.get('title')
            elif isinstance(employment_data, str):
                employment = employment_data

            # Обработка описания и требований
            description = (
                data.get('description') or 
                data.get('vacancyRichText') or 
                ''
            )

            # Если описание пустое, но есть requirements или responsibilities - объединяем их
            if not description.strip():
                desc_parts = []
                if data.get('requirements'):
                    desc_parts.append(data.get('requirements'))
                if data.get('responsibilities'):
                    desc_parts.append(data.get('responsibilities'))
                if desc_parts:
                    description = " ".join(desc_parts)

            requirements = None
            responsibilities = None

            # Для HH (snippet)
            snippet = data.get('snippet', {})
            if isinstance(snippet, dict):
                requirements = snippet.get('requirement')
                responsibilities = snippet.get('responsibility')

            # Для SuperJob (прямые поля)
            if not requirements:
                requirements = data.get('candidat')
            if not responsibilities:
                responsibilities = data.get('work')

            # Определяем источник на основе структуры данных
            source = data.get('source', 'unknown')
            if source == 'unknown':
                # Если source не указан, пытаемся определить по URL или структуре данных
                if 'alternate_url' in data or 'hh.ru' in url:
                    source = 'hh.ru'
                elif 'superjob.ru' in url or 'sj.ru' in url:
                    source = 'superjob.ru'
                elif 'profession' in data and 'candidat' in data:
                    source = 'superjob.ru'  # SuperJob использует эти поля
                elif 'name' in data and 'snippet' in data:
                    source = 'hh.ru'  # HH использует эти поля

            return cls(
                vacancy_id=vacancy_id,
                title=title,
                url=url,
                salary=salary,
                description=description,
                requirements=requirements,
                responsibilities=responsibilities,
                employer=employer,
                experience=experience,
                employment=employment,
                schedule=data.get('schedule', {}).get('name') if isinstance(data.get('schedule'), dict) else None,
                published_at=data.get('published_at') or data.get('date_published'),
                detailed_description=data.get('detailed_description'),
                benefits=data.get('benefits'),
                source=source
            )

        except Exception as e:
            logging.error(f"Ошибка создания унифицированной вакансии из данных: {data}\nОшибка: {e}")
            raise ValueError(f"Невозможно создать унифицированную вакансию: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в унифицированный словарь"""
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
        """Строковое представление унифицированной вакансии"""
        parts = [
            f"[{self.source.upper()}] Должность: {self.title}",
            f"Компания: {self.employer.get('name') if self.employer else 'Не указана'}",
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
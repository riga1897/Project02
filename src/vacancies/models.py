from typing import List, Dict, Any, Optional
import uuid
from .abstract import AbstractVacancy


class Vacancy(AbstractVacancy):
    """Класс для представления вакансии"""

    __slots__ = ('vacancy_id', 'title', 'url', 'salary', 'description')

    def __init__(self, title: str, url: str, salary: Optional[str], description: str, vacancy_id: Optional[str] = None):
        """
        Инициализация вакансии
        :param title: Название вакансии
        :param url: Ссылка на вакансию
        :param salary: Зарплата (может быть None)
        :param description: Описание вакансии
        :param vacancy_id: Уникальный идентификатор вакансии
        """
        self.vacancy_id = vacancy_id or str(uuid.uuid4())
        self.title = title
        self.url = url
        self.salary = salary
        self.description = description

    @classmethod
    def cast_to_object_list(cls, data: List[Dict[str, Any]]) -> List['Vacancy']:
        """Преобразует список словарей в список объектов Vacancy"""
        return [cls.from_dict(item) for item in data]

    def to_dict(self) -> Dict[str, Any]:
        """Возвращает словарь с данными вакансии"""
        return {
            'id': self.vacancy_id,
            'title': self.title,
            'url': self.url,
            'salary': self.salary,
            'description': self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Vacancy':
        """Создает объект Vacancy из словаря"""
        return cls(
            title=data.get('title', ''),
            url=data.get('url', ''),
            salary=data.get('salary'),
            description=data.get('description', ''),
            vacancy_id=data.get('id')
        )

    def __eq__(self, other: object) -> bool:
        """Сравнение вакансий по ID"""
        if not isinstance(other, Vacancy):
            return False
        return self.vacancy_id == other.vacancy_id

    def __str__(self) -> str:
        """Строковое представление вакансии"""
        return f"{self.title} ({self.salary or 'Зарплата не указана'})"

    def __hash__(self) -> int:
        """Хеш на основе ID вакансии"""
        return hash(self.vacancy_id)

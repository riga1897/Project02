from typing import List, Dict, Any, Optional
from .abstract import AbstractVacancy


class Vacancy(AbstractVacancy):
    """Класс для представления вакансии с реализацией всех методов"""

    __slots__ = ('title', 'url', 'salary', 'description')

    def __init__(self, title: str, url: str, salary: Optional[str], description: str):
        """
        Инициализация вакансии
        :param title: Название вакансии
        :param url: Ссылка на вакансию
        :param salary: Зарплата (может быть None)
        :param description: Описание вакансии
        """
        self.title = title
        self.url = url
        self.salary = salary
        self.description = description

    @classmethod
    def cast_to_object_list(cls, data: List[Dict[str, Any]]) -> List['Vacancy']:
        """
        Преобразует список словарей в список объектов Vacancy
        :param data: Список словарей с данными вакансий
        :return: Список объектов Vacancy
        """
        vacancies = []
        for item in data:
            # Оставляем только ожидаемые поля
            vacancy_data = {
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'salary': item.get('salary'),
                'description': item.get('description', '')
            }
            vacancies.append(cls.from_dict(vacancy_data))
        return vacancies

    def to_dict(self) -> Dict[str, Any]:
        """Возвращает словарь с данными вакансии"""
        return {attr: getattr(self, attr) for attr in self.__slots__}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Vacancy':
        """
        Создает объект вакансии из словаря
        :param data: Словарь с данными вакансии
        :return: Объект Vacancy
        """
        return cls(
            title=data.get('title', ''),
            url=data.get('url', ''),
            salary=data.get('salary'),
            description=data.get('description', '')
        )

    def __eq__(self, other):
        """Сравнение вакансий по всем атрибутам"""
        if not isinstance(other, Vacancy):
            return False
        return all(getattr(self, attr) == getattr(other, attr) for attr in self.__slots__)

    def __str__(self):
        """Строковое представление вакансии"""
        return f"{self.title} ({self.salary})"
        
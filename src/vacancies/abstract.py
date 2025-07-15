from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class AbstractVacancy(ABC):
    """Абстрактный класс для представления вакансии"""

    @abstractmethod
    def __init__(self, title: str, url: str, salary: Optional[str], description: str):
        """
        Инициализация вакансии
        :param title: Название вакансии
        :param url: Ссылка на вакансию
        :param salary: Зарплата (может быть None)
        :param description: Описание вакансии
        """


    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует вакансию в словарь"""


    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AbstractVacancy':
        """
        Создает объект вакансии из словаря
        :param data: Словарь с данными вакансии
        :return: Объект вакансии
        """

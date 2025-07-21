from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.vacancies.abstract import AbstractVacancy


class AbstractVacancyStorage(ABC):
    """Абстрактный класс для работы с хранилищем вакансий"""

    @abstractmethod
    def add_vacancy(self, vacancy: AbstractVacancy) -> None:
        """
        Добавляет вакансию в хранилище
        :param vacancy: Объект вакансии для добавления
        """

    @abstractmethod
    def get_vacancies(self, filters: Optional[Dict[str, Any]] = None) -> List[AbstractVacancy]:
        """
        Возвращает список вакансий с учетом фильтров
        :param filters: Словарь с критериями фильтрации
        :return: Список вакансий
        """

    @abstractmethod
    def delete_vacancy(self, vacancy: AbstractVacancy) -> None:
        """
        Удаляет вакансию из хранилища
        :param vacancy: Объект вакансии для удаления
        """

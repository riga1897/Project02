from pathlib import Path
from typing import List, Dict, Optional, Any
from src.vacancies.models import Vacancy
from src.storage.abstract import AbstractVacancyStorage
from src.utils.file_handlers import read_json, write_json


class JSONSaver(AbstractVacancyStorage):
    """Класс для сохранения вакансий в JSON-файл"""

    def __init__(self, file_path: str = 'vacancies.json'):
        """
        Инициализация хранилища
        :param file_path: Путь к JSON-файлу (по умолчанию 'vacancies.json')
        """
        self.file_path = Path(file_path)
        self.file_path.touch(exist_ok=True)

    def add_vacancy(self, vacancy: Vacancy) -> None:
        """Добавляет вакансию в JSON-файл"""
        data = read_json(self.file_path) or []
        data.append(vacancy.to_dict())
        write_json(self.file_path, data)

    def delete_vacancy(self, vacancy: Vacancy) -> None:
        """Удаляет вакансию из JSON-файла"""
        vacancies = self.get_vacancies()
        filtered = [v for v in vacancies if v != vacancy]
        write_json(self.file_path, [v.to_dict() for v in filtered])

    def get_vacancies(self, filters: Optional[Dict[str, Any]] = None) -> List[Vacancy]:
        """
        Возвращает список вакансий с учетом фильтров
        :param filters: Словарь с критериями фильтрации
        :return: Список объектов Vacancy
        """
        data = read_json(self.file_path) or []
        vacancies = [Vacancy.from_dict(item) for item in data]

        if not filters:
            return vacancies

        return [v for v in vacancies if all(
            getattr(v, key) == value for key, value in filters.items()
        )]
        
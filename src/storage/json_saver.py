from pathlib import Path
from typing import List, Dict, Optional, Any, Union, Iterator
from src.vacancies.models import Vacancy
from src.utils.file_handlers import json_handler


class JSONSaver:
    """Класс для работы с вакансиями в JSON-файле"""

    def __init__(self, file_path: str = "vacancies.json"):
        self.file_path = Path(file_path)
        self.file_path.touch(exist_ok=True)
        self.allowed_filters = {"id", "title", "url", "salary", "description"}
        self.updatable_fields = {"salary", "description"}

    @property
    def _data(self) -> List[Dict[str, Any]]:
        """Возвращает данные из файла"""
        return json_handler.read_json(self.file_path)

    def _save_data(self, data: List[Dict[str, Any]]) -> None:
        """Сохраняет данные в файл"""
        json_handler.write_json(self.file_path, data)

    def get_vacancies(self, filters: Optional[Dict[str, Any]] = None) -> Iterator[Vacancy]:
        """Возвращает отфильтрованные вакансии"""
        vacancies = (Vacancy.from_dict(item) for item in self._data)

        if not filters:
            yield from vacancies
            return

        # Проверяем допустимость фильтров, извлекая имена полей из операторов
        filter_fields = set()
        for key in filters.keys():
            if "__" in key:
                field, _ = key.split("__", 1)
                filter_fields.add(field)
            else:
                filter_fields.add(key)
        
        invalid_filters = filter_fields - self.allowed_filters
        if invalid_filters:
            raise ValueError(f"Недопустимые фильтры: {invalid_filters}")

        for v in vacancies:
            if all(self._apply_filter(v, key, value) for key, value in filters.items()):
                yield v

    def _apply_filter(self, vacancy: Vacancy, key: str, value: Any) -> bool:
        """Применяет фильтр к вакансии"""
        if "__" in key:
            field, op = key.split("__", 1)
            attr = getattr(vacancy, field, None)

            if op == "gt":
                return str(attr) > str(value)
            if op == "lt":
                return str(attr) < str(value)
            if op == "contains":
                return str(value).lower() in str(attr).lower()
            raise ValueError(f"Неизвестный оператор: {op}")
        return str(getattr(vacancy, key)) == str(value)

    def add_vacancy(self, vacancy: Union[Vacancy, List[Vacancy]]) -> None:
        """Добавляет вакансию(и) в хранилище"""
        data = self._data
        vacancies = [vacancy] if isinstance(vacancy, Vacancy) else vacancy

        for v in vacancies:
            if not hasattr(v, 'vacancy_id'):
                raise ValueError("Вакансия должна иметь атрибут vacancy_id")

            if any(item["id"] == v.vacancy_id for item in data):
                raise ValueError(f"Вакансия с ID {v.vacancy_id} уже существует")

            data.append(v.to_dict())

        self._save_data(data)

    def delete_vacancy(self, vacancy_id: str) -> None:
        """Удаляет вакансию по ID"""
        data = [item for item in self._data if item["id"] != vacancy_id]
        if len(data) == len(self._data):
            raise ValueError(f"Вакансия с ID {vacancy_id} не найдена")
        self._save_data(data)

    def update_vacancy(self, vacancy_id: str, updates: Dict[str, Any]) -> None:
        """Обновляет поля вакансии"""
        data = self._data
        updated = False

        for item in data:
            if item["id"] == vacancy_id:
                invalid_fields = set(updates.keys()) - self.updatable_fields
                if invalid_fields:
                    raise ValueError(f"Нельзя изменить поля: {invalid_fields}")

                item.update(updates)
                updated = True

        if not updated:
            raise ValueError(f"Вакансия с ID {vacancy_id} не найдена")
        self._save_data(data)

    def get_vacancy_by_id(self, vacancy_id: str) -> Optional[Vacancy]:
        """Находит вакансию по ID"""
        for item in self._data:
            if item["id"] == vacancy_id:
                return Vacancy.from_dict(item)
        return None

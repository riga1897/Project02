
import pytest
from abc import ABC
from unittest.mock import Mock
from typing import List, Dict, Any, Optional

from src.storage.abstract import AbstractVacancyStorage
from src.vacancies.abstract import AbstractVacancy


class TestAbstractVacancyStorage:
    """Тесты для абстрактного класса AbstractVacancyStorage"""

    def test_is_abstract_class(self):
        """Проверяем, что AbstractVacancyStorage является абстрактным классом"""
        assert issubclass(AbstractVacancyStorage, ABC)
        
        # Проверяем, что нельзя создать экземпляр абстрактного класса
        with pytest.raises(TypeError):
            AbstractVacancyStorage()

    def test_has_abstract_methods(self):
        """Проверяем наличие абстрактных методов"""
        abstract_methods = AbstractVacancyStorage.__abstractmethods__
        expected_methods = {'add_vacancy', 'get_vacancies', 'delete_vacancy'}
        assert abstract_methods == expected_methods

    def test_concrete_implementation_works(self):
        """Проверяем, что конкретная реализация работает"""
        
        # Создаем простую mock-реализацию AbstractVacancy для тестов
        class MockVacancy(AbstractVacancy):
            def __init__(self, id: str = "1", title: str = "Test"):
                self.id = id
                self.title = title
            
            def to_dict(self) -> Dict[str, Any]:
                return {"id": self.id, "title": self.title}
            
            @classmethod
            def from_dict(cls, data: Dict[str, Any]) -> 'MockVacancy':
                return cls(data.get("id", "1"), data.get("title", "Test"))

        class ConcreteStorage(AbstractVacancyStorage):
            def __init__(self):
                self.vacancies: List[AbstractVacancy] = []

            def add_vacancy(self, vacancy: AbstractVacancy) -> None:
                self.vacancies.append(vacancy)

            def get_vacancies(self, filters: Optional[Dict[str, Any]] = None) -> List[AbstractVacancy]:
                if filters is None:
                    return self.vacancies.copy()
                # Простая фильтрация по title
                if 'title' in filters:
                    return [v for v in self.vacancies if hasattr(v, 'title') and v.title == filters['title']]
                return self.vacancies.copy()

            def delete_vacancy(self, vacancy: AbstractVacancy) -> None:
                if vacancy in self.vacancies:
                    self.vacancies.remove(vacancy)

        # Тестируем конкретную реализацию
        storage = ConcreteStorage()
        vacancy = MockVacancy("1", "Test Job")

        # Тестируем add_vacancy
        storage.add_vacancy(vacancy)
        assert len(storage.vacancies) == 1

        # Тестируем get_vacancies без фильтров
        result = storage.get_vacancies()
        assert len(result) == 1
        assert result[0] == vacancy

        # Тестируем get_vacancies с фильтрами
        filtered = storage.get_vacancies({"title": "Test Job"})
        assert len(filtered) == 1
        
        no_match = storage.get_vacancies({"title": "Other Job"})
        assert len(no_match) == 0

        # Тестируем delete_vacancy
        storage.delete_vacancy(vacancy)
        assert len(storage.vacancies) == 0

    def test_incomplete_implementation_fails(self):
        """Проверяем, что неполная реализация не работает"""
        
        class IncompleteStorage(AbstractVacancyStorage):
            def add_vacancy(self, vacancy: AbstractVacancy) -> None:
                pass
            
            def get_vacancies(self, filters: Optional[Dict[str, Any]] = None) -> List[AbstractVacancy]:
                return []
            # delete_vacancy не реализован

        # Попытка создать экземпляр должна вызвать ошибку
        with pytest.raises(TypeError):
            IncompleteStorage()

    def test_method_signatures(self):
        """Проверяем сигнатуры методов"""
        import inspect
        
        # Проверяем add_vacancy
        add_method = getattr(AbstractVacancyStorage, 'add_vacancy')
        assert hasattr(add_method, '__isabstractmethod__')
        
        # Проверяем get_vacancies
        get_method = getattr(AbstractVacancyStorage, 'get_vacancies')
        assert hasattr(get_method, '__isabstractmethod__')
        
        # Проверяем delete_vacancy
        delete_method = getattr(AbstractVacancyStorage, 'delete_vacancy')
        assert hasattr(delete_method, '__isabstractmethod__')

    def test_inheritance_chain(self):
        """Проверяем цепочку наследования"""
        
        class ConcreteStorage(AbstractVacancyStorage):
            def add_vacancy(self, vacancy: AbstractVacancy) -> None:
                pass
            
            def get_vacancies(self, filters: Optional[Dict[str, Any]] = None) -> List[AbstractVacancy]:
                return []
            
            def delete_vacancy(self, vacancy: AbstractVacancy) -> None:
                pass

        storage = ConcreteStorage()
        assert isinstance(storage, AbstractVacancyStorage)
        assert isinstance(storage, ABC)

    def test_multiple_storage_implementations(self):
        """Проверяем работу нескольких реализаций хранилища"""
        
        class MockVacancy(AbstractVacancy):
            def __init__(self, id: str):
                self.id = id
            
            def to_dict(self) -> Dict[str, Any]:
                return {"id": self.id}
            
            @classmethod
            def from_dict(cls, data: Dict[str, Any]) -> 'MockVacancy':
                return cls(data.get("id", "1"))

        class MemoryStorage(AbstractVacancyStorage):
            def __init__(self):
                self.data = []
            
            def add_vacancy(self, vacancy: AbstractVacancy) -> None:
                self.data.append(vacancy)
            
            def get_vacancies(self, filters: Optional[Dict[str, Any]] = None) -> List[AbstractVacancy]:
                return self.data.copy()
            
            def delete_vacancy(self, vacancy: AbstractVacancy) -> None:
                if vacancy in self.data:
                    self.data.remove(vacancy)

        class DictStorage(AbstractVacancyStorage):
            def __init__(self):
                self.data = {}
            
            def add_vacancy(self, vacancy: AbstractVacancy) -> None:
                self.data[vacancy.id] = vacancy
            
            def get_vacancies(self, filters: Optional[Dict[str, Any]] = None) -> List[AbstractVacancy]:
                return list(self.data.values())
            
            def delete_vacancy(self, vacancy: AbstractVacancy) -> None:
                if vacancy.id in self.data:
                    del self.data[vacancy.id]

        # Тестируем обе реализации
        vacancy = MockVacancy("test_id")
        
        memory_storage = MemoryStorage()
        dict_storage = DictStorage()
        
        # Проверяем, что оба являются AbstractVacancyStorage
        assert isinstance(memory_storage, AbstractVacancyStorage)
        assert isinstance(dict_storage, AbstractVacancyStorage)
        
        # Тестируем одинаковое поведение
        for storage in [memory_storage, dict_storage]:
            storage.add_vacancy(vacancy)
            vacancies = storage.get_vacancies()
            assert len(vacancies) == 1
            assert vacancies[0] == vacancy
            
            storage.delete_vacancy(vacancy)
            assert len(storage.get_vacancies()) == 0

    def test_filters_parameter_optional(self):
        """Проверяем, что параметр filters является необязательным"""
        
        class ConcreteStorage(AbstractVacancyStorage):
            def add_vacancy(self, vacancy: AbstractVacancy) -> None:
                pass
            
            def get_vacancies(self, filters: Optional[Dict[str, Any]] = None) -> List[AbstractVacancy]:
                # Проверяем, что можно вызывать без параметров
                return []
            
            def delete_vacancy(self, vacancy: AbstractVacancy) -> None:
                pass

        storage = ConcreteStorage()
        # Должно работать без аргументов
        result = storage.get_vacancies()
        assert result == []
        
        # И с аргументами
        result_with_filters = storage.get_vacancies({"test": "value"})
        assert result_with_filters == []

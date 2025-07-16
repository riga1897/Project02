
import pytest
from abc import ABC
from typing import List, Dict, Any, Optional
from src.storage.abstract import AbstractVacancyStorage
from src.vacancies.abstract import AbstractVacancy


class MockVacancy(AbstractVacancy):
    """Mock implementation of AbstractVacancy for testing"""
    
    def __init__(self, title: str, url: str, salary: Optional[str], description: str):
        self.title = title
        self.url = url
        self.salary = salary
        self.description = description
        self.vacancy_id = f"mock_{title}_{url}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "salary": self.salary,
            "description": self.description,
            "id": self.vacancy_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MockVacancy':
        return cls(
            title=data["title"],
            url=data["url"],
            salary=data["salary"],
            description=data["description"]
        )


class ConcreteVacancyStorage(AbstractVacancyStorage):
    """Concrete implementation of AbstractVacancyStorage for testing"""
    
    def __init__(self):
        self.vacancies = []
    
    def add_vacancy(self, vacancy: AbstractVacancy) -> None:
        self.vacancies.append(vacancy)
    
    def get_vacancies(self, filters: Optional[Dict[str, Any]] = None) -> List[AbstractVacancy]:
        if not filters:
            return self.vacancies
        
        filtered = []
        for vacancy in self.vacancies:
            match = True
            for key, value in filters.items():
                if getattr(vacancy, key, None) != value:
                    match = False
                    break
            if match:
                filtered.append(vacancy)
        return filtered
    
    def delete_vacancy(self, vacancy: AbstractVacancy) -> None:
        if vacancy in self.vacancies:
            self.vacancies.remove(vacancy)


class TestAbstractVacancyStorage:
    """Tests for AbstractVacancyStorage abstract class"""

    def test_abstract_class_cannot_be_instantiated(self):
        """Test that AbstractVacancyStorage cannot be instantiated directly"""
        with pytest.raises(TypeError):
            AbstractVacancyStorage()

    def test_abstract_class_is_abc(self):
        """Test that AbstractVacancyStorage is an ABC"""
        assert issubclass(AbstractVacancyStorage, ABC)

    def test_abstract_methods_exist(self):
        """Test that all required abstract methods are defined"""
        abstract_methods = AbstractVacancyStorage.__abstractmethods__
        expected_methods = {'add_vacancy', 'get_vacancies', 'delete_vacancy'}
        assert abstract_methods == expected_methods

    def test_concrete_implementation_works(self):
        """Test that concrete implementation can be instantiated and used"""
        storage = ConcreteVacancyStorage()
        assert isinstance(storage, AbstractVacancyStorage)

    def test_add_vacancy_method_signature(self):
        """Test add_vacancy method signature"""
        storage = ConcreteVacancyStorage()
        vacancy = MockVacancy("Test", "http://test.com", "1000", "Description")
        
        # Should not raise any errors
        storage.add_vacancy(vacancy)
        assert len(storage.vacancies) == 1

    def test_get_vacancies_method_signature(self):
        """Test get_vacancies method signature"""
        storage = ConcreteVacancyStorage()
        vacancy = MockVacancy("Test", "http://test.com", "1000", "Description")
        storage.add_vacancy(vacancy)
        
        # Test without filters
        vacancies = storage.get_vacancies()
        assert len(vacancies) == 1
        assert vacancies[0] == vacancy
        
        # Test with filters
        vacancies = storage.get_vacancies({"title": "Test"})
        assert len(vacancies) == 1
        
        vacancies = storage.get_vacancies({"title": "NonExistent"})
        assert len(vacancies) == 0

    def test_delete_vacancy_method_signature(self):
        """Test delete_vacancy method signature"""
        storage = ConcreteVacancyStorage()
        vacancy = MockVacancy("Test", "http://test.com", "1000", "Description")
        storage.add_vacancy(vacancy)
        
        assert len(storage.vacancies) == 1
        storage.delete_vacancy(vacancy)
        assert len(storage.vacancies) == 0

    def test_incomplete_implementation_fails(self):
        """Test that incomplete implementation raises TypeError"""
        
        class IncompleteStorage(AbstractVacancyStorage):
            def add_vacancy(self, vacancy: AbstractVacancy) -> None:
                pass
            # Missing get_vacancies and delete_vacancy
        
        with pytest.raises(TypeError):
            IncompleteStorage()

    def test_method_annotations(self):
        """Test that abstract methods have correct annotations"""
        add_vacancy_annotations = AbstractVacancyStorage.add_vacancy.__annotations__
        get_vacancies_annotations = AbstractVacancyStorage.get_vacancies.__annotations__
        delete_vacancy_annotations = AbstractVacancyStorage.delete_vacancy.__annotations__
        
        # Check return types
        assert add_vacancy_annotations.get('return') is None
        assert get_vacancies_annotations.get('return') == List[AbstractVacancy]
        assert delete_vacancy_annotations.get('return') is None

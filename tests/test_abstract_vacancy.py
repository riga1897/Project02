
import pytest
from abc import ABC
from unittest.mock import Mock
from typing import Dict, Any

from src.vacancies.abstract import AbstractVacancy


class TestAbstractVacancy:
    """Тесты для абстрактного класса AbstractVacancy"""

    def test_is_abstract_class(self):
        """Проверяем, что AbstractVacancy является абстрактным классом"""
        assert issubclass(AbstractVacancy, ABC)
        
        # Проверяем, что нельзя создать экземпляр абстрактного класса
        with pytest.raises(TypeError):
            AbstractVacancy()

    def test_has_abstract_methods(self):
        """Проверяем наличие абстрактных методов"""
        abstract_methods = AbstractVacancy.__abstractmethods__
        expected_methods = {'__init__', 'to_dict', 'from_dict'}
        assert abstract_methods == expected_methods

    def test_concrete_implementation_works(self):
        """Проверяем, что конкретная реализация работает"""
        
        class ConcreteVacancy(AbstractVacancy):
            def __init__(self, title: str = "Test"):
                self.title = title
            
            def to_dict(self) -> Dict[str, Any]:
                return {"title": self.title}
            
            @classmethod
            def from_dict(cls, data: Dict[str, Any]) -> 'ConcreteVacancy':
                return cls(data.get("title", "Default"))

        # Создаем экземпляр конкретной реализации
        vacancy = ConcreteVacancy("Test Vacancy")
        assert vacancy.title == "Test Vacancy"
        
        # Тестируем to_dict
        result = vacancy.to_dict()
        assert result == {"title": "Test Vacancy"}
        
        # Тестируем from_dict
        vacancy_from_dict = ConcreteVacancy.from_dict({"title": "From Dict"})
        assert vacancy_from_dict.title == "From Dict"

    def test_incomplete_implementation_fails(self):
        """Проверяем, что неполная реализация не работает"""
        
        class IncompleteVacancy(AbstractVacancy):
            def __init__(self):
                pass
            
            def to_dict(self) -> Dict[str, Any]:
                return {}
            # from_dict не реализован

        # Попытка создать экземпляр должна вызвать ошибку
        with pytest.raises(TypeError):
            IncompleteVacancy()

    def test_method_signatures(self):
        """Проверяем сигнатуры методов"""
        import inspect
        
        # Проверяем to_dict
        to_dict_method = getattr(AbstractVacancy, 'to_dict')
        assert hasattr(to_dict_method, '__isabstractmethod__')
        
        # Проверяем from_dict
        from_dict_method = getattr(AbstractVacancy, 'from_dict')
        assert hasattr(from_dict_method, '__isabstractmethod__')
        
        # Проверяем __init__
        init_method = getattr(AbstractVacancy, '__init__')
        assert hasattr(init_method, '__isabstractmethod__')

    def test_inheritance_chain(self):
        """Проверяем цепочку наследования"""
        
        class ConcreteVacancy(AbstractVacancy):
            def __init__(self):
                pass
            
            def to_dict(self) -> Dict[str, Any]:
                return {}
            
            @classmethod
            def from_dict(cls, data: Dict[str, Any]) -> 'ConcreteVacancy':
                return cls()

        vacancy = ConcreteVacancy()
        assert isinstance(vacancy, AbstractVacancy)
        assert isinstance(vacancy, ABC)

    def test_multiple_concrete_implementations(self):
        """Проверяем работу нескольких конкретных реализаций"""
        
        class VacancyA(AbstractVacancy):
            def __init__(self, name: str = "A"):
                self.name = name
            
            def to_dict(self) -> Dict[str, Any]:
                return {"type": "A", "name": self.name}
            
            @classmethod
            def from_dict(cls, data: Dict[str, Any]) -> 'VacancyA':
                return cls(data.get("name", "A"))

        class VacancyB(AbstractVacancy):
            def __init__(self, value: int = 1):
                self.value = value
            
            def to_dict(self) -> Dict[str, Any]:
                return {"type": "B", "value": self.value}
            
            @classmethod
            def from_dict(cls, data: Dict[str, Any]) -> 'VacancyB':
                return cls(data.get("value", 1))

        # Создаем экземпляры разных реализаций
        vacancy_a = VacancyA("Test A")
        vacancy_b = VacancyB(42)
        
        # Проверяем, что оба являются AbstractVacancy
        assert isinstance(vacancy_a, AbstractVacancy)
        assert isinstance(vacancy_b, AbstractVacancy)
        
        # Проверяем различное поведение
        assert vacancy_a.to_dict() == {"type": "A", "name": "Test A"}
        assert vacancy_b.to_dict() == {"type": "B", "value": 42}


import pytest
from unittest.mock import Mock
from src.storage.abstract import AbstractVacancyStorage
from src.vacancies.abstract import AbstractVacancy


class TestAbstractVacancyStorage:
    
    def test_cannot_instantiate_abstract_class(self):
        """Тест что нельзя создать экземпляр абстрактного класса"""
        with pytest.raises(TypeError):
            AbstractVacancyStorage()
    
    def test_concrete_implementation_works(self):
        """Тест что конкретная реализация работает корректно"""
        
        class ConcreteStorage(AbstractVacancyStorage):
            def __init__(self):
                self.storage = []
            
            def add_vacancy(self, vacancy):
                self.storage.append(vacancy)
            
            def get_vacancies(self, filters=None):
                return self.storage
            
            def delete_vacancy(self, vacancy):
                if vacancy in self.storage:
                    self.storage.remove(vacancy)
        
        # Создаем моки для вакансий
        vacancy1 = Mock(spec=AbstractVacancy)
        vacancy2 = Mock(spec=AbstractVacancy)
        
        # Создаем конкретную реализацию
        storage = ConcreteStorage()
        
        # Тестируем добавление
        storage.add_vacancy(vacancy1)
        storage.add_vacancy(vacancy2)
        
        # Тестируем получение
        vacancies = storage.get_vacancies()
        assert len(vacancies) == 2
        assert vacancy1 in vacancies
        assert vacancy2 in vacancies
        
        # Тестируем удаление
        storage.delete_vacancy(vacancy1)
        remaining_vacancies = storage.get_vacancies()
        assert len(remaining_vacancies) == 1
        assert vacancy1 not in remaining_vacancies
        assert vacancy2 in remaining_vacancies
    
    def test_abstract_methods_must_be_implemented(self):
        """Тест что все абстрактные методы должны быть реализованы"""
        
        class IncompleteStorage(AbstractVacancyStorage):
            def add_vacancy(self, vacancy):
                pass
            # Намеренно не реализуем get_vacancies и delete_vacancy
        
        with pytest.raises(TypeError):
            IncompleteStorage()
    
    def test_methods_have_correct_signatures(self):
        """Тест что методы имеют корректные сигнатуры"""
        
        class ConcreteStorage(AbstractVacancyStorage):
            def add_vacancy(self, vacancy):
                return None
            
            def get_vacancies(self, filters=None):
                return []
            
            def delete_vacancy(self, vacancy):
                return None
        
        storage = ConcreteStorage()
        vacancy_mock = Mock(spec=AbstractVacancy)
        
        # Проверяем что методы вызываются без ошибок
        storage.add_vacancy(vacancy_mock)
        result = storage.get_vacancies()
        assert result == []
        
        result_with_filters = storage.get_vacancies({"key": "value"})
        assert result_with_filters == []
        
        storage.delete_vacancy(vacancy_mock)


import pytest
from unittest.mock import Mock
from src.utils.base_formatter import BaseFormatter
from src.vacancies.models import Vacancy


class TestBaseFormatter:
    
    def test_cannot_instantiate_abstract_class(self):
        """Тест что нельзя создать экземпляр абстрактного класса"""
        with pytest.raises(TypeError):
            BaseFormatter()
    
    def test_concrete_implementation_works(self):
        """Тест что конкретная реализация работает корректно"""
        
        class ConcreteFormatter(BaseFormatter):
            def format_vacancy_info(self, vacancy, number=None):
                return f"Vacancy: {vacancy.title}"
        
        formatter = ConcreteFormatter()
        vacancy_mock = Mock()
        vacancy_mock.title = "Test Job"
        
        result = formatter.format_vacancy_info(vacancy_mock, 1)
        assert result == "Vacancy: Test Job"
    
    def test_extract_company_name_with_dict(self):
        """Тест извлечения названия компании из словаря"""
        vacancy_mock = Mock()
        vacancy_mock.employer = {"name": "Test Company"}
        
        result = BaseFormatter._extract_company_name(vacancy_mock)
        assert result == "Test Company"
    
    def test_extract_company_name_with_string(self):
        """Тест извлечения названия компании из строки"""
        vacancy_mock = Mock()
        vacancy_mock.employer = "Test Company"
        
        result = BaseFormatter._extract_company_name(vacancy_mock)
        assert result == "Test Company"
    
    def test_extract_company_name_none(self):
        """Тест извлечения названия компании когда его нет"""
        vacancy_mock = Mock()
        vacancy_mock.employer = None
        
        result = BaseFormatter._extract_company_name(vacancy_mock)
        assert result is None
    
    def test_extract_salary_info_with_dict(self):
        """Тест извлечения зарплаты из словаря"""
        vacancy_mock = Mock()
        vacancy_mock.salary = {"from": 100000, "to": 150000, "currency": "RUR"}
        
        result = BaseFormatter._extract_salary_info(vacancy_mock)
        assert "от 100 000 до 150 000 руб." in result
    
    def test_extract_salary_info_with_string(self):
        """Тест извлечения зарплаты из строки"""
        vacancy_mock = Mock()
        vacancy_mock.salary = "100000 руб."
        
        result = BaseFormatter._extract_salary_info(vacancy_mock)
        assert result == "100000 руб."
    
    def test_extract_salary_info_none(self):
        """Тест извлечения зарплаты когда ее нет"""
        vacancy_mock = Mock()
        vacancy_mock.salary = None
        
        result = BaseFormatter._extract_salary_info(vacancy_mock)
        assert result is None
    
    def test_format_salary_dict_from_to(self):
        """Тест форматирования зарплаты с from и to"""
        salary_dict = {"from": 100000, "to": 150000, "currency": "RUR"}
        
        result = BaseFormatter._format_salary_dict(salary_dict)
        assert result == "от 100 000 до 150 000 руб. в месяц"
    
    def test_format_salary_dict_from_only(self):
        """Тест форматирования зарплаты только с from"""
        salary_dict = {"from": 100000, "currency": "USD"}
        
        result = BaseFormatter._format_salary_dict(salary_dict)
        assert result == "от 100 000 долл. в месяц"
    
    def test_format_salary_dict_to_only(self):
        """Тест форматирования зарплаты только с to"""
        salary_dict = {"to": 150000, "currency": "EUR"}
        
        result = BaseFormatter._format_salary_dict(salary_dict)
        assert result == "до 150 000 евро в месяц"
    
    def test_format_salary_dict_empty(self):
        """Тест форматирования пустого словаря зарплаты"""
        result = BaseFormatter._format_salary_dict({})
        assert result == "Не указана"
        
        result = BaseFormatter._format_salary_dict(None)
        assert result == "Не указана"
    
    def test_extract_responsibilities(self):
        """Тест извлечения обязанностей"""
        vacancy_mock = Mock()
        vacancy_mock.responsibilities = "Test responsibilities"
        
        result = BaseFormatter._extract_responsibilities(vacancy_mock)
        assert result == "Test responsibilities"
    
    def test_extract_requirements(self):
        """Тест извлечения требований"""
        vacancy_mock = Mock()
        vacancy_mock.requirements = "Test requirements"
        
        result = BaseFormatter._extract_requirements(vacancy_mock)
        assert result == "Test requirements"
    
    def test_extract_conditions(self):
        """Тест извлечения условий"""
        vacancy_mock = Mock()
        vacancy_mock.conditions = "Test conditions"
        
        result = BaseFormatter._extract_conditions(vacancy_mock)
        assert result == "Test conditions"
    
    def test_extract_conditions_with_schedule(self):
        """Тест извлечения условий через график работы"""
        vacancy_mock = Mock()
        vacancy_mock.conditions = None
        vacancy_mock.schedule = "Полный день"
        
        result = BaseFormatter._extract_conditions(vacancy_mock)
        assert result == "График: Полный день"
    
    def test_build_vacancy_lines(self):
        """Тест формирования строк вакансии"""
        vacancy_mock = Mock()
        vacancy_mock.vacancy_id = "123"
        vacancy_mock.title = "Test Job"
        vacancy_mock.employer = {"name": "Test Company"}
        vacancy_mock.salary = {"from": 100000, "currency": "RUR"}
        vacancy_mock.experience = "1-3 года"
        vacancy_mock.employment = "Полная занятость"
        vacancy_mock.source = "test.ru"
        vacancy_mock.url = "https://test.ru/vacancy/123"
        vacancy_mock.responsibilities = "Do work"
        vacancy_mock.requirements = "Be good"
        vacancy_mock.conditions = "Good office"
        
        result = BaseFormatter._build_vacancy_lines(vacancy_mock, 1)
        
        assert "1." in result
        assert "ID: 123" in result
        assert "Название: Test Job" in result
        assert "Компания: Test Company" in result
        assert "от 100 000 руб." in result
        assert "Опыт: 1-3 года" in result
        assert "Занятость: Полная занятость" in result
        assert "Источник: test.ru" in result
        assert "Ссылка: https://test.ru/vacancy/123" in result
        assert "Обязанности: Do work" in result
        assert "Требования: Be good" in result
        assert "Условия: Good office" in result
    
    def test_build_vacancy_lines_minimal(self):
        """Тест формирования строк с минимальными данными"""
        vacancy_mock = Mock()
        vacancy_mock.vacancy_id = "123"
        vacancy_mock.title = "Test Job"
        vacancy_mock.employer = None
        vacancy_mock.salary = None
        vacancy_mock.experience = None
        vacancy_mock.employment = None
        vacancy_mock.source = None
        vacancy_mock.url = None
        vacancy_mock.responsibilities = None
        vacancy_mock.requirements = None
        vacancy_mock.conditions = None
        
        result = BaseFormatter._build_vacancy_lines(vacancy_mock, None)
        
        assert "ID: 123" in result
        assert "Название: Test Job" in result
        # Проверяем что необязательные поля не добавляются
        assert any("Компания:" not in line for line in result)
        assert any("Зарплата:" not in line for line in result)
    
    def test_abstract_method_must_be_implemented(self):
        """Тест что абстрактный метод должен быть реализован"""
        
        class IncompleteFormatter(BaseFormatter):
            pass  # Не реализуем format_vacancy_info
        
        with pytest.raises(TypeError):
            IncompleteFormatter()

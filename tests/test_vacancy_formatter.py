
"""
Тесты для модуля vacancy_formatter
"""

import pytest
from src.utils.vacancy_formatter import VacancyFormatter
from src.vacancies.models import Vacancy


class TestVacancyFormatter:
    """Тесты для класса VacancyFormatter"""
    
    @pytest.fixture
    def vacancy_with_salary(self):
        """Вакансия с указанной зарплатой"""
        return Vacancy(
            title="Python Developer",
            url="https://example.com/1",
            salary={"from": 100000, "to": 150000, "currency": "RUR"},
            description="Разработка на Python",
            vacancy_id="1"
        )
    
    @pytest.fixture
    def vacancy_without_salary(self):
        """Вакансия без указанной зарплаты"""
        return Vacancy(
            title="Junior Developer",
            url="https://example.com/2",
            salary=None,
            description="Стажировка",
            vacancy_id="2"
        )
    
    @pytest.fixture
    def vacancy_with_partial_salary(self):
        """Вакансия с частично указанной зарплатой"""
        return Vacancy(
            title="Senior Developer",
            url="https://example.com/3",
            salary={"from": 200000, "currency": "RUR"},
            description="Старший разработчик",
            vacancy_id="3"
        )
    
    def test_format_salary_full_range(self, vacancy_with_salary):
        """Тест форматирования полного диапазона зарплаты"""
        result = VacancyFormatter.format_salary(vacancy_with_salary)
        
        assert result == "от 100,000 до 150,000 руб."
    
    def test_format_salary_only_from(self, vacancy_with_partial_salary):
        """Тест форматирования только нижней границы зарплаты"""
        result = VacancyFormatter.format_salary(vacancy_with_partial_salary)
        
        assert result == "от 200,000 руб."
    
    def test_format_salary_only_to(self):
        """Тест форматирования только верхней границы зарплаты"""
        vacancy = Vacancy(
            title="Test",
            url="https://test.com",
            salary={"to": 80000, "currency": "RUR"},
            description="Test",
            vacancy_id="test"
        )
        
        result = VacancyFormatter.format_salary(vacancy)
        
        assert result == "до 80,000 руб."
    
    def test_format_salary_no_salary(self, vacancy_without_salary):
        """Тест форматирования при отсутствии зарплаты"""
        result = VacancyFormatter.format_salary(vacancy_without_salary)
        
        assert result == "Зарплата не указана"
    
    def test_format_salary_usd_currency(self):
        """Тест форматирования зарплаты в USD"""
        vacancy = Vacancy(
            title="Test",
            url="https://test.com",
            salary={"from": 5000, "to": 8000, "currency": "USD"},
            description="Test",
            vacancy_id="test"
        )
        
        result = VacancyFormatter.format_salary(vacancy)
        
        assert result == "от 5,000 до 8,000 $"
    
    def test_format_salary_unknown_currency(self):
        """Тест форматирования зарплаты с неизвестной валютой"""
        vacancy = Vacancy(
            title="Test",
            url="https://test.com",
            salary={"from": 1000, "currency": "XYZ"},
            description="Test",
            vacancy_id="test"
        )
        
        result = VacancyFormatter.format_salary(vacancy)
        
        assert result == "от 1,000 XYZ"
    
    def test_format_salary_zero_values(self):
        """Тест форматирования нулевых значений зарплаты"""
        vacancy = Vacancy(
            title="Test",
            url="https://test.com",
            salary={"from": 0, "to": 0, "currency": "RUR"},
            description="Test",
            vacancy_id="test"
        )
        
        result = VacancyFormatter.format_salary(vacancy)
        
        assert result == "Зарплата не указана"
    
    def test_format_vacancy_info_with_salary(self, vacancy_with_salary):
        """Тест форматирования полной информации о вакансии с зарплатой"""
        result = VacancyFormatter.format_vacancy_info(vacancy_with_salary)
        
        assert "Python Developer" in result
        assert "от 100,000 до 150,000 руб." in result
        assert "https://example.com/1" in result
        assert "Разработка на Python" in result
    
    def test_format_vacancy_info_without_salary(self, vacancy_without_salary):
        """Тест форматирования полной информации о вакансии без зарплаты"""
        result = VacancyFormatter.format_vacancy_info(vacancy_without_salary)
        
        assert "Junior Developer" in result
        assert "Зарплата не указана" in result
        assert "https://example.com/2" in result
        assert "Стажировка" in result
    
    def test_format_vacancy_info_long_description(self):
        """Тест форматирования вакансии с длинным описанием"""
        long_desc = "Это очень длинное описание вакансии, которое превышает обычную длину описания и должно быть обрезано в определенном месте для лучшей читаемости и отображения в консоли пользователя."
        
        vacancy = Vacancy(
            title="Test Job",
            url="https://test.com",
            salary=None,
            description=long_desc,
            vacancy_id="test"
        )
        
        result = VacancyFormatter.format_vacancy_info(vacancy)
        
        assert "Test Job" in result
        assert len(result) > 0  # Проверяем, что результат не пустой
    
    def test_format_vacancy_info_empty_description(self):
        """Тест форматирования вакансии с пустым описанием"""
        vacancy = Vacancy(
            title="Test Job",
            url="https://test.com",
            salary=None,
            description="",
            vacancy_id="test"
        )
        
        result = VacancyFormatter.format_vacancy_info(vacancy)
        
        assert "Test Job" in result
        assert "https://test.com" in result
    
    def test_format_vacancy_info_special_characters(self):
        """Тест форматирования вакансии со специальными символами"""
        vacancy = Vacancy(
            title="C++ Developer",
            url="https://test.com",
            salary={"from": 120000, "currency": "RUR"},
            description="Разработка на C++/Qt",
            vacancy_id="test"
        )
        
        result = VacancyFormatter.format_vacancy_info(vacancy)
        
        assert "C++ Developer" in result
        assert "Разработка на C++/Qt" in result
    
    def test_format_vacancy_info_multiple_vacancies(self):
        """Тест форматирования нескольких вакансий"""
        vacancies = [
            Vacancy("Job1", "https://test1.com", None, "Desc1", "1"),
            Vacancy("Job2", "https://test2.com", {"from": 50000, "currency": "RUR"}, "Desc2", "2")
        ]
        
        for vacancy in vacancies:
            result = VacancyFormatter.format_vacancy_info(vacancy)
            assert vacancy.title in result
            assert vacancy.url in result

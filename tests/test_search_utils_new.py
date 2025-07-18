
"""
Новые тесты для модуля search_utils
"""

import pytest
from src.utils.search_utils import filter_vacancies_by_keyword, vacancy_contains_keyword
from src.vacancies.models import Vacancy


class TestSearchUtilsNew:
    """Новые тесты для модуля search_utils"""
    
    @pytest.fixture
    def test_vacancy(self):
        """Создание тестовой вакансии"""
        return Vacancy(
            title="Python Developer",
            url="https://example.com/1",
            salary={"from": 100000, "currency": "RUR"},
            description="Разработка на Python и Django",
            requirements="Опыт работы с Python, Django, PostgreSQL",
            responsibilities="Разработка веб-приложений",
            vacancy_id="1"
        )
    
    def test_vacancy_contains_keyword_in_title(self, test_vacancy):
        """Тест поиска ключевого слова в названии"""
        assert vacancy_contains_keyword(test_vacancy, "Python")
        assert vacancy_contains_keyword(test_vacancy, "python")
        assert vacancy_contains_keyword(test_vacancy, "Developer")
        assert not vacancy_contains_keyword(test_vacancy, "Java")
    
    def test_vacancy_contains_keyword_in_description(self, test_vacancy):
        """Тест поиска ключевого слова в описании"""
        assert vacancy_contains_keyword(test_vacancy, "Django")
        assert vacancy_contains_keyword(test_vacancy, "django")
        assert vacancy_contains_keyword(test_vacancy, "разработка")
        assert not vacancy_contains_keyword(test_vacancy, "React")
    
    def test_vacancy_contains_keyword_in_requirements(self, test_vacancy):
        """Тест поиска ключевого слова в требованиях"""
        assert vacancy_contains_keyword(test_vacancy, "PostgreSQL")
        assert vacancy_contains_keyword(test_vacancy, "опыт")
        assert not vacancy_contains_keyword(test_vacancy, "MongoDB")
    
    def test_vacancy_contains_keyword_in_responsibilities(self, test_vacancy):
        """Тест поиска ключевого слова в обязанностях"""
        assert vacancy_contains_keyword(test_vacancy, "веб-приложений")
        assert vacancy_contains_keyword(test_vacancy, "веб")
        assert not vacancy_contains_keyword(test_vacancy, "мобильных")
    
    def test_vacancy_contains_keyword_empty_fields(self):
        """Тест поиска в вакансии с пустыми полями"""
        vacancy = Vacancy(
            title="Test Job",
            url="https://example.com",
            salary=None,
            description="",
            vacancy_id="test"
        )
        
        assert vacancy_contains_keyword(vacancy, "Test")
        assert vacancy_contains_keyword(vacancy, "Job")
        assert not vacancy_contains_keyword(vacancy, "Python")
    
    def test_vacancy_contains_keyword_none_fields(self):
        """Тест поиска в вакансии с None полями"""
        vacancy = Vacancy(
            title="Test Job",
            url="https://example.com",
            salary=None,
            description=None,
            requirements=None,
            responsibilities=None,
            vacancy_id="test"
        )
        
        assert vacancy_contains_keyword(vacancy, "Test")
        assert not vacancy_contains_keyword(vacancy, "Python")
    
    def test_filter_vacancies_by_keyword_found(self, test_vacancy):
        """Тест фильтрации вакансий по ключевому слову - найдены"""
        vacancies = [test_vacancy]
        result = filter_vacancies_by_keyword(vacancies, "Python")
        
        assert len(result) == 1
        assert result[0] == test_vacancy
    
    def test_filter_vacancies_by_keyword_not_found(self, test_vacancy):
        """Тест фильтрации вакансий по ключевому слову - не найдены"""
        vacancies = [test_vacancy]
        result = filter_vacancies_by_keyword(vacancies, "Java")
        
        assert len(result) == 0
    
    def test_filter_vacancies_by_keyword_multiple_vacancies(self):
        """Тест фильтрации множества вакансий"""
        vacancies = [
            Vacancy("Python Developer", "https://example.com/1", None, "Python job", vacancy_id="1"),
            Vacancy("Java Developer", "https://example.com/2", None, "Java job", vacancy_id="2"),
            Vacancy("Python Engineer", "https://example.com/3", None, "Python work", vacancy_id="3"),
        ]
        
        result = filter_vacancies_by_keyword(vacancies, "Python")
        
        assert len(result) == 2
        assert result[0].vacancy_id == "1"
        assert result[1].vacancy_id == "3"
    
    def test_filter_vacancies_by_keyword_empty_list(self):
        """Тест фильтрации пустого списка"""
        result = filter_vacancies_by_keyword([], "Python")
        assert len(result) == 0
    
    def test_filter_vacancies_by_keyword_case_insensitive(self, test_vacancy):
        """Тест регистронезависимого поиска"""
        vacancies = [test_vacancy]
        
        assert len(filter_vacancies_by_keyword(vacancies, "PYTHON")) == 1
        assert len(filter_vacancies_by_keyword(vacancies, "python")) == 1
        assert len(filter_vacancies_by_keyword(vacancies, "Python")) == 1
        assert len(filter_vacancies_by_keyword(vacancies, "PyThOn")) == 1

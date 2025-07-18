
"""
Тесты для модуля vacancy_operations
"""

import pytest
from unittest.mock import patch, MagicMock
from src.utils.vacancy_operations import VacancyOperations
from src.vacancies.models import Vacancy


class TestVacancyOperations:
    """Тесты для класса VacancyOperations"""
    
    def create_test_vacancy(self, title: str, salary_from: int = None, 
                           salary_to: int = None):
        """Создает тестовую вакансию"""
        salary_data = None
        if salary_from is not None or salary_to is not None:
            salary_data = {
                'from': salary_from,
                'to': salary_to,
                'currency': 'RUR'
            }
        
        return Vacancy(
            title=title,
            url="https://example.com",
            salary=salary_data,
            description="Test description"
        )
    
    def test_get_vacancies_with_salary(self):
        """Тест получения вакансий с зарплатой"""
        vacancies = [
            self.create_test_vacancy("Job 1", salary_from=100000),
            self.create_test_vacancy("Job 2"),  # без зарплаты
            self.create_test_vacancy("Job 3", salary_to=200000)
        ]
        
        result = VacancyOperations.get_vacancies_with_salary(vacancies)
        
        assert len(result) == 2
        assert result[0].title == "Job 1"
        assert result[1].title == "Job 3"
    
    def test_sort_vacancies_by_salary_desc(self):
        """Тест сортировки вакансий по убыванию зарплаты"""
        vacancies = [
            self.create_test_vacancy("Job 1", salary_from=100000),
            self.create_test_vacancy("Job 2", salary_from=200000),
            self.create_test_vacancy("Job 3", salary_from=150000)
        ]
        
        result = VacancyOperations.sort_vacancies_by_salary(vacancies)
        
        assert len(result) == 3
        assert result[0].title == "Job 2"  # самая высокая зарплата
        assert result[1].title == "Job 3"
        assert result[2].title == "Job 1"
    
    def test_sort_vacancies_by_salary_asc(self):
        """Тест сортировки вакансий по возрастанию зарплаты"""
        vacancies = [
            self.create_test_vacancy("Job 1", salary_from=100000),
            self.create_test_vacancy("Job 2", salary_from=200000)
        ]
        
        result = VacancyOperations.sort_vacancies_by_salary(vacancies, reverse=False)
        
        assert result[0].title == "Job 1"  # самая низкая зарплата
        assert result[1].title == "Job 2"
    
    def test_filter_vacancies_by_min_salary(self):
        """Тест фильтрации по минимальной зарплате"""
        vacancies = [
            self.create_test_vacancy("Job 1", salary_from=100000),
            self.create_test_vacancy("Job 2", salary_from=200000),
            self.create_test_vacancy("Job 3", salary_from=50000)
        ]
        
        result = VacancyOperations.filter_vacancies_by_min_salary(vacancies, 150000)
        
        assert len(result) == 1
        assert result[0].title == "Job 2"
    
    def test_filter_vacancies_by_max_salary(self):
        """Тест фильтрации по максимальной зарплате"""
        vacancies = [
            self.create_test_vacancy("Job 1", salary_from=100000),
            self.create_test_vacancy("Job 2", salary_from=200000),
            self.create_test_vacancy("Job 3", salary_to=150000)
        ]
        
        result = VacancyOperations.filter_vacancies_by_max_salary(vacancies, 150000)
        
        assert len(result) == 2
        titles = [v.title for v in result]
        assert "Job 1" in titles
        assert "Job 3" in titles
    
    def test_filter_vacancies_by_salary_range(self):
        """Тест фильтрации по диапазону зарплат"""
        vacancies = [
            self.create_test_vacancy("Job 1", salary_from=100000),
            self.create_test_vacancy("Job 2", salary_from=200000),
            self.create_test_vacancy("Job 3", salary_from=50000)
        ]
        
        result = VacancyOperations.filter_vacancies_by_salary_range(
            vacancies, 80000, 150000
        )
        
        assert len(result) == 1
        assert result[0].title == "Job 1"
    
    @patch('src.utils.search_utils.filter_vacancies_by_keyword')
    def test_filter_vacancies_by_multiple_keywords(self, mock_filter):
        """Тест фильтрации по нескольким ключевым словам"""
        vacancies = [
            self.create_test_vacancy("Python Developer"),
            self.create_test_vacancy("Java Developer")
        ]
        
        mock_filter.return_value = vacancies
        
        result = VacancyOperations.filter_vacancies_by_multiple_keywords(
            vacancies, ["python", "java"]
        )
        
        assert len(result) == 2
        assert mock_filter.call_count == 2
    
    def test_filter_vacancies_by_multiple_keywords_empty(self):
        """Тест фильтрации по пустому списку ключевых слов"""
        vacancies = [self.create_test_vacancy("Test")]
        
        result = VacancyOperations.filter_vacancies_by_multiple_keywords(
            vacancies, []
        )
        
        assert result == vacancies
    
    @patch('src.utils.search_utils.filter_vacancies_by_keyword')
    def test_search_vacancies_advanced_and(self, mock_filter):
        """Тест продвинутого поиска с оператором AND"""
        vacancies = [self.create_test_vacancy("Test")]
        mock_filter.return_value = vacancies
        
        result = VacancyOperations.search_vacancies_advanced(
            vacancies, "python AND django"
        )
        
        assert mock_filter.call_count == 2
    
    @patch.object(VacancyOperations, 'filter_vacancies_by_multiple_keywords')
    def test_search_vacancies_advanced_or(self, mock_filter):
        """Тест продвинутого поиска с оператором OR"""
        vacancies = [self.create_test_vacancy("Test")]
        mock_filter.return_value = vacancies
        
        result = VacancyOperations.search_vacancies_advanced(
            vacancies, "python OR java"
        )
        
        mock_filter.assert_called_once_with(vacancies, ['python', 'java'])
    
    @patch('src.utils.search_utils.filter_vacancies_by_keyword')
    def test_search_vacancies_advanced_simple(self, mock_filter):
        """Тест простого продвинутого поиска"""
        vacancies = [self.create_test_vacancy("Test")]
        mock_filter.return_value = vacancies
        
        result = VacancyOperations.search_vacancies_advanced(
            vacancies, "python"
        )
        
        mock_filter.assert_called_once_with(vacancies, "python")
    
    def test_get_vacancy_keywords_summary(self):
        """Тест получения сводки по ключевым словам"""
        vacancies = [
            self.create_test_vacancy("Python Django Developer"),
            self.create_test_vacancy("Python Flask Developer"),
            self.create_test_vacancy("Java Spring Developer")
        ]
        
        result = VacancyOperations.get_vacancy_keywords_summary(vacancies)
        
        # Проверяем, что функция корректно извлекает ключевые слова из названий
        assert "python" in result or "Python" in result
        assert "java" in result or "Java" in result
    
    def test_get_vacancy_keywords_summary_empty(self):
        """Тест получения сводки для пустого списка"""
        result = VacancyOperations.get_vacancy_keywords_summary([])
        assert result == {}
    
    def test_get_vacancy_keywords_summary_no_keywords(self):
        """Тест получения сводки для вакансий без ключевых слов"""
        vacancies = [
            self.create_test_vacancy("Job 1"),
            self.create_test_vacancy("Job 2")
        ]
        
        result = VacancyOperations.get_vacancy_keywords_summary(vacancies)
        assert result == {}

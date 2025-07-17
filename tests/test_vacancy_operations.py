
"""
Тесты для модуля vacancy_operations
"""

import pytest
from unittest.mock import MagicMock, patch
from src.utils.vacancy_operations import VacancyOperations
from src.vacancies.models import Vacancy
from src.utils.salary import Salary


class TestVacancyOperations:
    """Тесты для класса VacancyOperations"""
    
    def create_test_vacancy(self, title: str, salary_from: int = None, salary_to: int = None, 
                           keywords: list = None, description: str = ""):
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
            description=description,
            keywords=keywords or []
        )
    
    def test_get_vacancies_with_salary(self):
        """Тест фильтрации вакансий с зарплатой"""
        vacancies = [
            self.create_test_vacancy("Job 1", salary_from=100000),
            self.create_test_vacancy("Job 2"),  # без зарплаты
            self.create_test_vacancy("Job 3", salary_to=200000)
        ]
        
        result = VacancyOperations.get_vacancies_with_salary(vacancies)
        
        assert len(result) == 2
        assert result[0].title == "Job 1"
        assert result[1].title == "Job 3"
    
    def test_sort_vacancies_by_salary(self):
        """Тест сортировки вакансий по зарплате"""
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
    
    def test_sort_vacancies_by_salary_ascending(self):
        """Тест сортировки вакансий по зарплате по возрастанию"""
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
        
        result = VacancyOperations.filter_vacancies_by_salary_range(vacancies, 80000, 150000)
        
        assert len(result) == 1
        assert result[0].title == "Job 1"
    
    @patch('src.utils.ui_helpers.filter_vacancies_by_keyword')
    def test_filter_vacancies_by_multiple_keywords(self, mock_filter):
        """Тест фильтрации по нескольким ключевым словам"""
        vacancies = [
            self.create_test_vacancy("Python Developer"),
            self.create_test_vacancy("Java Developer"),
            self.create_test_vacancy("Full Stack Developer")
        ]
        
        # Настраиваем мок для возврата разных результатов
        def mock_filter_side_effect(vacancy_list, keyword):
            if keyword == "python" and vacancy_list[0].title == "Python Developer":
                return [vacancy_list[0]]
            elif keyword == "java" and vacancy_list[0].title == "Java Developer":
                return [vacancy_list[0]]
            return []
        
        mock_filter.side_effect = mock_filter_side_effect
        
        result = VacancyOperations.filter_vacancies_by_multiple_keywords(vacancies, ["python", "java"])
        
        assert len(result) == 2
    
    def test_filter_vacancies_by_multiple_keywords_empty(self):
        """Тест фильтрации по пустому списку ключевых слов"""
        vacancies = [self.create_test_vacancy("Test")]
        
        result = VacancyOperations.filter_vacancies_by_multiple_keywords(vacancies, [])
        
        assert result == vacancies
    
    @patch('src.utils.ui_helpers.filter_vacancies_by_keyword')
    def test_search_vacancies_advanced_and(self, mock_filter):
        """Тест продвинутого поиска с оператором AND"""
        vacancies = [self.create_test_vacancy("Test")]
        
        # Настраиваем мок для возврата результатов
        mock_filter.return_value = vacancies
        
        result = VacancyOperations.search_vacancies_advanced(vacancies, "python AND django")
        
        assert mock_filter.call_count == 2  # Должен быть вызван для каждого ключевого слова
    
    @patch.object(VacancyOperations, 'filter_vacancies_by_multiple_keywords')
    def test_search_vacancies_advanced_or(self, mock_filter):
        """Тест продвинутого поиска с оператором OR"""
        vacancies = [self.create_test_vacancy("Test")]
        mock_filter.return_value = vacancies
        
        result = VacancyOperations.search_vacancies_advanced(vacancies, "python OR java")
        
        mock_filter.assert_called_once_with(vacancies, ['PYTHON', 'JAVA'])
    
    @patch('src.utils.ui_helpers.filter_vacancies_by_keyword')
    def test_search_vacancies_advanced_simple(self, mock_filter):
        """Тест простого продвинутого поиска"""
        vacancies = [self.create_test_vacancy("Test")]
        mock_filter.return_value = vacancies
        
        result = VacancyOperations.search_vacancies_advanced(vacancies, "python")
        
        mock_filter.assert_called_once_with(vacancies, "python")
    
    def test_get_vacancy_keywords_summary(self):
        """Тест получения сводки по ключевым словам"""
        vacancies = [
            self.create_test_vacancy("Job 1", keywords=["python", "django"]),
            self.create_test_vacancy("Job 2", keywords=["python", "flask"]),
            self.create_test_vacancy("Job 3", keywords=["java", "spring"])
        ]
        
        result = VacancyOperations.get_vacancy_keywords_summary(vacancies)
        
        assert result["python"] == 2
        assert result["django"] == 1
        assert result["flask"] == 1
        assert result["java"] == 1
        assert result["spring"] == 1
    
    def test_get_vacancy_keywords_summary_empty(self):
        """Тест получения сводки по ключевым словам для пустого списка"""
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

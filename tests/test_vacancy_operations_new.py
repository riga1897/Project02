
"""
Новые тесты для модуля vacancy_operations
"""

import pytest
from unittest.mock import MagicMock, patch
from src.utils.vacancy_operations import VacancyOperations
from src.vacancies.models import Vacancy
from src.utils.salary import Salary


class TestVacancyOperationsNew:
    """Новые тесты для класса VacancyOperations"""
    
    @pytest.fixture
    def sample_vacancies(self):
        """Создание тестовых вакансий"""
        return [
            Vacancy(
                title="Python Developer",
                url="https://example.com/1",
                salary={"from": 100000, "to": 150000, "currency": "RUR"},
                description="Python разработчик с опытом Django",
                requirements="Python, Django, PostgreSQL",
                vacancy_id="1"
            ),
            Vacancy(
                title="Java Developer",
                url="https://example.com/2",
                salary={"from": 120000, "to": 180000, "currency": "RUR"},
                description="Java разработчик Spring Boot",
                requirements="Java, Spring Boot, MySQL",
                vacancy_id="2"
            ),
            Vacancy(
                title="Frontend Developer",
                url="https://example.com/3",
                salary=None,
                description="React разработчик",
                requirements="React, TypeScript, HTML/CSS",
                vacancy_id="3"
            ),
            Vacancy(
                title="DevOps Engineer",
                url="https://example.com/4",
                salary={"from": 200000, "currency": "RUR"},
                description="DevOps инженер",
                requirements="Docker, Kubernetes, AWS",
                vacancy_id="4"
            )
        ]
    
    def test_get_vacancies_with_salary(self, sample_vacancies):
        """Тест фильтрации вакансий с зарплатой"""
        result = VacancyOperations.get_vacancies_with_salary(sample_vacancies)
        
        assert len(result) == 3
        assert result[0].vacancy_id == "1"
        assert result[1].vacancy_id == "2"
        assert result[2].vacancy_id == "4"
    
    def test_sort_vacancies_by_salary_descending(self, sample_vacancies):
        """Тест сортировки вакансий по зарплате по убыванию"""
        result = VacancyOperations.sort_vacancies_by_salary(sample_vacancies)
        
        # DevOps (200000) -> Java (150000) -> Python (125000) -> Frontend (0)
        expected_order = ["4", "2", "1", "3"]
        actual_order = [v.vacancy_id for v in result]
        
        assert actual_order == expected_order
    
    def test_sort_vacancies_by_salary_ascending(self, sample_vacancies):
        """Тест сортировки вакансий по зарплате по возрастанию"""
        result = VacancyOperations.sort_vacancies_by_salary(sample_vacancies, reverse=False)
        
        # Frontend (0) -> Python (125000) -> Java (150000) -> DevOps (200000)
        expected_order = ["3", "1", "2", "4"]
        actual_order = [v.vacancy_id for v in result]
        
        assert actual_order == expected_order
    
    def test_filter_vacancies_by_min_salary(self, sample_vacancies):
        """Тест фильтрации по минимальной зарплате"""
        result = VacancyOperations.filter_vacancies_by_min_salary(sample_vacancies, 150000)
        
        assert len(result) == 2
        ids = [v.vacancy_id for v in result]
        assert "2" in ids  # Java Developer
        assert "4" in ids  # DevOps Engineer
    
    def test_filter_vacancies_by_max_salary(self, sample_vacancies):
        """Тест фильтрации по максимальной зарплате"""
        result = VacancyOperations.filter_vacancies_by_max_salary(sample_vacancies, 150000)
        
        assert len(result) == 2
        ids = [v.vacancy_id for v in result]
        assert "1" in ids  # Python Developer
        assert "4" in ids  # DevOps Engineer
    
    def test_filter_vacancies_by_salary_range(self, sample_vacancies):
        """Тест фильтрации по диапазону зарплат"""
        result = VacancyOperations.filter_vacancies_by_salary_range(sample_vacancies, 100000, 160000)
        
        assert len(result) == 2
        ids = [v.vacancy_id for v in result]
        assert "1" in ids  # Python Developer
        assert "2" in ids  # Java Developer
    
    @patch('src.utils.search_utils.filter_vacancies_by_keyword')
    def test_filter_vacancies_by_multiple_keywords(self, mock_filter, sample_vacancies):
        """Тест фильтрации по нескольким ключевым словам"""
        # Настройка мока для имитации поиска
        def mock_filter_effect(vacancies, keyword):
            if keyword.lower() == "python":
                return [v for v in vacancies if "Python" in v.title or "python" in v.description.lower()]
            elif keyword.lower() == "java":
                return [v for v in vacancies if "Java" in v.title or "java" in v.description.lower()]
            return []
        
        mock_filter.side_effect = mock_filter_effect
        
        result = VacancyOperations.filter_vacancies_by_multiple_keywords(
            sample_vacancies, 
            ["python", "java"]
        )
        
        assert len(result) == 2
        ids = [v.vacancy_id for v in result]
        assert "1" in ids  # Python Developer
        assert "2" in ids  # Java Developer
    
    def test_filter_vacancies_by_multiple_keywords_empty_list(self, sample_vacancies):
        """Тест фильтрации по пустому списку ключевых слов"""
        result = VacancyOperations.filter_vacancies_by_multiple_keywords(sample_vacancies, [])
        
        assert result == sample_vacancies
    
    @patch('src.utils.search_utils.vacancy_contains_keyword')
    def test_search_vacancies_advanced_and_operator(self, mock_contains, sample_vacancies):
        """Тест продвинутого поиска с оператором AND"""
        # Настройка мока для поиска
        def mock_contains_effect(vacancy, keyword):
            if keyword.lower() == "python" and "Python" in vacancy.title:
                return True
            elif keyword.lower() == "django" and "Django" in vacancy.description:
                return True
            return False
        
        mock_contains.side_effect = mock_contains_effect
        
        result = VacancyOperations.search_vacancies_advanced(
            sample_vacancies, 
            "python AND django"
        )
        
        assert len(result) == 1
        assert result[0].vacancy_id == "1"
    
    def test_search_vacancies_advanced_or_operator(self, sample_vacancies):
        """Тест продвинутого поиска с оператором OR"""
        with patch.object(VacancyOperations, 'filter_vacancies_by_multiple_keywords') as mock_filter:
            mock_filter.return_value = sample_vacancies[:2]
            
            result = VacancyOperations.search_vacancies_advanced(
                sample_vacancies, 
                "python OR java"
            )
            
            mock_filter.assert_called_once()
            assert len(result) == 2
    
    def test_search_vacancies_advanced_comma_separator(self, sample_vacancies):
        """Тест продвинутого поиска с запятой как разделителем"""
        with patch.object(VacancyOperations, 'filter_vacancies_by_multiple_keywords') as mock_filter:
            mock_filter.return_value = sample_vacancies[:2]
            
            result = VacancyOperations.search_vacancies_advanced(
                sample_vacancies, 
                "python, java"
            )
            
            mock_filter.assert_called_once()
            keywords = mock_filter.call_args[0][1]
            assert "python" in keywords
            assert "java" in keywords
    
    @patch('src.utils.search_utils.filter_vacancies_by_keyword')
    def test_search_vacancies_advanced_simple_query(self, mock_filter, sample_vacancies):
        """Тест простого продвинутого поиска"""
        mock_filter.return_value = [sample_vacancies[0]]
        
        result = VacancyOperations.search_vacancies_advanced(sample_vacancies, "python")
        
        mock_filter.assert_called_once_with(sample_vacancies, "python")
        assert len(result) == 1

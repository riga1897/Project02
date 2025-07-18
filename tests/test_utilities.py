
"""
Комплексные тесты для утилит
"""

import pytest
from src.utils.salary import Salary
from src.utils.search_utils import VacancySearcher
from src.utils.vacancy_operations import VacancyOperations
from src.utils.vacancy_formatter import VacancyFormatter
from src.vacancies.models import Vacancy


class TestSalary:
    """Тесты для класса Salary"""
    
    def test_salary_with_from_and_to(self):
        """Тест зарплаты с диапазоном"""
        salary = Salary({'from': 100000, 'to': 150000, 'currency': 'RUR'})
        assert salary.salary_from == 100000
        assert salary.salary_to == 150000
        assert salary.currency == 'RUR'
        assert salary.average == 125000
    
    def test_salary_only_from(self):
        """Тест зарплаты только с минимумом"""
        salary = Salary({'from': 100000, 'currency': 'RUR'})
        assert salary.salary_from == 100000
        assert salary.salary_to is None
        assert salary.average == 100000
    
    def test_salary_only_to(self):
        """Тест зарплаты только с максимумом"""
        salary = Salary({'to': 150000, 'currency': 'RUR'})
        assert salary.salary_from is None
        assert salary.salary_to == 150000
        assert salary.average == 150000
    
    def test_salary_none(self):
        """Тест пустой зарплаты"""
        salary = Salary(None)
        assert salary.salary_from is None
        assert salary.salary_to is None
        assert salary.currency is None
        assert salary.average == 0
    
    def test_salary_comparison(self):
        """Тест сравнения зарплат"""
        salary1 = Salary({'from': 100000, 'currency': 'RUR'})
        salary2 = Salary({'from': 150000, 'currency': 'RUR'})
        
        assert salary2 > salary1
        assert salary1 < salary2
        assert salary1 != salary2
    
    def test_salary_str_representation(self):
        """Тест строкового представления зарплаты"""
        salary = Salary({'from': 100000, 'to': 150000, 'currency': 'RUR'})
        result = str(salary)
        assert '100000' in result
        assert '150000' in result
        assert 'RUR' in result


class TestVacancySearcher:
    """Тесты для VacancySearcher"""
    
    @pytest.fixture
    def sample_vacancies(self):
        """Тестовые вакансии для поиска"""
        return [
            Vacancy(
                title="Python Developer",
                url="https://test1.com",
                salary={'from': 100000, 'currency': 'RUR'},
                description="Python разработчик Django Flask",
                vacancy_id="1"
            ),
            Vacancy(
                title="Java Developer",
                url="https://test2.com",
                salary={'from': 120000, 'currency': 'RUR'},
                description="Java Spring Boot разработчик",
                vacancy_id="2"
            ),
            Vacancy(
                title="Frontend Developer",
                url="https://test3.com",
                salary=None,
                description="React TypeScript разработчик",
                vacancy_id="3"
            )
        ]
    
    def test_search_by_keyword(self, sample_vacancies):
        """Тест поиска по ключевому слову"""
        searcher = VacancySearcher()
        
        result = searcher.search_by_keyword(sample_vacancies, "Python")
        assert len(result) == 1
        assert result[0].title == "Python Developer"
    
    def test_search_case_insensitive(self, sample_vacancies):
        """Тест регистронезависимого поиска"""
        searcher = VacancySearcher()
        
        result = searcher.search_by_keyword(sample_vacancies, "python")
        assert len(result) == 1
        assert result[0].title == "Python Developer"
    
    def test_search_multiple_keywords(self, sample_vacancies):
        """Тест поиска по нескольким ключевым словам"""
        searcher = VacancySearcher()
        
        result = searcher.search_by_keywords(sample_vacancies, ["Python", "Java"])
        assert len(result) == 2
    
    def test_search_no_results(self, sample_vacancies):
        """Тест поиска без результатов"""
        searcher = VacancySearcher()
        
        result = searcher.search_by_keyword(sample_vacancies, "C++")
        assert len(result) == 0


class TestVacancyOperations:
    """Тесты для VacancyOperations"""
    
    @pytest.fixture
    def sample_vacancies(self):
        """Тестовые вакансии для операций"""
        return [
            Vacancy(
                title="Senior Python Developer",
                url="https://test1.com",
                salary={'from': 200000, 'to': 250000, 'currency': 'RUR'},
                description="Senior Python developer",
                vacancy_id="1"
            ),
            Vacancy(
                title="Junior Java Developer",
                url="https://test2.com",
                salary={'from': 80000, 'to': 100000, 'currency': 'RUR'},
                description="Junior Java developer",
                vacancy_id="2"
            ),
            Vacancy(
                title="Middle Python Developer",
                url="https://test3.com",
                salary={'from': 150000, 'to': 180000, 'currency': 'RUR'},
                description="Middle Python developer",
                vacancy_id="3"
            )
        ]
    
    def test_sort_by_salary_desc(self, sample_vacancies):
        """Тест сортировки по зарплате по убыванию"""
        operations = VacancyOperations()
        
        result = operations.sort_by_salary(sample_vacancies, reverse=True)
        
        assert result[0].title == "Senior Python Developer"
        assert result[1].title == "Middle Python Developer"
        assert result[2].title == "Junior Java Developer"
    
    def test_sort_by_salary_asc(self, sample_vacancies):
        """Тест сортировки по зарплате по возрастанию"""
        operations = VacancyOperations()
        
        result = operations.sort_by_salary(sample_vacancies, reverse=False)
        
        assert result[0].title == "Junior Java Developer"
        assert result[2].title == "Senior Python Developer"
    
    def test_get_top_vacancies(self, sample_vacancies):
        """Тест получения топ N вакансий"""
        operations = VacancyOperations()
        
        result = operations.get_top_by_salary(sample_vacancies, 2)
        
        assert len(result) == 2
        assert result[0].title == "Senior Python Developer"
    
    def test_filter_by_salary_range(self, sample_vacancies):
        """Тест фильтрации по диапазону зарплат"""
        operations = VacancyOperations()
        
        result = operations.filter_by_salary_range(
            sample_vacancies, 
            min_salary=120000, 
            max_salary=200000
        )
        
        assert len(result) == 1
        assert result[0].title == "Middle Python Developer"


class TestVacancyFormatter:
    """Тесты для VacancyFormatter"""
    
    @pytest.fixture
    def sample_vacancy(self):
        """Тестовая вакансия для форматирования"""
        return Vacancy(
            title="Python Developer",
            url="https://test.com",
            salary={'from': 100000, 'to': 150000, 'currency': 'RUR'},
            description="Python разработчик",
            vacancy_id="1"
        )
    
    def test_format_single_vacancy(self, sample_vacancy):
        """Тест форматирования одной вакансии"""
        formatter = VacancyFormatter()
        
        result = formatter.format_vacancy(sample_vacancy)
        
        assert "Python Developer" in result
        assert "100000" in result
        assert "150000" in result
        assert "https://test.com" in result
    
    def test_format_vacancy_list(self, sample_vacancy):
        """Тест форматирования списка вакансий"""
        formatter = VacancyFormatter()
        vacancies = [sample_vacancy]
        
        result = formatter.format_vacancy_list(vacancies)
        
        assert "1." in result  # Нумерация
        assert "Python Developer" in result
    
    def test_format_vacancy_without_salary(self):
        """Тест форматирования вакансии без зарплаты"""
        vacancy = Vacancy(
            title="Intern",
            url="https://test.com",
            salary=None,
            description="Стажировка",
            vacancy_id="1"
        )
        
        formatter = VacancyFormatter()
        result = formatter.format_vacancy(vacancy)
        
        assert "Intern" in result
        assert "не указана" in result.lower() or "не указано" in result.lower()

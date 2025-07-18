
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Добавляем путь к исходному коду
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vacancies.models import Vacancy
from src.vacancies.parsers.hh_parser import HHParser
from src.vacancies.parsers.sj_parser import SuperJobParser as SJParser

from src.utils.salary import Salary


class TestVacancy:
    
    @pytest.fixture
    def vacancy_data(self):
        return {
            'vacancy_id': 'test_123',
            'title': 'Python Developer',
            'url': 'https://example.com/vacancy/123',
            'salary_from': 50000,
            'salary_to': 80000,
            'currency': 'RUB',
            'employer': 'Test Company',
            'description': 'Test job description',
            'requirements': 'Python, Django, PostgreSQL',
            'area': 'Moscow',
            'published': '2024-01-01T12:00:00',
            'source': 'test_source'
        }
    
    def test_init(self, vacancy_data):
        vacancy = Vacancy(**vacancy_data)
        assert vacancy.vacancy_id == 'test_123'
        assert vacancy.title == 'Python Developer'
        assert vacancy.salary_from == 50000
    
    def test_str_representation(self, vacancy_data):
        vacancy = Vacancy(**vacancy_data)
        str_repr = str(vacancy)
        assert 'Python Developer' in str_repr
        assert 'Test Company' in str_repr
    
    def test_to_dict(self, vacancy_data):
        vacancy = Vacancy(**vacancy_data)
        result = vacancy.to_dict()
        assert isinstance(result, dict)
        assert result['vacancy_id'] == 'test_123'
        assert result['title'] == 'Python Developer'
    
    def test_get_max_salary(self, vacancy_data):
        vacancy = Vacancy(**vacancy_data)
        max_salary = vacancy.get_max_salary()
        assert max_salary == 80000
    
    def test_get_max_salary_no_to(self, vacancy_data):
        vacancy_data['salary_to'] = None
        vacancy = Vacancy(**vacancy_data)
        max_salary = vacancy.get_max_salary()
        assert max_salary == 50000
    
    def test_get_max_salary_no_salary(self, vacancy_data):
        vacancy_data['salary_from'] = None
        vacancy_data['salary_to'] = None
        vacancy = Vacancy(**vacancy_data)
        max_salary = vacancy.get_max_salary()
        assert max_salary is None


class TestHHParser:
    
    @pytest.fixture
    def hh_parser(self):
        return HHParser()
    
    @pytest.fixture
    def hh_vacancy_data(self):
        return {
            'id': '123',
            'name': 'Python Developer',
            'alternate_url': 'https://hh.ru/vacancy/123',
            'salary': {
                'from': 50000,
                'to': 80000,
                'currency': 'RUR'
            },
            'employer': {
                'name': 'Test Company'
            },
            'snippet': {
                'requirement': 'Python, Django',
                'responsibility': 'Development'
            },
            'area': {
                'name': 'Moscow'
            },
            'published_at': '2024-01-01T12:00:00+0300'
        }
    
    def test_parse_vacancy(self, hh_parser, hh_vacancy_data):
        vacancy = hh_parser.parse_vacancy(hh_vacancy_data)
        assert isinstance(vacancy, Vacancy)
        assert vacancy.vacancy_id == '123'
        assert vacancy.title == 'Python Developer'
        assert vacancy.salary_from == 50000
    
    def test_parse_vacancy_no_salary(self, hh_parser, hh_vacancy_data):
        hh_vacancy_data['salary'] = None
        vacancy = hh_parser.parse_vacancy(hh_vacancy_data)
        assert vacancy.salary_from is None
        assert vacancy.salary_to is None
    
    def test_parse_vacancies_list(self, hh_parser, hh_vacancy_data):
        vacancies_data = [hh_vacancy_data]
        vacancies = hh_parser.parse_vacancies_list(vacancies_data)
        assert len(vacancies) == 1
        assert isinstance(vacancies[0], Vacancy)


class TestSJParser:
    
    @pytest.fixture
    def sj_parser(self):
        return SJParser()
    
    @pytest.fixture
    def sj_vacancy_data(self):
        return {
            'id': 456,
            'profession': 'Python Developer',
            'link': 'https://superjob.ru/vacancy/456',
            'payment_from': 60000,
            'payment_to': 90000,
            'currency': 'rub',
            'firm_name': 'Test SJ Company',
            'candidat': 'Python, Flask requirements',
            'town': {
                'title': 'Moscow'
            },
            'date_published': 1640995200
        }
    
    def test_parse_vacancy(self, sj_parser, sj_vacancy_data):
        vacancy = sj_parser.parse_vacancy(sj_vacancy_data)
        assert isinstance(vacancy, Vacancy)
        assert vacancy.vacancy_id == '456'
        assert vacancy.title == 'Python Developer'
        assert vacancy.salary_from == 60000
    
    def test_parse_vacancy_no_payment(self, sj_parser, sj_vacancy_data):
        sj_vacancy_data['payment_from'] = 0
        sj_vacancy_data['payment_to'] = 0
        vacancy = sj_parser.parse_vacancy(sj_vacancy_data)
        assert vacancy.salary_from is None
        assert vacancy.salary_to is None
    
    def test_parse_vacancies_list(self, sj_parser, sj_vacancy_data):
        vacancies_data = [sj_vacancy_data]
        vacancies = sj_parser.parse_vacancies_list(vacancies_data)
        assert len(vacancies) == 1
        assert isinstance(vacancies[0], Vacancy)


class TestSalary:
    
    @pytest.fixture
    def salary_data(self):
        return {
            'from': 100000,
            'to': 150000,
            'currency': 'RUR'
        }
    
    def test_init_with_data(self, salary_data):
        salary = Salary(salary_data)
        assert salary.amount_from == 100000
        assert salary.amount_to == 150000
        assert salary.currency == 'RUR'
    
    def test_init_empty(self):
        salary = Salary()
        assert salary.amount_from == 0
        assert salary.amount_to == 0
        assert salary.currency == 'RUR'
    
    def test_average(self, salary_data):
        salary = Salary(salary_data)
        assert salary.average == 125000
    
    def test_average_only_from(self):
        salary = Salary({'from': 100000})
        assert salary.average == 100000
    
    def test_str_representation(self, salary_data):
        salary = Salary(salary_data)
        str_repr = str(salary)
        assert 'от 100,000' in str_repr
        assert 'до 150,000' in str_repr
        assert 'руб.' in str_repr
    
    def test_str_no_salary(self):
        salary = Salary()
        str_repr = str(salary)
        assert 'Зарплата не указана' in str_repr
    
    def test_to_dict(self, salary_data):
        salary = Salary(salary_data)
        result = salary.to_dict()
        assert result['from'] == 100000
        assert result['to'] == 150000
        assert result['currency'] == 'RUR'
    
    def test_get_max_salary(self, salary_data):
        salary = Salary(salary_data)
        assert salary.get_max_salary() == 150000
    
    def test_get_max_salary_only_from(self):
        salary = Salary({'from': 100000})
        assert salary.get_max_salary() == 100000
    
    def test_get_max_salary_none(self):
        salary = Salary()
        assert salary.get_max_salary() is None

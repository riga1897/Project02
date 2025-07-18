
"""
Тесты для модуля vacancy models
"""

import pytest
from datetime import datetime
from src.vacancies.models import Vacancy
from src.utils.salary import Salary


class TestVacancy:
    """Тесты для класса Vacancy"""
    
    def test_vacancy_creation_minimal(self):
        """Тест создания вакансии с минимальными данными"""
        vacancy = Vacancy(
            title="Test Job",
            url="https://example.com",
            salary=None,
            description="Test description"
        )
        
        assert vacancy.title == "Test Job"
        assert vacancy.url == "https://example.com"
        assert vacancy.description == "Test description"
        assert vacancy.salary.salary_from is None
        assert vacancy.salary.salary_to is None
        assert vacancy.vacancy_id is not None
    
    def test_vacancy_creation_full(self):
        """Тест создания вакансии с полными данными"""
        salary_data = {"from": 100000, "to": 150000, "currency": "RUR"}
        employer_data = {"name": "Test Company"}
        
        vacancy = Vacancy(
            title="Senior Python Developer",
            url="https://example.com/vacancy/123",
            salary=salary_data,
            description="Python development",
            requirements="Python, Django",
            responsibilities="Code development",
            employer=employer_data,
            experience="От 3 до 6 лет",
            vacancy_id="123"
        )
        
        assert vacancy.title == "Senior Python Developer"
        assert vacancy.salary.salary_from == 100000
        assert vacancy.salary.salary_to == 150000
        assert vacancy.requirements == "Python, Django"
        assert vacancy.employer == employer_data
        assert vacancy.vacancy_id == "123"
    
    def test_vacancy_from_dict(self):
        """Тест создания вакансии из словаря"""
        data = {
            'id': '456',
            'name': 'Frontend Developer',
            'alternate_url': 'https://hh.ru/vacancy/456',
            'salary': {'from': 80000, 'to': 120000, 'currency': 'RUR'},
            'snippet': {
                'requirement': 'JavaScript',
                'responsibility': 'UI development'
            },
            'employer': {'name': 'Web Company'},
            'experience': {'name': 'От 1 года до 3 лет'}
        }
        
        vacancy = Vacancy.from_dict(data)
        
        assert vacancy.vacancy_id == '456'
        assert vacancy.title == 'Frontend Developer'
        assert vacancy.url == 'https://hh.ru/vacancy/456'
        assert vacancy.salary.salary_from == 80000
        assert vacancy.requirements == 'JavaScript'
        assert vacancy.responsibilities == 'UI development'
    
    def test_vacancy_to_dict(self):
        """Тест преобразования вакансии в словарь"""
        vacancy = Vacancy(
            title="Test Job",
            url="https://example.com",
            salary={"from": 100000, "to": 150000, "currency": "RUR"},
            description="Test description",
            vacancy_id="test_id"
        )
        
        result = vacancy.to_dict()
        
        assert result['id'] == 'test_id'
        assert result['title'] == 'Test Job'
        assert result['url'] == 'https://example.com'
        assert result['salary']['from'] == 100000
        assert result['salary']['to'] == 150000
    
    def test_vacancy_comparison(self):
        """Тест сравнения вакансий"""
        vacancy1 = Vacancy(
            title="Job1",
            url="https://example.com/1",
            salary={"from": 100000, "to": 150000, "currency": "RUR"},
            description="Test",
            vacancy_id="1"
        )
        
        vacancy2 = Vacancy(
            title="Job2",
            url="https://example.com/2",
            salary={"from": 200000, "to": 250000, "currency": "RUR"},
            description="Test",
            vacancy_id="2"
        )
        
        assert vacancy1 < vacancy2  # По средней зарплате
        assert vacancy2 > vacancy1
        assert vacancy1 != vacancy2
    
    def test_vacancy_equality(self):
        """Тест равенства вакансий по ID"""
        vacancy1 = Vacancy(
            title="Job",
            url="https://example.com",
            salary=None,
            description="Test",
            vacancy_id="same_id"
        )
        
        vacancy2 = Vacancy(
            title="Different Job",
            url="https://different.com",
            salary=None,
            description="Different",
            vacancy_id="same_id"
        )
        
        assert vacancy1 == vacancy2
        assert hash(vacancy1) == hash(vacancy2)
    
    def test_cast_to_object_list(self):
        """Тест преобразования списка словарей в список вакансий"""
        data = [
            {
                'id': '1',
                'name': 'Job1',
                'alternate_url': 'https://example.com/1',
                'salary': {'from': 100000, 'currency': 'RUR'}
            },
            {
                'id': '2',
                'name': 'Job2',
                'alternate_url': 'https://example.com/2'
            },
            {'invalid': 'data'}  # Некорректные данные
        ]
        
        result = Vacancy.cast_to_object_list(data)
        
        assert len(result) == 2
        assert result[0].vacancy_id == '1'
        assert result[1].vacancy_id == '2'
    
    def test_html_cleaning(self):
        """Тест очистки HTML тегов"""
        vacancy = Vacancy(
            title="Test Job",
            url="https://example.com",
            salary=None,
            description="Test",
            requirements="<p>Python</p> and <b>Django</b>"
        )
        
        assert vacancy.requirements == "Python and Django"
    
    def test_datetime_parsing(self, sample_vacancy):
        """Тест парсинга даты и времени"""
        # Тестируем разные форматы даты
        test_dates = [
            "2024-01-15T10:30:45+0300",
            "2024-01-15T10:30:45",
            "2024-01-15 10:30:45"
        ]
        
        for date_str in test_dates:
            vacancy = Vacancy(
                title="Test",
                url="https://example.com",
                salary=None,
                description="Test",
                published_at=date_str
            )
            assert isinstance(vacancy.published_at, datetime)

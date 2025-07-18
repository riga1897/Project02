
"""
Новые тесты для модулей vacancy models
"""

import pytest
from datetime import datetime
from src.vacancies.models import Vacancy


class TestVacancyNew:
    """Новые тесты для класса Vacancy"""
    
    def test_vacancy_creation_minimal(self):
        """Тест создания вакансии с минимальными параметрами"""
        vacancy = Vacancy(
            title="Test Job",
            url="https://example.com",
            salary=None,
            description="Test description"
        )
        
        assert vacancy.title == "Test Job"
        assert vacancy.url == "https://example.com"
        assert vacancy.salary is not None  # Salary создается пустым
        assert vacancy.description == "Test description"
        assert vacancy.vacancy_id is not None
        assert vacancy.source == "hh.ru"
    
    def test_vacancy_creation_full(self):
        """Тест создания вакансии с полными параметрами"""
        salary_data = {"from": 100000, "to": 150000, "currency": "RUR"}
        employer_data = {"name": "Test Company"}
        skills_data = [{"name": "Python"}, {"name": "Django"}]
        
        vacancy = Vacancy(
            title="Python Developer",
            url="https://example.com/job",
            salary=salary_data,
            description="Python development job",
            requirements="Python, Django experience",
            responsibilities="Development tasks",
            employer=employer_data,
            experience="3-6 лет",
            employment="Полная занятость",
            schedule="Полный день",
            published_at="2024-01-15T10:30:45",
            skills=skills_data,
            detailed_description="Detailed job description",
            benefits="Health insurance",
            vacancy_id="custom_id",
            source="custom_source"
        )
        
        assert vacancy.title == "Python Developer"
        assert vacancy.url == "https://example.com/job"
        assert vacancy.salary.salary_from == 100000
        assert vacancy.salary.salary_to == 150000
        assert vacancy.description == "Python development job"
        assert vacancy.requirements == "Python, Django experience"
        assert vacancy.responsibilities == "Development tasks"
        assert vacancy.employer == employer_data
        assert vacancy.experience == "3-6 лет"
        assert vacancy.employment == "Полная занятость"
        assert vacancy.schedule == "Полный день"
        assert vacancy.skills == skills_data
        assert vacancy.detailed_description == "Detailed job description"
        assert vacancy.benefits == "Health insurance"
        assert vacancy.vacancy_id == "custom_id"
        assert vacancy.source == "custom_source"
    
    def test_vacancy_html_cleaning(self):
        """Тест очистки HTML-тегов"""
        vacancy = Vacancy(
            title="Test Job",
            url="https://example.com",
            salary=None,
            description="Test description",
            requirements="<p>Python <strong>experience</strong></p>",
            responsibilities="<ul><li>Development</li><li>Testing</li></ul>"
        )
        
        assert vacancy.requirements == "Python experience"
        assert vacancy.responsibilities == "DevelopmentTesting"
    
    def test_vacancy_from_dict_full_data(self):
        """Тест создания вакансии из словаря с полными данными"""
        data = {
            "id": "test_id",
            "title": "Test Job",
            "url": "https://example.com",
            "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
            "description": "Test description",
            "snippet": {
                "requirement": "Python experience",
                "responsibility": "Development work"
            },
            "employer": {"name": "Test Company"},
            "experience": {"name": "3-6 лет"},
            "employment": {"name": "Полная занятость"},
            "schedule": {"name": "Полный день"},
            "published_at": "2024-01-15T10:30:45",
            "detailed_description": "Detailed description",
            "benefits": "Health insurance",
            "source": "test_source"
        }
        
        vacancy = Vacancy.from_dict(data)
        
        assert vacancy.vacancy_id == "test_id"
        assert vacancy.title == "Test Job"
        assert vacancy.url == "https://example.com"
        assert vacancy.salary.salary_from == 100000
        assert vacancy.requirements == "Python experience"
        assert vacancy.responsibilities == "Development work"
        assert vacancy.employer["name"] == "Test Company"
        assert vacancy.experience == "3-6 лет"
        assert vacancy.employment == "Полная занятость"
        assert vacancy.schedule == "Полный день"
        assert vacancy.source == "test_source"
    
    def test_vacancy_from_dict_minimal_data(self):
        """Тест создания вакансии из словаря с минимальными данными"""
        data = {
            "id": "test_id",
            "title": "Test Job",
            "url": "https://example.com"
        }
        
        vacancy = Vacancy.from_dict(data)
        
        assert vacancy.vacancy_id == "test_id"
        assert vacancy.title == "Test Job"
        assert vacancy.url == "https://example.com"
        assert vacancy.salary.salary_from is None
        assert vacancy.requirements is None
        assert vacancy.employer is None
    
    def test_vacancy_from_dict_fallback_fields(self):
        """Тест создания вакансии с fallback полями"""
        data = {
            "id": "test_id",
            "name": "Test Job Name",  # fallback для title
            "alternate_url": "https://example.com/alt",  # fallback для url
            "description": "Test description"
        }
        
        vacancy = Vacancy.from_dict(data)
        
        assert vacancy.title == "Test Job Name"
        assert vacancy.url == "https://example.com/alt"
    
    def test_vacancy_from_dict_invalid_data(self):
        """Тест создания вакансии с некорректными данными"""
        with pytest.raises(ValueError):
            Vacancy.from_dict("not a dict")
    
    def test_vacancy_to_dict(self):
        """Тест преобразования вакансии в словарь"""
        vacancy = Vacancy(
            title="Test Job",
            url="https://example.com",
            salary={"from": 100000, "currency": "RUR"},
            description="Test description",
            vacancy_id="test_id"
        )
        
        result = vacancy.to_dict()
        
        assert result["id"] == "test_id"
        assert result["title"] == "Test Job"
        assert result["url"] == "https://example.com"
        assert result["salary"]["from"] == 100000
        assert result["description"] == "Test description"
    
    def test_vacancy_string_representation(self):
        """Тест строкового представления вакансии"""
        vacancy = Vacancy(
            title="Python Developer",
            url="https://example.com",
            salary={"from": 100000, "currency": "RUR"},
            description="Python development job",
            requirements="Python experience required",
            employer={"name": "Tech Company"},
            vacancy_id="test_id"
        )
        
        result = str(vacancy)
        
        assert "Python Developer" in result
        assert "Tech Company" in result
        assert "100000" in result
        assert "Python experience" in result
        assert "https://example.com" in result
    
    def test_vacancy_equality(self):
        """Тест сравнения вакансий на равенство"""
        vacancy1 = Vacancy("Job", "https://example.com", None, "Desc", vacancy_id="1")
        vacancy2 = Vacancy("Job", "https://example.com", None, "Desc", vacancy_id="1")
        vacancy3 = Vacancy("Job", "https://example.com", None, "Desc", vacancy_id="2")
        
        assert vacancy1 == vacancy2
        assert vacancy1 != vacancy3
    
    def test_vacancy_salary_comparison(self):
        """Тест сравнения вакансий по зарплате"""
        vacancy1 = Vacancy("Job1", "https://example.com/1", {"from": 100000}, "Desc", vacancy_id="1")
        vacancy2 = Vacancy("Job2", "https://example.com/2", {"from": 150000}, "Desc", vacancy_id="2")
        vacancy3 = Vacancy("Job3", "https://example.com/3", None, "Desc", vacancy_id="3")
        
        assert vacancy1 < vacancy2
        assert vacancy2 > vacancy1
        assert vacancy1 <= vacancy2
        assert vacancy2 >= vacancy1
        assert vacancy3 < vacancy1  # Нет зарплаты = 0
    
    def test_vacancy_hash(self):
        """Тест хеширования вакансий"""
        vacancy1 = Vacancy("Job", "https://example.com", None, "Desc", vacancy_id="1")
        vacancy2 = Vacancy("Job", "https://example.com", None, "Desc", vacancy_id="1")
        vacancy3 = Vacancy("Job", "https://example.com", None, "Desc", vacancy_id="2")
        
        assert hash(vacancy1) == hash(vacancy2)
        assert hash(vacancy1) != hash(vacancy3)
        
        # Проверяем работу в множестве
        vacancy_set = {vacancy1, vacancy2, vacancy3}
        assert len(vacancy_set) == 2
    
    def test_vacancy_cast_to_object_list(self):
        """Тест преобразования списка словарей в список вакансий"""
        data = [
            {"id": "1", "title": "Job1", "url": "https://example.com/1"},
            {"id": "2", "title": "Job2", "url": "https://example.com/2"},
            {"invalid": "data"}  # Некорректные данные должны быть пропущены
        ]
        
        result = Vacancy.cast_to_object_list(data)
        
        assert len(result) == 2
        assert result[0].vacancy_id == "1"
        assert result[1].vacancy_id == "2"
    
    def test_vacancy_datetime_parsing(self):
        """Тест парсинга различных форматов даты"""
        # Тест с корректной датой
        vacancy1 = Vacancy(
            title="Test", 
            url="https://example.com", 
            salary=None, 
            description="Test",
            published_at="2024-01-15T10:30:45+0300"
        )
        assert isinstance(vacancy1.published_at, datetime)
        
        # Тест с некорректной датой
        vacancy2 = Vacancy(
            title="Test", 
            url="https://example.com", 
            salary=None, 
            description="Test",
            published_at="invalid_date"
        )
        assert isinstance(vacancy2.published_at, datetime)  # Должна быть текущая дата

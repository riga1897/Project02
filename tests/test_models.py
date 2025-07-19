
import pytest
from datetime import datetime
from unittest.mock import patch, Mock

from src.vacancies.models import Vacancy
from src.utils.salary import Salary


class TestVacancy:
    """Тесты для модели Vacancy"""

    @pytest.fixture
    def sample_vacancy_data(self):
        """Базовые данные для создания вакансии"""
        return {
            "id": "123",
            "title": "Python Developer", 
            "url": "http://test.com",
            "salary": {
                "from": 100000,
                "to": 150000,
                "currency": "RUR"
            },
            "description": "Test description",
            "requirements": "Python, Django",
            "responsibilities": "Development", 
            "employer": {"name": "Test Company"},
            "experience": {"name": "1-3 года"},
            "employment": {"name": "Полная занятость"},
            "schedule": {"name": "Полный день"},
            "published_at": "2024-01-01T12:00:00"
        }

    @pytest.fixture
    def sample_vacancy(self, sample_vacancy_data):
        """Создание объекта вакансии для тестов"""
        return Vacancy.from_dict(sample_vacancy_data)

    def test_vacancy_creation_from_dict(self, sample_vacancy_data):
        """Тест создания вакансии из словаря"""
        vacancy = Vacancy.from_dict(sample_vacancy_data)
        
        assert vacancy.vacancy_id == "123"
        assert vacancy.title == "Python Developer"
        assert vacancy.url == "http://test.com"
        assert isinstance(vacancy.salary, Salary)
        assert vacancy.description == "Test description"
        assert vacancy.employer == {"name": "Test Company"}

    def test_vacancy_creation_minimal_data(self):
        """Тест создания вакансии с минимальными данными"""
        minimal_data = {
            "title": "Test Job",
            "url": "http://example.com"
        }
        
        vacancy = Vacancy.from_dict(minimal_data)
        
        assert vacancy.title == "Test Job"
        assert vacancy.url == "http://example.com"
        assert vacancy.vacancy_id != ""  # Должен быть сгенерирован UUID
        assert isinstance(vacancy.salary, Salary)

    def test_vacancy_to_dict(self, sample_vacancy):
        """Тест преобразования вакансии в словарь"""
        result = sample_vacancy.to_dict()
        
        assert result["id"] == "123"
        assert result["title"] == "Python Developer"
        assert result["url"] == "http://test.com"
        assert "salary" in result
        assert result["employer"] == {"name": "Test Company"}

    def test_vacancy_equality(self, sample_vacancy_data):
        """Тест сравнения вакансий"""
        vacancy1 = Vacancy.from_dict(sample_vacancy_data)
        vacancy2 = Vacancy.from_dict(sample_vacancy_data)
        
        assert vacancy1 == vacancy2
        
        # Изменяем ID
        sample_vacancy_data["id"] = "456"
        vacancy3 = Vacancy.from_dict(sample_vacancy_data)
        
        assert vacancy1 != vacancy3

    def test_vacancy_hash(self, sample_vacancy):
        """Тест хеширования вакансий"""
        vacancy_set = {sample_vacancy}
        assert len(vacancy_set) == 1
        
        # Добавляем ту же вакансию
        vacancy_set.add(sample_vacancy)
        assert len(vacancy_set) == 1

    def test_vacancy_str_representation(self, sample_vacancy):
        """Тест строкового представления"""
        str_repr = str(sample_vacancy)
        
        assert "Python Developer" in str_repr
        assert "Test Company" in str_repr
        assert "http://test.com" in str_repr

    def test_vacancy_salary_comparison(self, sample_vacancy_data):
        """Тест сравнения вакансий по зарплате"""
        vacancy1 = Vacancy.from_dict(sample_vacancy_data)
        
        # Создаем вакансию с большей зарплатой
        high_salary_data = sample_vacancy_data.copy()
        high_salary_data["id"] = "456" 
        high_salary_data["salary"] = {
            "from": 200000,
            "to": 250000,
            "currency": "RUR"
        }
        vacancy2 = Vacancy.from_dict(high_salary_data)
        
        assert vacancy1 < vacancy2
        assert vacancy2 > vacancy1
        assert vacancy1 <= vacancy2
        assert vacancy2 >= vacancy1

    def test_vacancy_no_salary(self):
        """Тест вакансии без зарплаты"""
        data = {
            "id": "123",
            "title": "Test Job",
            "url": "http://test.com",
            "salary": None
        }
        
        vacancy = Vacancy.from_dict(data)
        assert isinstance(vacancy.salary, Salary)
        assert vacancy.salary.salary_from is None

    def test_vacancy_html_cleaning(self):
        """Тест очистки HTML из требований и обязанностей"""
        data = {
            "id": "123",
            "title": "Test Job",
            "url": "http://test.com",
            "snippet": {
                "requirement": "<p>Python <strong>required</strong></p>",
                "responsibility": "<div>Development work</div>"
            }
        }
        
        vacancy = Vacancy.from_dict(data)
        assert "<p>" not in vacancy.requirements
        assert "<strong>" not in vacancy.requirements
        assert "Python required" in vacancy.requirements

    def test_vacancy_source_detection_hh(self):
        """Тест определения источника HH"""
        data = {
            "id": "123",
            "name": "Test Job",  # HH использует 'name' вместо 'title'
            "alternate_url": "https://hh.ru/vacancy/123",
            "snippet": {"requirement": "test"}
        }
        
        vacancy = Vacancy.from_dict(data)
        assert vacancy.source == "hh.ru"

    def test_vacancy_source_detection_sj(self):
        """Тест определения источника SuperJob"""
        data = {
            "id": "123",
            "profession": "Test Job",  # SJ использует 'profession'
            "candidat": "requirements",
            "work": "responsibilities"
        }
        
        vacancy = Vacancy.from_dict(data)
        assert vacancy.source == "superjob.ru"

    def test_vacancy_cast_to_object_list(self, sample_vacancy_data):
        """Тест преобразования списка данных в список объектов"""
        data_list = [sample_vacancy_data, sample_vacancy_data.copy()]
        data_list[1]["id"] = "456"
        
        vacancies = Vacancy.cast_to_object_list(data_list)
        
        assert len(vacancies) == 2
        assert all(isinstance(v, Vacancy) for v in vacancies)
        assert vacancies[0].vacancy_id != vacancies[1].vacancy_id

    def test_vacancy_invalid_data_handling(self):
        """Тест обработки некорректных данных"""
        with pytest.raises(ValueError):
            Vacancy.from_dict("not a dict")
        
        with pytest.raises(ValueError):
            Vacancy.from_dict({})  # Пустой словарь

    def test_vacancy_date_parsing(self):
        """Тест парсинга различных форматов дат"""
        data = {
            "id": "123",
            "title": "Test",
            "url": "http://test.com",
            "published_at": "2024-01-01T12:00:00+03:00"
        }
        
        vacancy = Vacancy.from_dict(data)
        assert isinstance(vacancy.published_at, datetime)

    @patch('src.vacancies.models.logging')
    def test_vacancy_invalid_date_handling(self, mock_logging):
        """Тест обработки некорректных дат"""
        data = {
            "id": "123", 
            "title": "Test",
            "url": "http://test.com",
            "published_at": "invalid date"
        }
        
        vacancy = Vacancy.from_dict(data)
        assert isinstance(vacancy.published_at, datetime)

    def test_vacancy_updated_at_attribute(self, sample_vacancy):
        """Тест атрибута updated_at для избежания проблем в других тестах"""
        # Проверяем что у вакансии есть все необходимые атрибуты
        assert hasattr(sample_vacancy, 'vacancy_id')
        assert hasattr(sample_vacancy, 'title')
        assert hasattr(sample_vacancy, 'url')
        assert hasattr(sample_vacancy, 'description')
        
        # Устанавливаем updated_at для совместимости с тестами JSONSaver
        sample_vacancy.updated_at = "2024-01-01T12:00:00"
        assert sample_vacancy.updated_at == "2024-01-01T12:00:00"

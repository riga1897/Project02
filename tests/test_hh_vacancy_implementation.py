
import pytest
import uuid
from datetime import datetime
from typing import Dict, Any
from unittest.mock import patch

from src.vacancies.hh_models import HHVacancy
from src.vacancies.abstract import AbstractVacancy
from src.utils.salary import Salary


class TestHHVacancyImplementation:
    """Тесты для HHVacancy как конкретной реализации AbstractVacancy"""

    @pytest.fixture
    def sample_hh_data(self):
        """Пример данных вакансии в формате HH API"""
        return {
            'id': '12345',
            'name': 'Python Developer',
            'alternate_url': 'https://hh.ru/vacancy/12345',
            'salary': {
                'from': 100000,
                'to': 150000,
                'currency': 'RUR'
            },
            'description': 'Отличная вакансия для Python разработчика',
            'snippet': {
                'requirement': 'Знание Python, Django',
                'responsibility': 'Разработка веб-приложений'
            },
            'employer': {
                'name': 'ТехКомпания',
                'id': '67890'
            },
            'experience': {
                'name': '1–3 года'
            },
            'employment': {
                'name': 'Полная занятость'
            },
            'schedule': {
                'name': 'Полный день'
            },
            'published_at': '2024-01-15T10:30:00+0300',
            'area': {
                'name': 'Москва',
                'id': '1'
            }
        }

    @pytest.fixture
    def hh_vacancy(self, sample_hh_data):
        """Создает экземпляр HHVacancy"""
        return HHVacancy.from_dict(sample_hh_data)

    def test_inherits_from_abstract_vacancy(self, hh_vacancy):
        """Проверяем, что HHVacancy наследуется от AbstractVacancy"""
        assert isinstance(hh_vacancy, AbstractVacancy)
        assert issubclass(HHVacancy, AbstractVacancy)

    def test_implements_all_abstract_methods(self):
        """Проверяем, что HHVacancy реализует все абстрактные методы"""
        # Получаем абстрактные методы из родительского класса
        abstract_methods = AbstractVacancy.__abstractmethods__
        
        # Проверяем, что все методы реализованы в HHVacancy
        for method_name in abstract_methods:
            assert hasattr(HHVacancy, method_name)
            method = getattr(HHVacancy, method_name)
            assert callable(method)
            # Проверяем, что метод не помечен как абстрактный
            assert not getattr(method, '__isabstractmethod__', False)

    def test_from_dict_method_signature(self, sample_hh_data):
        """Проверяем правильность сигнатуры метода from_dict"""
        vacancy = HHVacancy.from_dict(sample_hh_data)
        assert isinstance(vacancy, HHVacancy)
        assert isinstance(vacancy, AbstractVacancy)

    def test_to_dict_method_signature(self, hh_vacancy):
        """Проверяем правильность сигнатуры метода to_dict"""
        result = hh_vacancy.to_dict()
        assert isinstance(result, dict)
        
        # Проверяем наличие основных ключей в формате HH
        required_keys = ['id', 'name', 'alternate_url']
        for key in required_keys:
            assert key in result

    def test_hh_specific_fields(self, hh_vacancy, sample_hh_data):
        """Тестируем HH-специфичные поля"""
        # Проверяем, что HH-специфичные поля присутствуют
        assert hasattr(hh_vacancy, 'area')
        assert hasattr(hh_vacancy, 'snippet')
        assert hh_vacancy.source == "hh.ru"
        
        # Проверяем значения HH-специфичных полей
        assert hh_vacancy.area == sample_hh_data['area']
        assert hh_vacancy.snippet == sample_hh_data['snippet']

    def test_salary_validation_hh_format(self):
        """Тестируем валидацию зарплаты в формате HH"""
        # Тест с корректными данными зарплаты
        salary_data = {
            'from': 80000,
            'to': 120000,
            'currency': 'RUR'
        }
        
        vacancy = HHVacancy(
            title="Test",
            url="http://test.com",
            salary=salary_data,
            description="Test"
        )
        
        assert isinstance(vacancy.salary, Salary)
        assert vacancy.salary.salary_from == 80000
        assert vacancy.salary.salary_to == 120000

        # Тест с None
        vacancy_no_salary = HHVacancy(
            title="Test",
            url="http://test.com", 
            salary=None,
            description="Test"
        )
        
        assert isinstance(vacancy_no_salary.salary, Salary)

    def test_html_cleaning_functionality(self):
        """Тестируем функциональность очистки HTML"""
        html_text = "<p>Требования к кандидату:</p><ul><li>Python</li><li>Django</li></ul>"
        clean_text = HHVacancy._clean_html(html_text)
        
        assert "<p>" not in clean_text
        assert "<ul>" not in clean_text
        assert "<li>" not in clean_text
        assert "Требования к кандидату:" in clean_text
        assert "Python" in clean_text
        assert "Django" in clean_text

    def test_datetime_parsing_hh_format(self):
        """Тестируем парсинг времени в формате HH"""
        # Тест с ISO форматом и timezone
        iso_with_tz = "2024-01-15T10:30:45+0300"
        result = HHVacancy._parse_datetime(iso_with_tz)
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

        # Тест с ISO форматом без timezone
        iso_without_tz = "2024-01-15T10:30:45"
        result = HHVacancy._parse_datetime(iso_without_tz)
        assert isinstance(result, datetime)

        # Тест с некорректным форматом
        invalid_date = "invalid-date-string"
        result = HHVacancy._parse_datetime(invalid_date)
        assert isinstance(result, datetime)

        # Тест с None/пустой строкой
        result = HHVacancy._parse_datetime("")
        assert isinstance(result, datetime)

    def test_from_dict_with_complex_hh_data(self):
        """Тестируем создание из сложных данных HH"""
        complex_data = {
            'id': '54321',
            'name': 'Senior Python Developer',
            'alternate_url': 'https://hh.ru/vacancy/54321',
            'salary': {
                'from': 200000,
                'to': 300000,
                'currency': 'RUR'
            },
            'description': '<p>Описание вакансии</p>',
            'snippet': {
                'requirement': 'Опыт работы с <highlighttext>Python</highlighttext>',
                'responsibility': 'Разработка и поддержка <highlighttext>Django</highlighttext> приложений'
            },
            'employer': {
                'name': 'Инновационная IT-компания',
                'id': '99999',
                'url': 'https://hh.ru/employer/99999'
            },
            'experience': {'name': '3–6 лет'},
            'employment': {'name': 'Полная занятость'},
            'schedule': {'name': 'Удаленная работа'},
            'published_at': '2024-02-20T14:15:30+0300',
            'area': {
                'name': 'Санкт-Петербург',
                'id': '2'
            },
            'skills': [
                {'name': 'Python'},
                {'name': 'Django'},
                {'name': 'PostgreSQL'}
            ]
        }

        vacancy = HHVacancy.from_dict(complex_data)
        
        assert vacancy.vacancy_id == '54321'
        assert vacancy.title == 'Senior Python Developer'
        assert vacancy.url == 'https://hh.ru/vacancy/54321'
        assert vacancy.salary.salary_from == 200000
        assert vacancy.salary.salary_to == 300000
        assert vacancy.experience == '3–6 лет'
        assert vacancy.employment == 'Полная занятость'
        assert vacancy.schedule == 'Удаленная работа'
        assert vacancy.area['name'] == 'Санкт-Петербург'
        assert vacancy.source == "hh.ru"

    def test_from_dict_with_missing_fields(self):
        """Тестируем создание из данных с отсутствующими полями"""
        minimal_data = {
            'id': '11111',
            'name': 'Basic Job',
            'alternate_url': 'https://hh.ru/vacancy/11111'
        }

        vacancy = HHVacancy.from_dict(minimal_data)
        
        assert vacancy.vacancy_id == '11111'
        assert vacancy.title == 'Basic Job'
        assert vacancy.url == 'https://hh.ru/vacancy/11111'
        assert vacancy.source == "hh.ru"
        
        # Поля, которых нет в данных, должны иметь значения по умолчанию
        assert vacancy.description == ''
        assert vacancy.experience is None
        assert vacancy.employment is None
        assert vacancy.schedule is None

    def test_to_dict_roundtrip_consistency(self, sample_hh_data):
        """Тестируем консистентность преобразования from_dict -> to_dict"""
        original_vacancy = HHVacancy.from_dict(sample_hh_data)
        dict_repr = original_vacancy.to_dict()
        
        # Основные поля должны совпадать
        assert dict_repr['id'] == sample_hh_data['id']
        assert dict_repr['name'] == sample_hh_data['name']
        assert dict_repr['alternate_url'] == sample_hh_data['alternate_url']
        assert dict_repr['area'] == sample_hh_data['area']

    def test_string_representation(self, hh_vacancy):
        """Тестируем строковое представление HH вакансии"""
        str_repr = str(hh_vacancy)
        
        assert "[HH]" in str_repr
        assert "Python Developer" in str_repr
        assert "ТехКомпания" in str_repr
        assert "Москва" in str_repr
        assert "https://hh.ru/vacancy/12345" in str_repr

    def test_error_handling_invalid_data(self):
        """Тестируем обработку ошибок при некорректных данных"""
        # Тест с None
        with pytest.raises(ValueError):
            HHVacancy.from_dict(None)

        # Тест с не-словарем
        with pytest.raises(ValueError):
            HHVacancy.from_dict("not a dict")

        # Тест с пустым словарем
        empty_dict = {}
        vacancy = HHVacancy.from_dict(empty_dict)
        assert vacancy.title == ''
        assert vacancy.url == ''
        assert vacancy.vacancy_id != ''  # Должен быть сгенерирован UUID

    def test_slots_usage(self, hh_vacancy):
        """Тестируем использование __slots__ для оптимизации памяти"""
        assert hasattr(HHVacancy, '__slots__')
        
        # Проверяем, что нельзя добавить новый атрибут (благодаря __slots__)
        with pytest.raises(AttributeError):
            hh_vacancy.new_attribute = "test"

    def test_polymorphism_through_abstract_interface(self, hh_vacancy):
        """Тестируем полиморфизм через абстрактный интерфейс"""
        # Используем HHVacancy через интерфейс AbstractVacancy
        abstract_vacancy: AbstractVacancy = hh_vacancy

        # Все методы должны работать через абстрактный интерфейс
        dict_result = abstract_vacancy.to_dict()
        assert isinstance(dict_result, dict)
        
        # Проверяем, что объект ведет себя как AbstractVacancy
        assert hasattr(abstract_vacancy, 'title')
        assert hasattr(abstract_vacancy, 'url')
        assert hasattr(abstract_vacancy, 'vacancy_id')

    def test_unique_id_generation(self):
        """Тестируем генерацию уникальных ID"""
        vacancy1 = HHVacancy(
            title="Test 1",
            url="http://test1.com",
            salary=None,
            description="Test 1"
        )
        
        vacancy2 = HHVacancy(
            title="Test 2", 
            url="http://test2.com",
            salary=None,
            description="Test 2"
        )
        
        # ID должны быть разными
        assert vacancy1.vacancy_id != vacancy2.vacancy_id
        
        # ID должны быть валидными UUID строками
        try:
            uuid.UUID(vacancy1.vacancy_id)
            uuid.UUID(vacancy2.vacancy_id)
        except ValueError:
            pytest.fail("Generated IDs are not valid UUIDs")

    def test_hh_specific_parsing_logic(self):
        """Тестируем HH-специфичную логику парсинга"""
        # Тест парсинга experience как словаря
        data_with_experience_dict = {
            'id': '123',
            'name': 'Test Job',
            'alternate_url': 'http://test.com',
            'experience': {'name': 'От 1 года до 3 лет'}
        }
        
        vacancy = HHVacancy.from_dict(data_with_experience_dict)
        assert vacancy.experience == 'От 1 года до 3 лет'

        # Тест парсинга experience как строки
        data_with_experience_str = {
            'id': '124',
            'name': 'Test Job 2',
            'alternate_url': 'http://test2.com',
            'experience': 'Более 6 лет'
        }
        
        vacancy2 = HHVacancy.from_dict(data_with_experience_str)
        assert vacancy2.experience == 'Более 6 лет'

    @patch('src.vacancies.hh_models.logger')
    def test_logging_on_errors(self, mock_logger):
        """Тестируем логирование при ошибках"""
        # Попытка создать вакансию с некорректными данными
        try:
            HHVacancy.from_dict({"invalid": "data"})
        except ValueError:
            pass  # Ожидаемая ошибка

        # Проверяем, что была вызвана функция логирования
        mock_logger.error.assert_called()

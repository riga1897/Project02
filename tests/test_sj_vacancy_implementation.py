
import pytest
import uuid
from datetime import datetime
from typing import Dict, Any
from unittest.mock import patch

from src.vacancies.sj_models import SuperJobVacancy
from src.vacancies.abstract import AbstractVacancy
from src.utils.salary import Salary


class TestSuperJobVacancyImplementation:
    """Тесты для SuperJobVacancy как конкретной реализации AbstractVacancy"""

    @pytest.fixture
    def sample_sj_data(self):
        """Пример данных вакансии в формате SuperJob API"""
        return {
            'id': 12345,
            'profession': 'Python Разработчик',
            'link': 'https://www.superjob.ru/vakansii/python-razrabotchik-12345.html',
            'payment_from': 120000,
            'payment_to': 180000,
            'currency': 'rub',
            'vacancyRichText': 'Ищем опытного Python разработчика для работы над интересными проектами',
            'candidat': 'Опыт работы с Python от 2 лет, знание Django/Flask',
            'work': 'Разработка веб-приложений, участие в архитектурных решениях',
            'firm_name': 'СуперТех',
            'experience': {
                'title': '1–3 года'
            },
            'type_of_work': {
                'title': 'Полная занятость'
            },
            'date_published': 1705392600  # Unix timestamp
        }

    @pytest.fixture
    def sj_vacancy(self, sample_sj_data):
        """Создает экземпляр SuperJobVacancy"""
        return SuperJobVacancy.from_dict(sample_sj_data)

    def test_inherits_from_abstract_vacancy(self, sj_vacancy):
        """Проверяем, что SuperJobVacancy наследуется от AbstractVacancy"""
        assert isinstance(sj_vacancy, AbstractVacancy)
        assert issubclass(SuperJobVacancy, AbstractVacancy)

    def test_implements_all_abstract_methods(self):
        """Проверяем, что SuperJobVacancy реализует все абстрактные методы"""
        # Получаем абстрактные методы из родительского класса
        abstract_methods = AbstractVacancy.__abstractmethods__
        
        # Проверяем, что все методы реализованы в SuperJobVacancy
        for method_name in abstract_methods:
            assert hasattr(SuperJobVacancy, method_name)
            method = getattr(SuperJobVacancy, method_name)
            assert callable(method)
            # Проверяем, что метод не помечен как абстрактный
            assert not getattr(method, '__isabstractmethod__', False)

    def test_from_dict_method_signature(self, sample_sj_data):
        """Проверяем правильность сигнатуры метода from_dict"""
        vacancy = SuperJobVacancy.from_dict(sample_sj_data)
        assert isinstance(vacancy, SuperJobVacancy)
        assert isinstance(vacancy, AbstractVacancy)

    def test_to_dict_method_signature(self, sj_vacancy):
        """Проверяем правильность сигнатуры метода to_dict"""
        result = sj_vacancy.to_dict()
        assert isinstance(result, dict)
        
        # Проверяем наличие основных ключей в формате SuperJob
        required_keys = ['id', 'profession', 'link']
        for key in required_keys:
            assert key in result

    def test_sj_specific_fields(self, sj_vacancy, sample_sj_data):
        """Тестируем SuperJob-специфичные поля"""
        assert sj_vacancy.source == "superjob.ru"
        
        # Проверяем поля, специфичные для SuperJob
        assert hasattr(sj_vacancy, 'skills')
        assert hasattr(sj_vacancy, 'keywords')
        assert hasattr(sj_vacancy, 'detailed_description')
        assert hasattr(sj_vacancy, 'benefits')
        
        # Проверяем значения
        assert sj_vacancy.skills == []
        assert sj_vacancy.keywords == []

    def test_salary_validation_sj_format(self):
        """Тестируем валидацию зарплаты в формате SuperJob"""
        # Тест с корректными данными зарплаты
        salary_data = {
            'payment_from': 90000,
            'payment_to': 130000
        }
        
        vacancy = SuperJobVacancy(
            title="Test",
            url="http://test.com",
            salary=salary_data,
            description="Test"
        )
        
        assert isinstance(vacancy.salary, Salary)
        assert vacancy.salary.salary_from == 90000
        assert vacancy.salary.salary_to == 130000

        # Тест с нулевыми значениями (должны конвертироваться в None)
        salary_zero = {
            'payment_from': 0,
            'payment_to': 0
        }
        
        vacancy_zero = SuperJobVacancy(
            title="Test",
            url="http://test.com",
            salary=salary_zero,
            description="Test"
        )
        
        assert vacancy_zero.salary is None

        # Тест с частично нулевыми значениями
        salary_partial = {
            'payment_from': 80000,
            'payment_to': 0
        }
        
        vacancy_partial = SuperJobVacancy(
            title="Test",
            url="http://test.com",
            salary=salary_partial,
            description="Test"
        )
        
        assert vacancy_partial.salary.salary_from == 80000
        assert vacancy_partial.salary.salary_to is None

    def test_datetime_parsing_sj_format(self):
        """Тестируем парсинг времени в формате SuperJob"""
        # Тест с Unix timestamp (int)
        timestamp = 1705392600
        result = SuperJobVacancy._parse_datetime(timestamp)
        assert isinstance(result, datetime)
        assert result.year == 2024

        # Тест с ISO строкой
        iso_string = "2024-01-15T10:30:45"
        result = SuperJobVacancy._parse_datetime(iso_string)
        assert isinstance(result, datetime)
        assert result.year == 2024

        # Тест с некорректным форматом
        invalid_input = "invalid-timestamp"
        result = SuperJobVacancy._parse_datetime(invalid_input)
        assert isinstance(result, datetime)

        # Тест с None
        result = SuperJobVacancy._parse_datetime(None)
        assert isinstance(result, datetime)

    def test_from_dict_with_complex_sj_data(self):
        """Тестируем создание из сложных данных SuperJob"""
        complex_data = {
            'id': 67890,
            'profession': 'Senior Backend Developer',
            'link': 'https://www.superjob.ru/vakansii/senior-backend-developer-67890.html',
            'payment_from': 200000,
            'payment_to': 280000,
            'currency': 'rub',
            'vacancyRichText': 'Мы ищем опытного backend разработчика',
            'candidat': 'Требования:\n- Python 3.8+\n- Django/FastAPI',
            'work': 'Обязанности:\n- Разработка API\n- Код-ревью',
            'firm_name': 'Инновационный Стартап',
            'experience': {'title': '3–6 лет'},
            'type_of_work': {'title': 'Полная занятость'},
            'date_published': 1705392600
        }

        vacancy = SuperJobVacancy.from_dict(complex_data)
        
        assert vacancy.vacancy_id == '67890'
        assert vacancy.title == 'Senior Backend Developer'
        assert vacancy.url == 'https://www.superjob.ru/vakansii/senior-backend-developer-67890.html'
        assert vacancy.salary.salary_from == 200000
        assert vacancy.salary.salary_to == 280000
        assert vacancy.experience == '3–6 лет'
        assert vacancy.employment == 'Полная занятость'
        assert vacancy.source == "superjob.ru"
        assert vacancy.employer['name'] == 'Инновационный Стартап'

    def test_from_dict_with_missing_fields(self):
        """Тестируем создание из данных с отсутствующими полями"""
        minimal_data = {
            'id': 22222,
            'profession': 'Junior Developer',
            'link': 'https://www.superjob.ru/vakansii/junior-developer-22222.html'
        }

        vacancy = SuperJobVacancy.from_dict(minimal_data)
        
        assert vacancy.vacancy_id == '22222'
        assert vacancy.title == 'Junior Developer'
        assert vacancy.url == 'https://www.superjob.ru/vakansii/junior-developer-22222.html'
        assert vacancy.source == "superjob.ru"
        
        # Поля, которых нет в данных, должны иметь значения по умолчанию
        assert vacancy.description == ''
        assert vacancy.requirements == ''
        assert vacancy.responsibilities == ''
        assert vacancy.experience is None
        assert vacancy.employment is None
        assert vacancy.employer is None

    def test_to_dict_roundtrip_consistency(self, sample_sj_data):
        """Тестируем консистентность преобразования from_dict -> to_dict"""
        original_vacancy = SuperJobVacancy.from_dict(sample_sj_data)
        dict_repr = original_vacancy.to_dict()
        
        # Основные поля должны совпадать
        assert dict_repr['id'] == str(sample_sj_data['id'])
        assert dict_repr['profession'] == sample_sj_data['profession']
        assert dict_repr['link'] == sample_sj_data['link']
        assert dict_repr['payment_from'] == sample_sj_data['payment_from']
        assert dict_repr['payment_to'] == sample_sj_data['payment_to']

    def test_error_handling_invalid_data(self):
        """Тестируем обработку ошибок при некорректных данных"""
        # Тест с None
        with pytest.raises(ValueError):
            SuperJobVacancy.from_dict(None)

        # Тест с не-словарем
        with pytest.raises(ValueError):
            SuperJobVacancy.from_dict("not a dict")

        # Тест с пустым словарем
        empty_dict = {}
        vacancy = SuperJobVacancy.from_dict(empty_dict)
        assert vacancy.title == ''
        assert vacancy.url == ''
        assert vacancy.vacancy_id != ''  # Должен быть сгенерирован UUID

    def test_polymorphism_through_abstract_interface(self, sj_vacancy):
        """Тестируем полиморфизм через абстрактный интерфейс"""
        # Используем SuperJobVacancy через интерфейс AbstractVacancy
        abstract_vacancy: AbstractVacancy = sj_vacancy

        # Все методы должны работать через абстрактный интерфейс
        dict_result = abstract_vacancy.to_dict()
        assert isinstance(dict_result, dict)
        
        # Проверяем, что объект ведет себя как AbstractVacancy
        assert hasattr(abstract_vacancy, 'title')
        assert hasattr(abstract_vacancy, 'url')
        assert hasattr(abstract_vacancy, 'vacancy_id')

    def test_unique_id_generation(self):
        """Тестируем генерацию уникальных ID"""
        vacancy1 = SuperJobVacancy(
            title="Test 1",
            url="http://test1.com",
            salary=None,
            description="Test 1"
        )
        
        vacancy2 = SuperJobVacancy(
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

    def test_salary_edge_cases(self):
        """Тестируем граничные случаи обработки зарплаты"""
        # Тест с только payment_from
        salary_from_only = {'payment_from': 100000, 'payment_to': 0}
        vacancy = SuperJobVacancy(
            title="Test",
            url="http://test.com",
            salary=salary_from_only,
            description="Test"
        )
        assert vacancy.salary.salary_from == 100000
        assert vacancy.salary.salary_to is None

        # Тест с только payment_to
        salary_to_only = {'payment_from': 0, 'payment_to': 150000}
        vacancy = SuperJobVacancy(
            title="Test",
            url="http://test.com",
            salary=salary_to_only,
            description="Test"
        )
        assert vacancy.salary.salary_from is None
        assert vacancy.salary.salary_to == 150000

    def test_employer_handling(self, sample_sj_data):
        """Тестируем обработку информации о работодателе"""
        vacancy = SuperJobVacancy.from_dict(sample_sj_data)
        
        assert vacancy.employer is not None
        assert vacancy.employer['name'] == 'СуперТех'

        # Тест без информации о работодателе
        data_no_employer = sample_sj_data.copy()
        del data_no_employer['firm_name']
        
        vacancy_no_employer = SuperJobVacancy.from_dict(data_no_employer)
        assert vacancy_no_employer.employer is None

    def test_experience_parsing(self):
        """Тестируем парсинг опыта работы"""
        # С объектом experience
        data_with_exp = {
            'id': 111,
            'profession': 'Test',
            'link': 'http://test.com',
            'experience': {'title': 'От 3 до 6 лет'}
        }
        
        vacancy = SuperJobVacancy.from_dict(data_with_exp)
        assert vacancy.experience == 'От 3 до 6 лет'

        # Без experience
        data_no_exp = {
            'id': 112,
            'profession': 'Test',
            'link': 'http://test.com'
        }
        
        vacancy_no_exp = SuperJobVacancy.from_dict(data_no_exp)
        assert vacancy_no_exp.experience is None

    @patch('src.vacancies.sj_models.logger')
    def test_logging_on_errors(self, mock_logger):
        """Тестируем логирование при ошибках"""
        # Попытка создать вакансию с некорректными данными зарплаты
        invalid_salary_data = {'invalid_salary': 'data'}
        
        vacancy = SuperJobVacancy(
            title="Test",
            url="http://test.com",
            salary=invalid_salary_data,
            description="Test"
        )
        
        # Должно быть вызвано предупреждение о некорректной зарплате
        mock_logger.warning.assert_called()

    def test_sj_specific_constructor_params(self):
        """Тестируем SuperJob-специфичные параметры конструктора"""
        vacancy = SuperJobVacancy(
            title="Test Job",
            url="http://test.com",
            salary=None,
            description="Test description",
            skills=[{'name': 'Python'}, {'name': 'Django'}],
            keywords=['python', 'backend'],
            benefits="Хорошие условия работы"
        )
        
        assert vacancy.skills == [{'name': 'Python'}, {'name': 'Django'}]
        assert vacancy.keywords == ['python', 'backend']
        assert vacancy.benefits == "Хорошие условия работы"

    def test_timestamp_conversion_in_to_dict(self, sj_vacancy):
        """Тестируем конвертацию timestamp в to_dict"""
        dict_result = sj_vacancy.to_dict()
        
        # Проверяем, что дата публикации конвертируется в timestamp
        assert isinstance(dict_result['date_published'], int)
        assert dict_result['date_published'] > 0

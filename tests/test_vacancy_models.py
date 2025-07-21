
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import uuid
from src.vacancies.models import Vacancy
from src.utils.salary import Salary

def test_vacancy_lines_121_122():
    """Тест для покрытия строк 121-122"""
    vacancy = Vacancy(vacancy_id="123", title="Test", url="http://test.com")
    # Проверяем что опциональные поля устанавливаются в None по умолчанию
    assert vacancy.requirements is None
    assert vacancy.responsibilities is None

def test_vacancy_lines_177_185():
    """Тест для покрытия строк 177, 185"""
    # Тестируем создание из словаря с отсутствующими полями
    data = {"vacancy_id": "123", "title": "Test", "url": "http://test.com"}
    vacancy = Vacancy.from_dict(data)
    
    # Строка 177 - проверка наличия ключа 'salary'
    assert vacancy.salary is not None  # Создается пустая зарплата
    
    # Строка 185 - проверка наличия ключа 'published_at'  
    assert vacancy.published_at is None  # None когда нет данных

def test_vacancy_lines_228_230():
    """Тест для покрытия строк 228, 230"""
    # Создаем вакансию с минимальными данными
    data = {
        "vacancy_id": "123",
        "title": "Test Job", 
        "url": "http://test.com"
    }
    vacancy = Vacancy.from_dict(data)
    
    # Тестируем to_dict для покрытия строк с проверками полей
    result = vacancy.to_dict()
    
    # Строки 228, 230 - проверки наличия salary и employer
    assert result['salary'] is not None  # Создается даже если не было
    assert result['employer'] is None  # Был None


class TestVacancy:
    """Тесты для модели Vacancy"""

    def test_init_with_all_parameters(self):
        """Тест инициализации с полными параметрами"""
        salary_data = {"from": 100000, "to": 150000, "currency": "RUR"}
        employer_data = {"name": "Test Company", "id": "123"}
        skills_data = [{"name": "Python"}, {"name": "Django"}]
        
        vacancy = Vacancy(
            title="Python Developer",
            url="https://example.com/vacancy/123",
            salary=salary_data,
            description="Test description",
            requirements="Python, Django",
            responsibilities="Development",
            employer=employer_data,
            experience="От 1 года до 3 лет",
            employment="Полная занятость",
            schedule="Полный день",
            published_at="2023-01-01T10:00:00",
            skills=skills_data,
            detailed_description="Detailed test description",
            benefits="Health insurance",
            vacancy_id="test_id_123",
            source="hh.ru"
        )
        
        assert vacancy.title == "Python Developer"
        assert vacancy.url == "https://example.com/vacancy/123"
        assert isinstance(vacancy.salary, Salary)
        assert vacancy.description == "Test description"
        assert vacancy.requirements == "Python, Django"
        assert vacancy.responsibilities == "Development"
        assert vacancy.employer == employer_data
        assert vacancy.experience == "От 1 года до 3 лет"
        assert vacancy.employment == "Полная занятость"
        assert vacancy.schedule == "Полный день"
        assert isinstance(vacancy.published_at, datetime)
        assert vacancy.skills == skills_data
        assert vacancy.detailed_description == "Detailed test description"
        assert vacancy.benefits == "Health insurance"
        assert vacancy.vacancy_id == "test_id_123"
        assert vacancy.source == "hh.ru"

    def test_init_with_minimal_parameters(self):
        """Тест инициализации с минимальными параметрами"""
        vacancy = Vacancy(
            title="Test Job",
            url="https://example.com/job"
        )
        
        assert vacancy.title == "Test Job"
        assert vacancy.url == "https://example.com/job"
        assert isinstance(vacancy.salary, Salary)
        assert vacancy.description == ""
        assert vacancy.requirements is None
        assert vacancy.responsibilities is None
        assert vacancy.employer is None
        assert vacancy.experience is None
        assert vacancy.employment is None
        assert vacancy.schedule is None
        assert vacancy.published_at is None
        assert vacancy.skills == []
        assert vacancy.detailed_description == ""
        assert vacancy.benefits is None
        assert vacancy.source == "unknown"
        assert len(vacancy.vacancy_id) == 36  # UUID length

    @patch('uuid.uuid4')
    def test_init_generates_uuid_when_not_provided(self, mock_uuid):
        """Тест генерации UUID при отсутствии vacancy_id"""
        mock_uuid.return_value = "mocked-uuid"
        
        vacancy = Vacancy(title="Test", url="http://test.com")
        
        assert vacancy.vacancy_id == "mocked-uuid"
        mock_uuid.assert_called_once()

    def test_validate_salary_with_data(self):
        """Тест валидации зарплаты с данными"""
        salary_data = {"from": 50000, "to": 80000}
        result = Vacancy._validate_salary(salary_data)
        
        assert isinstance(result, Salary)

    def test_validate_salary_with_none(self):
        """Тест валидации зарплаты с None"""
        result = Vacancy._validate_salary(None)
        
        assert isinstance(result, Salary)

    def test_clean_html(self):
        """Тест очистки HTML тегов"""
        html_text = "<p>Test <b>bold</b> text</p>"
        clean_text = Vacancy._clean_html(html_text)
        
        assert clean_text == "Test bold text"

    def test_clean_html_with_plain_text(self):
        """Тест очистки обычного текста"""
        plain_text = "Just plain text"
        clean_text = Vacancy._clean_html(plain_text)
        
        assert clean_text == "Just plain text"

    def test_parse_datetime_with_string_iso_with_timezone(self):
        """Тест парсинга ISO даты с часовым поясом"""
        date_str = "2023-01-01T10:00:00+0300"
        result = Vacancy._parse_datetime(date_str)
        
        assert isinstance(result, datetime)

    def test_parse_datetime_with_string_iso_without_timezone(self):
        """Тест парсинга ISO даты без часового пояса"""
        date_str = "2023-01-01T10:00:00"
        result = Vacancy._parse_datetime(date_str)
        
        assert isinstance(result, datetime)

    def test_parse_datetime_with_standard_format(self):
        """Тест парсинга стандартного формата даты"""
        date_str = "2023-01-01 10:00:00"
        result = Vacancy._parse_datetime(date_str)
        
        assert isinstance(result, datetime)

    def test_parse_datetime_with_date_only(self):
        """Тест парсинга только даты"""
        date_str = "2023-01-01"
        result = Vacancy._parse_datetime(date_str)
        
        assert isinstance(result, datetime)

    def test_parse_datetime_with_timestamp_int(self):
        """Тест парсинга timestamp как int"""
        timestamp = 1672574400  # 2023-01-01 12:00:00 UTC
        result = Vacancy._parse_datetime(timestamp)
        
        assert isinstance(result, datetime)

    def test_parse_datetime_with_timestamp_float(self):
        """Тест парсинга timestamp как float"""
        timestamp = 1672574400.5
        result = Vacancy._parse_datetime(timestamp)
        
        assert isinstance(result, datetime)

    def test_parse_datetime_with_timestamp_string(self):
        """Тест парсинга timestamp как строки"""
        timestamp_str = "1672574400"
        result = Vacancy._parse_datetime(timestamp_str)
        
        assert isinstance(result, datetime)

    def test_parse_datetime_with_none(self):
        """Тест парсинга None"""
        result = Vacancy._parse_datetime(None)
        
        assert result is None

    def test_parse_datetime_with_empty_string(self):
        """Тест парсинга пустой строки"""
        result = Vacancy._parse_datetime("")
        
        assert result is None

    def test_parse_datetime_with_invalid_format(self):
        """Тест парсинга неверного формата даты"""
        result = Vacancy._parse_datetime("invalid-date")
        
        assert result is None

    def test_parse_datetime_with_empty_timestamp_string(self):
        """Тест парсинга пустой строки timestamp"""
        result = Vacancy._parse_datetime("")
        
        assert result is None

    def test_cast_to_object_list_success(self):
        """Тест успешного преобразования списка словарей"""
        data = [
            {"title": "Job 1", "url": "http://job1.com", "id": "1"},
            {"title": "Job 2", "url": "http://job2.com", "id": "2"}
        ]
        
        with patch.object(Vacancy, 'from_dict') as mock_from_dict:
            mock_vacancy1 = Mock()
            mock_vacancy2 = Mock()
            mock_from_dict.side_effect = [mock_vacancy1, mock_vacancy2]
            
            result = Vacancy.cast_to_object_list(data)
            
            assert len(result) == 2
            assert result[0] == mock_vacancy1
            assert result[1] == mock_vacancy2
            assert mock_from_dict.call_count == 2

    @patch('logging.warning')
    def test_cast_to_object_list_with_error(self, mock_warning):
        """Тест обработки ошибки при преобразовании"""
        data = [
            {"title": "Job 1", "url": "http://job1.com"},
            {"invalid": "data"}
        ]
        
        with patch.object(Vacancy, 'from_dict') as mock_from_dict:
            mock_vacancy = Mock()
            mock_from_dict.side_effect = [mock_vacancy, ValueError("Invalid data")]
            
            result = Vacancy.cast_to_object_list(data)
            
            assert len(result) == 1
            assert result[0] == mock_vacancy
            mock_warning.assert_called()

    def test_from_dict_hh_vacancy(self):
        """Тест создания вакансии из данных HH"""
        data = {
            "id": "123",
            "name": "Python Developer",
            "alternate_url": "https://hh.ru/vacancy/123",
            "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
            "employer": {"name": "Test Company"},
            "experience": {"name": "От 1 года до 3 лет"},
            "employment": {"name": "Полная занятость"},
            "schedule": {"name": "Полный день"},
            "published_at": "2023-01-01T10:00:00+0300",
            "snippet": {
                "requirement": "Python experience",
                "responsibility": "Development tasks"
            }
        }
        
        vacancy = Vacancy.from_dict(data)
        
        assert vacancy.vacancy_id == "123"
        assert vacancy.title == "Python Developer"
        assert vacancy.url == "https://hh.ru/vacancy/123"
        assert vacancy.requirements == "Python experience"
        assert vacancy.responsibilities == "Development tasks"
        assert vacancy.source == "hh.ru"

    def test_from_dict_superjob_vacancy(self):
        """Тест создания вакансии из данных SuperJob"""
        data = {
            "id": "456",
            "profession": "Python Developer",
            "link": "https://superjob.ru/vacancy/456",
            "payment_from": 80000,
            "payment_to": 120000,
            "firm_name": "SJ Company",
            "candidat": "Python knowledge required",
            "work": "Backend development",
            "type_of_work": {"title": "Полная занятость"},
            "date_published": 1672574400
        }
        
        vacancy = Vacancy.from_dict(data)
        
        assert vacancy.vacancy_id == "456"
        assert vacancy.title == "Python Developer"
        assert vacancy.url == "https://superjob.ru/vacancy/456"
        assert vacancy.requirements == "Python knowledge required"
        assert vacancy.responsibilities == "Backend development"
        assert vacancy.source == "superjob.ru"

    def test_from_dict_minimal_data(self):
        """Тест создания вакансии с минимальными данными"""
        data = {"id": "789"}
        
        vacancy = Vacancy.from_dict(data)
        
        assert vacancy.vacancy_id == "789"
        assert vacancy.title == "Без названия"
        assert vacancy.url == ""
        assert vacancy.source == "unknown"

    def test_from_dict_description_fallback(self):
        """Тест fallback для описания"""
        data = {
            "id": "123",
            "title": "Test Job",
            "requirements": "Req text",
            "responsibilities": "Resp text"
        }
        
        vacancy = Vacancy.from_dict(data)
        
        assert "Req text" in vacancy.description
        assert "Resp text" in vacancy.description

    def test_from_dict_invalid_data_type(self):
        """Тест с неверным типом данных"""
        with pytest.raises(ValueError, match="Данные должны быть словарем"):
            Vacancy.from_dict("not a dict")

    @patch('logging.error')
    def test_from_dict_with_exception(self, mock_error):
        """Тест обработки исключения в from_dict"""
        data = {"id": "123"}
        
        with patch.object(Vacancy, '__init__', side_effect=Exception("Test error")):
            with pytest.raises(ValueError, match="Невозможно создать унифицированную вакансию"):
                Vacancy.from_dict(data)
        
        mock_error.assert_called()

    def test_to_dict(self):
        """Тест преобразования в словарь"""
        salary_data = {"from": 100000, "to": 150000}
        published_at = datetime(2023, 1, 1, 10, 0, 0)
        
        vacancy = Vacancy(
            vacancy_id="123",
            title="Test Job",
            url="http://test.com",
            salary=salary_data,
            description="Test desc",
            requirements="Test req",
            responsibilities="Test resp",
            employer={"name": "Test Co"},
            experience="1-3 years",
            employment="Full time",
            schedule="Full day",
            skills=[{"name": "Python"}],
            detailed_description="Detailed desc",
            benefits="Benefits",
            source="test"
        )
        vacancy.published_at = published_at
        
        result = vacancy.to_dict()
        
        assert result["id"] == "123"
        assert result["title"] == "Test Job"
        assert result["url"] == "http://test.com"
        assert result["description"] == "Test desc"
        assert result["requirements"] == "Test req"
        assert result["responsibilities"] == "Test resp"
        assert result["employer"] == {"name": "Test Co"}
        assert result["experience"] == "1-3 years"
        assert result["employment"] == "Full time"
        assert result["schedule"] == "Full day"
        assert result["skills"] == [{"name": "Python"}]
        assert result["detailed_description"] == "Detailed desc"
        assert result["benefits"] == "Benefits"
        assert result["source"] == "test"
        assert result["published_at"] == "2023-01-01T10:00:00"

    def test_to_dict_with_none_values(self):
        """Тест to_dict с None значениями"""
        vacancy = Vacancy(title="Test", url="http://test.com")
        
        result = vacancy.to_dict()
        
        # salary создается как пустой объект Salary, не None
        assert isinstance(result["salary"], dict)
        assert result["published_at"] is None
        assert result["employer"] is None

    def test_str_representation(self):
        """Тест строкового представления"""
        vacancy = Vacancy(
            title="Python Developer",
            url="http://test.com",
            employer={"name": "Test Company"},
            requirements="Python, Django experience required",
            source="hh.ru"
        )
        vacancy.salary = Mock()
        vacancy.salary.__str__ = Mock(return_value="100000-150000 RUR")
        
        result = str(vacancy)
        
        assert "[HH.RU] Должность: Python Developer" in result
        assert "Компания: Test Company" in result
        assert "Зарплата: 100000-150000 RUR" in result
        assert "Требования: Python, Django experience required..." in result
        assert "Ссылка: http://test.com" in result

    def test_str_representation_no_employer(self):
        """Тест строкового представления без работодателя"""
        vacancy = Vacancy(title="Test Job", url="http://test.com")
        
        result = str(vacancy)
        
        assert "Компания: Не указана" in result

    def test_str_representation_long_requirements(self):
        """Тест строкового представления с длинными требованиями"""
        long_req = "a" * 150
        vacancy = Vacancy(
            title="Test Job", 
            url="http://test.com",
            requirements=long_req
        )
        
        result = str(vacancy)
        
        assert "Требования: " + "a" * 100 + "..." in result

    def test_eq_same_vacancy(self):
        """Тест сравнения одинаковых вакансий"""
        vacancy1 = Vacancy(title="Test", url="http://test.com", vacancy_id="123")
        vacancy2 = Vacancy(title="Other", url="http://other.com", vacancy_id="123")
        
        assert vacancy1 == vacancy2

    def test_eq_different_vacancy(self):
        """Тест сравнения разных вакансий"""
        vacancy1 = Vacancy(title="Test", url="http://test.com", vacancy_id="123")
        vacancy2 = Vacancy(title="Test", url="http://test.com", vacancy_id="456")
        
        assert vacancy1 != vacancy2

    def test_eq_different_type(self):
        """Тест сравнения с другим типом"""
        vacancy = Vacancy(title="Test", url="http://test.com")
        
        assert vacancy != "not a vacancy"

    def test_lt_comparison(self):
        """Тест сравнения 'меньше'"""
        vacancy1 = Vacancy(title="Test1", url="http://test1.com")
        vacancy2 = Vacancy(title="Test2", url="http://test2.com")
        
        vacancy1.salary = Mock()
        vacancy1.salary.average = 50000
        vacancy2.salary = Mock()
        vacancy2.salary.average = 80000
        
        assert vacancy1 < vacancy2

    def test_lt_different_type(self):
        """Тест сравнения 'меньше' с другим типом"""
        vacancy = Vacancy(title="Test", url="http://test.com")
        
        result = vacancy.__lt__("not a vacancy")
        
        assert result == NotImplemented

    def test_le_comparison(self):
        """Тест сравнения 'меньше или равно'"""
        vacancy1 = Vacancy(title="Test1", url="http://test1.com")
        vacancy2 = Vacancy(title="Test2", url="http://test2.com")
        
        vacancy1.salary = Mock()
        vacancy1.salary.average = 50000
        vacancy2.salary = Mock()
        vacancy2.salary.average = 50000
        
        assert vacancy1 <= vacancy2

    def test_le_different_type(self):
        """Тест сравнения 'меньше или равно' с другим типом"""
        vacancy = Vacancy(title="Test", url="http://test.com")
        
        result = vacancy.__le__("not a vacancy")
        
        assert result == NotImplemented

    def test_gt_comparison(self):
        """Тест сравнения 'больше'"""
        vacancy1 = Vacancy(title="Test1", url="http://test1.com")
        vacancy2 = Vacancy(title="Test2", url="http://test2.com")
        
        vacancy1.salary = Mock()
        vacancy1.salary.average = 80000
        vacancy2.salary = Mock()
        vacancy2.salary.average = 50000
        
        assert vacancy1 > vacancy2

    def test_gt_different_type(self):
        """Тест сравнения 'больше' с другим типом"""
        vacancy = Vacancy(title="Test", url="http://test.com")
        
        result = vacancy.__gt__("not a vacancy")
        
        assert result == NotImplemented

    def test_ge_comparison(self):
        """Тест сравнения 'больше или равно'"""
        vacancy1 = Vacancy(title="Test1", url="http://test1.com")
        vacancy2 = Vacancy(title="Test2", url="http://test2.com")
        
        vacancy1.salary = Mock()
        vacancy1.salary.average = 80000
        vacancy2.salary = Mock()
        vacancy2.salary.average = 80000
        
        assert vacancy1 >= vacancy2

    def test_ge_different_type(self):
        """Тест сравнения 'больше или равно' с другим типом"""
        vacancy = Vacancy(title="Test", url="http://test.com")
        
        result = vacancy.__ge__("not a vacancy")
        
        assert result == NotImplemented

    def test_hash(self):
        """Тест хеширования"""
        vacancy = Vacancy(title="Test", url="http://test.com", vacancy_id="123")
        
        result = hash(vacancy)
        expected = hash("123")
        
        assert result == expected

    def test_slots_attributes(self):
        """Тест __slots__ атрибутов"""
        vacancy = Vacancy(title="Test", url="http://test.com")
        
        # Проверяем, что все слоты присутствуют
        expected_slots = [
            'vacancy_id', 'title', 'url', 'salary', 'description', 
            'requirements', 'responsibilities', 'employer', 'experience',
            'employment', 'schedule', 'published_at', 'skills',
            'detailed_description', 'benefits', 'source'
        ]
        
        for slot in expected_slots:
            assert hasattr(vacancy, slot)

    def test_html_cleaning_in_init(self):
        """Тест очистки HTML в конструкторе"""
        vacancy = Vacancy(
            title="Test",
            url="http://test.com",
            requirements="<p>Python <b>required</b></p>",
            responsibilities="<div>Development <i>tasks</i></div>"
        )
        
        assert vacancy.requirements == "Python required"
        assert vacancy.responsibilities == "Development tasks"

    def test_raw_data_initialization(self):
        """Тест инициализации raw_data"""
        vacancy = Vacancy(title="Test", url="http://test.com")
        
        assert vacancy.raw_data is None
        assert vacancy.profession is None
        assert vacancy.area is None

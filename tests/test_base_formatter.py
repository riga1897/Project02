from unittest.mock import Mock

import pytest

from src.utils.base_formatter import BaseFormatter


class ConcreteFormatter(BaseFormatter):
    """Конкретная реализация BaseFormatter для тестирования"""

    def format_vacancy_info(self, vacancy, number=None):
        lines = self._build_vacancy_lines(vacancy, number)
        return "\n".join(lines)


class TestBaseFormatter:

    def test_cannot_instantiate_abstract_class(self):
        """Тест что нельзя создать экземпляр абстрактного класса"""
        with pytest.raises(TypeError):
            BaseFormatter()

    def test_concrete_implementation_works(self):
        """Тест что конкретная реализация работает"""
        formatter = ConcreteFormatter()
        vacancy_mock = Mock()
        vacancy_mock.vacancy_id = "123"
        vacancy_mock.title = "Test Job"

        result = formatter.format_vacancy_info(vacancy_mock)
        assert "ID: 123" in result
        assert "Название: Test Job" in result

    def test_build_vacancy_lines(self):
        """Тест формирования строк вакансии"""
        vacancy_mock = Mock()
        vacancy_mock.vacancy_id = "123"
        vacancy_mock.title = "Test Job"
        vacancy_mock.employer = {"name": "Test Company"}
        vacancy_mock.salary = {"from": 100000, "currency": "RUR"}
        vacancy_mock.experience = "1-3 года"
        vacancy_mock.employment = "Полная занятость"
        vacancy_mock.source = "test.ru"
        vacancy_mock.url = "https://test.ru/vacancy/123"
        vacancy_mock.responsibilities = "Do work"
        vacancy_mock.requirements = "Be good"
        vacancy_mock.conditions = "Good office"

        result = BaseFormatter._build_vacancy_lines(vacancy_mock, 1)

        result_str = "\n".join(result)
        assert "1." in result_str
        assert "ID: 123" in result_str
        assert "Название: Test Job" in result_str
        assert "Компания: Test Company" in result_str
        assert "от 100 000 руб. в месяц" in result_str
        assert "Опыт: 1-3 года" in result_str
        assert "Занятость: Полная занятость" in result_str
        assert "Источник: test.ru" in result_str
        assert "Ссылка: https://test.ru/vacancy/123" in result_str
        assert "Обязанности: Do work" in result_str
        assert "Требования: Be good" in result_str
        assert "Условия: Good office" in result_str

    def test_build_vacancy_lines_without_number(self):
        """Тест формирования строк без номера"""
        vacancy_mock = Mock()
        vacancy_mock.vacancy_id = "456"
        vacancy_mock.title = "Another Job"
        vacancy_mock.employer = None
        vacancy_mock.salary = None
        vacancy_mock.experience = None
        vacancy_mock.employment = None
        vacancy_mock.source = None
        vacancy_mock.url = None
        vacancy_mock.responsibilities = None
        vacancy_mock.requirements = None
        vacancy_mock.conditions = None

        result = BaseFormatter._build_vacancy_lines(vacancy_mock)

        assert "1." not in result
        assert "ID: 456" in result
        assert "Название: Another Job" in result

    def test_extract_company_name_dict(self):
        """Тест извлечения названия компании из словаря"""
        vacancy_mock = Mock()
        vacancy_mock.employer = {"name": "Test Company"}

        result = BaseFormatter._extract_company_name(vacancy_mock)
        assert result == "Test Company"

    def test_extract_company_name_string(self):
        """Тест извлечения названия компании из строки"""
        vacancy_mock = Mock()
        vacancy_mock.employer = "String Company"

        result = BaseFormatter._extract_company_name(vacancy_mock)
        assert result == "String Company"

    def test_extract_company_name_none(self):
        """Тест извлечения названия компании когда employer = None"""
        vacancy_mock = Mock()
        vacancy_mock.employer = None

        result = BaseFormatter._extract_company_name(vacancy_mock)
        assert result is None

    def test_extract_salary_info_dict(self):
        """Тест извлечения зарплаты из словаря"""
        vacancy_mock = Mock()
        vacancy_mock.salary = {"from": 50000, "to": 80000, "currency": "RUR"}

        result = BaseFormatter._extract_salary_info(vacancy_mock)
        assert result == "от 50 000 до 80 000 руб. в месяц"

    def test_extract_salary_info_string(self):
        """Тест извлечения зарплаты из строки"""
        vacancy_mock = Mock()
        vacancy_mock.salary = "договорная"

        result = BaseFormatter._extract_salary_info(vacancy_mock)
        assert result == "договорная"

    def test_extract_salary_info_none(self):
        """Тест извлечения зарплаты когда salary = None"""
        vacancy_mock = Mock()
        vacancy_mock.salary = None

        result = BaseFormatter._extract_salary_info(vacancy_mock)
        assert result is None

    def test_format_salary_dict_from_to(self):
        """Тест форматирования зарплаты с from и to"""
        salary_dict = {"from": 100000, "to": 150000, "currency": "RUR"}

        result = BaseFormatter._format_salary_dict(salary_dict)
        assert result == "от 100 000 до 150 000 руб. в месяц"

    def test_format_salary_dict_from_only(self):
        """Тест форматирования зарплаты только с from"""
        salary_dict = {"from": 80000, "currency": "USD"}

        result = BaseFormatter._format_salary_dict(salary_dict)
        assert result == "от 80 000 долл. в месяц"

    def test_format_salary_dict_to_only(self):
        """Тест форматирования зарплаты только с to"""
        salary_dict = {"to": 120000, "currency": "EUR"}

        result = BaseFormatter._format_salary_dict(salary_dict)
        assert result == "до 120 000 евро в месяц"

    def test_format_salary_dict_empty(self):
        """Тест форматирования пустого словаря зарплаты"""
        result = BaseFormatter._format_salary_dict({})
        assert result == "Не указана"

    def test_format_salary_dict_none(self):
        """Тест форматирования None зарплаты"""
        result = BaseFormatter._format_salary_dict(None)
        assert result == "Не указана"

    def test_extract_responsibilities(self):
        """Тест извлечения обязанностей"""
        vacancy_mock = Mock()
        vacancy_mock.responsibilities = "Test responsibilities"

        result = BaseFormatter._extract_responsibilities(vacancy_mock)
        assert result == "Test responsibilities"

    def test_extract_requirements(self):
        """Тест извлечения требований"""
        vacancy_mock = Mock()
        vacancy_mock.requirements = "Test requirements"

        result = BaseFormatter._extract_requirements(vacancy_mock)
        assert result == "Test requirements"

    def test_extract_conditions_direct(self):
        """Тест извлечения условий напрямую"""
        vacancy_mock = Mock()
        vacancy_mock.conditions = "Test conditions"
        vacancy_mock.schedule = None

        result = BaseFormatter._extract_conditions(vacancy_mock)
        assert result == "Test conditions"

    def test_extract_conditions_from_schedule(self):
        """Тест извлечения условий из графика работы"""
        vacancy_mock = Mock()
        vacancy_mock.conditions = None
        vacancy_mock.schedule = "Полный день"

        result = BaseFormatter._extract_conditions(vacancy_mock)
        assert result == "График: Полный день"

    def test_long_text_truncation(self):
        """Тест обрезания длинного текста"""
        vacancy_mock = Mock()
        vacancy_mock.vacancy_id = "123"
        vacancy_mock.title = "Test Job"
        vacancy_mock.employer = None
        vacancy_mock.salary = None
        vacancy_mock.experience = None
        vacancy_mock.employment = None
        vacancy_mock.source = None
        vacancy_mock.url = None
        vacancy_mock.responsibilities = "A" * 200  # Длинная строка
        vacancy_mock.requirements = "B" * 200
        vacancy_mock.conditions = "C" * 200

        result = BaseFormatter._build_vacancy_lines(vacancy_mock)

        # Проверяем что текст обрезан
        responsibilities_line = next(line for line in result if "Обязанности:" in line)
        requirements_line = next(line for line in result if "Требования:" in line)
        conditions_line = next(line for line in result if "Условия:" in line)

        assert len(responsibilities_line) <= 167  # 150 символов + "Обязанности: " (13 симв.) + "..." (3 симв.)
        assert len(requirements_line) <= 166  # 150 символов + "Требования: " (12 симв.) + "..." (3 симв.)
        assert len(conditions_line) <= 164  # 150 символов + "Условия: " (9 симв.) + "..." (3 симв.)
        assert responsibilities_line.endswith("...")
        assert requirements_line.endswith("...")
        assert conditions_line.endswith("...")

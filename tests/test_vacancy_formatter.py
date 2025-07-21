from unittest.mock import Mock, patch

from src.utils.vacancy_formatter import VacancyFormatter, vacancy_formatter
from src.vacancies.models import Vacancy


class TestVacancyFormatter:

    def test_extract_responsibilities(self):
        """Тест извлечения обязанностей"""
        vacancy = Mock()
        vacancy.responsibilities = "Test responsibilities"

        result = VacancyFormatter._extract_responsibilities(vacancy)
        assert result == "Test responsibilities"

    def test_extract_responsibilities_none(self):
        """Тест извлечения обязанностей когда None"""
        vacancy = Mock()
        vacancy.responsibilities = None

        result = VacancyFormatter._extract_responsibilities(vacancy)
        assert result is None

    def test_extract_requirements(self):
        """Тест извлечения требований"""
        vacancy = Mock()
        vacancy.requirements = "Test requirements"

        result = VacancyFormatter._extract_requirements(vacancy)
        assert result == "Test requirements"

    def test_extract_requirements_none(self):
        """Тест извлечения требований когда None"""
        vacancy = Mock()
        vacancy.requirements = None

        result = VacancyFormatter._extract_requirements(vacancy)
        assert result is None

    def test_extract_conditions_with_schedule(self):
        """Тест извлечения условий с графиком работы"""
        vacancy = Mock()
        vacancy.schedule = "Полный день"
        vacancy.source = "hh.ru"

        result = VacancyFormatter._extract_conditions(vacancy)
        assert result == "График: Полный день"

    def test_extract_conditions_without_schedule(self):
        """Тест извлечения условий без графика"""
        vacancy = Mock()
        vacancy.schedule = None
        vacancy.source = "hh.ru"

        result = VacancyFormatter._extract_conditions(vacancy)
        assert result is None

    def test_extract_conditions_superjob_source(self):
        """Тест извлечения условий для SuperJob"""
        vacancy = Mock()
        vacancy.schedule = "Гибкий график"
        vacancy.source = "superjob.ru"

        result = VacancyFormatter._extract_conditions(vacancy)
        assert result == "График: Гибкий график"

    def test_format_vacancy_info_with_number(self):
        """Тест форматирования информации о вакансии с номером"""
        vacancy = Mock(spec=Vacancy)
        vacancy.vacancy_id = "123"
        vacancy.title = "Python Developer"

        with patch.object(
            VacancyFormatter, "_build_vacancy_lines", return_value=["1.", "ID: 123", "Название: Python Developer"]
        ) as mock_build:
            result = VacancyFormatter.format_vacancy_info(vacancy, 1)

        mock_build.assert_called_once_with(vacancy, 1)
        assert result == "1.\nID: 123\nНазвание: Python Developer\n"

    def test_format_vacancy_info_without_number(self):
        """Тест форматирования информации о вакансии без номера"""
        vacancy = Mock(spec=Vacancy)

        with patch.object(VacancyFormatter, "_build_vacancy_lines", return_value=["ID: 456"]) as mock_build:
            result = VacancyFormatter.format_vacancy_info(vacancy)

        mock_build.assert_called_once_with(vacancy, None)
        assert result == "ID: 456\n"

    @patch("builtins.print")
    def test_display_vacancy_info_with_number(self, mock_print):
        """Тест отображения информации о вакансии с номером"""
        vacancy = Mock(spec=Vacancy)

        with patch.object(VacancyFormatter, "_build_vacancy_lines", return_value=["1.", "ID: 123"]) as mock_build:
            VacancyFormatter.display_vacancy_info(vacancy, 1)

        mock_build.assert_called_once_with(vacancy, 1)
        mock_print.assert_any_call("1.")
        mock_print.assert_any_call("ID: 123")
        mock_print.assert_any_call()

    @patch("builtins.print")
    def test_display_vacancy_info_without_number(self, mock_print):
        """Тест отображения информации о вакансии без номера"""
        vacancy = Mock(spec=Vacancy)

        with patch.object(VacancyFormatter, "_build_vacancy_lines", return_value=["ID: 456"]) as mock_build:
            VacancyFormatter.display_vacancy_info(vacancy)

        mock_build.assert_called_once_with(vacancy, None)
        mock_print.assert_any_call("ID: 456")
        mock_print.assert_any_call()

    def test_format_salary_none(self):
        """Тест форматирования пустой зарплаты"""
        result = VacancyFormatter.format_salary(None)
        assert result == "Зарплата не указана"

    def test_format_salary_dict(self):
        """Тест форматирования зарплаты из словаря"""
        salary_info = {"from": 50000, "to": 100000, "currency": "RUR"}

        with patch.object(
            VacancyFormatter, "_format_salary_dict", return_value="от 50000 до 100000 RUR"
        ) as mock_format:
            result = VacancyFormatter.format_salary(salary_info)

        mock_format.assert_called_once_with(salary_info)
        assert result == "от 50000 до 100000 RUR"

    def test_format_salary_string(self):
        """Тест форматирования зарплаты из строки"""
        result = VacancyFormatter.format_salary("100000 руб")
        assert result == "100000 руб"

    def test_build_vacancy_lines_full_info(self):
        """Тест построения полной информации о вакансии"""
        vacancy = Mock(spec=Vacancy)
        vacancy.vacancy_id = "123"
        vacancy.title = "Python Developer"
        vacancy.employer = {"name": "Test Company"}
        vacancy.salary = Mock()
        vacancy.salary.__str__ = Mock(return_value="100000 руб")
        vacancy.experience = "От 1 года"
        vacancy.employment = "Полная занятость"
        vacancy.source = "hh.ru"
        vacancy.url = "https://api.hh.ru/vacancies/123"
        vacancy.description = "Test description"
        vacancy.detailed_description = None
        vacancy.responsibilities = "Development tasks"
        vacancy.requirements = "Python knowledge"
        vacancy.schedule = "Полный день"

        with (
            patch.object(VacancyFormatter, "_extract_responsibilities", return_value="Development tasks"),
            patch.object(VacancyFormatter, "_extract_requirements", return_value="Python knowledge"),
            patch.object(VacancyFormatter, "_extract_conditions", return_value="График: Полный день"),
        ):

            result = VacancyFormatter._build_vacancy_lines(vacancy, 1)

        result_str = "\n".join(result)
        assert "1." in result_str
        assert "ID: 123" in result_str
        assert "Название: Python Developer" in result_str
        assert "Компания: Test Company" in result_str
        assert "Зарплата: 100000 руб" in result_str
        assert "Опыт: От 1 года" in result_str
        assert "Занятость: Полная занятость" in result_str
        assert "Источник: hh.ru" in result_str
        assert "Ссылка: https://hh.ru/vacancy/123" in result_str
        assert "Описание вакансии:" in result_str

    def test_build_vacancy_lines_minimal_info(self):
        """Тест построения минимальной информации о вакансии"""
        vacancy = Mock(spec=Vacancy)
        vacancy.vacancy_id = "456"
        vacancy.title = None
        vacancy.name = "Job Title"
        vacancy.employer = None
        vacancy.salary = None
        vacancy.experience = None
        vacancy.employment = None
        vacancy.source = "Не указан"
        vacancy.url = "Не указана"
        vacancy.description = None
        vacancy.detailed_description = None
        vacancy.responsibilities = None
        vacancy.requirements = None
        vacancy.schedule = None

        with (
            patch.object(VacancyFormatter, "_extract_responsibilities", return_value=None),
            patch.object(VacancyFormatter, "_extract_requirements", return_value=None),
            patch.object(VacancyFormatter, "_extract_conditions", return_value=None),
        ):

            result = VacancyFormatter._build_vacancy_lines(vacancy)

        result_str = "\n".join(result)
        assert "ID: 456" in result_str
        assert "Название: Job Title" in result_str
        assert "Компания: Не указана" in result_str
        assert "Зарплата: Не указана" in result_str
        assert "Описание вакансии: Описание отсутствует" in result_str

    def test_build_vacancy_lines_with_long_description(self):
        """Тест построения с длинным описанием"""
        vacancy = Mock(spec=Vacancy)
        vacancy.vacancy_id = "789"
        vacancy.title = "Test Job"
        vacancy.employer = None
        vacancy.salary = None
        vacancy.experience = None
        vacancy.employment = None
        vacancy.source = "test"
        vacancy.url = "http://test.com"
        vacancy.description = "A" * 200  # Длинное описание
        vacancy.detailed_description = None
        vacancy.responsibilities = None
        vacancy.requirements = None
        vacancy.schedule = None

        with (
            patch.object(VacancyFormatter, "_extract_responsibilities", return_value=None),
            patch.object(VacancyFormatter, "_extract_requirements", return_value=None),
            patch.object(VacancyFormatter, "_extract_conditions", return_value=None),
        ):

            result = VacancyFormatter._build_vacancy_lines(vacancy)

        result_str = "\n".join(result)
        assert "Описание вакансии:" in result_str
        assert "..." in result_str  # Проверяем обрезание

    def test_build_vacancy_lines_with_html_in_description(self):
        """Тест построения с HTML тегами в описании"""
        vacancy = Mock(spec=Vacancy)
        vacancy.vacancy_id = "101"
        vacancy.title = "Web Developer"
        vacancy.employer = None
        vacancy.salary = None
        vacancy.experience = None
        vacancy.employment = None
        vacancy.source = "test"
        vacancy.url = "http://test.com"
        vacancy.description = "<p>Test <b>description</b> with HTML</p>"
        vacancy.detailed_description = None
        vacancy.responsibilities = None
        vacancy.requirements = None
        vacancy.schedule = None

        with (
            patch.object(VacancyFormatter, "_extract_responsibilities", return_value=None),
            patch.object(VacancyFormatter, "_extract_requirements", return_value=None),
            patch.object(VacancyFormatter, "_extract_conditions", return_value=None),
        ):

            result = VacancyFormatter._build_vacancy_lines(vacancy)

        result_str = "\n".join(result)
        assert "Test description with HTML" in result_str
        assert "<p>" not in result_str
        assert "<b>" not in result_str

    def test_build_vacancy_lines_with_detailed_description_fallback(self):
        """Тест использования detailed_description при отсутствии description"""
        vacancy = Mock(spec=Vacancy)
        vacancy.vacancy_id = "202"
        vacancy.title = "Test Job"
        vacancy.employer = None
        vacancy.salary = None
        vacancy.experience = None
        vacancy.employment = None
        vacancy.source = "test"
        vacancy.url = "http://test.com"
        vacancy.description = ""
        vacancy.detailed_description = "Detailed job description"
        vacancy.responsibilities = None
        vacancy.requirements = None
        vacancy.schedule = None

        with (
            patch.object(VacancyFormatter, "_extract_responsibilities", return_value=None),
            patch.object(VacancyFormatter, "_extract_requirements", return_value=None),
            patch.object(VacancyFormatter, "_extract_conditions", return_value=None),
        ):

            result = VacancyFormatter._build_vacancy_lines(vacancy)

        result_str = "\n".join(result)
        assert "Detailed job description" in result_str

    def test_build_vacancy_lines_with_long_responsibilities(self):
        """Тест с длинными обязанностями"""
        vacancy = Mock(spec=Vacancy)
        vacancy.vacancy_id = "303"
        vacancy.title = "Test Job"
        vacancy.employer = None
        vacancy.salary = None
        vacancy.experience = None
        vacancy.employment = None
        vacancy.source = "test"
        vacancy.url = "http://test.com"
        vacancy.description = None
        vacancy.detailed_description = None
        vacancy.responsibilities = None
        vacancy.requirements = None
        vacancy.schedule = None

        long_resp = "A" * 200
        with (
            patch.object(VacancyFormatter, "_extract_responsibilities", return_value=long_resp),
            patch.object(VacancyFormatter, "_extract_requirements", return_value=None),
            patch.object(VacancyFormatter, "_extract_conditions", return_value=None),
        ):

            result = VacancyFormatter._build_vacancy_lines(vacancy)

        result_str = "\n".join(result)
        assert "Обязанности:" in result_str
        assert "..." in result_str

    def test_build_vacancy_lines_with_long_requirements(self):
        """Тест с длинными требованиями"""
        vacancy = Mock(spec=Vacancy)
        vacancy.vacancy_id = "404"
        vacancy.title = "Test Job"
        vacancy.employer = None
        vacancy.salary = None
        vacancy.experience = None
        vacancy.employment = None
        vacancy.source = "test"
        vacancy.url = "http://test.com"
        vacancy.description = None
        vacancy.detailed_description = None
        vacancy.responsibilities = None
        vacancy.requirements = None
        vacancy.schedule = None

        long_req = "B" * 200
        with (
            patch.object(VacancyFormatter, "_extract_responsibilities", return_value=None),
            patch.object(VacancyFormatter, "_extract_requirements", return_value=long_req),
            patch.object(VacancyFormatter, "_extract_conditions", return_value=None),
        ):

            result = VacancyFormatter._build_vacancy_lines(vacancy)

        result_str = "\n".join(result)
        assert "Требования:" in result_str
        assert "..." in result_str

    def test_build_vacancy_lines_with_long_conditions(self):
        """Тест с длинными условиями"""
        vacancy = Mock(spec=Vacancy)
        vacancy.vacancy_id = "505"
        vacancy.title = "Test Job"
        vacancy.employer = None
        vacancy.salary = None
        vacancy.experience = None
        vacancy.employment = None
        vacancy.source = "test"
        vacancy.url = "http://test.com"
        vacancy.description = None
        vacancy.detailed_description = None
        vacancy.responsibilities = None
        vacancy.requirements = None
        vacancy.schedule = None

        long_cond = "C" * 150
        with (
            patch.object(VacancyFormatter, "_extract_responsibilities", return_value=None),
            patch.object(VacancyFormatter, "_extract_requirements", return_value=None),
            patch.object(VacancyFormatter, "_extract_conditions", return_value=long_cond),
        ):

            result = VacancyFormatter._build_vacancy_lines(vacancy)

        result_str = "\n".join(result)
        assert "Условия:" in result_str
        assert "..." in result_str

    def test_build_vacancy_lines_with_very_long_combined_description(self):
        """Тест с очень длинным комбинированным описанием"""
        vacancy = Mock(spec=Vacancy)
        vacancy.vacancy_id = "606"
        vacancy.title = "Test Job"
        vacancy.employer = None
        vacancy.salary = None
        vacancy.experience = None
        vacancy.employment = None
        vacancy.source = "test"
        vacancy.url = "http://test.com"
        vacancy.description = "D" * 100
        vacancy.detailed_description = None
        vacancy.responsibilities = None
        vacancy.requirements = None
        vacancy.schedule = None

        long_resp = "E" * 100
        long_req = "F" * 100
        long_cond = "G" * 100

        with (
            patch.object(VacancyFormatter, "_extract_responsibilities", return_value=long_resp),
            patch.object(VacancyFormatter, "_extract_requirements", return_value=long_req),
            patch.object(VacancyFormatter, "_extract_conditions", return_value=long_cond),
        ):

            result = VacancyFormatter._build_vacancy_lines(vacancy)

        result_str = "\n".join(result)
        assert "Описание вакансии:" in result_str
        # Проверяем что общее описание обрезано
        description_line = [line for line in result if "Описание вакансии:" in line][0]
        assert len(description_line) <= 450  # 400 символов + заголовок + ...

    def test_format_company_info_none(self):
        """Тест форматирования информации о компании когда None"""
        result = VacancyFormatter.format_company_info(None)
        assert result == "Не указана"

    def test_format_company_info_dict(self):
        """Тест форматирования информации о компании из словаря"""
        employer_info = {"name": "Test Company"}
        result = VacancyFormatter.format_company_info(employer_info)
        assert result == "Test Company"

    def test_format_company_info_dict_no_name(self):
        """Тест форматирования информации о компании из словаря без name"""
        employer_info = {"title": "Some Company"}
        result = VacancyFormatter.format_company_info(employer_info)
        assert result == "Не указана"

    def test_format_company_info_string(self):
        """Тест форматирования информации о компании из строки"""
        result = VacancyFormatter.format_company_info("String Company")
        assert result == "String Company"

    def test_format_salary_dict_from_to_currency(self):
        """Тест форматирования зарплаты с from, to и currency"""
        salary_info = {"from": 50000, "to": 100000, "currency": "RUR"}
        result = VacancyFormatter._format_salary_dict(salary_info)
        assert result == "от 50000 до 100000 RUR"

    def test_format_salary_dict_only_from(self):
        """Тест форматирования зарплаты только с from"""
        salary_info = {"from": 75000, "currency": "USD"}
        result = VacancyFormatter._format_salary_dict(salary_info)
        assert result == "от 75000 USD"

    def test_format_salary_dict_only_to(self):
        """Тест форматирования зарплаты только с to"""
        salary_info = {"to": 90000, "currency": "EUR"}
        result = VacancyFormatter._format_salary_dict(salary_info)
        assert result == "до 90000 EUR"

    def test_format_salary_dict_no_values(self):
        """Тест форматирования зарплаты без значений"""
        salary_info = {"currency": "RUR"}
        result = VacancyFormatter._format_salary_dict(salary_info)
        assert result == "RUR"

    def test_format_salary_dict_empty(self):
        """Тест форматирования пустого словаря зарплаты"""
        result = VacancyFormatter._format_salary_dict({})
        assert result == "Зарплата не указана"

    def test_global_vacancy_formatter_instance(self):
        """Тест глобального экземпляра форматтера"""
        assert isinstance(vacancy_formatter, VacancyFormatter)

    def test_build_vacancy_lines_employer_string(self):
        """Тест с работодателем в виде строки"""
        vacancy = Mock(spec=Vacancy)
        vacancy.vacancy_id = "707"
        vacancy.title = "Test Job"
        vacancy.employer = "String Employer"
        vacancy.salary = None
        vacancy.experience = None
        vacancy.employment = None
        vacancy.source = "test"
        vacancy.url = "http://test.com"
        vacancy.description = None
        vacancy.detailed_description = None
        vacancy.responsibilities = None
        vacancy.requirements = None
        vacancy.schedule = None

        with (
            patch.object(VacancyFormatter, "_extract_responsibilities", return_value=None),
            patch.object(VacancyFormatter, "_extract_requirements", return_value=None),
            patch.object(VacancyFormatter, "_extract_conditions", return_value=None),
        ):

            result = VacancyFormatter._build_vacancy_lines(vacancy)

        result_str = "\n".join(result)
        assert "Компания: String Employer" in result_str

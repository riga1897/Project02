from unittest.mock import Mock, patch

from src.utils.ui_helpers import (
    confirm_action,
    debug_search_vacancies,
    debug_vacancy_search,
    display_vacancy_info,
    filter_vacancies_by_keyword,
    filter_vacancies_by_max_salary,
    filter_vacancies_by_min_salary,
    filter_vacancies_by_multiple_keywords,
    filter_vacancies_by_salary_range,
    get_positive_integer,
    get_user_input,
    get_vacancies_with_salary,
    parse_salary_range,
    search_vacancies_advanced,
    sort_vacancies_by_salary,
)
from src.vacancies.models import Vacancy


class TestGetUserInput:
    """Тесты для функции получения пользовательского ввода"""

    @patch("builtins.input", return_value="test input")
    def test_get_user_input_valid(self, mock_input):
        """Тест корректного ввода"""
        result = get_user_input("Enter text: ")
        assert result == "test input"
        mock_input.assert_called_once_with("Enter text: ")

    @patch("builtins.input", return_value="  test input  ")
    def test_get_user_input_with_spaces(self, mock_input):
        """Тест ввода с пробелами"""
        result = get_user_input("Enter text: ")
        assert result == "test input"

    @patch("builtins.input", return_value="")
    def test_get_user_input_empty_not_required(self, mock_input):
        """Тест пустого ввода когда поле не обязательно"""
        result = get_user_input("Enter text: ", required=False)
        assert result is None

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["", "valid input"])
    def test_get_user_input_empty_required(self, mock_input, mock_print):
        """Тест пустого ввода когда поле обязательно"""
        result = get_user_input("Enter text: ", required=True)
        assert result == "valid input"
        mock_print.assert_called_once_with("Поле не может быть пустым!")


class TestGetPositiveInteger:
    """Тесты для функции получения положительного числа"""

    @patch("builtins.input", return_value="5")
    def test_get_positive_integer_valid(self, mock_input):
        """Тест корректного положительного числа"""
        result = get_positive_integer("Enter number: ")
        assert result == 5

    @patch("builtins.print")
    @patch("builtins.input", return_value="0")
    def test_get_positive_integer_zero(self, mock_input, mock_print):
        """Тест нулевого значения"""
        result = get_positive_integer("Enter number: ")
        assert result is None
        mock_print.assert_called_once_with("Число должно быть положительным!")

    @patch("builtins.print")
    @patch("builtins.input", return_value="-5")
    def test_get_positive_integer_negative(self, mock_input, mock_print):
        """Тест отрицательного числа"""
        result = get_positive_integer("Enter number: ")
        assert result is None
        mock_print.assert_called_once_with("Число должно быть положительным!")

    @patch("builtins.print")
    @patch("builtins.input", return_value="abc")
    def test_get_positive_integer_invalid(self, mock_input, mock_print):
        """Тест некорректного ввода"""
        result = get_positive_integer("Enter number: ")
        assert result is None
        mock_print.assert_called_once_with("Введите корректное число!")


class TestParseSalaryRange:
    """Тесты для функции парсинга диапазона зарплат"""

    def test_parse_salary_range_with_spaces(self):
        """Тест парсинга с пробелами вокруг тире"""
        result = parse_salary_range("100000 - 150000")
        assert result == (100000, 150000)

    def test_parse_salary_range_without_spaces(self):
        """Тест парсинга без пробелов"""
        result = parse_salary_range("100000-150000")
        assert result == (100000, 150000)

    def test_parse_salary_range_reversed(self):
        """Тест парсинга с обратным порядком"""
        result = parse_salary_range("150000 - 100000")
        assert result == (100000, 150000)

    @patch("builtins.print")
    def test_parse_salary_range_invalid_format(self, mock_print):
        """Тест некорректного формата"""
        result = parse_salary_range("100000")
        assert result is None
        mock_print.assert_called_once_with("Неверный формат диапазона. Используйте формат: 100000 - 150000")

    @patch("builtins.print")
    def test_parse_salary_range_invalid_numbers(self, mock_print):
        """Тест некорректных чисел"""
        result = parse_salary_range("abc - def")
        assert result is None
        mock_print.assert_called_once_with("Введите корректные числа!")


class TestConfirmAction:
    """Тесты для функции подтверждения действия"""

    @patch("builtins.input", return_value="y")
    def test_confirm_action_yes_short(self, mock_input):
        """Тест подтверждения 'y'"""
        result = confirm_action("Confirm?")
        assert result is True

    @patch("builtins.input", return_value="yes")
    def test_confirm_action_yes_full(self, mock_input):
        """Тест подтверждения 'yes'"""
        result = confirm_action("Confirm?")
        assert result is True

    @patch("builtins.input", return_value="да")
    def test_confirm_action_yes_russian(self, mock_input):
        """Тест подтверждения 'да'"""
        result = confirm_action("Confirm?")
        assert result is True

    @patch("builtins.input", return_value="n")
    def test_confirm_action_no_short(self, mock_input):
        """Тест отказа 'n'"""
        result = confirm_action("Confirm?")
        assert result is False

    @patch("builtins.input", return_value="no")
    def test_confirm_action_no_full(self, mock_input):
        """Тест отказа 'no'"""
        result = confirm_action("Confirm?")
        assert result is False

    @patch("builtins.input", return_value="нет")
    def test_confirm_action_no_russian(self, mock_input):
        """Тест отказа 'нет'"""
        result = confirm_action("Confirm?")
        assert result is False

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["invalid", "y"])
    def test_confirm_action_invalid_then_valid(self, mock_input, mock_print):
        """Тест некорректного ввода, затем корректного"""
        result = confirm_action("Confirm?")
        assert result is True
        mock_print.assert_called_once_with("Введите 'y' для да или 'n' для нет.")


class TestFilterVacanciesByKeyword:
    """Тесты для функции фильтрации вакансий по ключевому слову"""

    def test_filter_by_vacancy_id(self):
        """Тест фильтрации по ID вакансии"""
        vacancy = Vacancy(vacancy_id="123", title="Test", url="http://test.com")
        vacancies = [vacancy]

        result = filter_vacancies_by_keyword(vacancies, "123")
        assert len(result) == 1
        assert result[0].vacancy_id == "123"
        assert result[0]._relevance_score == 15

    def test_filter_by_title(self):
        """Тест фильтрации по заголовку"""
        vacancy = Vacancy(vacancy_id="1", title="Python Developer", url="http://test.com")
        vacancies = [vacancy]

        result = filter_vacancies_by_keyword(vacancies, "python")
        assert len(result) == 1
        assert result[0]._relevance_score == 10

    def test_filter_by_requirements(self):
        """Тест фильтрации по требованиям"""
        vacancy = Vacancy(vacancy_id="1", title="Dev", url="http://test.com", requirements="Python required")
        vacancies = [vacancy]

        result = filter_vacancies_by_keyword(vacancies, "python")
        assert len(result) == 1
        assert result[0]._relevance_score == 5

    def test_filter_by_responsibilities(self):
        """Тест фильтрации по обязанностям"""
        vacancy = Vacancy(vacancy_id="1", title="Dev", url="http://test.com", responsibilities="Develop Python apps")
        vacancies = [vacancy]

        result = filter_vacancies_by_keyword(vacancies, "python")
        assert len(result) == 1
        assert result[0]._relevance_score == 5

    def test_filter_by_description(self):
        """Тест фильтрации по описанию"""
        vacancies = [
            Vacancy(vacancy_id="1", title="Other", url="http://test1.com", description="Python development"),
            Vacancy(vacancy_id="2", title="Java Developer", url="http://test2.com", description="Java programming"),
        ]

        result = filter_vacancies_by_keyword(vacancies, "python")

        assert len(result) == 1
        assert result[0].vacancy_id == "1"
        assert result[0]._relevance_score == 5

    def test_filter_by_detailed_description(self):
        """Тест фильтрации по детальному описанию"""
        vacancy = Vacancy(vacancy_id="1", title="Dev", url="http://test.com", detailed_description="Python backend")
        vacancies = [vacancy]

        result = filter_vacancies_by_keyword(vacancies, "python")
        assert len(result) == 1
        assert result[0]._relevance_score == 2

    def test_filter_by_skills_dict(self):
        """Тест фильтрации по навыкам в формате словаря"""
        vacancy = Vacancy(vacancy_id="1", title="Dev", url="http://test.com", skills=[{"name": "Python"}])
        vacancies = [vacancy]

        result = filter_vacancies_by_keyword(vacancies, "python")
        assert len(result) == 1
        assert result[0]._relevance_score == 6

    def test_filter_by_skills_string(self):
        """Тест фильтрации по навыкам в строковом формате"""
        vacancy = Vacancy(vacancy_id="1", title="Dev", url="http://test.com", skills=["Python"])
        vacancies = [vacancy]

        result = filter_vacancies_by_keyword(vacancies, "python")
        assert len(result) == 1
        assert result[0]._relevance_score == 6

    def test_filter_by_employer(self):
        """Тест фильтрации по работодателю"""
        vacancy = Vacancy(vacancy_id="1", title="Dev", url="http://test.com", employer={"name": "Python Corp"})
        vacancies = [vacancy]

        result = filter_vacancies_by_keyword(vacancies, "python")
        assert len(result) == 1
        assert result[0]._relevance_score == 4

    def test_filter_by_employment(self):
        """Тест фильтрации по типу занятости"""
        vacancy = Vacancy(vacancy_id="1", title="Dev", url="http://test.com", employment="Python developer")
        vacancies = [vacancy]

        result = filter_vacancies_by_keyword(vacancies, "python")
        assert len(result) == 1
        assert result[0]._relevance_score == 3

    def test_filter_by_schedule(self):
        """Тест фильтрации по графику"""
        vacancy = Vacancy(vacancy_id="1", title="Dev", url="http://test.com", schedule="Python shifts")
        vacancies = [vacancy]

        result = filter_vacancies_by_keyword(vacancies, "python")
        assert len(result) == 1
        assert result[0]._relevance_score == 3

    def test_filter_by_experience(self):
        """Тест фильтрации по опыту"""
        vacancy = Vacancy(vacancy_id="1", title="Dev", url="http://test.com", experience="Python experience")
        vacancies = [vacancy]

        result = filter_vacancies_by_keyword(vacancies, "python")
        assert len(result) == 1
        assert result[0]._relevance_score == 3

    def test_filter_by_benefits(self):
        """Тест фильтрации по льготам"""
        vacancy = Vacancy(vacancy_id="1", title="Dev", url="http://test.com", benefits="Python training")
        vacancies = [vacancy]

        result = filter_vacancies_by_keyword(vacancies, "python")
        assert len(result) == 1
        assert result[0]._relevance_score == 2

    def test_filter_no_matches(self):
        """Тест когда нет совпадений"""
        vacancy = Vacancy(vacancy_id="1", title="Java Dev", url="http://test.com")
        vacancies = [vacancy]

        result = filter_vacancies_by_keyword(vacancies, "python")
        assert len(result) == 0

    def test_filter_sort_by_relevance(self):
        """Тест сортировки по релевантности"""
        vacancy1 = Vacancy(vacancy_id="1", title="Dev", url="http://test1.com", description="Python")  # score 3
        vacancy2 = Vacancy(vacancy_id="2", title="Python Dev", url="http://test2.com")  # score 10
        vacancies = [vacancy1, vacancy2]

        result = filter_vacancies_by_keyword(vacancies, "python")
        assert len(result) == 2
        assert result[0].vacancy_id == "2"  # Больший score должен быть первым
        assert result[1].vacancy_id == "1"


class TestDebugVacancySearch:
    """Тесты для функции отладки поиска по вакансии"""

    @patch("builtins.print")
    def test_debug_vacancy_search_full_info(self, mock_print):
        """Тест отладки с полной информацией о вакансии"""
        vacancy = Vacancy(
            vacancy_id="123",
            title="Python Developer",
            url="http://test.com",
            description="Develop Python applications",
            requirements="Python skills required",
            responsibilities="Code in Python",
            skills=["Python"],
            employer={"name": "Tech Corp"},
            experience="2 years",
            employment="Full-time",
            schedule="9-6",
            benefits="Health insurance",
        )

        debug_vacancy_search(vacancy, "python")

        # Проверяем что вызывался print
        assert mock_print.called
        print_calls = [call[0][0] for call in mock_print.call_args_list]

        # Проверяем основные элементы в выводе
        assert any("Python Developer" in call for call in print_calls)
        assert any("123" in call for call in print_calls)
        assert any("заголовок" in call for call in print_calls)

    @patch("builtins.print")
    def test_debug_vacancy_search_no_matches(self, mock_print):
        """Тест отладки без совпадений"""
        vacancy = Vacancy(vacancy_id="123", title="Java Developer", url="http://test.com")

        debug_vacancy_search(vacancy, "python")

        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("НИГДЕ" in call for call in print_calls)


class TestDebugSearchVacancies:
    """Тесты для функции отладки поиска по всем вакансиям"""

    @patch("builtins.print")
    @patch("src.utils.ui_helpers.debug_vacancy_search")
    def test_debug_search_vacancies(self, mock_debug_vacancy, mock_print):
        """Тест отладки поиска по всем вакансиям"""
        vacancies = [
            Vacancy(vacancy_id="1", title="Python Dev", url="http://test1.com"),
            Vacancy(vacancy_id="2", title="Java Dev", url="http://test2.com"),
        ]

        debug_search_vacancies(vacancies, "python")

        # Проверяем что выводится общая информация
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("Всего вакансий: 2" in call for call in print_calls)
        assert any("python" in call for call in print_calls)

        # Проверяем что вызывается debug для каждой вакансии (максимум 5)
        assert mock_debug_vacancy.call_count == 2


class TestDisplayVacancyInfo:
    """Тесты для функции отображения информации о вакансии"""

    @patch("src.utils.ui_helpers.vacancy_formatter.display_vacancy_info")
    def test_display_vacancy_info(self, mock_display):
        """Тест отображения информации о вакансии"""
        vacancy = Vacancy(vacancy_id="123", title="Test", url="http://test.com")

        display_vacancy_info(vacancy, 1)

        mock_display.assert_called_once_with(vacancy, 1)

    @patch("src.utils.ui_helpers.vacancy_formatter.display_vacancy_info")
    def test_display_vacancy_info_no_number(self, mock_display):
        """Тест отображения без номера"""
        vacancy = Vacancy(vacancy_id="123", title="Test", url="http://test.com")

        display_vacancy_info(vacancy)

        mock_display.assert_called_once_with(vacancy, None)


class TestDeprecatedFunctions:
    """Тесты для устаревших функций (обратная совместимость)"""

    @patch("src.utils.ui_helpers.VacancyOperations.filter_vacancies_by_min_salary")
    def test_filter_vacancies_by_min_salary(self, mock_filter):
        """Тест устаревшей функции фильтрации по минимальной зарплате"""
        vacancies = [Mock()]
        min_salary = 100000

        filter_vacancies_by_min_salary(vacancies, min_salary)

        mock_filter.assert_called_once_with(vacancies, min_salary)

    @patch("src.utils.ui_helpers.VacancyOperations.filter_vacancies_by_max_salary")
    def test_filter_vacancies_by_max_salary(self, mock_filter):
        """Тест устаревшей функции фильтрации по максимальной зарплате"""
        vacancies = [Mock()]
        max_salary = 200000

        filter_vacancies_by_max_salary(vacancies, max_salary)

        mock_filter.assert_called_once_with(vacancies, max_salary)

    @patch("src.utils.ui_helpers.VacancyOperations.filter_vacancies_by_salary_range")
    def test_filter_vacancies_by_salary_range(self, mock_filter):
        """Тест устаревшей функции фильтрации по диапазону зарплат"""
        vacancies = [Mock()]
        min_salary = 100000
        max_salary = 200000

        filter_vacancies_by_salary_range(vacancies, min_salary, max_salary)

        mock_filter.assert_called_once_with(vacancies, min_salary, max_salary)

    @patch("src.utils.ui_helpers.VacancyOperations.get_vacancies_with_salary")
    def test_get_vacancies_with_salary(self, mock_get):
        """Тест устаревшей функции получения вакансий с зарплатой"""
        vacancies = [Mock()]

        get_vacancies_with_salary(vacancies)

        mock_get.assert_called_once_with(vacancies)

    @patch("src.utils.ui_helpers.VacancyOperations.sort_vacancies_by_salary")
    def test_sort_vacancies_by_salary(self, mock_sort):
        """Тест устаревшей функции сортировки по зарплате"""
        vacancies = [Mock()]

        sort_vacancies_by_salary(vacancies, reverse=False)

        mock_sort.assert_called_once_with(vacancies, False)

    @patch("src.utils.ui_helpers.VacancyOperations.filter_vacancies_by_multiple_keywords")
    def test_filter_vacancies_by_multiple_keywords(self, mock_filter):
        """Тест устаревшей функции фильтрации по множественным ключевым словам"""
        vacancies = [Mock()]
        keywords = ["python", "django"]

        filter_vacancies_by_multiple_keywords(vacancies, keywords)

        mock_filter.assert_called_once_with(vacancies, keywords)

    @patch("src.utils.ui_helpers.VacancyOperations.search_vacancies_advanced")
    def test_search_vacancies_advanced(self, mock_search):
        """Тест устаревшей функции расширенного поиска"""
        vacancies = [Mock()]
        query = "python developer"

        search_vacancies_advanced(vacancies, query)

        mock_search.assert_called_once_with(vacancies, query)

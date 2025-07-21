
import pytest
from unittest.mock import Mock, patch, call
from src.ui_interfaces.vacancy_display_handler import VacancyDisplayHandler
from src.storage.json_saver import JSONSaver
from src.vacancies.models import Vacancy
from src.utils.vacancy_operations import VacancyOperations


class TestVacancyDisplayHandler:
    """Тесты для класса VacancyDisplayHandler"""

    @pytest.fixture
    def mock_json_saver(self):
        """Фикстура для мок JSONSaver"""
        return Mock(spec=JSONSaver)

    @pytest.fixture
    def handler(self, mock_json_saver):
        """Фикстура для VacancyDisplayHandler"""
        return VacancyDisplayHandler(mock_json_saver)

    def test_init(self, mock_json_saver):
        """Тест инициализации обработчика"""
        handler = VacancyDisplayHandler(mock_json_saver)
        
        assert handler.json_saver is mock_json_saver
        assert isinstance(handler.vacancy_ops, VacancyOperations)

    @patch('builtins.print')
    def test_show_all_saved_vacancies_no_vacancies(self, mock_print, handler):
        """Тест отображения когда нет сохраненных вакансий"""
        handler.json_saver.get_vacancies.return_value = []
        
        handler.show_all_saved_vacancies()
        
        handler.json_saver.get_vacancies.assert_called_once()
        mock_print.assert_called_once_with("\nНет сохраненных вакансий.")

    @patch('src.ui_interfaces.vacancy_display_handler.quick_paginate')
    @patch('builtins.print')
    def test_show_all_saved_vacancies_with_data(self, mock_print, mock_paginate, handler):
        """Тест отображения сохраненных вакансий"""
        vacancies = [
            Mock(spec=Vacancy),
            Mock(spec=Vacancy)
        ]
        handler.json_saver.get_vacancies.return_value = vacancies
        
        handler.show_all_saved_vacancies()
        
        handler.json_saver.get_vacancies.assert_called_once()
        mock_print.assert_called_once_with("\nСохраненных вакансий: 2")
        mock_paginate.assert_called_once()

    @patch('src.ui_interfaces.vacancy_display_handler.logger')
    @patch('builtins.print')
    def test_show_all_saved_vacancies_exception(self, mock_print, mock_logger, handler):
        """Тест обработки исключения при отображении вакансий"""
        error_msg = "Test error"
        handler.json_saver.get_vacancies.side_effect = Exception(error_msg)
        
        handler.show_all_saved_vacancies()
        
        mock_logger.error.assert_called_once()
        mock_print.assert_called_once_with(f"Ошибка при загрузке вакансий: {error_msg}")

    @patch('src.ui_interfaces.vacancy_display_handler.get_positive_integer', return_value=None)
    def test_show_top_vacancies_by_salary_invalid_input(self, mock_input, handler):
        """Тест топ вакансий с некорректным вводом"""
        handler.show_top_vacancies_by_salary()
        
        mock_input.assert_called_once_with("\nВведите количество вакансий для отображения: ")

    @patch('src.ui_interfaces.vacancy_display_handler.get_positive_integer', return_value=5)
    @patch('builtins.print')
    def test_show_top_vacancies_by_salary_no_vacancies(self, mock_print, mock_input, handler):
        """Тест топ вакансий когда нет сохраненных вакансий"""
        handler.json_saver.get_vacancies.return_value = []
        
        handler.show_top_vacancies_by_salary()
        
        mock_print.assert_called_once_with("Нет сохраненных вакансий.")

    @patch('src.ui_interfaces.vacancy_display_handler.get_positive_integer', return_value=3)
    @patch('builtins.print')
    def test_show_top_vacancies_by_salary_no_salary_vacancies(self, mock_print, mock_input, handler):
        """Тест топ вакансий когда нет вакансий с зарплатой"""
        vacancies = [Mock(spec=Vacancy)]
        handler.json_saver.get_vacancies.return_value = vacancies
        
        # Мокаем VacancyOperations чтобы избежать вызовов input()
        handler.vacancy_ops = Mock()
        handler.vacancy_ops.get_vacancies_with_salary.return_value = []
        
        handler.show_top_vacancies_by_salary()
        
        # Проверяем, что было сообщение о том что нет вакансий с зарплатой
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Среди сохраненных вакансий нет ни одной с указанной зарплатой." in call for call in print_calls)

    @patch('src.ui_interfaces.vacancy_display_handler.quick_paginate')
    @patch('src.ui_interfaces.vacancy_display_handler.get_positive_integer', return_value=2)
    @patch('builtins.print')
    def test_show_top_vacancies_by_salary_success(self, mock_print, mock_input, mock_paginate, handler):
        """Тест успешного отображения топ вакансий"""
        vacancies = [Mock(spec=Vacancy), Mock(spec=Vacancy), Mock(spec=Vacancy)]
        vacancies_with_salary = vacancies.copy()
        sorted_vacancies = vacancies.copy()
        
        handler.json_saver.get_vacancies.return_value = vacancies
        
        # Мокаем методы VacancyOperations
        handler.vacancy_ops = Mock()
        handler.vacancy_ops.get_vacancies_with_salary.return_value = vacancies_with_salary
        handler.vacancy_ops.sort_vacancies_by_salary.return_value = sorted_vacancies
        
        handler.show_top_vacancies_by_salary()
        
        handler.vacancy_ops.get_vacancies_with_salary.assert_called_once_with(vacancies)
        handler.vacancy_ops.sort_vacancies_by_salary.assert_called_once_with(vacancies_with_salary)
        mock_paginate.assert_called_once()
        
        # Проверяем что было напечатано сообщение о топ вакансиях
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Топ 2 сохраненных вакансий по зарплате:" in call for call in print_calls)

    @patch('src.ui_interfaces.vacancy_display_handler.get_positive_integer', return_value=5)
    @patch('src.ui_interfaces.vacancy_display_handler.logger')
    @patch('builtins.print')
    def test_show_top_vacancies_by_salary_exception(self, mock_print, mock_logger, mock_input, handler):
        """Тест обработки исключения при получении топ вакансий"""
        error_msg = "Test error"
        handler.json_saver.get_vacancies.side_effect = Exception(error_msg)
        
        handler.show_top_vacancies_by_salary()
        
        mock_logger.error.assert_called_once()
        mock_print.assert_called_once_with(f"Ошибка при поиске: {error_msg}")

    @patch('src.utils.ui_helpers.get_user_input', return_value=None)
    def test_search_saved_vacancies_by_keyword_no_input(self, mock_input, handler):
        """Тест поиска без ввода ключевого слова"""
        handler.search_saved_vacancies_by_keyword()
        
        mock_input.assert_called_once_with("\nВведите ключевое слово для поиска в описании: ")

    @patch('src.utils.ui_helpers.get_user_input', return_value="python")
    @patch('builtins.print')
    def test_search_saved_vacancies_by_keyword_no_vacancies(self, mock_print, mock_input, handler):
        """Тест поиска когда нет сохраненных вакансий"""
        handler.json_saver.get_vacancies.return_value = []
        
        handler.search_saved_vacancies_by_keyword()
        
        mock_print.assert_called_once_with("Нет сохраненных вакансий.")

    @patch('src.ui_interfaces.vacancy_display_handler.filter_vacancies_by_keyword')
    @patch('src.utils.ui_helpers.get_user_input', return_value="python")
    @patch('builtins.print')
    def test_search_saved_vacancies_by_keyword_no_matches(self, mock_print, mock_input, mock_filter, handler):
        """Тест поиска без совпадений"""
        vacancies = [Mock(spec=Vacancy)]
        handler.json_saver.get_vacancies.return_value = vacancies
        mock_filter.return_value = []
        
        handler.search_saved_vacancies_by_keyword()
        
        mock_filter.assert_called_once_with(vacancies, "python")
        mock_print.assert_called_once_with("Среди сохраненных вакансий не найдено ни одной с ключевым словом 'python'.")

    @patch('src.ui_interfaces.vacancy_display_handler.quick_paginate')
    @patch('src.ui_interfaces.vacancy_display_handler.filter_vacancies_by_keyword')
    @patch('src.utils.ui_helpers.get_user_input', return_value="java")
    @patch('builtins.print')
    def test_search_saved_vacancies_by_keyword_success(self, mock_print, mock_input, mock_filter, mock_paginate, handler):
        """Тест успешного поиска по ключевому слову"""
        vacancies = [Mock(spec=Vacancy), Mock(spec=Vacancy)]
        filtered_vacancies = [Mock(spec=Vacancy)]
        
        handler.json_saver.get_vacancies.return_value = vacancies
        mock_filter.return_value = filtered_vacancies
        
        handler.search_saved_vacancies_by_keyword()
        
        mock_filter.assert_called_once_with(vacancies, "java")
        mock_print.assert_called_once_with("\nНайдено 1 сохраненных вакансий с ключевым словом 'java':")
        mock_paginate.assert_called_once()

    @patch('src.utils.ui_helpers.get_user_input', return_value="test")
    @patch('src.ui_interfaces.vacancy_display_handler.logger')
    @patch('builtins.print')
    def test_search_saved_vacancies_by_keyword_exception(self, mock_print, mock_logger, mock_input, handler):
        """Тест обработки исключения при поиске по ключевому слову"""
        error_msg = "Test error"
        handler.json_saver.get_vacancies.side_effect = Exception(error_msg)
        
        handler.search_saved_vacancies_by_keyword()
        
        mock_logger.error.assert_called_once()
        mock_print.assert_called_once_with(f"Ошибка при поиске: {error_msg}")

    @patch('src.ui_interfaces.vacancy_display_handler.logger')
    @patch('builtins.print')
    def test_show_all_saved_vacancies_logger_exception_coverage(self, mock_print, mock_logger, handler):
        """Тест покрытия логирования в show_all_saved_vacancies (строка 43)"""
        error_msg = "Database connection error"
        handler.json_saver.get_vacancies.side_effect = Exception(error_msg)
        
        handler.show_all_saved_vacancies()
        
        # Проверяем, что ошибка была залогирована (строка 43)
        mock_logger.error.assert_called_once_with(f"Ошибка при отображении сохраненных вакансий: {error_msg}")
        mock_print.assert_called_once_with(f"Ошибка при загрузке вакансий: {error_msg}")

    @patch('src.ui_interfaces.vacancy_display_handler.get_positive_integer', return_value=5)
    @patch('src.ui_interfaces.vacancy_display_handler.logger')
    @patch('builtins.print')
    def test_show_top_vacancies_by_salary_logger_exception_coverage(self, mock_print, mock_logger, mock_input, handler):
        """Тест покрытия логирования в show_top_vacancies_by_salary (строка 83)"""
        error_msg = "Salary processing error"
        handler.json_saver.get_vacancies.side_effect = Exception(error_msg)
        
        handler.show_top_vacancies_by_salary()
        
        # Проверяем, что ошибка была залогирована (строка 83)
        mock_logger.error.assert_called_once_with(f"Ошибка при получении топ сохраненных вакансий: {error_msg}")
        mock_print.assert_called_once_with(f"Ошибка при поиске: {error_msg}")

    @patch('src.utils.ui_helpers.get_user_input', return_value="python")
    @patch('src.ui_interfaces.vacancy_display_handler.logger')
    @patch('builtins.print')
    def test_search_saved_vacancies_by_keyword_logger_exception_coverage(self, mock_print, mock_logger, mock_input, handler):
        """Тест покрытия логирования в search_saved_vacancies_by_keyword (строка 120)"""
        error_msg = "Search operation failed"
        handler.json_saver.get_vacancies.side_effect = Exception(error_msg)
        
        handler.search_saved_vacancies_by_keyword()
        
        # Проверяем, что ошибка была залогирована (строка 120)
        mock_logger.error.assert_called_once_with(f"Ошибка при поиске по ключевому слову: {error_msg}")
        mock_print.assert_called_once_with(f"Ошибка при поиске: {error_msg}")

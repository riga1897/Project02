import pytest
from unittest.mock import MagicMock, patch
from src.ui_interfaces.vacancy_display_handler import VacancyDisplayHandler


class TestVacancyDisplayHandlerFinal:
    """Tests for remaining uncovered lines in vacancy_display_handler.py"""

    def test_show_all_saved_vacancies_line_43(self):
        """Test line 43 - exception in show_all_saved_vacancies"""
        json_saver_mock = MagicMock()
        handler = VacancyDisplayHandler(json_saver_mock)

        # Mock get_vacancies to raise exception
        json_saver_mock.get_vacancies.side_effect = Exception("Storage error")

        # Should handle exception gracefully
        handler.show_all_saved_vacancies()

    def test_show_top_vacancies_by_salary_line_83(self):
        """Test line 83 - exception in show_top_vacancies_by_salary"""
        json_saver_mock = MagicMock()
        handler = VacancyDisplayHandler(json_saver_mock)

        # Mock get_vacancies to raise exception
        json_saver_mock.get_vacancies.side_effect = Exception("Storage error")

        with patch('src.utils.ui_helpers.get_positive_integer', return_value=5):
            handler.show_top_vacancies_by_salary()

    def test_search_saved_vacancies_by_keyword_line_120(self):
        """Test line 120 - exception in search_saved_vacancies_by_keyword"""
        json_saver_mock = MagicMock()
        handler = VacancyDisplayHandler(json_saver_mock)

        # Mock get_vacancies to raise exception
        json_saver_mock.get_vacancies.side_effect = Exception("Storage error")

        with patch('src.utils.ui_helpers.get_user_input', return_value='test'):
            handler.search_saved_vacancies_by_keyword()
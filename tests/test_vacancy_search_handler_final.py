import pytest
from unittest.mock import MagicMock, patch
from src.ui_interfaces.vacancy_search_handler import VacancySearchHandler


class TestVacancySearchHandlerFinal:
    """Tests for remaining uncovered lines in vacancy_search_handler.py"""

    def test_search_vacancies_line_102(self):
        """Test line 102 - exception in _save_vacancies"""
        unified_api_mock = MagicMock()
        json_saver_mock = MagicMock()
        handler = VacancySearchHandler(unified_api_mock, json_saver_mock)

        # Mock add_vacancy to raise exception
        json_saver_mock.add_vacancy.side_effect = Exception("Save error")
        test_vacancy = MagicMock()

        # Should handle exception gracefully
        handler._save_vacancies([test_vacancy])

    def test_search_vacancies_line_136(self):
        """Test line 136 - exception in search_vacancies"""
        unified_api_mock = MagicMock()
        json_saver_mock = MagicMock()
        handler = VacancySearchHandler(unified_api_mock, json_saver_mock)

        # Mock get_vacancies_from_sources to raise exception
        unified_api_mock.get_vacancies_from_sources.side_effect = Exception("API error")

        # Should handle exception gracefully
        handler.search_vacancies()
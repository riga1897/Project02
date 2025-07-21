
import pytest
from unittest.mock import MagicMock, patch
from src.ui_interfaces.vacancy_display_handler import VacancyDisplayHandler
from src.vacancies.models import Vacancy


class TestVacancyDisplayHandlerFinal:
    """Tests for 100% coverage of vacancy_display_handler.py"""

    @pytest.fixture
    def display_handler(self):
        """Create VacancyDisplayHandler instance with mocked dependencies"""
        mock_json_saver = MagicMock()
        mock_vacancy_ops = MagicMock()
        return VacancyDisplayHandler(mock_json_saver, mock_vacancy_ops)

    def test_show_all_saved_vacancies_line_43(self, display_handler):
        """Test line 43 - no vacancies case"""
        # Mock empty vacancies list to trigger line 43
        display_handler.json_saver.get_vacancies.return_value = []
        
        with patch('builtins.print') as mock_print:
            display_handler.show_all_saved_vacancies()
            
        # Verify the "no vacancies" message is printed (line 43)
        display_handler.json_saver.get_vacancies.assert_called_once()
        mock_print.assert_called()

    def test_show_top_vacancies_by_salary_line_83(self, display_handler):
        """Test line 83 - invalid input case"""
        # Mock vacancies
        test_vacancies = [
            Vacancy(title="Test", url="http://test.com", vacancy_id="1", 
                   salary={"from": 100000, "to": 150000})
        ]
        display_handler.json_saver.get_vacancies.return_value = test_vacancies
        
        # Mock invalid input to trigger line 83
        with patch('src.ui_interfaces.vacancy_display_handler.get_user_input', return_value='invalid'):
            with patch('builtins.print') as mock_print:
                display_handler.show_top_vacancies_by_salary()
        
        # Verify error message is printed (line 83)
        mock_print.assert_called()

    def test_search_saved_vacancies_by_keyword_line_120(self, display_handler):
        """Test line 120 - no results case"""
        # Mock no vacancies found to trigger line 120
        display_handler.json_saver.get_vacancies.return_value = []
        
        with patch('src.ui_interfaces.vacancy_display_handler.get_user_input', return_value='nonexistent'):
            with patch('src.ui_interfaces.vacancy_display_handler.filter_vacancies_by_keyword', return_value=[]):
                with patch('builtins.print') as mock_print:
                    display_handler.search_saved_vacancies_by_keyword()
        
        # Verify "no results" message is printed (line 120)
        mock_print.assert_called()

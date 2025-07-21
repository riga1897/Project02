
import pytest
from unittest.mock import MagicMock, patch
from src.ui_interfaces.vacancy_search_handler import VacancySearchHandler
from src.vacancies.models import Vacancy


class TestVacancySearchHandlerFinal:
    """Tests for 100% coverage of vacancy_search_handler.py"""

    @pytest.fixture
    def search_handler(self):
        """Create VacancySearchHandler instance with mocked dependencies"""
        mock_unified_api = MagicMock()
        mock_json_saver = MagicMock()
        mock_source_selector = MagicMock()
        return VacancySearchHandler(mock_unified_api, mock_json_saver, mock_source_selector)

    def test_search_vacancies_line_102(self, search_handler):
        """Test line 102 - exception handling during search"""
        # Mock source selection and search query
        search_handler.source_selector.get_user_source_choice.return_value = {'hh'}
        
        # Mock exception during API call to trigger line 102
        search_handler.unified_api.search_vacancies.side_effect = Exception("API Error")
        
        with patch('src.ui_interfaces.vacancy_search_handler.get_user_input', return_value='python'):
            with patch('src.ui_interfaces.vacancy_search_handler.get_period_choice', return_value=30):
                with patch('builtins.print') as mock_print:
                    search_handler.search_vacancies()
        
        # Verify error handling (line 102)
        mock_print.assert_called()

    def test_search_vacancies_line_136(self, search_handler):
        """Test line 136 - save confirmation declined"""
        # Mock successful search
        test_vacancies = [
            Vacancy(title="Python Developer", url="http://test.com", vacancy_id="1")
        ]
        search_handler.unified_api.search_vacancies.return_value = test_vacancies
        search_handler.source_selector.get_user_source_choice.return_value = {'hh'}
        
        with patch('src.ui_interfaces.vacancy_search_handler.get_user_input', return_value='python'):
            with patch('src.ui_interfaces.vacancy_search_handler.get_period_choice', return_value=30):
                with patch('src.ui_interfaces.vacancy_search_handler.confirm_action', return_value=False):
                    with patch('builtins.print') as mock_print:
                        search_handler.search_vacancies()
        
        # Verify that save was declined (line 136)
        search_handler.json_saver.add_vacancies.assert_not_called()
        mock_print.assert_called()

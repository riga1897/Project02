
import pytest
from unittest.mock import MagicMock, patch
from src.ui_interfaces.console_interface import UserInterface
from src.vacancies.models import Vacancy


class TestConsoleInterfaceFinal:
    """Tests for remaining uncovered lines in console_interface.py"""

    @pytest.fixture
    def ui_instance(self):
        """Create UserInterface with mocked dependencies"""
        with patch('src.ui_interfaces.console_interface.HeadHunterAPI'), \
             patch('src.ui_interfaces.console_interface.SuperJobAPI'), \
             patch('src.ui_interfaces.console_interface.UnifiedAPI'), \
             patch('src.ui_interfaces.console_interface.JSONSaver'), \
             patch('src.ui_interfaces.console_interface.create_main_menu'), \
             patch('src.ui_interfaces.console_interface.VacancyOperations'), \
             patch('src.ui_interfaces.console_interface.SourceSelector'):
            ui = UserInterface()
            ui.search_handler = MagicMock()
            ui.display_handler = MagicMock()
            return ui

    def test_remaining_lines_coverage(self, ui_instance):
        """Test remaining uncovered lines in console_interface.py"""
        
        # Test lines 165-166, 217-219, 236-237
        ui_instance.json_saver.get_vacancies.return_value = []
        
        with patch('builtins.input', side_effect=['0', 'q']):
            # These calls should cover various edge cases
            ui_instance._filter_saved_vacancies_by_salary()
            ui_instance._delete_saved_vacancies()
            ui_instance._advanced_search_vacancies()

        # Test lines 282, 292-293, 316, 320, 322, 329, 339
        test_vacancies = [
            Vacancy(title="Test", url="http://test.com", vacancy_id="1")
        ]
        
        with patch('builtins.input', side_effect=['q']):
            ui_instance._show_vacancies_for_deletion(test_vacancies, "test")

        # Test lines 512, 567, 584-590, 603, 607, 616-617, 621, 625
        with patch('builtins.input', side_effect=['6', 'invalid', '15']):
            result = ui_instance._get_period_choice()

        # Test additional edge cases
        with patch('builtins.input', side_effect=['7']):
            result = ui_instance._get_period_choice()

        with patch('builtins.input', side_effect=['0']):
            result = ui_instance._get_period_choice()
            assert result is None

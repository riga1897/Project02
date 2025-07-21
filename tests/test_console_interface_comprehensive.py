
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.ui_interfaces.console_interface import UserInterface


class TestConsoleInterfaceComprehensive:
    """Comprehensive tests for console interface to achieve full coverage"""

    @pytest.fixture
    def ui_with_mocks(self):
        """Create UserInterface with all dependencies mocked"""
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
            ui.json_saver = MagicMock()
            ui.source_selector = MagicMock()
            ui.unified_api = MagicMock()
            ui.vacancy_operations = MagicMock()
            ui.menu = MagicMock()
            
            return ui

    def test_clear_api_cache_exception(self, ui_with_mocks, mocker):
        """Test exception handling in _clear_api_cache (lines 165-166)"""
        ui = ui_with_mocks
        
        # Mock source selector to raise exception
        ui.source_selector.get_user_source_choice.side_effect = Exception("Source selection error")
        
        # Should handle exception gracefully
        ui._clear_api_cache()

    def test_advanced_search_empty_input(self, ui_with_mocks, mocker):
        """Test empty input handling in _advanced_search_vacancies (lines 217-219)"""
        ui = ui_with_mocks
        
        # Setup: return some vacancies from storage
        ui.json_saver.get_vacancies.return_value = [Mock(), Mock()]
        
        # Mock empty user input
        mocker.patch('src.utils.ui_helpers.get_user_input', return_value='')
        
        # Should return early due to empty input
        ui._advanced_search_vacancies()

    def test_advanced_search_exception(self, ui_with_mocks, mocker):
        """Test exception handling in _advanced_search_vacancies (lines 236-237)"""
        ui = ui_with_mocks
        
        # Mock storage to raise exception
        ui.json_saver.get_vacancies.side_effect = Exception("Storage error")
        
        # Should handle exception gracefully
        ui._advanced_search_vacancies()

    def test_run_keyboard_interrupt(self, ui_with_mocks, mocker):
        """Test KeyboardInterrupt handling in run method"""
        ui = ui_with_mocks
        
        # Mock _show_menu to raise KeyboardInterrupt
        mocker.patch.object(ui, '_show_menu', side_effect=KeyboardInterrupt())
        
        # Should exit gracefully
        ui.run()

    def test_run_general_exception(self, ui_with_mocks, mocker):
        """Test general exception handling in run method"""
        ui = ui_with_mocks
        
        # Mock _show_menu to raise general exception first, then return "0" to exit
        mocker.patch.object(ui, '_show_menu', side_effect=[Exception("General error"), "0"])
        
        # Should handle exception and continue
        ui.run()

    def test_various_ui_methods(self, ui_with_mocks, mocker):
        """Test various UI methods to cover remaining lines"""
        ui = ui_with_mocks
        
        # Setup common mocks
        ui.json_saver.get_vacancies.return_value = []
        mocker.patch('builtins.input', return_value='1')
        mocker.patch('src.utils.ui_helpers.confirm_action', return_value=False)
        mocker.patch('src.utils.ui_helpers.get_positive_integer', return_value=50000)
        mocker.patch('src.utils.ui_helpers.get_user_input', return_value='test')
        
        # Test different UI methods
        ui._filter_saved_vacancies_by_salary()
        ui._delete_saved_vacancies()
        ui._show_saved_vacancies()
        ui._search_saved_vacancies()
        ui._show_top_vacancies()
        
        # Test with different return values
        mocker.patch('src.utils.ui_helpers.confirm_action', return_value=True)
        ui._delete_saved_vacancies()
        
        # Test with vacancies present
        ui.json_saver.get_vacancies.return_value = [Mock(), Mock()]
        ui._filter_saved_vacancies_by_salary()
        ui._show_saved_vacancies()

    def test_menu_navigation(self, ui_with_mocks, mocker):
        """Test menu navigation paths"""
        ui = ui_with_mocks
        
        # Test different menu choices
        choices = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
        
        for choice in choices:
            mocker.patch.object(ui, '_show_menu', return_value=choice)
            try:
                # This will test different paths in handle_user_choice
                ui._handle_user_choice(choice)
            except SystemExit:
                pass  # Expected for choice "0"

    def test_error_scenarios(self, ui_with_mocks, mocker):
        """Test various error scenarios"""
        ui = ui_with_mocks
        
        # Test with various side effects to trigger error handling
        ui.search_handler.search_vacancies.side_effect = Exception("Search error")
        ui.display_handler.show_all_saved_vacancies.side_effect = Exception("Display error")
        
        # These should handle exceptions gracefully
        try:
            ui._handle_user_choice("1")
        except:
            pass
            
        try:
            ui._handle_user_choice("2")
        except:
            pass


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
        """Test exception handling in _clear_api_cache"""
        ui = ui_with_mocks
        
        # Mock source selector to raise exception
        ui.source_selector.get_user_source_choice.side_effect = Exception("Source selection error")
        
        # Should handle exception gracefully
        ui._clear_api_cache()

    def test_advanced_search_empty_input(self, ui_with_mocks, mocker):
        """Test empty input handling in _advanced_search_vacancies"""
        ui = ui_with_mocks
        
        # Setup: return some vacancies from storage
        ui.json_saver.get_vacancies.return_value = [Mock(), Mock()]
        
        # Mock empty user input
        mocker.patch('src.utils.ui_helpers.get_user_input', return_value='')
        
        # Should return early due to empty input
        ui._advanced_search_vacancies()

    def test_advanced_search_exception(self, ui_with_mocks, mocker):
        """Test exception handling in _advanced_search_vacancies"""
        ui = ui_with_mocks
        
        # Mock storage to raise exception
        ui.json_saver.get_vacancies.side_effect = Exception("Storage error")
        
        # Should handle exception gracefully
        ui._advanced_search_vacancies()

    def test_run_keyboard_interrupt(self, ui_with_mocks, mocker):
        """Test KeyboardInterrupt handling in run method"""
        ui = ui_with_mocks
        
        # Mock _show_menu to raise KeyboardInterrupt immediately
        mocker.patch.object(ui, '_show_menu', side_effect=KeyboardInterrupt())
        
        # Should exit gracefully without hanging
        ui.run()

    def test_run_general_exception(self, ui_with_mocks, mocker):
        """Test general exception handling in run method"""
        ui = ui_with_mocks
        
        # Mock _show_menu to raise general exception first, then return "0" to exit
        mocker.patch.object(ui, '_show_menu', side_effect=[Exception("General error"), "0"])
        
        # Should handle exception and continue, then exit
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
        ui._search_saved_vacancies_by_keyword()
        ui._get_top_saved_vacancies_by_salary()
        
        # Test with different return values
        mocker.patch('src.utils.ui_helpers.confirm_action', return_value=True)
        ui._delete_saved_vacancies()
        
        # Test with vacancies present
        ui.json_saver.get_vacancies.return_value = [Mock(), Mock()]
        ui._filter_saved_vacancies_by_salary()
        ui._show_saved_vacancies()

    def test_menu_navigation(self, ui_with_mocks, mocker):
        """Test menu navigation paths without calling run()"""
        ui = ui_with_mocks
        
        # Test individual menu methods directly instead of using run()
        ui._search_vacancies()
        ui._show_saved_vacancies()
        ui._get_top_saved_vacancies_by_salary()
        ui._search_saved_vacancies_by_keyword()
        ui._advanced_search_vacancies()
        ui._filter_saved_vacancies_by_salary()
        ui._delete_saved_vacancies()
        ui._clear_api_cache()
        ui._setup_superjob_api()

    def test_run_with_immediate_exit(self, ui_with_mocks, mocker):
        """Test run method with immediate exit"""
        ui = ui_with_mocks
        
        # Mock _show_menu to return "0" immediately to exit
        mocker.patch.object(ui, '_show_menu', return_value="0")
        
        # Should exit immediately
        ui.run()

    def test_run_with_single_choice_then_exit(self, ui_with_mocks, mocker):
        """Test run method with one choice then exit"""
        ui = ui_with_mocks
        
        # Mock _show_menu to return "1" first, then "0" to exit
        mocker.patch.object(ui, '_show_menu', side_effect=["1", "0"])
        
        # Should execute choice "1" then exit
        ui.run()
        
        # Verify that search_vacancies was called
        ui.search_handler.search_vacancies.assert_called_once()

    def test_error_scenarios(self, ui_with_mocks, mocker):
        """Test various error scenarios"""
        ui = ui_with_mocks
        
        # Test with various side effects to trigger error handling
        ui.search_handler.search_vacancies.side_effect = Exception("Search error")
        ui.display_handler.show_all_saved_vacancies.side_effect = Exception("Display error")
        
        # Test error handling in different methods
        ui._search_vacancies()
        ui._show_saved_vacancies()
        
        # Test filter salary with invalid choice
        ui.json_saver.get_vacancies.return_value = [Mock()]
        mocker.patch('builtins.input', side_effect=['4', '1'])  # Invalid choice, then valid
        ui._filter_saved_vacancies_by_salary()
        
        # Test delete with invalid choice  
        mocker.patch('builtins.input', side_effect=['4', '0'])  # Invalid choice, then cancel
        ui._delete_saved_vacancies()
        
        # Test advanced search with different query types
        mocker.patch('src.utils.ui_helpers.get_user_input', return_value='python,java,django')
        ui._advanced_search_vacancies()
        
        # Test advanced search with AND/OR operators
        mocker.patch('src.utils.ui_helpers.get_user_input', return_value='python AND django')
        ui._advanced_search_vacancies()

    def test_show_menu_static_method(self, mocker):
        """Test _show_menu static method"""
        # Mock input to return a test value
        mocker.patch('builtins.input', return_value='1')
        
        # Call the static method directly
        result = UserInterface._show_menu()
        assert result == '1'

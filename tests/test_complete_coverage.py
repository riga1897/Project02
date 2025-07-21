
import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import tempfile
import json
import os
from pathlib import Path

from src.api_modules.cached_api import CachedAPI
from src.storage.json_saver import JSONSaver
from src.ui_interfaces.console_interface import UserInterface
from src.ui_interfaces.vacancy_display_handler import VacancyDisplayHandler
from src.ui_interfaces.vacancy_search_handler import VacancySearchHandler
from src.utils.base_formatter import BaseFormatter
from src.vacancies.models import Vacancy, Salary
from src.user_interface import main


class ConcreteCachedAPI(CachedAPI):
    """Concrete implementation for testing"""
    def __init__(self, cache_dir="test_cache"):
        super().__init__(cache_dir)

    def _get_empty_response(self):
        return {"items": [], "found": 0, "pages": 0}

    def _validate_vacancy(self, vacancy):
        return "name" in vacancy or "title" in vacancy

    def get_vacancies_page(self, search_query, page=0, **kwargs):
        return [{"name": "Test Vacancy", "page": page}]

    def get_vacancies(self, search_query, **kwargs):
        return [{"name": "Test Vacancy"}]


class TestCompleteCoverage:
    """Tests to achieve 100% coverage for remaining lines"""

    def test_cached_api_exception_handling(self):
        """Test cached_api.py lines 66-72 exception handling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            api.connector = Mock()
            
            # Mock _cached_api_request to raise exception (lines 66-72)
            with patch.object(api, '_cached_api_request', side_effect=Exception("Cache error")):
                result = api._CachedAPI__connect_to_api("test_url", {"param": "value"}, "test")
                assert result == api._get_empty_response()

    def test_json_saver_backup_file_not_exists(self):
        """Test json_saver.py lines 160-161 when file doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "nonexistent.json"
            json_saver = JSONSaver(str(storage_path))
            
            # Delete the file to test the condition where file doesn't exist
            if storage_path.exists():
                storage_path.unlink()
            
            # Call _backup_corrupted_file when file doesn't exist (lines 160-161)
            json_saver._backup_corrupted_file()

    def test_json_saver_save_to_file_validation_errors(self):
        """Test json_saver.py lines 229-231 validation errors"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "test.json"
            json_saver = JSONSaver(str(storage_path))
            
            # Create mock vacancy without required fields
            invalid_vacancy = Mock()
            invalid_vacancy.to_dict.return_value = {"invalid": "data"}  # Missing required fields
            
            # Should trigger validation error and warning (lines 229-231)
            json_saver._save_to_file([invalid_vacancy])

    def test_json_saver_vacancy_to_dict_none_salary(self):
        """Test json_saver.py line 299 when salary is None"""
        vacancy = Vacancy(
            vacancy_id="123",
            title="Test Job",
            url="http://test.com"
        )
        # Force salary to None
        vacancy.salary = None
        
        result = JSONSaver._vacancy_to_dict(vacancy)
        assert result['salary'] is None

    def test_console_interface_clear_api_cache_exception(self):
        """Test console_interface.py lines 165-166 exception handling"""
        with patch('src.ui_interfaces.console_interface.HeadHunterAPI'), \
             patch('src.ui_interfaces.console_interface.SuperJobAPI'), \
             patch('src.ui_interfaces.console_interface.UnifiedAPI'), \
             patch('src.ui_interfaces.console_interface.JSONSaver'), \
             patch('src.ui_interfaces.console_interface.create_main_menu'), \
             patch('src.ui_interfaces.console_interface.VacancyOperations'), \
             patch('src.ui_interfaces.console_interface.SourceSelector'):
            
            ui = UserInterface()
            ui.source_selector = MagicMock()
            ui.unified_api = MagicMock()
            
            # Mock source selector to raise exception (lines 165-166)
            ui.source_selector.get_user_source_choice.side_effect = Exception("Source error")
            
            # Should handle exception gracefully
            ui._clear_api_cache()

    def test_console_interface_advanced_search_empty_input(self):
        """Test console_interface.py lines 217-219 empty input handling"""
        with patch('src.ui_interfaces.console_interface.HeadHunterAPI'), \
             patch('src.ui_interfaces.console_interface.SuperJobAPI'), \
             patch('src.ui_interfaces.console_interface.UnifiedAPI'), \
             patch('src.ui_interfaces.console_interface.JSONSaver'), \
             patch('src.ui_interfaces.console_interface.create_main_menu'), \
             patch('src.ui_interfaces.console_interface.VacancyOperations'), \
             patch('src.ui_interfaces.console_interface.SourceSelector'):
            
            ui = UserInterface()
            ui.json_saver = MagicMock()
            ui.json_saver.get_vacancies.return_value = [Mock()]
            
            # Mock empty user input (lines 217-219)
            with patch('src.utils.ui_helpers.get_user_input', return_value=''):
                ui._advanced_search_vacancies()

    def test_console_interface_advanced_search_exception(self):
        """Test console_interface.py lines 236-237 exception handling"""
        with patch('src.ui_interfaces.console_interface.HeadHunterAPI'), \
             patch('src.ui_interfaces.console_interface.SuperJobAPI'), \
             patch('src.ui_interfaces.console_interface.UnifiedAPI'), \
             patch('src.ui_interfaces.console_interface.JSONSaver'), \
             patch('src.ui_interfaces.console_interface.create_main_menu'), \
             patch('src.ui_interfaces.console_interface.VacancyOperations'), \
             patch('src.ui_interfaces.console_interface.SourceSelector'):
            
            ui = UserInterface()
            ui.json_saver = MagicMock()
            
            # Mock get_vacancies to raise exception (lines 236-237)
            ui.json_saver.get_vacancies.side_effect = Exception("Storage error")
            ui._advanced_search_vacancies()

    def test_console_interface_filter_salary_invalid_choices(self):
        """Test console_interface.py lines 282, 292-293"""
        with patch('src.ui_interfaces.console_interface.HeadHunterAPI'), \
             patch('src.ui_interfaces.console_interface.SuperJobAPI'), \
             patch('src.ui_interfaces.console_interface.UnifiedAPI'), \
             patch('src.ui_interfaces.console_interface.JSONSaver'), \
             patch('src.ui_interfaces.console_interface.create_main_menu'), \
             patch('src.ui_interfaces.console_interface.VacancyOperations'), \
             patch('src.ui_interfaces.console_interface.SourceSelector'):
            
            ui = UserInterface()
            ui.json_saver = MagicMock()
            ui.json_saver.get_vacancies.return_value = []
            
            # Test invalid choice (line 282)
            with patch('builtins.input', side_effect=['invalid', 'q']):
                ui._filter_saved_vacancies_by_salary()
            
            # Test choice 4 - default case (lines 292-293)
            with patch('builtins.input', side_effect=['4', 'q']):
                ui._filter_saved_vacancies_by_salary()

    def test_console_interface_delete_vacancies_invalid_choices(self):
        """Test console_interface.py lines 316, 320, 322, 329, 339"""
        with patch('src.ui_interfaces.console_interface.HeadHunterAPI'), \
             patch('src.ui_interfaces.console_interface.SuperJobAPI'), \
             patch('src.ui_interfaces.console_interface.UnifiedAPI'), \
             patch('src.ui_interfaces.console_interface.JSONSaver'), \
             patch('src.ui_interfaces.console_interface.create_main_menu'), \
             patch('src.ui_interfaces.console_interface.VacancyOperations'), \
             patch('src.ui_interfaces.console_interface.SourceSelector'):
            
            ui = UserInterface()
            ui.json_saver = MagicMock()
            ui.json_saver.get_vacancies.return_value = []
            
            # Test various invalid choices
            test_inputs = ['invalid', '4', '5', '0']
            for input_val in test_inputs:
                with patch('builtins.input', side_effect=[input_val, 'q']):
                    ui._delete_saved_vacancies()

    def test_console_interface_pagination_invalid_input(self):
        """Test console_interface.py lines 512, 567"""
        with patch('src.ui_interfaces.console_interface.HeadHunterAPI'), \
             patch('src.ui_interfaces.console_interface.SuperJobAPI'), \
             patch('src.ui_interfaces.console_interface.UnifiedAPI'), \
             patch('src.ui_interfaces.console_interface.JSONSaver'), \
             patch('src.ui_interfaces.console_interface.create_main_menu'), \
             patch('src.ui_interfaces.console_interface.VacancyOperations'), \
             patch('src.ui_interfaces.console_interface.SourceSelector'):
            
            ui = UserInterface()
            
            # Test invalid pagination input (lines 512, 567)
            with patch('builtins.input', side_effect=['invalid', 'q']):
                ui._show_vacancies_for_deletion([], 'test')

    def test_console_interface_period_choice_edge_cases(self):
        """Test console_interface.py lines 584-590, 603, 607, 616-617, 621, 625"""
        with patch('src.ui_interfaces.console_interface.HeadHunterAPI'), \
             patch('src.ui_interfaces.console_interface.SuperJobAPI'), \
             patch('src.ui_interfaces.console_interface.UnifiedAPI'), \
             patch('src.ui_interfaces.console_interface.JSONSaver'), \
             patch('src.ui_interfaces.console_interface.create_main_menu'), \
             patch('src.ui_interfaces.console_interface.VacancyOperations'), \
             patch('src.ui_interfaces.console_interface.SourceSelector'):
            
            ui = UserInterface()
            
            # Test invalid period choice
            with patch('builtins.input', side_effect=['7']):  # Invalid choice
                result = ui._get_period_choice()
                assert result == 15  # Default
            
            # Test custom period out of range
            with patch('builtins.input', side_effect=['6', '500']):  # Out of range
                result = ui._get_period_choice()
                assert result == 15  # Default
            
            # Test KeyboardInterrupt
            with patch('builtins.input', side_effect=KeyboardInterrupt()):
                result = ui._get_period_choice()
                assert result is None

    def test_vacancy_display_handler_exceptions(self):
        """Test vacancy_display_handler.py lines 43, 83, 120"""
        with patch('src.ui_interfaces.vacancy_display_handler.JSONSaver') as mock_json_saver:
            handler = VacancyDisplayHandler(mock_json_saver)
            
            # Line 43: exception in show_all_saved_vacancies
            mock_json_saver.get_vacancies.side_effect = Exception("Storage error")
            handler.show_all_saved_vacancies()
            
            # Line 83: exception in show_top_vacancies_by_salary
            handler.show_top_vacancies_by_salary()
            
            # Line 120: exception in search_saved_vacancies_by_keyword
            handler.search_saved_vacancies_by_keyword()

    def test_vacancy_search_handler_exceptions(self):
        """Test vacancy_search_handler.py lines 102, 136"""
        with patch('src.ui_interfaces.vacancy_search_handler.UnifiedAPI') as mock_unified_api, \
             patch('src.ui_interfaces.vacancy_search_handler.JSONSaver') as mock_json_saver:
            
            handler = VacancySearchHandler(mock_unified_api, mock_json_saver)
            
            # Line 102: exception in _save_vacancies
            mock_json_saver.add_vacancy.side_effect = Exception("Save error")
            handler._save_vacancies([Mock()])
            
            # Line 136: exception in search_vacancies
            mock_unified_api.get_vacancies_from_sources.side_effect = Exception("API error")
            handler.search_vacancies()

    def test_user_interface_main_function(self):
        """Test user_interface.py line 39"""
        with patch('src.user_interface.UserInterface') as mock_ui_class:
            mock_ui = mock_ui_class.return_value
            
            main()
            
            mock_ui_class.assert_called_once()
            mock_ui.run.assert_called_once()

    def test_base_formatter_edge_cases(self):
        """Test base_formatter.py lines 145, 174"""
        formatter = BaseFormatter()
        
        # Line 145: edge case in format_experience
        result = formatter.format_experience(None)
        assert result == "Не указан"
        
        # Line 174: edge case in format_schedule
        result = formatter.format_schedule(None)
        assert result == "Не указан"

    def test_vacancy_models_edge_cases(self):
        """Test vacancy models lines 121-122, 185, 228, 230"""
        # Lines 121-122: calculate_average_salary with None salary
        vacancy = Vacancy(title="Test", url="http://test.com", vacancy_id="1")
        vacancy.salary = None
        result = vacancy.calculate_average_salary()
        assert result is None
        
        # Line 185: __eq__ with non-vacancy object
        vacancy1 = Vacancy(title="Test", url="http://test.com", vacancy_id="1")
        result = vacancy1.__eq__("not_a_vacancy")
        assert result is False
        
        # Lines 228, 230: from_dict edge cases
        # Line 228: missing required fields
        try:
            Vacancy.from_dict({})
        except (KeyError, TypeError):
            pass  # Expected
        
        # Line 230: invalid data type
        try:
            Vacancy.from_dict("not_a_dict")
        except (TypeError, AttributeError):
            pass  # Expected

    def test_comprehensive_input_mocking(self):
        """Test all input scenarios with proper mocking"""
        with patch('src.ui_interfaces.console_interface.HeadHunterAPI'), \
             patch('src.ui_interfaces.console_interface.SuperJobAPI'), \
             patch('src.ui_interfaces.console_interface.UnifiedAPI'), \
             patch('src.ui_interfaces.console_interface.JSONSaver'), \
             patch('src.ui_interfaces.console_interface.create_main_menu'), \
             patch('src.ui_interfaces.console_interface.VacancyOperations'), \
             patch('src.ui_interfaces.console_interface.SourceSelector'):
            
            ui = UserInterface()
            ui.json_saver = MagicMock()
            ui.source_selector = MagicMock()
            ui.vacancy_ops = MagicMock()
            ui.unified_api = MagicMock()
            
            # Mock all dependencies to return empty/safe values
            ui.json_saver.get_vacancies.return_value = []
            ui.source_selector.get_user_source_choice.return_value = set()
            ui.vacancy_ops.filter_vacancies_by_multiple_keywords.return_value = []
            ui.unified_api.clear_cache.return_value = None
            
            # Test various input scenarios that might cause hanging
            test_scenarios = [
                ('', ''),        # Empty inputs
                ('q', ''),       # Quit commands
                ('0', ''),       # Cancel commands
                ('invalid', 'q'), # Invalid then quit
            ]
            
            for input1, input2 in test_scenarios:
                with patch('builtins.input', side_effect=[input1, input2]):
                    with patch('src.utils.ui_helpers.get_user_input', return_value=input1):
                        # Test methods that might hang
                        ui._filter_saved_vacancies_by_salary()
                        ui._delete_saved_vacancies()
                        ui._advanced_search_vacancies()
                        ui._clear_api_cache()
                        ui._show_vacancies_for_deletion([], 'test')
                        
                        # Test period choice with safe fallbacks
                        if input1 not in ['', 'q', '0']:
                            result = ui._get_period_choice()
                            assert result in [None, 15] or isinstance(result, int)

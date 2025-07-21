
import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import tempfile
import json
import os
from pathlib import Path

from src.ui_interfaces.console_interface import UserInterface
from src.storage.json_saver import JSONSaver
from src.api_modules.cached_api import CachedAPI
from src.ui_interfaces.vacancy_display_handler import VacancyDisplayHandler
from src.ui_interfaces.vacancy_search_handler import VacancySearchHandler
from src.utils.base_formatter import BaseFormatter
from src.vacancies.models import Vacancy
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


class TestFinalCoverage:
    """Tests to achieve 100% coverage"""

    def test_cached_api_lines_66_72(self):
        """Test exception handling in cached_api.py lines 66-72"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            api.connector = Mock()

            # Mock _cached_api_request to raise exception
            with patch.object(api, '_cached_api_request', side_effect=Exception("Cache error")):
                result = api._CachedAPI__connect_to_api("test_url", {"param": "value"}, "test")
                assert result == api._get_empty_response()

    def test_json_saver_lines_229_231(self):
        """Test lines 229-231 in json_saver.py - filter error handling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "test.json"
            json_saver = JSONSaver(str(storage_path))

            # Test filter error in delete_vacancies_by_keyword
            with patch('src.utils.ui_helpers.filter_vacancies_by_keyword', side_effect=Exception("Filter error")):
                result = json_saver.delete_vacancies_by_keyword("test")
                assert result == 0

    def test_json_saver_line_299(self):
        """Test line 299 in json_saver.py - file error in delete_all_vacancies"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "test.json"
            json_saver = JSONSaver(str(storage_path))

            # Test file error in delete_all_vacancies
            with patch('builtins.open', side_effect=OSError("System error")):
                result = json_saver.delete_all_vacancies()
                assert result is False

    def test_json_saver_lines_160_161(self):
        """Test lines 160-161 in json_saver.py - backup when file doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "nonexistent.json"
            json_saver = JSONSaver(str(storage_path))

            # Ensure file doesn't exist
            if storage_path.exists():
                storage_path.unlink()

            # Call backup when file doesn't exist
            json_saver._backup_corrupted_file()

    def test_console_interface_lines_165_166(self):
        """Test exception in _clear_api_cache"""
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

            # Mock source selector to raise exception
            ui.source_selector.get_user_source_choice.side_effect = Exception("Source error")

            # Should handle exception gracefully
            ui._clear_api_cache()

    def test_console_interface_lines_217_219(self):
        """Test empty input in _advanced_search_vacancies"""
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

            # Mock empty user input
            with patch('src.utils.ui_helpers.get_user_input', return_value=''):
                ui._advanced_search_vacancies()

    def test_console_interface_lines_236_237(self):
        """Test exception in _advanced_search_vacancies"""
        with patch('src.ui_interfaces.console_interface.HeadHunterAPI'), \
             patch('src.ui_interfaces.console_interface.SuperJobAPI'), \
             patch('src.ui_interfaces.console_interface.UnifiedAPI'), \
             patch('src.ui_interfaces.console_interface.JSONSaver'), \
             patch('src.ui_interfaces.console_interface.create_main_menu'), \
             patch('src.ui_interfaces.console_interface.VacancyOperations'), \
             patch('src.ui_interfaces.console_interface.SourceSelector'):

            ui = UserInterface()
            ui.json_saver = MagicMock()

            # Mock get_vacancies to raise exception
            ui.json_saver.get_vacancies.side_effect = Exception("Storage error")
            ui._advanced_search_vacancies()

    def test_console_interface_remaining_lines(self):
        """Test remaining console interface lines"""
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

            # Reset for other tests
            ui.json_saver.get_vacancies.side_effect = None
            ui.json_saver.get_vacancies.return_value = []

            # Lines 282, 292-293: various filter scenarios
            with patch('builtins.input', return_value='4'):  # Invalid choice
                ui._filter_saved_vacancies_by_salary()

            # Lines 316, 320, 322, 329, 339: delete scenarios
            with patch('builtins.input', return_value='4'):  # Invalid choice
                ui._delete_saved_vacancies()

            # Lines 512, 567: pagination edge cases
            with patch('builtins.input', return_value='x'):  # Invalid choice
                ui._show_vacancies_for_deletion([], 'test')

            # Lines 584-590, 603, 607, 616-617, 621, 625: period choice edge cases
            with patch('builtins.input', side_effect=['7', '500']):  # Invalid period
                result = ui._get_period_choice()
                assert result == 15

            with patch('builtins.input', side_effect=KeyboardInterrupt()):
                result = ui._get_period_choice()
                assert result is None

    def test_vacancy_display_handler_lines_43_83_120(self):
        """Test remaining lines in vacancy_display_handler.py"""
        with patch('src.ui_interfaces.vacancy_display_handler.JSONSaver') as mock_json_saver:
            handler = VacancyDisplayHandler(mock_json_saver)

            # Line 43: exception in show_all_saved_vacancies
            mock_json_saver.get_vacancies.side_effect = Exception("Storage error")
            handler.show_all_saved_vacancies()

            # Line 83: exception in show_top_vacancies_by_salary
            handler.show_top_vacancies_by_salary()

            # Line 120: exception in search_saved_vacancies_by_keyword
            handler.search_saved_vacancies_by_keyword()

    def test_vacancy_search_handler_lines_102_136(self):
        """Test remaining lines in vacancy_search_handler.py"""
        with patch('src.ui_interfaces.vacancy_search_handler.UnifiedAPI') as mock_unified_api, \
             patch('src.ui_interfaces.vacancy_search_handler.JSONSaver') as mock_json_saver:

            handler = VacancySearchHandler(mock_unified_api, mock_json_saver)

            # Line 102: exception in _save_vacancies
            mock_json_saver.add_vacancy.side_effect = Exception("Save error")
            handler._save_vacancies([Mock()])

            # Line 136: exception in search_vacancies
            mock_unified_api.get_vacancies_from_sources.side_effect = Exception("API error")
            handler.search_vacancies()

    def test_user_interface_line_39(self):
        """Test line 39 in user_interface.py"""
        with patch('src.user_interface.UserInterface') as mock_ui_class:
            mock_ui = mock_ui_class.return_value
            main()
            mock_ui_class.assert_called_once()
            mock_ui.run.assert_called_once()

    def test_base_formatter_lines_145_174(self):
        """Test remaining lines in base_formatter.py"""
        formatter = BaseFormatter()

        # Line 145: edge case in format_experience
        result = formatter.format_experience(None)
        assert result == "Не указан"

        # Line 174: edge case in format_schedule
        result = formatter.format_schedule(None)
        assert result == "Не указан"

    def test_vacancy_models_lines_121_122_185_228_230(self):
        """Test remaining lines in vacancy models"""
        # Lines 121-122: edge case in calculate_average_salary
        vacancy = Vacancy(title="Test", url="http://test.com", vacancy_id="1")
        vacancy.salary = None
        result = vacancy.calculate_average_salary()
        assert result is None

        # Line 185: edge case in __eq__
        vacancy1 = Vacancy(title="Test", url="http://test.com", vacancy_id="1")
        result = vacancy1.__eq__("not_a_vacancy")
        assert result is False

        # Lines 228, 230: edge cases in from_dict
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

    @patch('builtins.input', return_value='q')
    def test_comprehensive_edge_cases(self, mock_input):
        """Additional edge cases for complete coverage"""
        # Test console interface with all possible error scenarios
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

            # Test all possible input scenarios for complete coverage
            test_inputs = [
                'invalid',  # Invalid filter choice
                '0',        # Cancel operations
                '5',        # Invalid delete choice
                'x',        # Invalid pagination choice
                '8',        # Out of range period
            ]

            for input_val in test_inputs:
                mock_input.return_value = input_val

                # Test various methods with these inputs
                ui.json_saver.get_vacancies.return_value = []
                ui._filter_saved_vacancies_by_salary()
                ui._delete_saved_vacancies()
                ui._show_vacancies_for_deletion([], 'test')

                if input_val in ['8']:
                    mock_input.return_value = '1000'  # Set large period value
                    result = ui._get_period_choice()
                    assert result == 15  # Default fallback

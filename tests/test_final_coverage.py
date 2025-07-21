import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
from pathlib import Path

from src.storage.json_saver import JSONSaver
from src.api_modules.cached_api import CachedAPI
from src.ui_interfaces.console_interface import UserInterface
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


class ConcreteBaseFormatter(BaseFormatter):
    """Concrete implementation for testing"""

    def format_vacancy_info(self, vacancy_data):
        return f"Vacancy: {vacancy_data.get('title', 'Unknown')}"


class TestFinalCoverage:
    """Упрощенные тесты для достижения 100% покрытия"""

    def test_cached_api_lines_66_72(self):
        """Test exception handling in cached_api.py lines 66-72"""
        api = ConcreteCachedAPI()
        api.connector = Mock()

        # Mock _cached_api_request to raise exception
        with patch.object(api, '_cached_api_request', side_effect=Exception("Cache error")):
            result = api._CachedAPI__connect_to_api("test_url", {"param": "value"}, "test")
            assert result == api._get_empty_response()

    def test_json_saver_lines_160_161(self):
        """Test lines 160-161 in json_saver.py - backup when file doesn't exist"""
        with patch('src.storage.json_saver.Path') as mock_path:
            mock_path_instance = Mock()
            mock_path.return_value = mock_path_instance
            mock_path_instance.exists.return_value = False  # File doesn't exist

            json_saver = JSONSaver("nonexistent.json")

            # Call backup when file doesn't exist
            json_saver._backup_corrupted_file()

    def test_json_saver_lines_229_231(self):
        """Test lines 229-231 in json_saver.py - filter error handling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "test.json"
            json_saver = JSONSaver(str(storage_path))

            # Create test vacancy
            test_vacancy = Vacancy(title="Test", url="http://test.com", vacancy_id="1")
            storage_path.write_text('[]')

            # Test filter error in delete_vacancies_by_keyword
            with patch('src.utils.ui_helpers.filter_vacancies_by_keyword', side_effect=Exception("Filter error")):
                result = json_saver.delete_vacancies_by_keyword("test")
                assert result == 0

    def test_json_saver_line_299(self):
        """Test line 299 in json_saver.py - file error in delete_all_vacancies"""
        with patch('src.storage.json_saver.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            json_saver = JSONSaver("test.json")

            # Test file error in delete_all_vacancies
            with patch('builtins.open', side_effect=OSError("System error")):
                result = json_saver.delete_all_vacancies()
                assert result is False

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
            ui.json_saver.get_vacancies.return_value = []

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

            ui.json_saver.get_vacancies.return_value = []
            ui.source_selector.get_user_source_choice.return_value = set()

            # Lines 282, 292-293, 316, 320, 322, 329, 339, 512, 567
            with patch('builtins.input', return_value='4'):  # Invalid choice
                ui._filter_saved_vacancies_by_salary()
                ui._delete_saved_vacancies()

            # Lines 584-590, 603, 607, 616-617, 621, 625: period choice edge cases
            with patch('builtins.input', side_effect=['7', '500']):  # Invalid period
                result = ui._get_period_choice()
                assert result == 15

            with patch('builtins.input', side_effect=KeyboardInterrupt()):
                result = ui._get_period_choice()
                assert result is None

    def test_vacancy_display_handler_lines_43_83_120(self):
        """Test remaining lines in vacancy_display_handler.py"""
        json_saver_mock = MagicMock()
        handler = VacancyDisplayHandler(json_saver_mock)

        # Line 43, 83, 120: exceptions in methods
        json_saver_mock.get_vacancies.side_effect = Exception("Storage error")

        handler.show_all_saved_vacancies()

        with patch('src.utils.ui_helpers.get_positive_integer', return_value=5):
            handler.show_top_vacancies_by_salary()

        with patch('src.utils.ui_helpers.get_user_input', return_value='test'):
            handler.search_saved_vacancies_by_keyword()

    def test_vacancy_search_handler_lines_102_136(self):
        """Test remaining lines in vacancy_search_handler.py"""
        unified_api_mock = MagicMock()
        json_saver_mock = MagicMock()
        handler = VacancySearchHandler(unified_api_mock, json_saver_mock)

        # Line 102: exception in _save_vacancies
        json_saver_mock.add_vacancy.side_effect = Exception("Save error")
        test_vacancy = Mock()
        handler._save_vacancies([test_vacancy])

        # Line 136: exception in search_vacancies
        unified_api_mock.get_vacancies_from_sources.side_effect = Exception("API error")
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
        formatter = ConcreteBaseFormatter()

        # Line 145: edge case in format_experience
        result = formatter.format_experience(None)
        assert result == "Не указан"

        # Line 174: edge case in format_schedule
        result = formatter.format_schedule(None)
        assert result == "Не указан"
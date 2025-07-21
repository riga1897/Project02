
import pytest
from unittest.mock import Mock, patch, MagicMock, call
import tempfile
import json
import os
from pathlib import Path
import time

from src.ui_interfaces.console_interface import UserInterface
from src.storage.json_saver import JSONSaver
from src.api_modules.cached_api import CachedAPI
from src.ui_interfaces.vacancy_display_handler import VacancyDisplayHandler
from src.ui_interfaces.vacancy_search_handler import VacancySearchHandler
from src.utils.base_formatter import BaseFormatter
from src.vacancies.models import Vacancy, Salary
from src.user_interface import main


class TestCachedAPI(CachedAPI):
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


class TestFormatter(BaseFormatter):
    """Concrete implementation for testing"""
    def format_vacancy_info(self, vacancy):
        return f"Test: {getattr(vacancy, 'title', 'Unknown')}"


class Test100PercentCoverage:
    """Comprehensive test to achieve 100% coverage"""

    def test_cached_api_exception_handling(self):
        """Test cached_api.py lines 66-72"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = TestCachedAPI(temp_dir)
            api.connector = Mock()
            
            # Mock _cached_api_request to raise exception to trigger lines 66-72
            with patch.object(api, '_cached_api_request', side_effect=Exception("Cache error")):
                with patch('src.api_modules.cached_api.logger') as mock_logger:
                    result = api._CachedAPI__connect_to_api("test_url", {"param": "value"}, "test")
                    assert result == api._get_empty_response()
                    mock_logger.error.assert_called_once()

    def test_json_saver_file_operations(self):
        """Test json_saver.py error handling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "test.json"
            saver = JSONSaver(str(storage_path))
            
            # Test lines 160-161: backup when file doesn't exist
            with patch('src.storage.json_saver.Path') as mock_path:
                mock_path_instance = Mock()
                mock_path.return_value = mock_path_instance
                mock_path_instance.exists.return_value = False
                saver._backup_corrupted_file()
            
            # Test lines 229-231: filter error handling
            storage_path.write_text('[]')
            with patch('src.utils.ui_helpers.filter_vacancies_by_keyword', side_effect=Exception("Filter error")):
                result = saver.delete_vacancies_by_keyword("test")
                assert result == 0
            
            # Test line 299: file error in delete_all_vacancies
            with patch('builtins.open', side_effect=OSError("File error")):
                result = saver.delete_all_vacancies()
                assert result is False

    def test_console_interface_comprehensive(self):
        """Test console_interface.py all problematic lines"""
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
            ui.json_saver = MagicMock()
            ui.search_handler = MagicMock()
            ui.display_handler = MagicMock()
            ui.vacancy_operations = MagicMock()
            
            # Lines 165-166: exception in _clear_api_cache
            ui.source_selector.get_user_source_choice.side_effect = Exception("Source error")
            ui._clear_api_cache()
            
            # Lines 217-219: empty input in _advanced_search_vacancies
            ui.source_selector.get_user_source_choice.side_effect = None
            ui.json_saver.get_vacancies.return_value = [Mock()]
            with patch('src.utils.ui_helpers.get_user_input', return_value=''):
                ui._advanced_search_vacancies()
            
            # Lines 236-237: exception in _advanced_search_vacancies
            ui.json_saver.get_vacancies.side_effect = Exception("Storage error")
            ui._advanced_search_vacancies()
            
            # Reset side effects
            ui.json_saver.get_vacancies.side_effect = None
            ui.json_saver.get_vacancies.return_value = []
            
            # Test filter salary menu invalid choices
            with patch('builtins.input', side_effect=['invalid', 'q']):
                ui._filter_saved_vacancies_by_salary()
            
            with patch('builtins.input', side_effect=['4', 'q']):
                ui._filter_saved_vacancies_by_salary()
            
            # Test delete vacancies invalid choices
            with patch('builtins.input', side_effect=['invalid', 'q']):
                ui._delete_saved_vacancies()
            
            with patch('builtins.input', side_effect=['4', 'q']):
                ui._delete_saved_vacancies()
            
            with patch('builtins.input', side_effect=['5', 'q']):
                ui._delete_saved_vacancies()
            
            # Test period choice edge cases
            with patch('builtins.input', side_effect=['7']):
                result = ui._get_period_choice()
                assert result == 15
            
            with patch('builtins.input', side_effect=['6', '500']):
                result = ui._get_period_choice()
                assert result == 15
            
            with patch('builtins.input', side_effect=KeyboardInterrupt()):
                result = ui._get_period_choice()
                assert result is None
            
            # Test pagination invalid input
            with patch('builtins.input', side_effect=['invalid', 'q']):
                ui._show_vacancies_for_deletion([], 'test')
            
            # Test specific lines in console_interface.py
            # Lines 282, 292-293, 316, 320, 322, 329, 339: various menu interactions
            with patch('builtins.input', side_effect=['invalid', '0']):
                ui._show_saved_vacancies_menu()
            
            # Lines 512, 567: specific menu handlers
            with patch('builtins.input', side_effect=['0']):
                ui._show_filter_menu()
            
            # Lines 584-590: period choice edge cases
            with patch('builtins.input', side_effect=['8', '0']):
                result = ui._get_period_choice()
                assert result is None
            
            # Lines 603, 607, 616-617, 621, 625: various input validations
            with patch('builtins.input', side_effect=['invalid', '0']):
                ui._show_advanced_search_menu()
            
            # Test run method with exceptions
            with patch.object(ui, '_show_menu', side_effect=KeyboardInterrupt()):
                ui.run()
            
            with patch.object(ui, '_show_menu', side_effect=[Exception("General error"), "0"]):
                ui.run()

    def test_vacancy_handlers_exceptions(self):
        """Test vacancy handlers exception paths"""
        # VacancyDisplayHandler tests
        json_saver_mock = MagicMock()
        display_handler = VacancyDisplayHandler(json_saver_mock)
        
        # Line 43: exception in show_all_saved_vacancies
        json_saver_mock.get_vacancies.side_effect = Exception("Storage error")
        display_handler.show_all_saved_vacancies()
        
        # Line 83: exception in search_saved_vacancies_by_keyword
        with patch('src.utils.ui_helpers.get_user_input', return_value='test'):
            display_handler.search_saved_vacancies_by_keyword()
        
        # Line 120: exception in show_top_vacancies_by_salary
        with patch('src.ui_interfaces.vacancy_display_handler.get_positive_integer', return_value=5):
            display_handler.show_top_vacancies_by_salary()
        
        # VacancySearchHandler tests
        unified_api_mock = MagicMock()
        search_handler = VacancySearchHandler(unified_api_mock, json_saver_mock)
        
        # Line 102: empty sources in search_vacancies
        with patch.object(search_handler.source_selector, 'get_user_source_choice', return_value=set()):
            search_handler.search_vacancies()
        
        # Line 136: None period in search_vacancies
        with patch.object(search_handler.source_selector, 'get_user_source_choice', return_value={'hh'}):
            with patch('src.ui_interfaces.vacancy_search_handler.get_user_input', return_value='test'):
                with patch.object(search_handler, '_get_period_choice', return_value=None):
                    search_handler.search_vacancies()

    def test_base_formatter_edge_cases(self):
        """Test base_formatter.py lines 145, 174"""
        formatter = TestFormatter()
        
        # Test line 145: currency mapping in _format_salary_dict
        salary_dict = {"from": 1000, "to": 2000, "currency": "USD"}
        result = formatter._format_salary_dict(salary_dict)
        assert "долл." in result
        
        # Test with EUR currency
        salary_dict = {"from": 1000, "to": 2000, "currency": "EUR"}
        result = formatter._format_salary_dict(salary_dict)
        assert "евро" in result
        
        # Test line 174: _extract_conditions with schedule fallback
        vacancy_mock = Mock()
        vacancy_mock.conditions = None
        vacancy_mock.schedule = "Полный день"
        
        result = formatter._extract_conditions(vacancy_mock)
        assert result == "График: Полный день"
        
        # Test with both conditions and schedule None
        vacancy_mock.conditions = None
        vacancy_mock.schedule = None
        result = formatter._extract_conditions(vacancy_mock)
        assert result is None

    def test_vacancy_models_edge_cases(self):
        """Test vacancy models lines 121-122, 185, 228, 230"""
        # Lines 121-122: float timestamp
        data_float = {
            'title': 'Test Job',
            'url': 'https://example.com',
            'published_at': 1640995200.5
        }
        vacancy = Vacancy.from_dict(data_float)
        assert vacancy.published_at is not None
        
        # Line 185: invalid date parsing
        data_invalid = {
            'title': 'Test Job',
            'url': 'https://example.com',
            'published_at': 'invalid_date'
        }
        vacancy = Vacancy.from_dict(data_invalid)
        assert vacancy.published_at is None
        
        # Line 185: Test date parsing with ValueError
        with patch('src.vacancies.models.datetime') as mock_datetime:
            mock_datetime.fromisoformat.side_effect = ValueError("Invalid date")
            mock_datetime.fromtimestamp.side_effect = ValueError("Invalid timestamp")
            
            data_invalid = {
                'title': 'Test Job',
                'url': 'https://example.com',
                'published_at': 'completely_invalid_date'
            }
            vacancy = Vacancy.from_dict(data_invalid)
            assert vacancy.published_at is None
        
        # Lines 228, 230: comparison operators __le__ and __ge__
        vacancy1 = Vacancy(title="Job1", url="http://test.com/1", salary={"from": 100000})
        vacancy2 = Vacancy(title="Job2", url="http://test.com/2", salary={"from": 150000})
        
        # Test __le__ (line 228)
        assert vacancy1 <= vacancy2
        assert vacancy1 <= vacancy1
        
        # Test __ge__ (line 230)  
        assert vacancy2 >= vacancy1
        assert vacancy1 >= vacancy1
        
        # Test Salary with empty data
        salary = Salary(salary_data={"from": None, "to": None})
        result = str(salary)
        assert "не указана" in result.lower()
        
        # Test Vacancy comparison with non-vacancy
        result = vacancy1.__eq__("not a vacancy")
        assert result is False

    def test_user_interface_main(self):
        """Test user_interface.py line 39"""
        with patch('src.user_interface.UserInterface') as mock_ui_class:
            mock_ui = mock_ui_class.return_value
            mock_ui.run.side_effect = Exception("Test exception")
            try:
                main()
            except Exception:
                pass
            mock_ui_class.assert_called_once()
            mock_ui.run.assert_called_once()

    def test_remaining_console_interface_lines(self):
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
            ui.vacancy_operations = MagicMock()
            
            # Line 282: invalid menu choice
            with patch('builtins.input', side_effect=['99', '0']):
                ui._show_saved_vacancies_menu()
            
            # Lines 292-293: various invalid inputs
            with patch('builtins.input', side_effect=['abc', '0']):
                ui._show_filter_menu()
            
            # Line 316: invalid choice handling
            with patch('builtins.input', side_effect=['-1', '0']):
                ui._show_advanced_search_menu()
            
            # Lines 320, 322: edge cases in menu navigation
            with patch('builtins.input', side_effect=['', '0']):
                ui._show_saved_vacancies_menu()
            
            # Line 329: invalid delete option
            with patch('builtins.input', side_effect=['10', 'q']):
                ui._delete_saved_vacancies()
            
            # Line 339: exception in vacancy operations
            ui.vacancy_operations.get_sorted_vacancies.side_effect = Exception("Error")
            with patch('builtins.input', side_effect=['0']):
                ui._show_top_vacancies_by_salary()
            
            # Line 512: filter menu edge case
            with patch('builtins.input', side_effect=['9', '0']):
                ui._show_filter_menu()
            
            # Line 567: advanced search edge case
            with patch('builtins.input', side_effect=['8', '0']):
                ui._show_advanced_search_menu()
            
            # Lines 584-590: period choice comprehensive test
            with patch('builtins.input', side_effect=['9', '0']):
                result = ui._get_period_choice()
                assert result is None
            
            # Lines 603, 607: pagination edge cases
            with patch('builtins.input', side_effect=['next', 'q']):
                ui._show_vacancies_for_deletion([], 'test')
            
            # Lines 616-617: keyboard interrupt handling
            with patch('builtins.input', side_effect=KeyboardInterrupt()):
                ui._show_vacancies_for_deletion([], 'test')
            
            # Lines 621, 625: additional edge cases
            with patch('builtins.input', side_effect=['invalid_page', 'q']):
                ui._show_vacancies_for_deletion([], 'test')

    def test_integration_workflow(self):
        """Full integration test"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "integration.json"
            json_saver = JSONSaver(str(storage_path))
            
            test_vacancy = Vacancy(
                title="Python Developer",
                url="https://example.com/job/123",
                vacancy_id="test_123",
                salary={"from": 100000, "to": 150000, "currency": "RUR"},
                employer={"name": "Test Company"},
                experience="1-3 года",
                description="Test description"
            )
            
            # Add and verify vacancy
            messages = json_saver.add_vacancy([test_vacancy])
            assert len(messages) > 0
            
            saved_vacancies = json_saver.get_vacancies()
            assert len(saved_vacancies) == 1
            assert saved_vacancies[0].title == "Python Developer"
            
            # Test formatter
            formatter = TestFormatter()
            formatted = formatter.format_vacancy_info(test_vacancy)
            assert "Python Developer" in formatted


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


class TestFormatter(BaseFormatter):
    """Concrete implementation for testing"""
    def format_vacancy_info(self, vacancy):
        return f"Test: {getattr(vacancy, 'title', 'Unknown')}"


class Test100PercentCoverage:
    """Comprehensive test to achieve 100% coverage"""

    def test_cached_api_exception_handling(self):
        """Test cached_api.py lines 66-72"""
        with tempfile.TemporaryDirectory() as temp_dir:
            api = ConcreteCachedAPI(temp_dir)
            api.connector = Mock()
            
            # Test the actual exception handling in __connect_to_api method
            with patch.object(api.connector, 'get', side_effect=Exception("Connection error")):
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
            saver.storage_path = Path(temp_dir) / "nonexistent.json"
            saver._backup_corrupted_file()  # Should handle non-existent file
            
            # Test lines 229-231: filter error handling  
            storage_path.write_text('[{"title": "test"}]')
            saver.storage_path = storage_path
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
            with patch('builtins.input', side_effect=['7']):  # Invalid choice returns default
                result = UserInterface._get_period_choice()
                assert result == 15
            
            with patch('builtins.input', side_effect=['6', '500']):
                result = UserInterface._get_period_choice()
                assert result == 15
            
            with patch('builtins.input', side_effect=KeyboardInterrupt()):
                result = UserInterface._get_period_choice()
                assert result is None
            
            # Test pagination invalid input
            with patch('builtins.input', side_effect=['invalid', 'q']):
                ui._show_vacancies_for_deletion([], 'test')
            
            # Test specific lines in console_interface.py
            # Lines 584-590: period choice edge cases
            with patch('builtins.input', side_effect=['8']):
                result = UserInterface._get_period_choice()
                assert result == 15
            
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
        
        # Reset side effect
        json_saver_mock.get_vacancies.side_effect = None
        
        # Line 43: empty vacancies in show_all_saved_vacancies  
        json_saver_mock.get_vacancies.return_value = []
        display_handler.show_all_saved_vacancies()
        
        # Line 83: empty vacancies in search_saved_vacancies_by_keyword
        with patch('src.utils.ui_helpers.get_user_input', return_value='test'):
            display_handler.search_saved_vacancies_by_keyword()
        
        # Line 120: empty vacancies in show_top_vacancies_by_salary
        with patch('src.ui_interfaces.vacancy_display_handler.get_positive_integer', return_value=5):
            display_handler.show_top_vacancies_by_salary()
        
        # VacancySearchHandler tests
        unified_api_mock = MagicMock()
        search_handler = VacancySearchHandler(unified_api_mock, json_saver_mock)
        
        # Line 102: empty sources in search_vacancies
        search_handler.source_selector.get_user_source_choice = Mock(return_value=set())
        search_handler.search_vacancies()
        
        # Line 136: None period in search_vacancies
        search_handler.source_selector.get_user_source_choice = Mock(return_value={'hh'})
        with patch('src.ui_interfaces.vacancy_search_handler.get_user_input', return_value='test'):
            with patch('src.ui_interfaces.vacancy_search_handler.UserInterface._get_period_choice', return_value=None):
                search_handler.search_vacancies()

    def test_base_formatter_edge_cases(self):
        """Test base_formatter.py lines 145, 174"""
        formatter = TestFormatter()
        
        # Test line 145: currency mapping in _format_salary_dict
        salary_dict = {"from": 1000, "to": 2000, "currency": "BYR"}  # Test unmapped currency
        result = formatter._format_salary_dict(salary_dict)
        assert "BYR" in result
        
        # Test EUR currency for line 145
        salary_dict = {"from": 1000, "to": 2000, "currency": "EUR"}
        result = formatter._format_salary_dict(salary_dict)
        assert "евро" in result
        
        # Test line 174: _extract_conditions with schedule when conditions is None
        vacancy_mock = Mock()
        vacancy_mock.conditions = None
        vacancy_mock.schedule = "Полный день"
        
        result = formatter._extract_conditions(vacancy_mock)
        assert result == "График: Полный день"
        
        # Test with both conditions and schedule None for line 174
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
        
        # Line 185: Test exception in _parse_datetime
        with patch('src.vacancies.models.datetime') as mock_datetime:
            mock_datetime.fromisoformat.side_effect = ValueError("Invalid ISO date")
            mock_datetime.fromtimestamp.side_effect = ValueError("Invalid timestamp")  
            mock_datetime.strptime.side_effect = ValueError("Invalid strptime format")
            
            # This should trigger the exception handling in line 185
            result = Vacancy._parse_datetime("invalid_date_string")
            assert result is None
        
        # Lines 228, 230: comparison operators __le__ and __ge__
        # Create vacancies with different salary values to test comparisons
        vacancy1 = Vacancy(title="Job1", url="http://test.com/1", salary={"from": 100000})
        vacancy2 = Vacancy(title="Job2", url="http://test.com/2", salary={"from": 150000})
        
        # Test __le__ (line 228) - should return NotImplemented and fall back to __ge__
        result = vacancy1.__le__(vacancy2)
        assert result is NotImplemented
        
        # Test __ge__ (line 230) - should return NotImplemented and fall back to __le__
        result = vacancy2.__ge__(vacancy1) 
        assert result is NotImplemented
        
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
            main()
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
            
            # Line 329: invalid delete option
            with patch('builtins.input', side_effect=['10', 'q']):
                ui._delete_saved_vacancies()
            
            # Lines 584-590: period choice comprehensive test
            with patch('builtins.input', side_effect=['9']):
                result = UserInterface._get_period_choice()
                assert result == 15
            
            # Lines 282, 292-293, 316, 320, 322: salary filter edge cases
            with patch('builtins.input', side_effect=['4', 'q']):  # Invalid choice 4
                ui._filter_saved_vacancies_by_salary()
            
            # Lines 329, 567: delete vacancies edge cases  
            with patch('builtins.input', side_effect=['10', 'q']):  # Invalid choice 10
                ui._delete_saved_vacancies()
            
            # Lines 603, 607: pagination edge cases
            vacancy_mock = Mock()
            vacancy_mock.vacancy_id = "test"
            vacancy_mock.title = "Test"
            vacancy_mock.employer = {"name": "Test"}
            vacancy_mock.salary = None
            vacancy_mock.url = "test.com"
            
            with patch('builtins.input', side_effect=['invalid', 'q']):
                ui._show_vacancies_for_deletion([vacancy_mock], 'test')
            
            # Lines 616-617: keyboard interrupt handling
            with patch('builtins.input', side_effect=KeyboardInterrupt()):
                try:
                    ui._show_vacancies_for_deletion([vacancy_mock], 'test')
                except KeyboardInterrupt:
                    pass  # Expected behavior
            
            # Lines 621, 625: additional edge cases
            with patch('builtins.input', side_effect=['999', 'q']):
                ui._show_vacancies_for_deletion([vacancy_mock], 'test')

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

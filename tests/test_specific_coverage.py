
import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
from pathlib import Path

from src.api_modules.cached_api import CachedAPI
from src.storage.json_saver import JSONSaver
from src.vacancies.models import Vacancy
from src.utils.base_formatter import BaseFormatter


class TestSpecificCoverage:
    """Tests for specific hard-to-reach code paths"""

    def test_cached_api_memory_cache_error(self):
        """Test memory cache error handling in cached_api.py"""
        
        class TestCachedAPI(CachedAPI):
            def _get_empty_response(self):
                return {"items": [], "found": 0}
            
            def _validate_vacancy(self, vacancy):
                return True
            
            def get_vacancies_page(self, search_query, page=0, **kwargs):
                return []
            
            def get_vacancies(self, search_query, **kwargs):
                return []

        with tempfile.TemporaryDirectory() as temp_dir:
            api = TestCachedAPI(temp_dir)
            
            # Mock the _cached_api_request to raise exception
            with patch.object(api, '_cached_api_request') as mock_cached:
                mock_cached.side_effect = Exception("Memory cache error")
                
                # This should trigger lines 66-72 in cached_api.py
                result = api._CachedAPI__connect_to_api("test_url", {}, "test")
                assert result == {"items": [], "found": 0}

    def test_json_saver_file_operations_errors(self):
        """Test file operation errors in json_saver.py"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "test.json"
            saver = JSONSaver(str(storage_path))
            
            vacancy = Vacancy(title="Test", url="http://test.com", vacancy_id="1")
            
            # Test _save_to_file with permission error (lines 160-161)
            with patch('builtins.open') as mock_open:
                mock_open.side_effect = PermissionError("No permission")
                
                try:
                    saver._save_to_file([vacancy])
                    assert False, "Should have raised exception"
                except PermissionError:
                    pass  # Expected
            
            # Test delete_vacancies_by_keyword with filter error (lines 229-231)
            with patch('src.utils.ui_helpers.filter_vacancies_by_keyword') as mock_filter:
                mock_filter.side_effect = Exception("Filter failed")
                
                result = saver.delete_vacancies_by_keyword("test")
                assert result == 0
            
            # Test delete_all_vacancies with OS error (line 299)
            with patch('builtins.open') as mock_open:
                mock_open.side_effect = OSError("OS Error")
                
                result = saver.delete_all_vacancies()
                assert result is False

    def test_vacancy_models_edge_cases(self):
        """Test edge cases in vacancy models"""
        
        # Test float timestamp handling (lines 121-122)
        data_float = {
            'title': 'Test',
            'url': 'http://test.com',
            'published_at': 1640995200.5  # float timestamp
        }
        vacancy = Vacancy.from_dict(data_float)
        assert vacancy.published_at is not None
        
        # Test invalid date parsing (line 185)
        data_invalid = {
            'title': 'Test',
            'url': 'http://test.com', 
            'published_at': 'not-a-date'
        }
        vacancy = Vacancy.from_dict(data_invalid)
        assert vacancy.published_at is None
        
        # Test comparison operators (lines 228, 230)
        v1 = Vacancy(title="A", url="http://a.com", salary={"from": 50000})
        v2 = Vacancy(title="B", url="http://b.com", salary={"from": 100000})
        
        # Test __le__ (less than or equal)
        assert v1 <= v2
        assert v1 <= v1
        
        # Test __ge__ (greater than or equal)
        assert v2 >= v1
        assert v2 >= v2

    def test_base_formatter_error_paths(self):
        """Test error handling in base_formatter.py"""
        
        class TestFormatter(BaseFormatter):
            def format_vacancy_info(self, vacancy, number=None):
                return "test"
        
        formatter = TestFormatter()
        
        # Test salary formatting with problematic data (line 174)
        # Test with None salary dict
        result = formatter._format_salary_dict(None)
        assert result == "Не указана"
        
        # Test with empty salary dict
        result = formatter._format_salary_dict({})
        assert result == "Не указана"
        
        # Test _extract_salary_info with non-dict salary (line 145)
        class MockVacancy:
            salary = "string_salary"
        
        vacancy = MockVacancy()
        result = formatter._extract_salary_info(vacancy)
        assert result == "string_salary"

    def test_ui_components_empty_states(self, mocker):
        """Test UI components with empty states"""
        from src.ui_interfaces.vacancy_display_handler import VacancyDisplayHandler
        from src.ui_interfaces.vacancy_search_handler import VacancySearchHandler
        
        # Test VacancyDisplayHandler with empty vacancies
        json_saver = Mock()
        json_saver.get_vacancies.return_value = []
        
        display_handler = VacancyDisplayHandler(json_saver)
        
        # Line 43: show_all_saved_vacancies with empty list
        display_handler.show_all_saved_vacancies()
        
        # Line 83: search_saved_vacancies_by_keyword with empty list  
        mocker.patch('src.utils.ui_helpers.get_user_input', return_value='test')
        display_handler.search_saved_vacancies_by_keyword()
        
        # Line 120: show_top_vacancies_by_salary with exception
        json_saver.get_vacancies.side_effect = Exception("Error")
        mocker.patch('src.ui_interfaces.vacancy_display_handler.get_positive_integer', return_value=5)
        display_handler.show_top_vacancies_by_salary()
        
        # Test VacancySearchHandler edge cases
        unified_api = Mock()
        json_saver_mock = Mock()
        search_handler = VacancySearchHandler(unified_api, json_saver_mock)
        
        # Line 102: empty source selection
        mocker.patch.object(search_handler.source_selector, 'get_user_source_choice', return_value=set())
        search_handler.search_vacancies()
        
        # Line 136: None period selection
        mocker.patch.object(search_handler.source_selector, 'get_user_source_choice', return_value={'hh'})
        mocker.patch('src.ui_interfaces.vacancy_search_handler.get_user_input', return_value='query')
        mocker.patch.object(search_handler, '_get_period_choice', return_value=None)
        search_handler.search_vacancies()

    def test_user_interface_main(self, mocker):
        """Test main function in user_interface.py (line 39)"""
        # Mock UserInterface class
        mock_ui_class = mocker.patch('src.user_interface.UserInterface')
        mock_ui_instance = Mock()
        mock_ui_class.return_value = mock_ui_instance
        
        # Import and call main
        from src.user_interface import main
        main()
        
        # Verify UserInterface was created and run was called
        mock_ui_class.assert_called_once()
        mock_ui_instance.run.assert_called_once()

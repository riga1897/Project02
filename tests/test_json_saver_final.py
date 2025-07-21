
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from src.storage.json_saver import JSONSaver
from src.vacancies.models import Vacancy


class TestJSONSaverFinal:
    """Tests for remaining uncovered lines in json_saver.py"""

    def test_line_160_161_file_not_exists(self):
        """Test lines 160-161 when backup file doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "test.json"
            json_saver = JSONSaver(str(storage_path))
            
            # Mock Path.exists to return False for backup scenario
            with patch('src.storage.json_saver.Path') as mock_path:
                mock_path_instance = MagicMock()
                mock_path.return_value = mock_path_instance
                mock_path_instance.exists.return_value = False
                
                # Call _backup_corrupted_file when file doesn't exist
                json_saver._backup_corrupted_file()

    def test_lines_229_231_permission_error(self):
        """Test lines 229-231 filter error handling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "test.json"
            json_saver = JSONSaver(str(storage_path))
            
            # Create a valid JSON file
            storage_path.write_text('[]')
            
            # Mock filter_vacancies_by_keyword to raise exception
            with patch('src.utils.ui_helpers.filter_vacancies_by_keyword', side_effect=Exception("Filter error")):
                result = json_saver.delete_vacancies_by_keyword("test")
                assert result == 0

    def test_line_299_backup_error(self):
        """Test line 299 file error handling in delete_all_vacancies"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "test.json"
            json_saver = JSONSaver(str(storage_path))
            
            # Mock file operations to fail
            with patch('builtins.open', side_effect=OSError("File error")):
                result = json_saver.delete_all_vacancies()
                assert result is False

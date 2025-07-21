
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.storage.json_saver import JSONSaver
from src.vacancies.models import Vacancy


class TestJSONSaverFinal:
    """Tests for remaining uncovered lines in json_saver.py"""

    def test_line_160_161_file_not_exists(self):
        """Test lines 160-161 when backup file doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "test.json"
            json_saver = JSONSaver(str(storage_path))
            
            # Ensure file doesn't exist to trigger lines 160-161
            if storage_path.exists():
                storage_path.unlink()
            
            # Call _backup_corrupted_file when file doesn't exist
            json_saver._backup_corrupted_file()

    def test_lines_229_231_permission_error(self):
        """Test lines 229-231 permission error handling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "test.json"
            json_saver = JSONSaver(str(storage_path))
            
            test_vacancy = Vacancy(title="Test", url="http://test.com", vacancy_id="1")
            
            # Mock permission error to trigger lines 229-231
            with patch('builtins.open', side_effect=PermissionError("Access denied")):
                json_saver._save_to_file([test_vacancy])

    def test_line_299_backup_error(self):
        """Test line 299 backup error handling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "test.json"
            json_saver = JSONSaver(str(storage_path))
            
            # Create a corrupted file
            with open(storage_path, 'w') as f:
                f.write("invalid json content")
            
            # Mock backup operation to fail
            with patch.object(json_saver, '_backup_corrupted_file', side_effect=Exception("Backup failed")):
                result = json_saver._load_from_file()
                assert result == []

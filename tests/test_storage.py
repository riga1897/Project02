
import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
from src.storage.json_saver import JSONSaver
from src.vacancies.models import Vacancy


class TestJSONSaver:
    
    @pytest.fixture
    def json_saver(self):
        return JSONSaver()
    
    @pytest.fixture
    def sample_vacancy(self):
        return Vacancy(
            id="123",
            name="Python Developer",
            url="https://example.com",
            salary_from=50000,
            salary_to=80000,
            currency="RUB",
            employer="Test Company",
            description="Test description",
            requirements="Python, Django",
            area="Moscow",
            published="2024-01-01",
            source="hh.ru"
        )
    
    def test_init(self, json_saver):
        assert json_saver is not None
        assert json_saver.filename == "data/storage/vacancies.json"
    
    def test_init_with_filename(self):
        saver = JSONSaver("test.json")
        assert saver.filename == "test.json"
    
    @patch('src.storage.json_saver.Path.exists')
    @patch('src.storage.json_saver.Path.read_text')
    def test_load_vacancies_file_exists(self, mock_read_text, mock_exists, json_saver):
        mock_exists.return_value = True
        mock_read_text.return_value = '[{"id": "123", "name": "Test"}]'
        
        result = json_saver.load_vacancies()
        assert isinstance(result, list)
        mock_read_text.assert_called_once()
    
    @patch('src.storage.json_saver.Path.exists')
    def test_load_vacancies_file_not_exists(self, mock_exists, json_saver):
        mock_exists.return_value = False
        
        result = json_saver.load_vacancies()
        assert result == []
    
    @patch('src.storage.json_saver.Path.exists')
    @patch('src.storage.json_saver.Path.read_text')
    def test_load_vacancies_json_error(self, mock_read_text, mock_exists, json_saver):
        mock_exists.return_value = True
        mock_read_text.return_value = 'invalid json'
        
        result = json_saver.load_vacancies()
        assert result == []
    
    @patch('src.storage.json_saver.Path.write_text')
    @patch('src.storage.json_saver.Path.mkdir')
    def test_save_vacancies(self, mock_mkdir, mock_write_text, json_saver, sample_vacancy):
        vacancies = [sample_vacancy]
        
        json_saver.save_vacancies(vacancies)
        
        mock_mkdir.assert_called_once()
        mock_write_text.assert_called_once()
    
    @patch('src.storage.json_saver.Path.write_text')
    @patch('src.storage.json_saver.Path.mkdir')
    def test_save_vacancies_error(self, mock_mkdir, mock_write_text, json_saver, sample_vacancy):
        mock_write_text.side_effect = Exception("Write error")
        vacancies = [sample_vacancy]
        
        # Should not raise exception
        json_saver.save_vacancies(vacancies)
    
    @patch('src.storage.json_saver.Path.exists')
    @patch('src.storage.json_saver.Path.unlink')
    def test_delete_file_exists(self, mock_unlink, mock_exists, json_saver):
        mock_exists.return_value = True
        
        result = json_saver.delete_file()
        assert result is True
        mock_unlink.assert_called_once()
    
    @patch('src.storage.json_saver.Path.exists')
    def test_delete_file_not_exists(self, mock_exists, json_saver):
        mock_exists.return_value = False
        
        result = json_saver.delete_file()
        assert result is False
    
    @patch('src.storage.json_saver.Path.exists')
    @patch('src.storage.json_saver.Path.unlink')
    def test_delete_file_error(self, mock_unlink, mock_exists, json_saver):
        mock_exists.return_value = True
        mock_unlink.side_effect = Exception("Delete error")
        
        result = json_saver.delete_file()
        assert result is False
    
    @patch('src.storage.json_saver.Path.exists')
    @patch('src.storage.json_saver.Path.stat')
    def test_get_file_size_exists(self, mock_stat, mock_exists, json_saver):
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 1024
        
        result = json_saver.get_file_size()
        assert result == 1024
    
    @patch('src.storage.json_saver.Path.exists')
    def test_get_file_size_not_exists(self, mock_exists, json_saver):
        mock_exists.return_value = False
        
        result = json_saver.get_file_size()
        assert result == 0

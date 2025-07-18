import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# Добавляем путь к исходному коду
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.json_saver import JSONSaver
from src.vacancies.models import Vacancy


class TestJSONSaver:

    @pytest.fixture
    def json_saver(self, tmp_path):
        """JSONSaver с временным файлом"""
        test_file = tmp_path / "test_vacancies.json"
        return JSONSaver(str(test_file))

    def test_init(self, json_saver):
        assert json_saver is not None
        assert isinstance(json_saver.filename, str)

    @patch('builtins.open', new_callable=mock_open, read_data='[{"id": "1", "title": "Test"}]')
    def test_load_from_file(self, mock_file, json_saver):
        result = json_saver.load_from_file()
        assert isinstance(result, list)
        assert len(result) == 1

    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.exists')
    def test_load_from_file_not_exists(self, mock_exists, mock_file, json_saver):
        mock_exists.return_value = False

        result = json_saver.load_from_file()
        assert result == []

    @patch('builtins.open', new_callable=mock_open)
    def test_save_to_file(self, mock_file, json_saver):
        test_data = [{"id": "1", "title": "Test"}]
        json_saver.save_to_file(test_data)
        mock_file.assert_called()

    def test_add_vacancy(self, json_saver):
        vacancy = Vacancy(
            vacancy_id="test_1",
            title="Test Vacancy",
            url="https://test.com",
            salary_from=50000,
            salary_to=80000,
            currency="RUR",
            employer="Test Company",
            description="Test description",
            requirements="Test requirements"
        )

        with patch.object(json_saver, 'save_to_file') as mock_save:
            json_saver.add_vacancy(vacancy)
            mock_save.assert_called_once()

    @patch('builtins.open', new_callable=mock_open, read_data='[{"vacancy_id": "1", "title": "Test"}]')
    def test_get_vacancies(self, mock_file, json_saver):
        result = json_saver.get_vacancies()
        assert isinstance(result, list)
        assert len(result) == 1

    @patch('builtins.open', new_callable=mock_open, read_data='[{"vacancy_id": "1", "title": "Test"}]')
    def test_get_vacancies_by_salary(self, mock_file, json_saver):
        result = json_saver.get_vacancies_by_salary(min_salary=1000)
        assert isinstance(result, list)

    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    def test_delete_vacancy(self, mock_file, json_saver):
        with patch.object(json_saver, 'save_to_file') as mock_save:
            json_saver.delete_vacancy("test_id")
            mock_save.assert_called_once()

    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    def test_clear_vacancies(self, mock_file, json_saver):
        with patch.object(json_saver, 'save_to_file') as mock_save:
            json_saver.clear_vacancies()
            mock_save.assert_called_once_with([])

import json
import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
from datetime import datetime

from src.storage.json_saver import JSONSaver
from src.vacancies.models import Vacancy
from src.utils.salary import Salary


class TestJSONSaver:
    """Упрощенные тесты для 100% покрытия JSONSaver"""

    @pytest.fixture
    def json_saver(self):
        with patch('src.storage.json_saver.JSONSaver._ensure_data_directory'), \
             patch('src.storage.json_saver.JSONSaver._ensure_file_exists'):
            return JSONSaver("test.json")

    @pytest.fixture
    def sample_vacancy(self):
        return Vacancy(
            title="Test",
            url="http://test.com",
            salary=None,
            description="desc",
            requirements="req",
            responsibilities="resp",
            employer={"name": "Test"},
            experience="1-3",
            employment="full",
            schedule="day",
            published_at="2024-01-01T12:00:00",
            vacancy_id="123"
            
        )

    # Инициализация
    def test_init_default(self):
        with patch('src.storage.json_saver.JSONSaver._ensure_data_directory'), \
             patch('src.storage.json_saver.JSONSaver._ensure_file_exists'):
            saver = JSONSaver()
            assert saver.filename == "data/storage/vacancies.json"

    def test_init_custom(self):
        with patch('src.storage.json_saver.JSONSaver._ensure_data_directory'), \
             patch('src.storage.json_saver.JSONSaver._ensure_file_exists'):
            saver = JSONSaver("custom.json")
            assert saver.filename == "custom.json"

    # Валидация
    def test_validate_filename_empty(self):
        result = JSONSaver._validate_filename("")
        assert result == "data/storage/vacancies.json"

    def test_validate_filename_none(self):
        result = JSONSaver._validate_filename(None)
        assert result == "data/storage/vacancies.json"

    def test_validate_filename_valid(self):
        result = JSONSaver._validate_filename("test.json")
        assert result == "test.json"

    # Загрузка вакансий
    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    def test_load_vacancies_empty(self, mock_file, json_saver):
        result = json_saver.load_vacancies()
        assert result == []

    @patch('builtins.open', new_callable=mock_open, read_data='')
    def test_load_vacancies_empty_content(self, mock_file, json_saver):
        result = json_saver.load_vacancies()
        assert result == []

    @patch('builtins.open', new_callable=mock_open, read_data='[{"id": "1", "title": "Test", "url": "test"}]')
    @patch('src.vacancies.models.Vacancy.from_dict')
    def test_load_vacancies_valid(self, mock_from_dict, mock_file, json_saver):
        mock_vacancy = Mock()
        mock_from_dict.return_value = mock_vacancy
        result = json_saver.load_vacancies()
        assert len(result) == 1

    @patch('builtins.open', new_callable=mock_open, read_data='invalid')
    @patch('src.storage.json_saver.JSONSaver._backup_corrupted_file')
    def test_load_vacancies_invalid_json(self, mock_backup, mock_file, json_saver):
        result = json_saver.load_vacancies()
        assert result == []
        mock_backup.assert_called_once()

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_vacancies_file_not_found(self, mock_file, json_saver):
        result = json_saver.load_vacancies()
        assert result == []

    @patch('builtins.open', new_callable=mock_open, read_data='{}')
    @patch('src.storage.json_saver.JSONSaver._backup_corrupted_file')
    def test_load_vacancies_not_list(self, mock_backup, mock_file, json_saver):
        result = json_saver.load_vacancies()
        assert result == []
        mock_backup.assert_called_once()

    # Добавление вакансий
    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    @patch('src.storage.json_saver.JSONSaver._save_to_file')
    def test_add_vacancy_new(self, mock_save, mock_file, json_saver, sample_vacancy):
        messages = json_saver.add_vacancy(sample_vacancy)
        assert len(messages) == 1
        assert "Добавлена новая вакансия" in messages[0]
        mock_save.assert_called_once()

    @patch('src.storage.json_saver.JSONSaver.load_vacancies')
    @patch('src.storage.json_saver.JSONSaver._save_to_file')
    def test_add_vacancy_update(self, mock_save, mock_load, json_saver, sample_vacancy):
        existing = Mock()
        existing.vacancy_id = "123"
        existing.title = "Old"
        existing.url = "old"
        existing.salary = None
        existing.description = "old"
        existing.updated_at = "old"
        
        mock_load.return_value = [existing]
        messages = json_saver.add_vacancy(sample_vacancy)
        assert len(messages) == 1
        assert "обновлена" in messages[0]
        mock_save.assert_called_once()

    @patch('src.storage.json_saver.JSONSaver.load_vacancies')
    def test_add_vacancy_no_changes(self, mock_load, json_saver, sample_vacancy):
        existing = Mock()
        existing.vacancy_id = "123"
        existing.title = "Test"
        existing.url = "http://test.com"
        existing.salary = None
        existing.description = "desc"
        existing.updated_at = "2024-01-01T12:00:00"
        
        mock_load.return_value = [existing]
        messages = json_saver.add_vacancy(sample_vacancy)
        assert len(messages) == 0

    # Удаление
    @patch('builtins.open', new_callable=mock_open)
    def test_delete_all_success(self, mock_file, json_saver):
        result = json_saver.delete_all_vacancies()
        assert result is True

    @patch('builtins.open', side_effect=Exception)
    def test_delete_all_error(self, mock_file, json_saver):
        result = json_saver.delete_all_vacancies()
        assert result is False

    @patch('src.storage.json_saver.JSONSaver.load_vacancies')
    @patch('src.storage.json_saver.JSONSaver._save_to_file')
    def test_delete_by_id_success(self, mock_save, mock_load, json_saver, sample_vacancy):
        mock_load.return_value = [sample_vacancy]
        result = json_saver.delete_vacancy_by_id("123")
        assert result is True
        mock_save.assert_called_once()

    @patch('src.storage.json_saver.JSONSaver.load_vacancies')
    def test_delete_by_id_not_found(self, mock_load, json_saver, sample_vacancy):
        mock_load.return_value = [sample_vacancy]
        result = json_saver.delete_vacancy_by_id("999")
        assert result is False

    @patch('src.storage.json_saver.JSONSaver.load_vacancies', side_effect=Exception)
    def test_delete_by_id_error(self, mock_load, json_saver):
        result = json_saver.delete_vacancy_by_id("123")
        assert result is False

    @patch('src.utils.ui_helpers.filter_vacancies_by_keyword')
    @patch('src.storage.json_saver.JSONSaver.load_vacancies')
    @patch('src.storage.json_saver.JSONSaver._save_to_file')
    def test_delete_by_keyword_success(self, mock_save, mock_load, mock_filter, json_saver, sample_vacancy):
        mock_filter.return_value = [sample_vacancy]
        mock_load.return_value = [sample_vacancy]
        result = json_saver.delete_vacancies_by_keyword("test")
        assert result == 1
        mock_save.assert_called_once()

    @patch('src.utils.ui_helpers.filter_vacancies_by_keyword', return_value=[])
    @patch('src.storage.json_saver.JSONSaver.load_vacancies')
    def test_delete_by_keyword_no_matches(self, mock_load, mock_filter, json_saver, sample_vacancy):
        mock_load.return_value = [sample_vacancy]
        result = json_saver.delete_vacancies_by_keyword("java")
        assert result == 0

    @patch('src.storage.json_saver.JSONSaver.load_vacancies', side_effect=Exception)
    def test_delete_by_keyword_error(self, mock_load, json_saver):
        result = json_saver.delete_vacancies_by_keyword("test")
        assert result == 0

    # Сохранение
    @patch('builtins.open', new_callable=mock_open)
    def test_save_to_file_success(self, mock_file, json_saver, sample_vacancy):
        json_saver._save_to_file([sample_vacancy])
        mock_file.assert_called()

    def test_save_to_file_invalid(self, json_saver):
        invalid = Mock(spec=[])  # Без to_dict
        with patch('builtins.open', new_callable=mock_open):
            json_saver._save_to_file([invalid])

    def test_save_to_file_missing_fields(self, json_saver):
        invalid_vacancy = Mock()
        invalid_vacancy.to_dict = Mock(return_value={'wrong': 'data'})
        with patch('builtins.open', new_callable=mock_open):
            json_saver._save_to_file([invalid_vacancy])

    # Утилиты
    @patch('pathlib.Path.stat')
    @patch('pathlib.Path.exists', return_value=True)
    def test_get_file_size_success(self, mock_exists, mock_stat, json_saver):
        mock_stat.return_value.st_size = 1024
        size = json_saver.get_file_size()
        assert size == 1024

    @patch('pathlib.Path.exists', return_value=False)
    def test_get_file_size_not_exists(self, mock_exists, json_saver):
        size = json_saver.get_file_size()
        assert size == 0

    @patch('pathlib.Path.exists', side_effect=Exception)
    def test_get_file_size_error(self, mock_exists, json_saver):
        size = json_saver.get_file_size()
        assert size == 0

    def test_backup_corrupted_success(self, json_saver):
        with patch('pathlib.Path.exists', return_value=True), \
             patch('shutil.copy2'), \
             patch('builtins.open', new_callable=mock_open):
            json_saver._backup_corrupted_file()

    def test_backup_corrupted_error(self, json_saver):
        with patch('pathlib.Path.exists', side_effect=Exception):
            json_saver._backup_corrupted_file()

    def test_parse_date_valid(self, json_saver):
        result = json_saver._parse_date("2024-01-01T12:00:00+00:00")
        assert isinstance(result, datetime)

    def test_parse_date_invalid(self, json_saver):
        result = json_saver._parse_date("invalid")
        assert result == datetime.min

    def test_ensure_json_serializable_dict(self, json_saver):
        result = json_saver._ensure_json_serializable({"key": "value"})
        assert result == {"key": "value"}

    def test_ensure_json_serializable_list(self, json_saver):
        result = json_saver._ensure_json_serializable(["a", 1])
        assert result == ["a", 1]

    def test_ensure_json_serializable_object(self, json_saver):
        obj = Mock()
        obj.__str__ = Mock(return_value="test")
        result = json_saver._ensure_json_serializable(obj)
        assert result == "test"

    def test_vacancy_to_dict_with_salary(self, json_saver):
        vacancy = Mock()
        salary_mock = Mock()
        salary_mock.salary_from = 100
        salary_mock.salary_to = 200
        salary_mock.currency = "RUB"
        
        vacancy.salary = salary_mock
        vacancy.title = "Test"
        vacancy.url = "test"
        vacancy.description = "desc"
        vacancy.requirements = "req"
        vacancy.responsibilities = "resp"
        vacancy.experience = "1-3"
        vacancy.employment = "full"
        vacancy.schedule = "day"
        vacancy.employer = {"name": "Test"}
        vacancy.vacancy_id = "123"
        vacancy.published_at = "2024-01-01"

        result = json_saver._vacancy_to_dict(vacancy)
        assert result['salary']['from'] == 100

    def test_vacancy_to_dict_no_salary(self, json_saver):
        vacancy = Mock()
        vacancy.salary = None
        vacancy.title = "Test"
        vacancy.url = "test"
        vacancy.description = "desc"
        vacancy.requirements = "req"
        vacancy.responsibilities = "resp"
        vacancy.experience = "1-3"
        vacancy.employment = "full"
        vacancy.schedule = "day"
        vacancy.employer = {"name": "Test"}
        vacancy.vacancy_id = "123"
        vacancy.published_at = "2024-01-01"

        result = json_saver._vacancy_to_dict(vacancy)
        assert result['salary'] is None

    @patch('src.storage.json_saver.JSONSaver.load_vacancies', return_value=[])
    def test_get_vacancies_delegates(self, mock_load, json_saver):
        result = json_saver.get_vacancies()
        mock_load.assert_called_once()
        assert result == []

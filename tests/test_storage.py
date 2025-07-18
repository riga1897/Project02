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

    @patch('builtins.open', new_callable=mock_open, read_data='[{"vacancy_id": "1", "title": "Test"}]')
    def test_load_vacancies(self, mock_file, json_saver):
        result = json_saver.load_vacancies()
        assert isinstance(result, list)

    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.exists')
    def test_load_vacancies_not_exists(self, mock_exists, mock_file, json_saver):
        mock_exists.return_value = False

        result = json_saver.load_vacancies()
        assert result == []

    @patch('builtins.open', new_callable=mock_open)
    def test_save_vacancies(self, mock_file, json_saver):
        vacancy = Vacancy(
            vacancy_id="test_1",
            title="Test Vacancy",
            url="https://test.com",
            salary=None,
            employer="Test Company",
            description="Test description",
            requirements="Test requirements"
        )
        json_saver._save_to_file([vacancy])
        mock_file.assert_called()

    def test_add_vacancy(self, json_saver):
        vacancy = Vacancy(
            vacancy_id="test_1",
            title="Test Vacancy",
            url="https://test.com",
            salary=None,
            employer="Test Company",
            description="Test description",
            requirements="Test requirements"
        )

        with patch('src.storage.json_saver.JSONSaver.load_vacancies', return_value=[]):
            with patch('src.storage.json_saver.JSONSaver._save_to_file') as mock_save:
                json_saver.add_vacancy(vacancy)
                mock_save.assert_called_once()

    @patch('builtins.open', new_callable=mock_open, read_data='[{"vacancy_id": "1", "title": "Test"}]')
    def test_get_vacancies(self, mock_file, json_saver):
        result = json_saver.get_vacancies()
        assert isinstance(result, list)

    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    def test_delete_vacancy_by_id(self, mock_file, json_saver):
        with patch('src.storage.json_saver.JSONSaver.load_vacancies', return_value=[]):
            with patch('src.storage.json_saver.JSONSaver._save_to_file') as mock_save:
                result = json_saver.delete_vacancy_by_id("test_id")
                assert isinstance(result, bool)

    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    def test_delete_all_vacancies(self, mock_file, json_saver):
        result = json_saver.delete_all_vacancies()
        assert isinstance(result, bool)
import pytest
import sys
import json
from pathlib import Path
from unittest.mock import patch, mock_open

# Добавляем путь к исходному коду
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.abstract import AbstractVacancyStorage
from src.storage.json_saver import JSONSaver


class TestAbstractVacancyStorage:
    
    def test_abstract_methods(self):
        # Тест что нельзя создать экземпляр абстрактного класса
        with pytest.raises(TypeError):
            AbstractVacancyStorage()


class TestJSONSaver:
    
    @pytest.fixture
    def temp_json_file(self, tmp_path):
        """Создает временный JSON файл"""
        json_file = tmp_path / "test_vacancies.json"
        return str(json_file)
    
    @pytest.fixture
    def json_saver(self, temp_json_file):
        return JSONSaver(temp_json_file)
    
    def test_init(self, json_saver, temp_json_file):
        assert json_saver.filename == temp_json_file
    
    def test_save_and_load_basic(self, json_saver):
        # Тест базового сохранения и загрузки с реальными объектами Vacancy
        from src.vacancies.models import Vacancy
        
        vacancy = Vacancy(
            vacancy_id="test_1",
            title="Test Job",
            url="http://test.com",
            salary=None,
            employer="Test Company",
            description="Test description",
            requirements="Test requirements"
        )
        
        json_saver.add_vacancy(vacancy)
        loaded_data = json_saver.get_vacancies()
        
        assert len(loaded_data) == 1
        assert loaded_data[0].vacancy_id == "test_1"
    
    def test_load_empty_file(self, json_saver):
        # Тест загрузки из несуществующего файла
        result = json_saver.load_vacancies()
        assert result == []
    
    def test_delete_vacancy(self, json_saver):
        # Тест удаления вакансии
        from src.vacancies.models import Vacancy
        
        vacancy = Vacancy(
            vacancy_id="test_delete",
            title="Test Job",
            url="http://test.com",
            salary=None,
            employer="Test Company",
            description="Test description",
            requirements="Test requirements"
        )
        
        json_saver.add_vacancy(vacancy)
        result = json_saver.delete_vacancy_by_id("test_delete")
        assert result is True
        
        loaded_data = json_saver.get_vacancies()
        assert len(loaded_data) == 0
    
    def test_file_creation(self, json_saver):
        # Тест создания файла
        from src.vacancies.models import Vacancy
        
        vacancy = Vacancy(
            vacancy_id="test_create",
            title="Test Job",
            url="http://test.com",
            salary=None,
            employer="Test Company",
            description="Test description",
            requirements="Test requirements"
        )
        
        json_saver.add_vacancy(vacancy)
        assert Path(json_saver.filename).exists()


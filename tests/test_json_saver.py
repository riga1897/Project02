import pytest
from unittest.mock import patch, MagicMock
from src.storage.json_saver import JSONSaver
from src.vacancies.models import Vacancy


class TestJSONSaver:
    """Тесты для JSONSaver"""

    @pytest.fixture
    def mock_file_handler(self):
        """Мокируем файловый обработчик"""
        with patch('src.storage.json_saver.json_handler') as mock:
            mock.read_json.return_value = []
            yield mock

    @pytest.fixture
    def sample_vacancy(self):
        """Тестовая вакансия"""
        return Vacancy(
            title="Python Developer",
            url="http://example.com",
            salary="100000",
            description="Test description",
            vacancy_id="test_id_1"
        )

    def test_add_vacancy(self, mock_file_handler, sample_vacancy):
        """Тест добавления вакансии"""
        saver = JSONSaver("test.json")
        saver.add_vacancy(sample_vacancy)

        written_data = mock_file_handler.write_json.call_args[0][1]
        assert len(written_data) == 1
        assert written_data[0]["id"] == "test_id_1"

    def test_get_vacancies(self, mock_file_handler):
        """Тест получения вакансий"""
        saver = JSONSaver("test.json")
        mock_file_handler.read_json.return_value = [{
            "id": "1",
            "title": "Python",
            "url": "http://test.com",
            "salary": "100000",
            "description": "Test"
        }]

        vacancies = list(saver.get_vacancies())
        assert len(vacancies) == 1
        assert vacancies[0].title == "Python"
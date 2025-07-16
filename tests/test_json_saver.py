import pytest
from unittest.mock import patch, MagicMock
from src.storage.json_saver import JSONSaver
from src.vacancies.models import Vacancy


class TestJSONSaver:
    @pytest.fixture
    def mock_file_handler(self):
        with patch('src.storage.json_saver.json_handler') as mock:
            mock.read_json.return_value = []
            yield mock

    def test_add_vacancy(self, mock_file_handler):
        saver = JSONSaver()
        vacancy = Vacancy(
            title="Test",
            url="http://test.com",
            salary={"from": 100000},
            description="Test"
        )

        saver.add_vacancy(vacancy)
        written_data = mock_file_handler.write_json.call_args[0][1]

        assert len(written_data) == 1
        assert written_data[0]["title"] == "Test"
        assert written_data[0]["salary"]["from"] == 100000

    def test_get_vacancies_with_filter(self, mock_file_handler):
        mock_file_handler.read_json.return_value = [
            {
                "id": "1",
                "title": "Python",
                "url": "http://python.com",
                "salary": {"from": 100000},
                "description": "Desc"
            },
            {
                "id": "2",
                "title": "Java",
                "url": "http://java.com",
                "salary": {"from": 90000},
                "description": "Desc"
            }
        ]

        saver = JSONSaver()
        result = list(saver.get_vacancies({"salary__gt": 95000}))

        assert len(result) == 1
        assert result[0].title == "Python"

    def test_delete_vacancy(self, mock_file_handler):
        mock_file_handler.read_json.return_value = [
            {"id": "1", "title": "A", "url": "http://a.com", "salary": None, "description": ""},
            {"id": "2", "title": "B", "url": "http://b.com", "salary": None, "description": ""}
        ]

        saver = JSONSaver()
        saver.delete_vacancy("1")

        written_data = mock_file_handler.write_json.call_args[0][1]
        assert len(written_data) == 1
        assert written_data[0]["id"] == "2"
        
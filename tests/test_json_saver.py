
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.storage.json_saver import JSONSaver
from src.vacancies.models import Vacancy


class TestJSONSaver:
    """Comprehensive tests for JSONSaver"""

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

    @pytest.fixture
    def sample_data(self):
        """Тестовые данные в формате JSON"""
        return [
            {
                "id": "1",
                "title": "Python Developer",
                "url": "http://test.com",
                "salary": "100000",
                "description": "Python desc"
            },
            {
                "id": "2", 
                "title": "Java Developer",
                "url": "http://test2.com",
                "salary": "120000",
                "description": "Java desc"
            }
        ]

    def test_add_vacancy(self, mock_file_handler, sample_vacancy):
        """Тест добавления вакансии"""
        saver = JSONSaver("test.json")
        saver.add_vacancy(sample_vacancy)

        written_data = mock_file_handler.write_json.call_args[0][1]
        assert len(written_data) == 1
        assert written_data[0]["id"] == "test_id_1"

    def test_add_multiple_vacancies(self, mock_file_handler):
        """Тест добавления списка вакансий"""
        saver = JSONSaver("test.json")
        vacancies = [
            Vacancy("Python Dev", "http://test1.com", "100000", "Desc1", "id1"),
            Vacancy("Java Dev", "http://test2.com", "120000", "Desc2", "id2")
        ]
        
        saver.add_vacancy(vacancies)
        written_data = mock_file_handler.write_json.call_args[0][1]
        assert len(written_data) == 2

    def test_add_vacancy_without_id_error(self, mock_file_handler):
        """Тест ошибки при добавлении вакансии без vacancy_id"""
        saver = JSONSaver("test.json")
        vacancy = Vacancy("Test", "http://test.com", "1000", "Desc")
        # Удаляем атрибут vacancy_id полностью
        delattr(vacancy, 'vacancy_id')
        
        with pytest.raises(ValueError, match="Вакансия должна иметь атрибут vacancy_id"):
            saver.add_vacancy(vacancy)

    def test_add_duplicate_vacancy_error(self, mock_file_handler, sample_data):
        """Тест ошибки при добавлении дублирующей вакансии"""
        mock_file_handler.read_json.return_value = sample_data
        saver = JSONSaver("test.json")
        
        duplicate_vacancy = Vacancy("New Title", "http://new.com", "90000", "New desc", "1")
        
        with pytest.raises(ValueError, match="Вакансия с ID 1 уже существует"):
            saver.add_vacancy(duplicate_vacancy)

    def test_get_vacancies_without_filters(self, mock_file_handler, sample_data):
        """Тест получения всех вакансий без фильтров"""
        mock_file_handler.read_json.return_value = sample_data
        saver = JSONSaver("test.json")
        
        vacancies = list(saver.get_vacancies())
        assert len(vacancies) == 2
        assert vacancies[0].title == "Python Developer"

    def test_get_vacancies_with_simple_filter(self, mock_file_handler, sample_data):
        """Тест фильтрации по простому критерию"""
        mock_file_handler.read_json.return_value = sample_data
        saver = JSONSaver("test.json")
        
        vacancies = list(saver.get_vacancies({"title": "Python Developer"}))
        assert len(vacancies) == 1
        assert vacancies[0].title == "Python Developer"

    def test_get_vacancies_with_contains_filter(self, mock_file_handler, sample_data):
        """Тест фильтрации с оператором contains"""
        mock_file_handler.read_json.return_value = sample_data
        saver = JSONSaver("test.json")
        # Добавляем 'title' в allowed_filters для операторов
        saver.allowed_filters.add("title__contains")
        
        vacancies = list(saver.get_vacancies({"title__contains": "Developer"}))
        assert len(vacancies) == 2

    def test_get_vacancies_with_gt_filter(self, mock_file_handler, sample_data):
        """Тест фильтрации с оператором gt"""
        mock_file_handler.read_json.return_value = sample_data
        saver = JSONSaver("test.json")
        saver.allowed_filters.add("salary__gt")
        
        vacancies = list(saver.get_vacancies({"salary__gt": "110000"}))
        assert len(vacancies) == 1
        assert vacancies[0].title == "Java Developer"

    def test_get_vacancies_with_lt_filter(self, mock_file_handler, sample_data):
        """Тест фильтрации с оператором lt"""
        mock_file_handler.read_json.return_value = sample_data
        saver = JSONSaver("test.json")
        saver.allowed_filters.add("salary__lt")
        
        vacancies = list(saver.get_vacancies({"salary__lt": "110000"}))
        assert len(vacancies) == 1
        assert vacancies[0].title == "Python Developer"

    def test_invalid_filter_error(self, mock_file_handler):
        """Тест ошибки при недопустимом фильтре"""
        saver = JSONSaver("test.json")
        
        with pytest.raises(ValueError, match="Недопустимые фильтры"):
            list(saver.get_vacancies({"invalid_field": "value"}))

    def test_invalid_operator_error(self, mock_file_handler, sample_data):
        """Тест ошибки при неизвестном операторе"""
        mock_file_handler.read_json.return_value = sample_data
        saver = JSONSaver("test.json")
        saver.allowed_filters.add("title__unknown")
        
        with pytest.raises(ValueError, match="Неизвестный оператор"):
            list(saver.get_vacancies({"title__unknown": "value"}))

    def test_delete_vacancy(self, mock_file_handler, sample_data):
        """Тест удаления вакансии"""
        mock_file_handler.read_json.return_value = sample_data
        saver = JSONSaver("test.json")
        
        saver.delete_vacancy("1")
        written_data = mock_file_handler.write_json.call_args[0][1]
        assert len(written_data) == 1
        assert written_data[0]["id"] == "2"

    def test_delete_nonexistent_vacancy_error(self, mock_file_handler, sample_data):
        """Тест ошибки при удалении несуществующей вакансии"""
        mock_file_handler.read_json.return_value = sample_data
        saver = JSONSaver("test.json")
        
        with pytest.raises(ValueError, match="Вакансия с ID nonexistent не найдена"):
            saver.delete_vacancy("nonexistent")

    def test_update_vacancy(self, mock_file_handler, sample_data):
        """Тест обновления вакансии"""
        mock_file_handler.read_json.return_value = sample_data
        saver = JSONSaver("test.json")
        
        saver.update_vacancy("1", {"salary": "150000", "description": "Updated desc"})
        written_data = mock_file_handler.write_json.call_args[0][1]
        
        updated_vacancy = next(item for item in written_data if item["id"] == "1")
        assert updated_vacancy["salary"] == "150000"
        assert updated_vacancy["description"] == "Updated desc"

    def test_update_vacancy_invalid_fields_error(self, mock_file_handler, sample_data):
        """Тест ошибки при обновлении недопустимых полей"""
        mock_file_handler.read_json.return_value = sample_data
        saver = JSONSaver("test.json")
        
        with pytest.raises(ValueError, match="Нельзя изменить поля"):
            saver.update_vacancy("1", {"title": "New Title"})

    def test_update_nonexistent_vacancy_error(self, mock_file_handler, sample_data):
        """Тест ошибки при обновлении несуществующей вакансии"""
        mock_file_handler.read_json.return_value = sample_data
        saver = JSONSaver("test.json")
        
        with pytest.raises(ValueError, match="Вакансия с ID nonexistent не найдена"):
            saver.update_vacancy("nonexistent", {"salary": "150000"})

    def test_get_vacancy_by_id(self, mock_file_handler, sample_data):
        """Тест получения вакансии по ID"""
        mock_file_handler.read_json.return_value = sample_data
        saver = JSONSaver("test.json")
        
        vacancy = saver.get_vacancy_by_id("1")
        assert vacancy is not None
        assert vacancy.title == "Python Developer"

    def test_get_vacancy_by_id_not_found(self, mock_file_handler, sample_data):
        """Тест получения несуществующей вакансии по ID"""
        mock_file_handler.read_json.return_value = sample_data
        saver = JSONSaver("test.json")
        
        vacancy = saver.get_vacancy_by_id("nonexistent")
        assert vacancy is None

    def test_initialization_creates_file(self):
        """Тест создания файла при инициализации"""
        with patch('pathlib.Path.touch') as mock_touch:
            JSONSaver("new_file.json")
            mock_touch.assert_called_once_with(exist_ok=True)

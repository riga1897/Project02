
import json
import pytest
from typing import Optional
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
from datetime import datetime

from src.storage.json_saver import JSONSaver
from src.vacancies.models import Vacancy
from src.utils.salary import Salary


class TestJSONSaver:
    """Тесты для класса JSONSaver с использованием моков"""

    @pytest.fixture
    def json_saver(self):
        """Фикстура для создания экземпляра JSONSaver"""
        with patch('src.storage.json_saver.JSONSaver._ensure_data_directory'), \
             patch('src.storage.json_saver.JSONSaver._ensure_file_exists'):
            return JSONSaver("test_vacancies.json")

    @pytest.fixture
    def sample_vacancy(self):
        """Фикстура с примером вакансии"""
        salary = Salary({
            "from": 100000,
            "to": 150000,
            "currency": "RUB",
            "period": "месяц"
        })
        
        return Vacancy(
            vacancy_id="123",
            title="Python разработчик",
            url="https://example.com/vacancy/123",
            salary=salary.to_dict(),
            description="Описание вакансии",
            requirements="Требования",
            responsibilities="Обязанности",
            employer={"name": "Тестовая компания"},
            experience="От 1 года до 3 лет",
            employment="Полная занятость",
            schedule="Полный день",
            published_at=datetime.now().isoformat(),
            source="test",
            area={"name": "Москва"}
        )

    @pytest.fixture
    def sample_vacancies_data(self):
        """Фикстура с тестовыми данными вакансий в формате JSON"""
        return [
            {
                "vacancy_id": "123",
                "title": "Python разработчик",
                "url": "https://example.com/vacancy/123",
                "salary": {
                    "from": 100000,
                    "to": 150000,
                    "currency": "RUB",
                    "period": "месяц"
                },
                "description": "Описание вакансии",
                "requirements": "Требования",
                "responsibilities": "Обязанности",
                "employer": {"name": "Тестовая компания"},
                "experience": "От 1 года до 3 лет",
                "employment": "Полная занятость",
                "schedule": "Полный день",
                "published_at": "2024-01-01T12:00:00",
                "source": "test",
                "area": {"name": "Москва"}
            },
            {
                "vacancy_id": "456",
                "title": "Java разработчик",
                "url": "https://example.com/vacancy/456",
                "salary": None,
                "description": "Описание Java вакансии",
                "requirements": "Java требования",
                "responsibilities": "Java обязанности",
                "employer": {"name": "Java компания"},
                "experience": "От 3 до 6 лет",
                "employment": "Частичная занятость",
                "schedule": "Гибкий график",
                "published_at": "2024-01-02T12:00:00",
                "source": "test",
                "area": {"name": "Санкт-Петербург"}
            }
        ]

    def test_init_default_filename(self):
        """Тест инициализации с дефолтным именем файла"""
        with patch('src.storage.json_saver.JSONSaver._ensure_data_directory'), \
             patch('src.storage.json_saver.JSONSaver._ensure_file_exists'):
            saver = JSONSaver()
            assert saver.filename == "data/storage/vacancies.json"

    def test_init_custom_filename(self):
        """Тест инициализации с кастомным именем файла"""
        with patch('src.storage.json_saver.JSONSaver._ensure_data_directory'), \
             patch('src.storage.json_saver.JSONSaver._ensure_file_exists'):
            saver = JSONSaver("custom.json")
            assert saver.filename == "custom.json"

    def test_validate_filename_empty(self):
        """Тест валидации пустого имени файла"""
        result = JSONSaver._validate_filename("")
        assert result == "data/storage/vacancies.json"

    def _validate_filename(self, filename: Optional[str]) -> str:
        if not filename:
            return "data/storage/vacancies.json"
        return filename

    def test_validate_filename_valid(self):
        """Тест валидации корректного имени файла"""
        result = JSONSaver._validate_filename("test.json")
        assert result == "test.json"

    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_vacancies_empty_file(self, mock_exists, mock_file, json_saver):
        """Тест загрузки из пустого файла"""
        vacancies = json_saver.load_vacancies()
        assert vacancies == []

    @patch('builtins.open', new_callable=mock_open, read_data='')
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_vacancies_empty_content(self, mock_exists, mock_file, json_saver):
        """Тест загрузки из файла с пустым содержимым"""
        vacancies = json_saver.load_vacancies()
        assert vacancies == []

    @patch('builtins.open', new_callable=mock_open)
    def test_load_vacancies_valid_data(self, mock_file, json_saver, sample_vacancies_data):
        """Тест загрузки корректных данных"""
        mock_file.return_value.read.return_value = json.dumps(sample_vacancies_data)
        
        with patch('src.vacancies.models.Vacancy.from_dict') as mock_from_dict:
            mock_vacancy = Mock()
            mock_from_dict.return_value = mock_vacancy
            
            vacancies = json_saver.load_vacancies()
            
            assert len(vacancies) == 2
            assert mock_from_dict.call_count == 2

    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_vacancies_invalid_json(self, mock_exists, mock_file, json_saver):
        """Тест загрузки при некорректном JSON"""
        with patch.object(json_saver, '_backup_corrupted_file') as mock_backup:
            vacancies = json_saver.load_vacancies()
            assert vacancies == []
            mock_backup.assert_called_once()

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_vacancies_file_not_found(self, mock_file, json_saver):
        """Тест загрузки при отсутствии файла"""
        vacancies = json_saver.load_vacancies()
        assert vacancies == []

    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    @patch('pathlib.Path.exists', return_value=True)
    def test_add_vacancy_new(self, mock_exists, mock_file, json_saver, sample_vacancy):
        """Тест добавления новой вакансии"""
        with patch.object(json_saver, '_save_to_file') as mock_save:
            messages = json_saver.add_vacancy(sample_vacancy)
            
            assert len(messages) == 1
            assert "Добавлена новая вакансия" in messages[0]
            assert sample_vacancy.vacancy_id in messages[0]
            mock_save.assert_called_once()

    @patch('builtins.open', new_callable=mock_open)
    def test_add_vacancy_update_existing(self, mock_file, json_saver, sample_vacancy):
        """Тест обновления существующей вакансии"""
        # Мокаем существующую вакансию
        existing_vacancy = Mock()
        existing_vacancy.vacancy_id = sample_vacancy.vacancy_id
        existing_vacancy.title = "Старое название"
        existing_vacancy.url = sample_vacancy.url
        existing_vacancy.salary = sample_vacancy.salary
        existing_vacancy.description = sample_vacancy.description
        existing_vacancy.updated_at = sample_vacancy.published_at
        
        with patch.object(json_saver, 'load_vacancies', return_value=[existing_vacancy]), \
             patch.object(json_saver, '_save_to_file') as mock_save:
            
            messages = json_saver.add_vacancy(sample_vacancy)
            
            assert len(messages) == 1
            assert "обновлена" in messages[0]
            mock_save.assert_called_once()

    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    @patch('pathlib.Path.exists', return_value=True)
    def test_add_vacancy_list(self, mock_exists, mock_file, json_saver, sample_vacancy):
        """Тест добавления списка вакансий"""
        vacancy2 = Mock()
        vacancy2.vacancy_id = "456"
        vacancy2.title = "Java разработчик"
        
        with patch.object(json_saver, '_save_to_file') as mock_save:
            messages = json_saver.add_vacancy([sample_vacancy, vacancy2])
            
            assert len(messages) == 2
            mock_save.assert_called_once()

    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    def test_delete_all_vacancies_success(self, mock_file, json_saver):
        """Тест успешного удаления всех вакансий"""
        result = json_saver.delete_all_vacancies()
        assert result is True
        mock_file.assert_called_once()

    @patch('builtins.open', side_effect=Exception("Write error"))
    def test_delete_all_vacancies_error(self, mock_file, json_saver):
        """Тест ошибки при удалении всех вакансий"""
        result = json_saver.delete_all_vacancies()
        assert result is False

    def test_delete_vacancy_by_id_success(self, json_saver, sample_vacancy):
        """Тест успешного удаления вакансии по ID"""
        vacancy_to_keep = Mock()
        vacancy_to_keep.vacancy_id = "456"
        
        with patch.object(json_saver, 'load_vacancies', return_value=[sample_vacancy, vacancy_to_keep]), \
             patch.object(json_saver, '_save_to_file') as mock_save:
            
            result = json_saver.delete_vacancy_by_id("123")
            
            assert result is True
            mock_save.assert_called_once()
            # Проверяем, что была сохранена только одна вакансия
            saved_vacancies = mock_save.call_args[0][0]
            assert len(saved_vacancies) == 1
            assert saved_vacancies[0].vacancy_id == "456"

    def test_delete_vacancy_by_id_not_found(self, json_saver, sample_vacancy):
        """Тест удаления несуществующей вакансии"""
        with patch.object(json_saver, 'load_vacancies', return_value=[sample_vacancy]):
            result = json_saver.delete_vacancy_by_id("999")
            assert result is False

    def test_delete_vacancy_by_id_error(self, json_saver):
        """Тест ошибки при удалении вакансии по ID"""
        with patch.object(json_saver, 'load_vacancies', side_effect=Exception("Error")):
            result = json_saver.delete_vacancy_by_id("123")
            assert result is False

    def test_delete_vacancies_by_keyword_success(self, json_saver, sample_vacancy):
        """Тест удаления вакансий по ключевому слову"""
        with patch.object(json_saver, 'load_vacancies', return_value=[sample_vacancy]), \
             patch('src.utils.ui_helpers.filter_vacancies_by_keyword', return_value=[sample_vacancy]), \
             patch.object(json_saver, '_save_to_file') as mock_save:
            
            deleted_count = json_saver.delete_vacancies_by_keyword("Python")
            
            assert deleted_count == 1
            mock_save.assert_called_once()

    def test_delete_vacancies_by_keyword_no_matches(self, json_saver, sample_vacancy):
        """Тест удаления вакансий по ключевому слову без совпадений"""
        with patch.object(json_saver, 'load_vacancies', return_value=[sample_vacancy]), \
             patch('src.utils.ui_helpers.filter_vacancies_by_keyword', return_value=[]):
            
            deleted_count = json_saver.delete_vacancies_by_keyword("Java")
            assert deleted_count == 0

    def test_delete_vacancies_by_keyword_error(self, json_saver):
        """Тест ошибки при удалении вакансий по ключевому слову"""
        with patch.object(json_saver, 'load_vacancies', side_effect=Exception("Error")):
            deleted_count = json_saver.delete_vacancies_by_keyword("Python")
            assert deleted_count == 0

    @patch('builtins.open', new_callable=mock_open)
    def test_save_to_file_success(self, mock_file, json_saver, sample_vacancy):
        """Тест успешного сохранения в файл"""
        with patch.object(sample_vacancy, 'to_dict', return_value={'id': '123', 'title': 'Test', 'url': 'test.com'}):
            json_saver._save_to_file([sample_vacancy])
            
            # Проверяем, что файл был открыт для записи
            mock_file.assert_called()
            handle = mock_file()
            handle.write.assert_called()

    def test_save_to_file_invalid_vacancy(self, json_saver):
        """Тест сохранения с невалидной вакансией"""
        # Создаем объект без метода to_dict
        invalid_vacancy = Mock(spec=[])  # Объект без метода to_dict
        
        with patch('builtins.open', new_callable=mock_open):
            json_saver._save_to_file([invalid_vacancy])
            # Должно пройти без ошибок, но с логированием

    @patch('pathlib.Path.stat')
    @patch('pathlib.Path.exists', return_value=True)
    def test_get_file_size_success(self, mock_exists, mock_stat, json_saver):
        """Тест получения размера файла"""
        mock_stat.return_value.st_size = 1024
        size = json_saver.get_file_size()
        assert size == 1024

    @patch('pathlib.Path.exists', return_value=False)
    def test_get_file_size_file_not_exists(self, mock_exists, json_saver):
        """Тест получения размера несуществующего файла"""
        size = json_saver.get_file_size()
        assert size == 0

    @patch('pathlib.Path.stat', side_effect=Exception("Error"))
    @patch('pathlib.Path.exists', return_value=True)
    def test_get_file_size_error(self, mock_exists, mock_stat, json_saver):
        """Тест ошибки при получении размера файла"""
        size = json_saver.get_file_size()
        assert size == 0

    def test_backup_corrupted_file_success(self, json_saver):
        """Тест создания резервной копии поврежденного файла"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('shutil.copy2') as mock_copy, \
             patch('builtins.open', new_callable=mock_open):
            
            json_saver._backup_corrupted_file()
            mock_copy.assert_called_once()

    def test_backup_corrupted_file_error(self, json_saver):
        """Тест ошибки при создании резервной копии"""
        with patch('pathlib.Path.exists', side_effect=Exception("Error")):
            # Должно пройти без ошибок, но с логированием
            json_saver._backup_corrupted_file()

    def test_vacancy_to_dict_with_salary(self, sample_vacancy):
        """Тест преобразования вакансии с зарплатой в словарь"""
        result = JSONSaver._vacancy_to_dict(sample_vacancy)
        
        assert result['title'] == sample_vacancy.title
        assert result['url'] == sample_vacancy.url
        assert result['salary'] is not None
        assert result['salary']['from'] == 100000
        assert result['salary']['to'] == 150000
        assert result['area'] == {"name": "Москва"}

    def test_vacancy_to_dict_without_salary(self, sample_vacancy):
        """Тест преобразования вакансии без зарплаты в словарь"""
        sample_vacancy.salary = None
        result = JSONSaver._vacancy_to_dict(sample_vacancy)
        
        assert result['title'] == sample_vacancy.title
        assert result['salary'] is None
        assert result['area'] == {"name": "Москва"}

    def test_ensure_json_serializable_dict(self, json_saver):
        """Тест обеспечения JSON-сериализуемости словаря"""
        test_dict = {"key": "value", "number": 123}
        result = json_saver._ensure_json_serializable(test_dict)
        assert result == test_dict

    def test_ensure_json_serializable_list(self, json_saver):
        """Тест обеспечения JSON-сериализуемости списка"""
        test_list = ["string", 123, True]
        result = json_saver._ensure_json_serializable(test_list)
        assert result == test_list

    def test_ensure_json_serializable_object(self, json_saver):
        """Тест обеспечения JSON-сериализуемости объекта"""
        test_obj = Mock()
        test_obj.__str__ = Mock(return_value="mock_object")
        result = json_saver._ensure_json_serializable(test_obj)
        assert result == "mock_object"

    def test_parse_date_valid(self, json_saver):
        """Тест парсинга корректной даты"""
        date_str = "2024-01-01T12:00:00+00:00"
        result = json_saver._parse_date(date_str)
        assert isinstance(result, datetime)

    def test_parse_date_invalid(self, json_saver):
        """Тест парсинга некорректной даты"""
        date_str = "invalid_date"
        result = json_saver._parse_date(date_str)
        assert result == datetime.min

    def test_get_vacancies_delegates_to_load(self, json_saver):
        """Тест что get_vacancies делегирует в load_vacancies"""
        with patch.object(json_saver, 'load_vacancies', return_value=[]) as mock_load:
            result = json_saver.get_vacancies()
            mock_load.assert_called_once()
            assert result == []

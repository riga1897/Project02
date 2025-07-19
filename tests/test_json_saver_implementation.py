import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from typing import List, Dict, Any

from src.storage.json_saver import JSONSaver
from src.storage.abstract import AbstractVacancyStorage
from src.vacancies.models import Vacancy
from src.vacancies.abstract import AbstractVacancy
from src.vacancies.models import Salary


class TestJSONSaverImplementation():
    """Тесты для JSONSaver как конкретной реализации AbstractVacancyStorage"""

    @pytest.fixture
    def temp_json_file(self):
        """Создает временный JSON файл для тестов"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([], f)
            temp_path = f.name
        yield temp_path
        Path(temp_path).unlink(missing_ok=True)

    @pytest.fixture
    def json_saver(self, temp_json_file):
        """Создает экземпляр JSONSaver с временным файлом"""
        return JSONSaver(temp_json_file)

    @pytest.fixture
    def sample_vacancy(self):
        """Создает образец вакансии для тестов"""
        return Vacancy(
            title="Python Developer",
            url="https://example.com/job/123",
            salary=None,
            description="Great job",
            requirements="Python skills",
            responsibilities="Code development",
            employer={"name": "Tech Company"},
            experience="1-3 года",
            employment="Полная занятость",
            schedule="Полный день",
            published_at="2024-01-15T10:30:00",
            vacancy_id="123"
        )

    def test_inherits_from_abstract_storage(self, json_saver):
        """Проверяем, что JSONSaver наследуется от AbstractVacancyStorage"""
        assert isinstance(json_saver, AbstractVacancyStorage)
        assert issubclass(JSONSaver, AbstractVacancyStorage)

    def test_implements_all_abstract_methods(self):
        """Проверяем, что JSONSaver реализует все абстрактные методы"""
        # Получаем абстрактные методы из родительского класса
        abstract_methods = AbstractVacancyStorage.__abstractmethods__

        # Проверяем, что все методы реализованы в JSONSaver
        for method_name in abstract_methods:
            assert hasattr(JSONSaver, method_name)
            method = getattr(JSONSaver, method_name)
            assert callable(method)
            # Проверяем, что метод не помечен как абстрактный
            assert not getattr(method, '__isabstractmethod__', False)

    def test_add_vacancy_method_signature(self, json_saver, sample_vacancy):
        """Проверяем правильность сигнатуры метода add_vacancy"""
        # Метод должен принимать AbstractVacancy и возвращать что-то
        result = json_saver.add_vacancy(sample_vacancy)
        assert result is not None  # JSONSaver возвращает список сообщений

    def test_get_vacancies_method_signature(self, json_saver):
        """Проверяем правильность сигнатуры метода get_vacancies"""
        # Метод должен возвращать список AbstractVacancy
        result = json_saver.get_vacancies()
        assert isinstance(result, list)

        # Если есть элементы, проверяем, что они AbstractVacancy
        if result:
            for vacancy in result:
                assert isinstance(vacancy, AbstractVacancy)

    def test_delete_vacancy_method_exists(self, json_saver):
        """Проверяем наличие метода delete_vacancy"""
        # Проверяем, что метод существует (в JSONSaver он называется delete_vacancy_by_id)
        assert hasattr(json_saver, 'delete_vacancy_by_id')
        assert callable(getattr(json_saver, 'delete_vacancy_by_id'))

    def test_add_and_retrieve_vacancy_integration(self, json_saver, sample_vacancy):
        """Тестируем интеграцию добавления и получения вакансии"""
        # Добавляем вакансию
        messages = json_saver.add_vacancy(sample_vacancy)
        assert len(messages) > 0
        assert "Добавлена новая вакансия" in messages[0]

        # Получаем вакансии
        vacancies = json_saver.get_vacancies()
        assert len(vacancies) == 1
        assert isinstance(vacancies[0], AbstractVacancy)
        assert vacancies[0].title == sample_vacancy.title
        assert vacancies[0].vacancy_id == sample_vacancy.vacancy_id

    def test_add_multiple_vacancies(self, json_saver):
        """Тестируем добавление нескольких вакансий"""
        vacancies = [
            Vacancy(
                title=f"Job {i}",
                url=f"https://example.com/job/{i}",
                salary=None,
                description=f"Description {i}",
                vacancy_id=str(i)
            )
            for i in range(1, 4)
        ]

        # Добавляем список вакансий
        messages = json_saver.add_vacancy(vacancies)
        assert len(messages) == 3

        # Проверяем, что все добавились
        stored_vacancies = json_saver.get_vacancies()
        assert len(stored_vacancies) == 3

    def test_update_existing_vacancy(self, json_saver, sample_vacancy):
        """Тестируем обновление существующей вакансии"""
        # Добавляем первоначальную вакансию
        json_saver.add_vacancy(sample_vacancy)

        # Создаем обновленную версию
        updated_vacancy = Vacancy(
            title="Updated Python Developer",  # Изменили название
            url=sample_vacancy.url,
            salary=sample_vacancy.salary,
            description="Updated description",  # Изменили описание
            requirements=sample_vacancy.requirements,
            responsibilities=sample_vacancy.responsibilities,
            employer=sample_vacancy.employer,
            experience=sample_vacancy.experience,
            employment=sample_vacancy.employment,
            schedule=sample_vacancy.schedule,
            published_at=sample_vacancy.published_at,
            vacancy_id=sample_vacancy.vacancy_id  # Тот же ID
        )

        # Обновляем вакансию
        messages = json_saver.add_vacancy(updated_vacancy)
        assert len(messages) == 1
        assert "обновлена" in messages[0]
        assert "title" in messages[0]

        # Проверяем, что вакансия обновилась
        vacancies = json_saver.get_vacancies()
        assert len(vacancies) == 1  # Должна быть одна вакансия
        assert vacancies[0].title == "Updated Python Developer"

    def test_delete_vacancy_functionality(self, json_saver, sample_vacancy):
        """Тестируем функциональность удаления вакансии"""
        # Добавляем вакансию
        json_saver.add_vacancy(sample_vacancy)
        assert len(json_saver.get_vacancies()) == 1

        # Удаляем вакансию
        result = json_saver.delete_vacancy_by_id(sample_vacancy.vacancy_id)
        assert result is True

        # Проверяем, что вакансия удалилась
        assert len(json_saver.get_vacancies()) == 0

    def test_delete_nonexistent_vacancy(self, json_saver):
        """Тестируем удаление несуществующей вакансии"""
        result = json_saver.delete_vacancy_by_id("nonexistent_id")
        assert result is False

    def test_delete_all_vacancies(self, json_saver, sample_vacancy):
        """Тестируем удаление всех вакансий"""
        # Добавляем несколько вакансий
        for i in range(3):
            vacancy = Vacancy(
                title=f"Job {i}",
                url=f"https://example.com/job/{i}",
                salary=None,
                description=f"Description {i}",
                vacancy_id=str(i)
            )
            json_saver.add_vacancy(vacancy)

        assert len(json_saver.get_vacancies()) == 3

        # Удаляем все вакансии
        result = json_saver.delete_all_vacancies()
        assert result is True
        assert len(json_saver.get_vacancies()) == 0

    @patch('builtins.open', side_effect=IOError("File error"))
    def test_file_error_handling(self, mock_file, temp_json_file):
        """Тестируем обработку ошибок файловых операций"""
        json_saver = JSONSaver(temp_json_file)

        # При ошибке файла должен возвращаться пустой список
        vacancies = json_saver.get_vacancies()
        assert isinstance(vacancies, list)
        assert len(vacancies) == 0

    def test_corrupted_json_handling(self, temp_json_file):
        """Тестируем обработку поврежденного JSON файла"""
        # Записываем некорректный JSON
        with open(temp_json_file, 'w') as f:
            f.write("invalid json content {")

        json_saver = JSONSaver(temp_json_file)
        vacancies = json_saver.get_vacancies()

        # Должен возвращаться пустой список и создаваться резервная копия
        assert isinstance(vacancies, list)
        assert len(vacancies) == 0

    def test_file_creation_on_init(self):
        """Тестируем создание файла при инициализации"""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test_vacancies.json"

            # Файл не существует
            assert not file_path.exists()

            # Создаем JSONSaver
            json_saver = JSONSaver(str(file_path))

            # Файл должен быть создан
            assert file_path.exists()
            assert json_saver.filename == str(file_path)

    def test_validate_filename(self):
        """Тестируем валидацию имени файла"""
        # Тест с None
        result = JSONSaver._validate_filename(None)
        assert result == "data/storage/vacancies.json"

        # Тест с пустой строкой
        result = JSONSaver._validate_filename("")
        assert result == "data/storage/vacancies.json"

        # Тест с валидным именем
        result = JSONSaver._validate_filename("test.json")
        assert result == "test.json"

        # Тест с пробелами
        result = JSONSaver._validate_filename("  test.json  ")
        assert result == "test.json"

    def test_polymorphism_with_abstract_interface(self, json_saver, sample_vacancy):
        """Тестируем полиморфизм через абстрактный интерфейс"""
        # Используем JSONSaver через интерфейс AbstractVacancyStorage
        storage: AbstractVacancyStorage = json_saver

        # Все методы должны работать через абстрактный интерфейс
        # Note: JSONSaver не реализует точно такой же интерфейс delete_vacancy,
        # но мы можем протестировать add_vacancy и get_vacancies
        messages = storage.add_vacancy(sample_vacancy)
        assert isinstance(messages, list)

        vacancies = storage.get_vacancies()
        assert isinstance(vacancies, list)
        assert len(vacancies) == 1
        assert isinstance(vacancies[0], AbstractVacancy)

    def test_vacancy_serialization_consistency(self, json_saver):
        """Тестируем консистентность сериализации/десериализации вакансий"""
        # Создаем вакансию с различными типами данных
        original_vacancy = Vacancy(
            title="Test Job",
            url="https://test.com",
            salary=None,
            description="Test description",
            requirements="Python, Django",
            responsibilities="Development tasks",
            employer={"name": "Test Company", "id": "12345"},
            experience="1-3 года",
            employment="Полная занятость",
            schedule="Полный день",
            published_at="2024-01-15T10:30:00",
            vacancy_id="test_123"
        )

        # Сохраняем и загружаем
        json_saver.add_vacancy(original_vacancy)
        loaded_vacancies = json_saver.get_vacancies()

        # Проверяем консистентность
        assert len(loaded_vacancies) == 1
        loaded_vacancy = loaded_vacancies[0]

        assert loaded_vacancy.title == original_vacancy.title
        assert loaded_vacancy.url == original_vacancy.url
        assert loaded_vacancy.description == original_vacancy.description
        assert loaded_vacancy.vacancy_id == original_vacancy.vacancy_id
        assert loaded_vacancy.employer == original_vacancy.employer

    def test_concurrent_access_safety(self, json_saver, sample_vacancy):
        """Тестируем безопасность при одновременном доступе (базовый тест)"""
        # Этот тест проверяет, что операции не приводят к исключениям
        # при последовательном выполнении операций

        for i in range(5):
            vacancy = Vacancy(
                title=f"Concurrent Job {i}",
                url=f"https://example.com/{i}",
                salary=None,
                description=f"Description {i}",
                vacancy_id=f"concurrent_{i}"
            )
            json_saver.add_vacancy(vacancy)

        # Получаем вакансии несколько раз
        for _ in range(3):
            vacancies = json_saver.get_vacancies()
            assert len(vacancies) == 5

        # Удаляем некоторые вакансии
        json_saver.delete_vacancy_by_id("concurrent_0")
        json_saver.delete_vacancy_by_id("concurrent_2")

        final_vacancies = json_saver.get_vacancies()
        assert len(final_vacancies) == 3
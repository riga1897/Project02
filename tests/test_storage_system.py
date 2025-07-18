
"""
Комплексные тесты для системы хранения данных
"""

import pytest
import json
from pathlib import Path
from src.storage.json_saver import JSONSaver
from src.vacancies.models import Vacancy


class TestJSONSaver:
    """Тесты для JSONSaver"""
    
    @pytest.fixture
    def temp_json_file(self, tmp_path):
        """Временный JSON файл для тестов"""
        return tmp_path / "test_vacancies.json"
    
    @pytest.fixture
    def sample_vacancies(self):
        """Тестовые вакансии"""
        return [
            Vacancy(
                title="Python Developer",
                url="https://test1.com",
                salary={'from': 100000, 'currency': 'RUR'},
                description="Python dev",
                vacancy_id="1"
            ),
            Vacancy(
                title="Java Developer",
                url="https://test2.com",
                salary={'from': 120000, 'currency': 'RUR'},
                description="Java dev",
                vacancy_id="2"
            )
        ]
    
    def test_json_saver_init(self, temp_json_file):
        """Тест инициализации JSONSaver"""
        saver = JSONSaver(temp_json_file)
        assert saver.file_path == temp_json_file
        assert temp_json_file.exists()
        assert json.loads(temp_json_file.read_text()) == []
    
    def test_add_vacancy(self, temp_json_file, sample_vacancies):
        """Тест добавления вакансии"""
        saver = JSONSaver(temp_json_file)
        vacancy = sample_vacancies[0]
        
        saver.add_vacancy(vacancy)
        
        stored_data = json.loads(temp_json_file.read_text())
        assert len(stored_data) == 1
        assert stored_data[0]['title'] == 'Python Developer'
    
    def test_add_multiple_vacancies(self, temp_json_file, sample_vacancies):
        """Тест добавления нескольких вакансий"""
        saver = JSONSaver(temp_json_file)
        
        for vacancy in sample_vacancies:
            saver.add_vacancy(vacancy)
        
        stored_data = json.loads(temp_json_file.read_text())
        assert len(stored_data) == 2
    
    def test_get_vacancies(self, temp_json_file, sample_vacancies):
        """Тест получения вакансий"""
        saver = JSONSaver(temp_json_file)
        
        # Добавляем вакансии
        for vacancy in sample_vacancies:
            saver.add_vacancy(vacancy)
        
        # Получаем вакансии
        result = saver.get_vacancies()
        
        assert len(result) == 2
        assert all(isinstance(v, Vacancy) for v in result)
        assert result[0].title == 'Python Developer'
    
    def test_get_vacancies_with_filters(self, temp_json_file, sample_vacancies):
        """Тест получения вакансий с фильтрами"""
        saver = JSONSaver(temp_json_file)
        
        for vacancy in sample_vacancies:
            saver.add_vacancy(vacancy)
        
        # Фильтр по названию
        result = saver.get_vacancies({'title': 'Python Developer'})
        assert len(result) == 1
        assert result[0].title == 'Python Developer'
    
    def test_delete_vacancy(self, temp_json_file, sample_vacancies):
        """Тест удаления вакансии"""
        saver = JSONSaver(temp_json_file)
        vacancy = sample_vacancies[0]
        
        saver.add_vacancy(vacancy)
        assert len(saver.get_vacancies()) == 1
        
        saver.delete_vacancy(vacancy)
        assert len(saver.get_vacancies()) == 0
    
    def test_clear_all_vacancies(self, temp_json_file, sample_vacancies):
        """Тест очистки всех вакансий"""
        saver = JSONSaver(temp_json_file)
        
        for vacancy in sample_vacancies:
            saver.add_vacancy(vacancy)
        
        assert len(saver.get_vacancies()) == 2
        
        saver.clear_all()
        assert len(saver.get_vacancies()) == 0
        
        # Проверяем, что файл содержит пустой список
        stored_data = json.loads(temp_json_file.read_text())
        assert stored_data == []
    
    def test_file_corruption_handling(self, temp_json_file):
        """Тест обработки поврежденного файла"""
        # Записываем некорректный JSON
        temp_json_file.write_text("invalid json")
        
        # Должен создаться новый пустой файл
        saver = JSONSaver(temp_json_file)
        assert saver.get_vacancies() == []
        
        # Файл должен быть восстановлен
        stored_data = json.loads(temp_json_file.read_text())
        assert stored_data == []

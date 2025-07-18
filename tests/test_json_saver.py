
"""
Тесты для модуля json_saver
"""

import pytest
import json
from pathlib import Path
from src.storage.json_saver import JSONSaver
from src.vacancies.models import Vacancy


class TestJSONSaver:
    """Тесты для класса JSONSaver"""
    
    def test_init_creates_file(self, temp_json_file):
        """Тест создания файла при инициализации"""
        saver = JSONSaver(str(temp_json_file))
        assert Path(temp_json_file).exists()
        assert saver.filename == str(temp_json_file)
    
    def test_add_single_vacancy(self, json_saver, sample_vacancy):
        """Тест добавления одной вакансии"""
        messages = json_saver.add_vacancy(sample_vacancy)
        
        assert len(messages) == 1
        assert "Добавлена новая вакансия" in messages[0]
        
        vacancies = json_saver.load_vacancies()
        assert len(vacancies) == 1
        assert vacancies[0].vacancy_id == sample_vacancy.vacancy_id
    
    def test_add_multiple_vacancies(self, json_saver, sample_vacancies):
        """Тест добавления нескольких вакансий"""
        messages = json_saver.add_vacancy(sample_vacancies)
        
        assert len(messages) == 3
        
        vacancies = json_saver.load_vacancies()
        assert len(vacancies) == 3
    
    def test_update_existing_vacancy(self, json_saver, sample_vacancy):
        """Тест обновления существующей вакансии"""
        # Добавляем вакансию
        json_saver.add_vacancy(sample_vacancy)
        
        # Обновляем ту же вакансию
        updated_vacancy = Vacancy(
            title="Updated Python Developer",
            url=sample_vacancy.url,
            salary={"from": 200000, "to": 250000, "currency": "RUR"},
            description="Updated description",
            vacancy_id=sample_vacancy.vacancy_id
        )
        
        messages = json_saver.add_vacancy(updated_vacancy)
        
        assert len(messages) == 1
        assert "обновлена" in messages[0]
        
        vacancies = json_saver.load_vacancies()
        assert len(vacancies) == 1
        assert vacancies[0].title == "Updated Python Developer"
    
    def test_load_empty_file(self, json_saver):
        """Тест загрузки пустого файла"""
        vacancies = json_saver.load_vacancies()
        assert vacancies == []
    
    def test_delete_all_vacancies(self, json_saver, sample_vacancies):
        """Тест удаления всех вакансий"""
        json_saver.add_vacancy(sample_vacancies)
        
        result = json_saver.delete_all_vacancies()
        assert result is True
        
        vacancies = json_saver.load_vacancies()
        assert len(vacancies) == 0
    
    def test_delete_vacancy_by_id(self, json_saver, sample_vacancies):
        """Тест удаления вакансии по ID"""
        json_saver.add_vacancy(sample_vacancies)
        
        result = json_saver.delete_vacancy_by_id("1")
        assert result is True
        
        vacancies = json_saver.load_vacancies()
        assert len(vacancies) == 2
        assert not any(v.vacancy_id == "1" for v in vacancies)
    
    def test_delete_nonexistent_vacancy(self, json_saver, sample_vacancies):
        """Тест удаления несуществующей вакансии"""
        json_saver.add_vacancy(sample_vacancies)
        
        result = json_saver.delete_vacancy_by_id("nonexistent")
        assert result is False
        
        vacancies = json_saver.load_vacancies()
        assert len(vacancies) == 3
    
    def test_delete_vacancies_by_keyword(self, json_saver, sample_vacancies):
        """Тест удаления вакансий по ключевому слову"""
        json_saver.add_vacancy(sample_vacancies)
        
        deleted_count = json_saver.delete_vacancies_by_keyword("Python")
        assert deleted_count == 1
        
        vacancies = json_saver.load_vacancies()
        assert len(vacancies) == 2
        assert not any("Python" in v.title for v in vacancies)
    
    def test_corrupted_file_handling(self, temp_json_file):
        """Тест обработки поврежденного файла"""
        # Создаем поврежденный JSON файл
        with open(temp_json_file, 'w') as f:
            f.write("invalid json content")
        
        saver = JSONSaver(str(temp_json_file))
        vacancies = saver.load_vacancies()
        
        assert vacancies == []
        # Проверяем, что создан новый пустой файл
        with open(temp_json_file, 'r') as f:
            data = json.load(f)
            assert data == []
    
    def test_get_vacancies(self, json_saver, sample_vacancies):
        """Тест получения вакансий"""
        json_saver.add_vacancy(sample_vacancies)
        
        vacancies = json_saver.get_vacancies()
        assert len(vacancies) == 3
        assert all(isinstance(v, Vacancy) for v in vacancies)

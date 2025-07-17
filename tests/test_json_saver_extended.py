
"""
Расширенные тесты для модуля json_saver (новые методы удаления)
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from src.storage.json_saver import JSONSaver
from src.vacancies.models import Vacancy


class TestJSONSaverExtended:
    """Расширенные тесты для класса JSONSaver"""
    
    def create_test_vacancy(self, vacancy_id: str, title: str, keywords: list = None):
        """Создает тестовую вакансию"""
        return Vacancy(
            title=title,
            url="https://example.com",
            salary=None,
            description="Test description",
            keywords=keywords or [],
            vacancy_id=vacancy_id
        )
    
    def test_delete_all_vacancies_success(self):
        """Тест успешного удаления всех вакансий"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            # Создаем файл с тестовыми данными
            test_data = [
                {
                    "id": "1",
                    "title": "Job 1",
                    "url": "https://example.com",
                    "salary": None,
                    "description": "Test"
                }
            ]
            json.dump(test_data, f)
            temp_filename = f.name
        
        try:
            saver = JSONSaver(temp_filename)
            result = saver.delete_all_vacancies()
            
            assert result is True
            
            # Проверяем, что файл пуст
            with open(temp_filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert data == []
        
        finally:
            os.unlink(temp_filename)
    
    def test_delete_all_vacancies_file_error(self):
        """Тест ошибки при удалении всех вакансий"""
        saver = JSONSaver("/invalid/path/file.json")
        result = saver.delete_all_vacancies()
        
        assert result is False
    
    def test_delete_vacancy_by_id_success(self):
        """Тест успешного удаления вакансии по ID"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            test_data = [
                {
                    "id": "1",
                    "title": "Job 1",
                    "url": "https://example.com",
                    "salary": None,
                    "description": "Test"
                },
                {
                    "id": "2",
                    "title": "Job 2",
                    "url": "https://example.com",
                    "salary": None,
                    "description": "Test"
                }
            ]
            json.dump(test_data, f)
            temp_filename = f.name
        
        try:
            saver = JSONSaver(temp_filename)
            result = saver.delete_vacancy_by_id("1")
            
            assert result is True
            
            # Проверяем, что осталась только одна вакансия
            vacancies = saver.get_vacancies()
            assert len(vacancies) == 1
            assert vacancies[0].vacancy_id == "2"
        
        finally:
            os.unlink(temp_filename)
    
    def test_delete_vacancy_by_id_not_found(self):
        """Тест удаления несуществующей вакансии"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            test_data = [
                {
                    "id": "1",
                    "title": "Job 1",
                    "url": "https://example.com",
                    "salary": None,
                    "description": "Test"
                }
            ]
            json.dump(test_data, f)
            temp_filename = f.name
        
        try:
            saver = JSONSaver(temp_filename)
            result = saver.delete_vacancy_by_id("nonexistent")
            
            assert result is False
            
            # Проверяем, что вакансия не была удалена
            vacancies = saver.get_vacancies()
            assert len(vacancies) == 1
        
        finally:
            os.unlink(temp_filename)
    
    @patch('src.utils.ui_helpers.filter_vacancies_by_keyword')
    def test_delete_vacancies_by_keyword_success(self, mock_filter):
        """Тест успешного удаления вакансий по ключевому слову"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            test_data = [
                {
                    "id": "1",
                    "title": "Python Developer",
                    "url": "https://example.com",
                    "salary": None,
                    "description": "Python development"
                },
                {
                    "id": "2",
                    "title": "Java Developer",
                    "url": "https://example.com",
                    "salary": None,
                    "description": "Java development"
                }
            ]
            json.dump(test_data, f)
            temp_filename = f.name
        
        try:
            saver = JSONSaver(temp_filename)
            
            # Настраиваем мок для возврата вакансий с Python
            def mock_filter_side_effect(vacancies, keyword):
                if keyword == "python":
                    return [v for v in vacancies if v.vacancy_id == "1"]
                return []
            
            mock_filter.side_effect = mock_filter_side_effect
            
            result = saver.delete_vacancies_by_keyword("python")
            
            assert result == 1
            
            # Проверяем, что осталась только Java вакансия
            vacancies = saver.get_vacancies()
            assert len(vacancies) == 1
            assert vacancies[0].vacancy_id == "2"
        
        finally:
            os.unlink(temp_filename)
    
    @patch('src.utils.ui_helpers.filter_vacancies_by_keyword')
    def test_delete_vacancies_by_keyword_not_found(self, mock_filter):
        """Тест удаления вакансий по несуществующему ключевому слову"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            test_data = [
                {
                    "id": "1",
                    "title": "Job 1",
                    "url": "https://example.com",
                    "salary": None,
                    "description": "Test"
                }
            ]
            json.dump(test_data, f)
            temp_filename = f.name
        
        try:
            saver = JSONSaver(temp_filename)
            
            # Настраиваем мок для возврата пустого списка
            mock_filter.return_value = []
            
            result = saver.delete_vacancies_by_keyword("nonexistent")
            
            assert result == 0
            
            # Проверяем, что вакансия не была удалена
            vacancies = saver.get_vacancies()
            assert len(vacancies) == 1
        
        finally:
            os.unlink(temp_filename)
    
    def test_delete_vacancy_by_id_error(self):
        """Тест ошибки при удалении вакансии по ID"""
        saver = JSONSaver("/invalid/path/file.json")
        result = saver.delete_vacancy_by_id("1")
        
        assert result is False
    
    def test_delete_vacancies_by_keyword_error(self):
        """Тест ошибки при удалении вакансий по ключевому слову"""
        saver = JSONSaver("/invalid/path/file.json")
        result = saver.delete_vacancies_by_keyword("test")
        
        assert result == 0

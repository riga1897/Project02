
"""
Тесты для вспомогательных модулей
"""

import pytest
from unittest.mock import Mock, patch
from src.utils.paginator import Paginator
from src.utils.ui_helpers import filter_vacancies_by_keyword
from src.utils.vacancy_formatter import VacancyFormatter


class TestPaginator:
    """Тесты для пагинатора"""
    
    def test_paginate_multiple_pages(self):
        """Тест сбора данных с нескольких страниц"""
        def fetch_func(page):
            if page == 0:
                return ['a', 'b']
            elif page == 1:
                return ['c', 'd']
            return []
        
        result = Paginator.paginate(fetch_func, total_pages=3)
        assert result == ['a', 'b', 'c', 'd']
    
    def test_paginate_empty_page_stops(self):
        """Тест остановки при пустой странице"""
        def fetch_func(page):
            return ['data'] if page == 0 else []
        
        result = Paginator.paginate(fetch_func, total_pages=5)
        assert result == ['data']
    
    def test_paginate_empty_result(self):
        """Тест с пустым результатом"""
        def fetch_func(page):
            return []
        
        result = Paginator.paginate(fetch_func, total_pages=3)
        assert result == []
    
    def test_paginate_respects_total_pages(self):
        """Тест ограничения по total_pages"""
        call_count = 0
        
        def fetch_func(page):
            nonlocal call_count
            call_count += 1
            return [f'page{page}']
        
        result = Paginator.paginate(fetch_func, total_pages=2)
        assert call_count == 2
        assert len(result) == 2


class TestUIHelpers:
    """Тесты для UI helpers"""
    
    def test_filter_vacancies_by_keyword(self, sample_vacancies):
        """Тест фильтрации вакансий по ключевому слову"""
        result = filter_vacancies_by_keyword(sample_vacancies, "Python")
        
        assert len(result) == 1
        assert "Python" in result[0].title
    
    def test_filter_vacancies_case_insensitive(self, sample_vacancies):
        """Тест регистронезависимой фильтрации"""
        result1 = filter_vacancies_by_keyword(sample_vacancies, "python")
        result2 = filter_vacancies_by_keyword(sample_vacancies, "PYTHON")
        result3 = filter_vacancies_by_keyword(sample_vacancies, "Python")
        
        assert len(result1) == len(result2) == len(result3) == 1
    
    def test_filter_vacancies_no_matches(self, sample_vacancies):
        """Тест фильтрации без совпадений"""
        result = filter_vacancies_by_keyword(sample_vacancies, "NonExistent")
        assert len(result) == 0
    
    def test_filter_vacancies_empty_keyword(self, sample_vacancies):
        """Тест фильтрации с пустым ключевым словом"""
        result = filter_vacancies_by_keyword(sample_vacancies, "")
        assert len(result) == 0


class TestVacancyFormatter:
    """Тесты для форматтера вакансий"""
    
    def test_format_vacancy_full(self, sample_vacancy):
        """Тест форматирования полной вакансии"""
        result = VacancyFormatter.format_vacancy(sample_vacancy)
        
        assert sample_vacancy.title in result
        assert sample_vacancy.url in result
        assert "100 000" in result  # Проверяем форматирование зарплаты
    
    def test_format_vacancy_no_salary(self, sample_vacancies):
        """Тест форматирования вакансии без зарплаты"""
        vacancy_no_salary = sample_vacancies[2]  # Frontend Developer без зарплаты
        result = VacancyFormatter.format_vacancy(vacancy_no_salary)
        
        assert vacancy_no_salary.title in result
        assert "Не указана" in result
    
    def test_format_vacancy_list(self, sample_vacancies):
        """Тест форматирования списка вакансий"""
        result = VacancyFormatter.format_vacancy_list(sample_vacancies)
        
        assert len(result) > 0
        assert "Python Developer" in result
        assert "Java Developer" in result
    
    def test_format_vacancy_short(self, sample_vacancy):
        """Тест краткого форматирования вакансии"""
        result = VacancyFormatter.format_vacancy_short(sample_vacancy)
        
        assert sample_vacancy.title in result
        assert len(result) < len(VacancyFormatter.format_vacancy(sample_vacancy))

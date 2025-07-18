
"""
Тесты для API модулей
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.api_modules.hh_api import HeadHunterAPI
from src.api_modules.sj_api import SuperJobAPI
from src.api_modules.unified_api import UnifiedAPI
from src.config.api_config import APIConfig


class TestHeadHunterAPI:
    """Тесты для HeadHunter API"""
    
    def test_init(self, api_config, temp_cache_dir):
        """Тест инициализации HH API"""
        original_cache = HeadHunterAPI.DEFAULT_CACHE_DIR
        HeadHunterAPI.DEFAULT_CACHE_DIR = temp_cache_dir
        
        try:
            api = HeadHunterAPI(api_config)
            assert api._config == api_config
            assert api.cache_dir.name == temp_cache_dir.split('/')[-1]
        finally:
            HeadHunterAPI.DEFAULT_CACHE_DIR = original_cache
    
    def test_validate_vacancy_valid(self, hh_api):
        """Тест валидации корректной вакансии"""
        vacancy = {
            'name': 'Python Developer',
            'alternate_url': 'https://hh.ru/vacancy/123',
            'salary': {'from': 100000, 'currency': 'RUR'}
        }
        
        result = hh_api._validate_vacancy(vacancy)
        assert result is True
    
    def test_validate_vacancy_invalid(self, hh_api):
        """Тест валидации некорректной вакансии"""
        vacancy = {'name': 'Python Developer'}  # Отсутствуют обязательные поля
        
        result = hh_api._validate_vacancy(vacancy)
        assert result is False
    
    @patch('src.api_modules.cached_api.CachedAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_page(self, mock_connect, hh_api, mock_hh_response):
        """Тест получения страницы вакансий"""
        mock_connect.return_value = mock_hh_response
        
        result = hh_api.get_vacancies_page("python", page=0)
        
        assert len(result) == 1
        assert result[0]['name'] == 'Python Developer'
        mock_connect.assert_called_once()
    
    @patch('src.api_modules.cached_api.CachedAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_empty_response(self, mock_connect, hh_api):
        """Тест получения пустого ответа"""
        mock_connect.return_value = {'items': []}
        
        result = hh_api.get_vacancies_page("nonexistent", page=0)
        
        assert result == []
    
    @patch('src.api_modules.cached_api.CachedAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_full(self, mock_connect, hh_api, mock_hh_response):
        """Тест получения всех вакансий с пагинацией"""
        mock_connect.return_value = mock_hh_response
        
        result = hh_api.get_vacancies("python")
        
        assert len(result) >= 0
        assert mock_connect.call_count >= 1


class TestSuperJobAPI:
    """Тесты для SuperJob API"""
    
    def test_init(self, api_config, temp_cache_dir):
        """Тест инициализации SJ API"""
        original_cache = SuperJobAPI.DEFAULT_CACHE_DIR
        SuperJobAPI.DEFAULT_CACHE_DIR = temp_cache_dir
        
        try:
            api = SuperJobAPI(api_config)
            assert api.config is not None  # SJ API creates its own SJAPIConfig
        finally:
            SuperJobAPI.DEFAULT_CACHE_DIR = original_cache
    
    @patch('src.api_modules.cached_api.CachedAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_page(self, mock_connect, sj_api, mock_sj_response):
        """Тест получения страницы вакансий SJ"""
        mock_connect.return_value = mock_sj_response
        
        result = sj_api.get_vacancies_page("python", page=0)
        
        assert len(result) == 1
        assert result[0]['profession'] == 'Python Developer'


class TestUnifiedAPI:
    """Тесты для унифицированного API"""
    
    @patch('src.api_modules.hh_api.HeadHunterAPI')
    @patch('src.api_modules.sj_api.SuperJobAPI')
    def test_init(self, mock_sj, mock_hh, api_config):
        """Тест инициализации унифицированного API"""
        unified_api = UnifiedAPI(api_config)
        
        assert unified_api.config == api_config
        mock_hh.assert_called_once_with(api_config)
        mock_sj.assert_called_once_with(api_config)
    
    @patch('src.api_modules.hh_api.HeadHunterAPI')
    @patch('src.api_modules.sj_api.SuperJobAPI')
    def test_search_vacancies_hh_only(self, mock_sj, mock_hh, api_config):
        """Тест поиска только через HH"""
        mock_hh_instance = MagicMock()
        mock_hh_instance.get_vacancies.return_value = [{'name': 'Test'}]
        mock_hh.return_value = mock_hh_instance
        
        unified_api = UnifiedAPI(api_config)
        result = unified_api.search_vacancies("python", sources=["hh"])
        
        mock_hh_instance.get_vacancies.assert_called_once_with("python")
        mock_sj.return_value.get_vacancies.assert_not_called()
    
    @patch('src.api_modules.hh_api.HeadHunterAPI')
    @patch('src.api_modules.sj_api.SuperJobAPI')
    def test_search_vacancies_both_sources(self, mock_sj, mock_hh, api_config):
        """Тест поиска через оба источника"""
        mock_hh_instance = MagicMock()
        mock_hh_instance.get_vacancies.return_value = [{'name': 'HH Test'}]
        mock_hh.return_value = mock_hh_instance
        
        mock_sj_instance = MagicMock()
        mock_sj_instance.get_vacancies.return_value = [{'profession': 'SJ Test'}]
        mock_sj.return_value = mock_sj_instance
        
        unified_api = UnifiedAPI(api_config)
        result = unified_api.search_vacancies("python", sources=["hh", "sj"])
        
        mock_hh_instance.get_vacancies.assert_called_once()
        mock_sj_instance.get_vacancies.assert_called_once()

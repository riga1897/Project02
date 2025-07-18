
"""
Тесты для модуля unified_api
"""

import pytest
from unittest.mock import MagicMock, patch, call
from src.api_modules.unified_api import UnifiedAPI
from src.vacancies.models import Vacancy


class TestUnifiedAPI:
    """Тесты для класса UnifiedAPI"""
    
    @pytest.fixture
    def unified_api(self):
        """Фикстура для создания экземпляра UnifiedAPI"""
        return UnifiedAPI()
    
    @pytest.fixture
    def sample_hh_vacancy_data(self):
        """Тестовые данные HH вакансии"""
        return {
            'id': '123',
            'name': 'Python Developer',
            'alternate_url': 'https://hh.ru/vacancy/123',
            'salary': {'from': 100000, 'to': 150000, 'currency': 'RUR'},
            'snippet': {'responsibility': 'Разработка на Python'}
        }
    
    @pytest.fixture
    def sample_sj_vacancy_data(self):
        """Тестовые данные SuperJob вакансии"""
        return {
            'id': 456,
            'profession': 'Java Developer',
            'link': 'https://superjob.ru/vacancy/456',
            'payment_from': 120000,
            'payment_to': 180000,
            'currency': 'rub',
            'candidat': 'Разработка на Java'
        }
    
    @patch('src.api_modules.unified_api.logger')
    def test_get_vacancies_from_sources_hh_only(self, mock_logger, unified_api, sample_hh_vacancy_data):
        """Тест получения вакансий только с HH"""
        with patch.object(unified_api.hh_api, 'get_vacancies') as mock_hh_get:
            mock_hh_get.return_value = [sample_hh_vacancy_data]
            
            result = unified_api.get_vacancies_from_sources('python', sources=['hh'])
            
            assert len(result) == 1
            assert isinstance(result[0], Vacancy)
            mock_hh_get.assert_called_once_with('python')
            mock_logger.info.assert_called()
    
    @patch('src.api_modules.unified_api.logger')
    def test_get_vacancies_from_sources_sj_only(self, mock_logger, unified_api, sample_sj_vacancy_data):
        """Тест получения вакансий только с SuperJob"""
        with patch.object(unified_api.sj_api, 'get_vacancies') as mock_sj_get, \
             patch.object(unified_api.parser, 'parse_vacancies') as mock_parse, \
             patch.object(unified_api.parser, 'convert_to_unified_format') as mock_convert:
            
            mock_sj_get.return_value = [sample_sj_vacancy_data]
            mock_parse.return_value = [MagicMock()]
            mock_convert.return_value = {
                'id': '456',
                'name': 'Java Developer',
                'alternate_url': 'https://superjob.ru/vacancy/456',
                'salary': {'from': 120000, 'to': 180000, 'currency': 'RUR'},
                'snippet': {'responsibility': 'Разработка на Java'}
            }
            
            result = unified_api.get_vacancies_from_sources('java', sources=['sj'])
            
            assert len(result) == 1
            assert isinstance(result[0], Vacancy)
            mock_sj_get.assert_called_once_with('java')
            mock_logger.info.assert_called()
    
    @patch('src.api_modules.unified_api.logger')
    def test_get_vacancies_from_sources_both(self, mock_logger, unified_api, sample_hh_vacancy_data, sample_sj_vacancy_data):
        """Тест получения вакансий с обоих источников"""
        with patch.object(unified_api.hh_api, 'get_vacancies') as mock_hh_get, \
             patch.object(unified_api.sj_api, 'get_vacancies') as mock_sj_get, \
             patch.object(unified_api.parser, 'parse_vacancies') as mock_parse, \
             patch.object(unified_api.parser, 'convert_to_unified_format') as mock_convert:
            
            mock_hh_get.return_value = [sample_hh_vacancy_data]
            mock_sj_get.return_value = [sample_sj_vacancy_data]
            mock_parse.return_value = [MagicMock()]
            mock_convert.return_value = {
                'id': '456',
                'name': 'Java Developer',
                'alternate_url': 'https://superjob.ru/vacancy/456',
                'salary': {'from': 120000, 'to': 180000, 'currency': 'RUR'},
                'snippet': {'responsibility': 'Разработка на Java'}
            }
            
            result = unified_api.get_vacancies_from_sources('developer', sources=['hh', 'sj'])
            
            assert len(result) == 2
            mock_hh_get.assert_called_once_with('developer')
            mock_sj_get.assert_called_once_with('developer')
    
    @patch('src.api_modules.unified_api.logger')
    def test_get_vacancies_from_sources_hh_error(self, mock_logger, unified_api):
        """Тест обработки ошибки HH API"""
        with patch.object(unified_api.hh_api, 'get_vacancies') as mock_hh_get:
            mock_hh_get.side_effect = Exception("API Error")
            
            result = unified_api.get_vacancies_from_sources('python', sources=['hh'])
            
            assert len(result) == 0
            mock_logger.error.assert_called()
    
    @patch('src.api_modules.unified_api.logger')
    def test_get_vacancies_from_sources_sj_error(self, mock_logger, unified_api):
        """Тест обработки ошибки SuperJob API"""
        with patch.object(unified_api.sj_api, 'get_vacancies') as mock_sj_get:
            mock_sj_get.side_effect = Exception("API Error")
            
            result = unified_api.get_vacancies_from_sources('python', sources=['sj'])
            
            assert len(result) == 0
            mock_logger.error.assert_called()
    
    def test_get_hh_vacancies(self, unified_api, sample_hh_vacancy_data):
        """Тест получения только HH вакансий"""
        with patch.object(unified_api, 'get_vacancies_from_sources') as mock_get:
            mock_get.return_value = [Vacancy.from_dict(sample_hh_vacancy_data)]
            
            result = unified_api.get_hh_vacancies('python')
            
            assert len(result) == 1
            mock_get.assert_called_once_with('python', sources=['hh'])
    
    def test_get_sj_vacancies(self, unified_api, sample_sj_vacancy_data):
        """Тест получения только SuperJob вакансий"""
        with patch.object(unified_api, 'get_vacancies_from_sources') as mock_get:
            mock_get.return_value = [Vacancy.from_dict({
                'id': '456',
                'name': 'Java Developer',
                'alternate_url': 'https://superjob.ru/vacancy/456',
                'salary': {'from': 120000, 'to': 180000, 'currency': 'RUR'},
                'snippet': {'responsibility': 'Разработка на Java'}
            })]
            
            result = unified_api.get_sj_vacancies('java', period=7)
            
            assert len(result) == 1
            mock_get.assert_called_once_with('java', sources=['sj'], published=7)
    
    @patch('src.api_modules.unified_api.logger')
    def test_clear_cache(self, mock_logger, unified_api):
        """Тест очистки кэша"""
        with patch.object(unified_api.hh_api, 'clear_cache') as mock_hh_clear, \
             patch.object(unified_api.sj_api, 'clear_cache') as mock_sj_clear:
            
            unified_api.clear_cache({'hh': True, 'sj': True})
            
            mock_hh_clear.assert_called_once()
            mock_sj_clear.assert_called_once()
            mock_logger.info.assert_called()
    
    @patch('src.api_modules.unified_api.logger')
    def test_clear_cache_hh_only(self, mock_logger, unified_api):
        """Тест очистки кэша только HH"""
        with patch.object(unified_api.hh_api, 'clear_cache') as mock_hh_clear, \
             patch.object(unified_api.sj_api, 'clear_cache') as mock_sj_clear:
            
            unified_api.clear_cache({'hh': True, 'sj': False})
            
            mock_hh_clear.assert_called_once()
            mock_sj_clear.assert_not_called()
    
    @patch('src.api_modules.unified_api.logger')
    def test_clear_all_cache(self, mock_logger, unified_api):
        """Тест очистки всего кэша"""
        with patch.object(unified_api.hh_api, 'clear_cache') as mock_hh_clear, \
             patch.object(unified_api.sj_api, 'clear_cache') as mock_sj_clear:
            
            unified_api.clear_all_cache()
            
            mock_hh_clear.assert_called_once()
            mock_sj_clear.assert_called_once()
            mock_logger.info.assert_called()
    
    @patch('src.api_modules.unified_api.logger')
    def test_clear_cache_error(self, mock_logger, unified_api):
        """Тест обработки ошибки при очистке кэша"""
        with patch.object(unified_api.hh_api, 'clear_cache') as mock_hh_clear:
            mock_hh_clear.side_effect = Exception("Clear error")
            
            unified_api.clear_cache({'hh': True})
            
            mock_logger.error.assert_called()
    
    def test_get_available_sources(self, unified_api):
        """Тест получения доступных источников"""
        sources = unified_api.get_available_sources()
        
        assert sources == ['hh', 'sj']
    
    def test_validate_sources_valid(self, unified_api):
        """Тест валидации валидных источников"""
        result = unified_api.validate_sources(['hh', 'sj'])
        
        assert result == ['hh', 'sj']
    
    def test_validate_sources_invalid(self, unified_api):
        """Тест валидации невалидных источников"""
        with patch('src.api_modules.unified_api.logger') as mock_logger:
            result = unified_api.validate_sources(['invalid'])
            
            assert result == ['hh', 'sj']
            mock_logger.warning.assert_called()
    
    def test_validate_sources_mixed(self, unified_api):
        """Тест валидации смешанных источников"""
        result = unified_api.validate_sources(['hh', 'invalid', 'sj'])
        
        assert result == ['hh', 'sj']

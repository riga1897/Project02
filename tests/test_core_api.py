
"""
Комплексные тесты для основных API модулей
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.api_modules.hh_api import HeadHunterAPI
from src.api_modules.sj_api import SuperJobAPI
from src.api_modules.unified_api import UnifiedAPI
from src.config.api_config import APIConfig


class TestHeadHunterAPI:
    """Тесты для HeadHunterAPI"""
    
    @pytest.fixture
    def hh_api(self):
        """Создание экземпляра HH API"""
        config = APIConfig()
        return HeadHunterAPI(config)
    
    @pytest.fixture
    def mock_api_response(self):
        """Мок ответа от API"""
        return {
            'items': [
                {
                    'name': 'Python Developer',
                    'alternate_url': 'https://hh.ru/vacancy/123',
                    'salary': {'from': 100000, 'to': 150000, 'currency': 'RUR'},
                    'snippet': {'responsibility': 'Разработка на Python'},
                    'employer': {'name': 'Tech Company'},
                    'id': '123'
                }
            ],
            'found': 1,
            'pages': 1
        }
    
    def test_init(self, hh_api):
        """Тест инициализации"""
        assert hh_api.BASE_URL == "https://api.hh.ru/vacancies"
        assert hh_api._config is not None
        assert hh_api._connector is not None
        assert hh_api._paginator is not None
    
    def test_validate_vacancy_valid(self, hh_api):
        """Тест валидации корректной вакансии"""
        vacancy = {
            'name': 'Python Developer',
            'alternate_url': 'https://hh.ru/vacancy/123',
            'salary': {'from': 100000, 'currency': 'RUR'},
            'id': '123'
        }
        assert hh_api._validate_vacancy(vacancy) is True
    
    def test_validate_vacancy_invalid(self, hh_api):
        """Тест валидации некорректной вакансии"""
        vacancy = {'name': 'Python Developer'}  # Отсутствуют обязательные поля
        assert hh_api._validate_vacancy(vacancy) is False
    
    @patch.object(HeadHunterAPI, '_CachedAPI__connect_to_api')
    def test_get_vacancies_page_success(self, mock_connect, hh_api, mock_api_response):
        """Тест успешного получения страницы вакансий"""
        mock_connect.return_value = mock_api_response
        
        result = hh_api.get_vacancies_page("Python", page=0)
        
        assert len(result) == 1
        assert result[0]['name'] == 'Python Developer'
        mock_connect.assert_called_once()
    
    @patch.object(HeadHunterAPI, '_CachedAPI__connect_to_api')
    def test_get_vacancies_page_error(self, mock_connect, hh_api):
        """Тест обработки ошибки при получении страницы"""
        mock_connect.side_effect = Exception("API Error")
        
        result = hh_api.get_vacancies_page("Python", page=0)
        
        assert result == []
    
    @patch.object(HeadHunterAPI, '_CachedAPI__connect_to_api')
    def test_get_vacancies_success(self, mock_connect, hh_api, mock_api_response):
        """Тест успешного получения всех вакансий"""
        mock_connect.return_value = mock_api_response
        
        result = hh_api.get_vacancies("Python")
        
        assert len(result) >= 1
        assert mock_connect.call_count >= 1
    
    def test_get_empty_response(self, hh_api):
        """Тест получения пустого ответа"""
        result = hh_api._get_empty_response()
        assert result == {'items': []}


class TestSuperJobAPI:
    """Тесты для SuperJobAPI"""
    
    @pytest.fixture
    def sj_api(self):
        """Создание экземпляра SJ API"""
        config = APIConfig()
        return SuperJobAPI(config)
    
    @pytest.fixture
    def mock_sj_response(self):
        """Мок ответа от SuperJob API"""
        return {
            'objects': [
                {
                    'profession': 'Python Developer',
                    'link': 'https://superjob.ru/vacancy/123',
                    'payment_from': 100000,
                    'payment_to': 150000,
                    'currency': 'rub',
                    'candidat': 'Опыт работы с Python',
                    'firm_name': 'Tech Company',
                    'id': 123
                }
            ],
            'total': 1
        }
    
    def test_init(self, sj_api):
        """Тест инициализации SuperJob API"""
        assert sj_api.BASE_URL == "https://api.superjob.ru/2.0/vacancies/"
        assert sj_api._config is not None
    
    @patch.object(SuperJobAPI, '_CachedAPI__connect_to_api')
    def test_get_vacancies_success(self, mock_connect, sj_api, mock_sj_response):
        """Тест успешного получения вакансий из SuperJob"""
        mock_connect.return_value = mock_sj_response
        
        result = sj_api.get_vacancies("Python")
        
        assert len(result) >= 1
        mock_connect.assert_called()


class TestUnifiedAPI:
    """Тесты для UnifiedAPI"""
    
    @pytest.fixture
    def unified_api(self):
        """Создание экземпляра UnifiedAPI"""
        return UnifiedAPI()
    
    @patch('src.api_modules.unified_api.HeadHunterAPI')
    @patch('src.api_modules.unified_api.SuperJobAPI')
    def test_search_from_both_sources(self, mock_sj, mock_hh, unified_api):
        """Тест поиска из обоих источников"""
        mock_hh_instance = Mock()
        mock_sj_instance = Mock()
        mock_hh.return_value = mock_hh_instance
        mock_sj.return_value = mock_sj_instance
        
        mock_hh_instance.get_vacancies.return_value = [{'name': 'HH Vacancy', 'source': 'hh'}]
        mock_sj_instance.get_vacancies.return_value = [{'profession': 'SJ Vacancy', 'source': 'sj'}]
        
        result = unified_api.search_vacancies("Python", sources=['hh', 'sj'])
        
        assert len(result) == 2
        mock_hh_instance.get_vacancies.assert_called_once()
        mock_sj_instance.get_vacancies.assert_called_once()

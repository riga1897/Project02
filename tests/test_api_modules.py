
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.api_modules.hh_api import HeadHunterAPI
from src.api_modules.sj_api import SuperJobAPI
from src.api_modules.unified_api import UnifiedAPI
from src.api_modules.get_api import APIConnector
from src.config.api_config import APIConfig


class TestHeadHunterAPI:
    
    @pytest.fixture
    def mock_config(self):
        config = Mock()
        config.hh_config = Mock()
        config.hh_config.get_params.return_value = {}
        config.get_pagination_params.return_value = {"max_pages": 5}
        return config
    
    @pytest.fixture
    def hh_api(self, mock_config):
        with patch('src.api_modules.hh_api.APIConnector'), \
             patch('src.api_modules.hh_api.Paginator'):
            return HeadHunterAPI(mock_config)
    
    def test_init(self, hh_api):
        assert hh_api is not None
        assert hh_api.BASE_URL == "https://api.hh.ru/vacancies"
        assert hh_api.DEFAULT_CACHE_DIR == "data/cache/hh"
    
    def test_get_empty_response(self, hh_api):
        response = hh_api._get_empty_response()
        assert response == {'items': []}
    
    def test_validate_vacancy_valid(self, hh_api):
        vacancy = {
            'name': 'Python Developer',
            'alternate_url': 'https://example.com',
            'salary': {'from': 50000}
        }
        assert hh_api._validate_vacancy(vacancy) is True
    
    def test_validate_vacancy_invalid(self, hh_api):
        vacancy = {'name': 'Python Developer'}  # Missing required fields
        assert hh_api._validate_vacancy(vacancy) is False
    
    def test_get_vacancies_page(self, hh_api):
        with patch.object(hh_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.return_value = {
                'items': [
                    {
                        'name': 'Python Developer',
                        'alternate_url': 'https://example.com',
                        'salary': {'from': 50000}
                    }
                ]
            }
            
            result = hh_api.get_vacancies_page("Python", 0)
            assert len(result) == 1
            assert result[0]['name'] == 'Python Developer'
    
    def test_get_vacancies_empty_response(self, hh_api):
        with patch.object(hh_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.return_value = {'items': []}
            
            result = hh_api.get_vacancies_page("Python", 0)
            assert result == []
    
    def test_get_vacancies_full(self, hh_api):
        with patch.object(hh_api, '_CachedAPI__connect_to_api') as mock_connect, \
             patch.object(hh_api._paginator, 'paginate') as mock_paginate:
            
            mock_connect.return_value = {
                'found': 10,
                'pages': 2
            }
            mock_paginate.return_value = []
            
            result = hh_api.get_vacancies("Python")
            assert isinstance(result, list)
            mock_paginate.assert_called_once()


class TestSuperJobAPI:
    
    @pytest.fixture
    def mock_config(self):
        config = Mock()
        config.get_params.return_value = {}
        return config
    
    @pytest.fixture
    def sj_api(self, mock_config):
        with patch('src.api_modules.sj_api.APIConnector'), \
             patch('src.api_modules.sj_api.Paginator'), \
             patch('src.api_modules.sj_api.EnvLoader.get_env_var') as mock_env:
            mock_env.return_value = 'test_key'
            return SuperJobAPI(mock_config)
    
    def test_init(self, sj_api):
        assert sj_api is not None
        assert sj_api.BASE_URL == "https://api.superjob.ru/2.0/vacancies"
        assert sj_api.DEFAULT_CACHE_DIR == "data/cache/sj"
    
    def test_get_empty_response(self, sj_api):
        response = sj_api._get_empty_response()
        assert response == {'objects': []}
    
    def test_validate_vacancy_valid(self, sj_api):
        vacancy = {
            'profession': 'Python Developer',
            'link': 'https://example.com'
        }
        assert sj_api._validate_vacancy(vacancy) is True
    
    def test_validate_vacancy_invalid(self, sj_api):
        vacancy = {'profession': 'Python Developer'}  # Missing required fields
        assert sj_api._validate_vacancy(vacancy) is False
    
    def test_get_vacancies_page(self, sj_api):
        with patch.object(sj_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.return_value = {
                'objects': [
                    {
                        'profession': 'Python Developer',
                        'link': 'https://example.com'
                    }
                ]
            }
            
            result = sj_api.get_vacancies_page("Python", 0)
            assert len(result) == 1
            assert result[0]['profession'] == 'Python Developer'
            assert result[0]['source'] == 'superjob.ru'


class TestUnifiedAPI:
    
    @pytest.fixture
    def unified_api(self):
        with patch('src.api_modules.unified_api.HeadHunterAPI') as mock_hh, \
             patch('src.api_modules.unified_api.SuperJobAPI') as mock_sj, \
             patch('src.api_modules.unified_api.SuperJobParser') as mock_parser:
            
            api = UnifiedAPI()
            api.hh_api = mock_hh.return_value
            api.sj_api = mock_sj.return_value
            api.parser = mock_parser.return_value
            return api
    
    def test_init(self, unified_api):
        assert unified_api is not None
        assert unified_api.hh_api is not None
        assert unified_api.sj_api is not None
        assert unified_api.parser is not None
    
    def test_get_available_sources(self, unified_api):
        sources = unified_api.get_available_sources()
        assert sources == ['hh', 'sj']
    
    def test_validate_sources_valid(self, unified_api):
        valid_sources = unified_api.validate_sources(['hh', 'sj'])
        assert valid_sources == ['hh', 'sj']
    
    def test_validate_sources_invalid(self, unified_api):
        valid_sources = unified_api.validate_sources(['invalid'])
        assert valid_sources == ['hh', 'sj']  # Should return all available
    
    def test_clear_cache(self, unified_api):
        unified_api.clear_cache({'hh': True, 'sj': False})
        unified_api.hh_api.clear_cache.assert_called_once()
        unified_api.sj_api.clear_cache.assert_not_called()
    
    def test_clear_all_cache(self, unified_api):
        unified_api.clear_all_cache()
        unified_api.hh_api.clear_cache.assert_called_once()
        unified_api.sj_api.clear_cache.assert_called_once()


class TestAPIConnector:
    
    @pytest.fixture
    def api_config(self):
        return APIConfig(user_agent="TestApp/1.0", timeout=10)
    
    @pytest.fixture
    def connector(self, api_config):
        return APIConnector(api_config)
    
    def test_init(self, connector):
        assert connector is not None
        assert connector.headers['User-Agent'] == "TestApp/1.0"
        assert connector.headers['Accept'] == 'application/json'
    
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_success(self, mock_get, connector):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'test': 'data'}
        mock_get.return_value = mock_response
        
        result = connector.connect('https://api.test.com', {'param': 'value'})
        assert result == {'test': 'data'}
    
    def test_connect_timeout_error(self, connector):
        with patch('src.api_modules.get_api.requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection timeout")
            
            with pytest.raises(Exception):
                connector.connect('https://api.test.com', {})
    
    def test_connect_http_error(self, connector):
        with patch('src.api_modules.get_api.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = Exception("Not found")
            mock_get.return_value = mock_response
            
            with pytest.raises(Exception):
                connector.connect('https://api.test.com', {})

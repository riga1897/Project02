
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from typing import Dict, List

from src.api_modules.cached_api import CachedAPI


class TestCachedAPIImplementation(CachedAPI):
    """Concrete implementation of CachedAPI for testing"""
    
    def _get_empty_response(self) -> Dict:
        return {'items': [], 'found': 0}
    
    def _validate_vacancy(self, vacancy: Dict) -> bool:
        return vacancy is not None and 'id' in vacancy
    
    def get_vacancies_page(self, search_query: str, page: int = 0, **kwargs) -> List[Dict]:
        return []
    
    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict]:
        return []


class TestCachedAPI:
    """Tests for CachedAPI class"""
    
    @pytest.fixture
    def cached_api(self):
        """Create a test instance of CachedAPI"""
        with patch('src.api_modules.cached_api.Path') as mock_path:
            mock_path_instance = Mock()
            mock_path.return_value = mock_path_instance
            
            api = TestCachedAPIImplementation("test_cache")
            api.connector = Mock()
            return api
    
    def test_init_cache(self, cached_api):
        """Test cache initialization"""
        assert cached_api.cache_dir is not None
        assert cached_api.cache is not None
    
    @patch('src.api_modules.cached_api.logger')
    def test_cached_api_request_success(self, mock_logger, cached_api):
        """Test successful cached API request"""
        test_data = {'items': [{'id': 1}], 'found': 1}
        cached_api.connector._APIConnector__connect.return_value = test_data
        
        result = cached_api._cached_api_request("http://test.com", {"param": "value"}, "test")
        
        assert result == test_data
        cached_api.connector._APIConnector__connect.assert_called_once_with("http://test.com", {"param": "value"})
    
    @patch('src.api_modules.cached_api.logger')
    def test_cached_api_request_exception(self, mock_logger, cached_api):
        """Test cached API request with exception"""
        cached_api.connector._APIConnector__connect.side_effect = Exception("API Error")
        
        result = cached_api._cached_api_request("http://test.com", {"param": "value"}, "test")
        
        assert result == {'items': [], 'found': 0}
        mock_logger.error.assert_called_once()
    
    @patch('src.api_modules.cached_api.logger')
    def test_connect_to_api_memory_cache_hit(self, mock_logger, cached_api):
        """Test connect to API with memory cache hit"""
        test_data = {'items': [{'id': 1}], 'found': 1}
        
        with patch.object(cached_api, '_cached_api_request', return_value=test_data):
            result = cached_api._CachedAPI__connect_to_api("http://test.com", {"param": "value"}, "test")
            
            assert result == test_data
            mock_logger.debug.assert_called_with("Данные получены из кэша в памяти для test")
    
    @patch('src.api_modules.cached_api.logger')
    def test_connect_to_api_file_cache_hit(self, mock_logger, cached_api):
        """Test connect to API with file cache hit"""
        empty_response = {'items': [], 'found': 0}
        cached_response = {'data': {'items': [{'id': 1}], 'found': 1}}
        
        with patch.object(cached_api, '_cached_api_request', return_value=empty_response):
            cached_api.cache.load_response.return_value = cached_response
            
            result = cached_api._CachedAPI__connect_to_api("http://test.com", {"param": "value"}, "test")
            
            assert result == cached_response['data']
            mock_logger.debug.assert_called_with("Данные получены из файлового кэша для test")
    
    @patch('src.api_modules.cached_api.logger')
    def test_connect_to_api_direct_request(self, mock_logger, cached_api):
        """Test connect to API with direct request"""
        empty_response = {'items': [], 'found': 0}
        api_response = {'items': [{'id': 1}], 'found': 1}
        
        with patch.object(cached_api, '_cached_api_request', return_value=empty_response):
            cached_api.cache.load_response.return_value = None
            cached_api.connector._APIConnector__connect.return_value = api_response
            
            result = cached_api._CachedAPI__connect_to_api("http://test.com", {"param": "value"}, "test")
            
            assert result == api_response
            cached_api.cache.save_response.assert_called_once_with("test", {"param": "value"}, api_response)
    
    @patch('src.api_modules.cached_api.logger')
    def test_connect_to_api_memory_cache_exception(self, mock_logger, cached_api):
        """Test connect to API with memory cache exception"""
        cached_response = {'data': {'items': [{'id': 1}], 'found': 1}}
        
        with patch.object(cached_api, '_cached_api_request', side_effect=Exception("Cache error")):
            cached_api.cache.load_response.return_value = cached_response
            
            result = cached_api._CachedAPI__connect_to_api("http://test.com", {"param": "value"}, "test")
            
            assert result == cached_response['data']
    
    @patch('src.api_modules.cached_api.logger')
    def test_connect_to_api_direct_request_exception(self, mock_logger, cached_api):
        """Test connect to API with direct request exception"""
        empty_response = {'items': [], 'found': 0}
        
        with patch.object(cached_api, '_cached_api_request', return_value=empty_response):
            cached_api.cache.load_response.return_value = None
            cached_api.connector._APIConnector__connect.side_effect = Exception("API Error")
            
            result = cached_api._CachedAPI__connect_to_api("http://test.com", {"param": "value"}, "test")
            
            assert result == empty_response
            mock_logger.error.assert_called_with("Ошибка многоуровневого кэширования: API Error")
    
    @patch('src.api_modules.cached_api.logger')
    def test_clear_cache_success(self, mock_logger, cached_api):
        """Test successful cache clearing"""
        mock_clear_cache = Mock()
        cached_api._cached_api_request.clear_cache = mock_clear_cache
        
        cached_api.clear_cache("test")
        
        cached_api.cache.clear.assert_called_once_with("test")
        mock_clear_cache.assert_called_once()
        mock_logger.info.assert_called_with("Кэш test очищен (файловый и в памяти)")
    
    @patch('src.api_modules.cached_api.logger')
    def test_clear_cache_memory_error(self, mock_logger, cached_api):
        """Test cache clearing with memory cache error"""
        mock_clear_cache = Mock(side_effect=Exception("Memory cache error"))
        cached_api._cached_api_request.clear_cache = mock_clear_cache
        
        cached_api.clear_cache("test")
        
        cached_api.cache.clear.assert_called_once_with("test")
        mock_logger.warning.assert_called_with("Ошибка очистки кэша в памяти: Memory cache error")
        mock_logger.info.assert_called_with("Кэш test очищен (файловый и в памяти)")
    
    @patch('src.api_modules.cached_api.logger')
    def test_clear_cache_no_clear_method(self, mock_logger, cached_api):
        """Test cache clearing when clear_cache method doesn't exist"""
        # Remove clear_cache method
        if hasattr(cached_api._cached_api_request, 'clear_cache'):
            delattr(cached_api._cached_api_request, 'clear_cache')
        
        cached_api.clear_cache("test")
        
        cached_api.cache.clear.assert_called_once_with("test")
        mock_logger.info.assert_called_with("Кэш test очищен (файловый и в памяти)")
    
    @patch('src.api_modules.cached_api.logger')
    def test_clear_cache_exception(self, mock_logger, cached_api):
        """Test cache clearing with general exception"""
        cached_api.cache.clear.side_effect = Exception("Clear error")
        
        cached_api.clear_cache("test")
        
        mock_logger.error.assert_called_with("Ошибка очистки кэша test: Clear error")
    
    @patch('src.api_modules.cached_api.Path')
    def test_get_cache_status_success(self, mock_path, cached_api):
        """Test successful cache status retrieval"""
        # Mock file listing
        mock_file1 = Mock()
        mock_file1.name = "test_file1.json"
        mock_file2 = Mock()
        mock_file2.name = "test_file2.json"
        cached_api.cache_dir.glob.return_value = [mock_file1, mock_file2]
        
        # Mock cache info
        mock_cache_info = {'size': 5, 'max_size': 1000, 'ttl': 300}
        cached_api._cached_api_request.cache_info = Mock(return_value=mock_cache_info)
        
        result = cached_api.get_cache_status("test")
        
        expected = {
            'cache_dir': str(cached_api.cache_dir),
            'cache_dir_exists': cached_api.cache_dir.exists(),
            'file_cache_count': 2,
            'cache_files': ['test_file1.json', 'test_file2.json'],
            'memory_cache': mock_cache_info
        }
        
        assert result == expected
        cached_api.cache_dir.glob.assert_called_once_with("test_*.json")
    
    def test_get_cache_status_no_cache_info(self, cached_api):
        """Test cache status when cache_info method doesn't exist"""
        # Remove cache_info method
        if hasattr(cached_api._cached_api_request, 'cache_info'):
            delattr(cached_api._cached_api_request, 'cache_info')
        
        cached_api.cache_dir.glob.return_value = []
        
        result = cached_api.get_cache_status("test")
        
        assert result['memory_cache'] == {}
    
    @patch('src.api_modules.cached_api.logger')
    def test_get_cache_status_exception(self, mock_logger, cached_api):
        """Test cache status with exception"""
        cached_api.cache_dir.glob.side_effect = Exception("Status error")
        
        result = cached_api.get_cache_status("test")
        
        assert result == {'error': 'Status error'}
        mock_logger.error.assert_called_with("Ошибка получения статуса кэша: Status error")
    
    def test_abstract_methods_exist(self, cached_api):
        """Test that abstract methods are implemented"""
        assert hasattr(cached_api, '_get_empty_response')
        assert hasattr(cached_api, '_validate_vacancy')
        assert hasattr(cached_api, 'get_vacancies_page')
        assert hasattr(cached_api, 'get_vacancies')
        
        # Test calling abstract methods
        assert cached_api._get_empty_response() == {'items': [], 'found': 0}
        assert cached_api._validate_vacancy({'id': 1}) is True
        assert cached_api._validate_vacancy(None) is False
        assert cached_api.get_vacancies_page("test") == []
        assert cached_api.get_vacancies("test") == []


class TestCachedAPIEdgeCases:
    """Test edge cases for CachedAPI"""
    
    @pytest.fixture
    def cached_api(self):
        """Create a test instance of CachedAPI"""
        with patch('src.api_modules.cached_api.Path') as mock_path:
            mock_path_instance = Mock()
            mock_path.return_value = mock_path_instance
            
            api = TestCachedAPIImplementation("test_cache")
            api.connector = Mock()
            return api
    
    @patch('src.api_modules.cached_api.logger')
    def test_connect_to_api_empty_response_not_cached(self, mock_logger, cached_api):
        """Test that empty responses are not cached"""
        empty_response = {'items': [], 'found': 0}
        
        with patch.object(cached_api, '_cached_api_request', return_value=empty_response):
            cached_api.cache.load_response.return_value = None
            cached_api.connector._APIConnector__connect.return_value = empty_response
            
            result = cached_api._CachedAPI__connect_to_api("http://test.com", {"param": "value"}, "test")
            
            assert result == empty_response
            # Should not save empty response to cache
            cached_api.cache.save_response.assert_not_called()
    
    @patch('src.api_modules.cached_api.logger') 
    def test_connect_to_api_none_response_not_cached(self, mock_logger, cached_api):
        """Test that None responses are not cached"""
        empty_response = {'items': [], 'found': 0}
        
        with patch.object(cached_api, '_cached_api_request', return_value=empty_response):
            cached_api.cache.load_response.return_value = None
            cached_api.connector._APIConnector__connect.return_value = None
            
            result = cached_api._CachedAPI__connect_to_api("http://test.com", {"param": "value"}, "test")
            
            assert result == empty_response
            cached_api.cache.save_response.assert_not_called()

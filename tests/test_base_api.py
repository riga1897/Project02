
import pytest
from abc import ABC
from unittest.mock import Mock, patch
from typing import Any, Optional

from src.api_modules.base_api import BaseAPI
from src.config.api_config import APIConfig


class TestBaseAPI:
    """Тесты для абстрактного класса BaseAPI"""

    def test_is_abstract_class(self):
        """Проверяем, что BaseAPI является абстрактным классом"""
        assert issubclass(BaseAPI, ABC)
        
        # Проверяем, что нельзя создать экземпляр абстрактного класса
        with pytest.raises(TypeError):
            BaseAPI()

    def test_has_abstract_methods(self):
        """Проверяем наличие абстрактных методов"""
        abstract_methods = BaseAPI.__abstractmethods__
        expected_methods = {'get_vacancies', 'clear_cache'}
        assert abstract_methods == expected_methods

    @patch('src.api_modules.base_api.APIConnector')
    def test_init_with_default_config(self, mock_connector):
        """Проверяем инициализацию с конфигурацией по умолчанию"""
        
        class ConcreteAPI(BaseAPI):
            def get_vacancies(self, search_query: str, **kwargs) -> Any:
                return []
            
            def clear_cache(self, api_prefix: str):
                pass

        # Создаем экземпляр с конфигурацией по умолчанию
        api = ConcreteAPI()
        
        # Проверяем, что создался APIConfig по умолчанию
        assert api.config is not None
        assert isinstance(api.config, APIConfig)
        
        # Проверяем, что создался connector
        mock_connector.assert_called_once_with(api.config)

    @patch('src.api_modules.base_api.APIConnector')
    def test_init_with_custom_config(self, mock_connector):
        """Проверяем инициализацию с пользовательской конфигурацией"""
        
        class ConcreteAPI(BaseAPI):
            def get_vacancies(self, search_query: str, **kwargs) -> Any:
                return []
            
            def clear_cache(self, api_prefix: str):
                pass

        # Создаем пользовательскую конфигурацию
        custom_config = APIConfig()
        
        # Создаем экземпляр с пользовательской конфигурацией
        api = ConcreteAPI(custom_config)
        
        # Проверяем, что используется переданная конфигурация
        assert api.config is custom_config
        
        # Проверяем, что создался connector с правильной конфигурацией
        mock_connector.assert_called_once_with(custom_config)

    def test_concrete_implementation_works(self):
        """Проверяем, что конкретная реализация работает"""
        
        class ConcreteAPI(BaseAPI):
            def __init__(self, config: Optional[APIConfig] = None):
                # Мокаем connector для избежания реального создания
                with patch('src.api_modules.base_api.APIConnector'):
                    super().__init__(config)
                self.cache_data = {}

            def get_vacancies(self, search_query: str, **kwargs) -> Any:
                # Простая реализация
                limit = kwargs.get('limit', 10)
                return [f"Vacancy {i} for {search_query}" for i in range(min(limit, 5))]

            def clear_cache(self, api_prefix: str):
                # Простая очистка кэша
                if api_prefix in self.cache_data:
                    del self.cache_data[api_prefix]
                    return True
                return False

        # Тестируем конкретную реализацию
        api = ConcreteAPI()
        
        # Тестируем get_vacancies
        result = api.get_vacancies("Python developer")
        assert len(result) == 5
        assert "Python developer" in result[0]
        
        # Тестируем с параметрами
        result_limited = api.get_vacancies("Java developer", limit=3)
        assert len(result_limited) == 3
        
        # Тестируем clear_cache
        api.cache_data["test"] = "data"
        result = api.clear_cache("test")
        assert result is True
        assert "test" not in api.cache_data
        
        # Тест очистки несуществующего кэша
        result_false = api.clear_cache("nonexistent")
        assert result_false is False

    def test_incomplete_implementation_fails(self):
        """Проверяем, что неполная реализация не работает"""
        
        class IncompleteAPI(BaseAPI):
            def get_vacancies(self, search_query: str, **kwargs) -> Any:
                return []
            # clear_cache не реализован

        # Попытка создать экземпляр должна вызвать ошибку
        with pytest.raises(TypeError):
            IncompleteAPI()

    def test_method_signatures(self):
        """Проверяем сигнатуры методов"""
        
        # Проверяем get_vacancies
        get_method = getattr(BaseAPI, 'get_vacancies')
        assert hasattr(get_method, '__isabstractmethod__')
        
        # Проверяем clear_cache
        clear_method = getattr(BaseAPI, 'clear_cache')
        assert hasattr(clear_method, '__isabstractmethod__')

    def test_inheritance_chain(self):
        """Проверяем цепочку наследования"""
        
        class ConcreteAPI(BaseAPI):
            def __init__(self):
                with patch('src.api_modules.base_api.APIConnector'):
                    super().__init__()

            def get_vacancies(self, search_query: str, **kwargs) -> Any:
                return []
            
            def clear_cache(self, api_prefix: str):
                pass

        api = ConcreteAPI()
        assert isinstance(api, BaseAPI)
        assert isinstance(api, ABC)

    def test_multiple_api_implementations(self):
        """Проверяем работу нескольких API реализаций"""
        
        class HAPI(BaseAPI):
            def __init__(self):
                with patch('src.api_modules.base_api.APIConnector'):
                    super().__init__()

            def get_vacancies(self, search_query: str, **kwargs) -> Any:
                return [f"HH: {search_query}"]
            
            def clear_cache(self, api_prefix: str):
                return f"HH cache cleared for {api_prefix}"

        class SJAPI(BaseAPI):
            def __init__(self):
                with patch('src.api_modules.base_api.APIConnector'):
                    super().__init__()

            def get_vacancies(self, search_query: str, **kwargs) -> Any:
                return [f"SJ: {search_query}"]
            
            def clear_cache(self, api_prefix: str):
                return f"SJ cache cleared for {api_prefix}"

        # Создаем экземпляры разных реализаций
        hh_api = HAPI()
        sj_api = SJAPI()
        
        # Проверяем, что оба являются BaseAPI
        assert isinstance(hh_api, BaseAPI)
        assert isinstance(sj_api, BaseAPI)
        
        # Проверяем различное поведение
        hh_result = hh_api.get_vacancies("Python")
        sj_result = sj_api.get_vacancies("Python")
        
        assert hh_result == ["HH: Python"]
        assert sj_result == ["SJ: Python"]
        
        # Проверяем clear_cache
        hh_clear = hh_api.clear_cache("test")
        sj_clear = sj_api.clear_cache("test")
        
        assert hh_clear == "HH cache cleared for test"
        assert sj_clear == "SJ cache cleared for test"

    @patch('src.api_modules.base_api.APIConnector')
    def test_connector_attribute_exists(self, mock_connector):
        """Проверяем, что у экземпляра есть атрибут connector"""
        
        class ConcreteAPI(BaseAPI):
            def get_vacancies(self, search_query: str, **kwargs) -> Any:
                return []
            
            def clear_cache(self, api_prefix: str):
                pass

        api = ConcreteAPI()
        
        # Проверяем, что атрибут connector существует
        assert hasattr(api, 'connector')
        assert api.connector is not None

    @patch('src.api_modules.base_api.APIConnector')
    def test_config_attribute_exists(self, mock_connector):
        """Проверяем, что у экземпляра есть атрибут config"""
        
        class ConcreteAPI(BaseAPI):
            def get_vacancies(self, search_query: str, **kwargs) -> Any:
                return []
            
            def clear_cache(self, api_prefix: str):
                pass

        api = ConcreteAPI()
        
        # Проверяем, что атрибут config существует
        assert hasattr(api, 'config')
        assert api.config is not None
        assert isinstance(api.config, APIConfig)

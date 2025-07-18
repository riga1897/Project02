
"""
Тесты для конфигурационных модулей
"""

import pytest
from src.config.api_config import APIConfig
from src.config.hh_api_config import HHAPIConfig
from src.config.sj_api_config import SJAPIConfig


class TestAPIConfig:
    """Тесты для основной конфигурации API"""
    
    def test_default_config(self):
        """Тест конфигурации по умолчанию"""
        config = APIConfig()
        
        assert config.user_agent is not None
        assert config.timeout > 0
        assert isinstance(config.hh_config, HHAPIConfig)
        assert isinstance(config.sj_config, SJAPIConfig)
    
    def test_custom_config(self):
        """Тест пользовательской конфигурации"""
        config = APIConfig(
            user_agent="Custom Agent",
            timeout=30
        )
        
        assert config.user_agent == "Custom Agent"
        assert config.timeout == 30
    
    def test_pagination_params(self):
        """Тест параметров пагинации"""
        config = APIConfig()
        
        params = config.get_pagination_params()
        assert "max_pages" in params
        assert "per_page" in params
        
        # С пользовательскими параметрами
        custom_params = config.get_pagination_params(max_pages=10)
        assert custom_params["max_pages"] == 10


class TestHHAPIConfig:
    """Тесты для конфигурации HH API"""
    
    def test_default_params(self):
        """Тест параметров по умолчанию"""
        config = HHAPIConfig()
        params = config.get_params()
        
        assert "per_page" in params
        assert "only_with_salary" in params
        assert "area" in params
    
    def test_custom_params(self):
        """Тест пользовательских параметров"""
        config = HHAPIConfig()
        params = config.get_params(
            text="python",
            area=1,
            experience="between3And6"
        )
        
        assert params["text"] == "python"
        assert params["area"] == 1
        assert params["experience"] == "between3And6"


class TestSJAPIConfig:
    """Тесты для конфигурации SJ API"""
    
    def test_default_params(self):
        """Тест параметров по умолчанию"""
        config = SJAPIConfig()
        params = config.get_params()
        
        assert "count" in params
        assert "page" in params
    
    def test_custom_params(self):
        """Тест пользовательских параметров"""
        config = SJAPIConfig()
        params = config.get_params(
            keyword="python",
            town=4,
            catalogues=48
        )
        
        assert params["keyword"] == "python"
        assert params["town"] == 4
        assert params["catalogues"] == 48

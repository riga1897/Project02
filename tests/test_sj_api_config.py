
import pytest
from unittest.mock import Mock
from src.config.sj_api_config import SJAPIConfig


class TestSJAPIConfig:
    """Тест конфигурации SuperJob API"""

    def test_default_initialization(self):
        """Тест инициализации с параметрами по умолчанию"""
        config = SJAPIConfig()
        
        assert config.count == 500
        assert config.published == 15
        assert config.custom_params is None

    def test_custom_initialization(self):
        """Тест инициализации с кастомными параметрами"""
        custom_params = {"test": "value"}
        config = SJAPIConfig(
            count=100,
            published=30,
            custom_params=custom_params
        )
        
        assert config.count == 100
        assert config.published == 30
        assert config.custom_params == custom_params

    def test_get_params_default(self):
        """Тест получения параметров по умолчанию"""
        config = SJAPIConfig()
        params = config.get_params()
        
        expected = {
            "count": 500,
            "order_field": "date",
            "order_direction": "desc",
            "published": 15
        }
        assert params == expected

    def test_get_params_with_overrides(self):
        """Тест получения параметров с переопределением"""
        config = SJAPIConfig()
        params = config.get_params(
            count=200,
            order_field="salary",
            order_direction="asc",
            published=7
        )
        
        expected = {
            "count": 200,
            "order_field": "salary",
            "order_direction": "asc",
            "published": 7
        }
        assert params == expected

    def test_get_params_with_page(self):
        """Тест получения параметров с пагинацией"""
        config = SJAPIConfig()
        params = config.get_params(page=2)
        
        expected = {
            "count": 500,
            "order_field": "date",
            "order_direction": "desc",
            "published": 15,
            "page": 2
        }
        assert params == expected

    def test_get_params_with_town(self):
        """Тест получения параметров с указанием города"""
        config = SJAPIConfig()
        params = config.get_params(town="Москва")
        
        expected = {
            "count": 500,
            "order_field": "date",
            "order_direction": "desc",
            "published": 15,
            "town": "Москва"
        }
        assert params == expected

    def test_get_params_with_custom_params(self):
        """Тест получения параметров с кастомными параметрами"""
        custom_params = {"param1": "value1", "param2": "value2"}
        config = SJAPIConfig(custom_params=custom_params)
        params = config.get_params(param3="value3")
        
        expected = {
            "count": 500,
            "order_field": "date",
            "order_direction": "desc",
            "published": 15,
            "param1": "value1",
            "param2": "value2",
            "param3": "value3"
        }
        assert params == expected

    def test_get_params_kwargs_override_custom(self):
        """Тест переопределения кастомных параметров через kwargs"""
        custom_params = {"param1": "old_value"}
        config = SJAPIConfig(custom_params=custom_params)
        params = config.get_params(param1="new_value")
        
        assert params["param1"] == "new_value"

    def test_get_params_all_optional_fields(self):
        """Тест получения параметров со всеми опциональными полями"""
        config = SJAPIConfig()
        params = config.get_params(
            page=1,
            town="Санкт-Петербург",
            extra_param="test"
        )
        
        expected = {
            "count": 500,
            "order_field": "date",
            "order_direction": "desc",
            "published": 15,
            "page": 1,
            "town": "Санкт-Петербург",
            "extra_param": "test"
        }
        assert params == expected

    def test_get_params_with_none_custom_params(self):
        """Тест получения параметров когда custom_params равен None"""
        config = SJAPIConfig(custom_params=None)
        params = config.get_params(test="value")
        
        expected = {
            "count": 500,
            "order_field": "date",
            "order_direction": "desc",
            "published": 15,
            "test": "value"
        }
        assert params == expected

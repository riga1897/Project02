from src.config.hh_api_config import HHAPIConfig


class TestHHAPIConfig:
    """Тест конфигурации HH API"""

    def test_default_initialization(self):
        """Тест инициализации с параметрами по умолчанию"""
        config = HHAPIConfig()
        
        assert config.area == 113
        assert config.per_page == 50
        assert config.only_with_salary is False
        assert config.period == 15
        assert config.custom_params == {}

    def test_custom_initialization(self):
        """Тест инициализации с кастомными параметрами"""
        custom_params = {"test": "value"}
        config = HHAPIConfig(
            area=1,
            per_page=100,
            only_with_salary=True,
            period=30,
            custom_params=custom_params
        )
        
        assert config.area == 1
        assert config.per_page == 100
        assert config.only_with_salary is True
        assert config.period == 30
        assert config.custom_params == custom_params

    def test_post_init_with_none_custom_params(self):
        """Тест __post_init__ с None в custom_params"""
        config = HHAPIConfig(custom_params=None)
        
        assert config.custom_params == {}

    def test_post_init_with_existing_custom_params(self):
        """Тест __post_init__ с существующими custom_params"""
        custom_params = {"param1": "value1"}
        config = HHAPIConfig(custom_params=custom_params)
        
        assert config.custom_params == custom_params

    def test_get_params_default(self):
        """Тест получения параметров по умолчанию"""
        config = HHAPIConfig()
        params = config.get_params()
        
        expected = {
            "area": 113,
            "per_page": 50,
            "only_with_salary": False,
            "period": 15
        }
        assert params == expected

    def test_get_params_with_overrides(self):
        """Тест получения параметров с переопределением"""
        config = HHAPIConfig()
        params = config.get_params(area=1, per_page=25, custom_param="test")
        
        expected = {
            "area": 1,
            "per_page": 25,
            "only_with_salary": False,
            "period": 15,
            "custom_param": "test"
        }
        assert params == expected

    def test_get_params_with_custom_params(self):
        """Тест получения параметров с кастомными параметрами"""
        custom_params = {"param1": "value1", "param2": "value2"}
        config = HHAPIConfig(custom_params=custom_params)
        params = config.get_params(param3="value3")
        
        expected = {
            "area": 113,
            "per_page": 50,
            "only_with_salary": False,
            "period": 15,
            "param1": "value1",
            "param2": "value2",
            "param3": "value3"
        }
        assert params == expected

    def test_get_params_kwargs_override_custom(self):
        """Тест переопределения кастомных параметров через kwargs"""
        custom_params = {"param1": "old_value"}
        config = HHAPIConfig(custom_params=custom_params)
        params = config.get_params(param1="new_value")
        
        assert params["param1"] == "new_value"

    def test_get_hh_params_compatibility(self):
        """Тест метода get_hh_params для совместимости"""
        config = HHAPIConfig()
        params = config.get_hh_params(area=1, custom_param="test")
        
        expected = {
            "area": 1,
            "per_page": 50,
            "only_with_salary": False,
            "period": 15,
            "custom_param": "test"
        }
        assert params == expected

    def test_get_hh_params_returns_same_as_get_params(self):
        """Тест что get_hh_params возвращает то же самое что и get_params"""
        config = HHAPIConfig(area=1, period=30)
        
        params1 = config.get_params(per_page=25)
        params2 = config.get_hh_params(per_page=25)
        
        assert params1 == params2

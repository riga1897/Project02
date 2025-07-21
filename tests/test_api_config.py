from src.config.api_config import APIConfig, HHAPIConfig


class TestHHAPIConfig:
    """Тест конфигурации HH API"""

    def test_default_initialization(self):
        """Тест инициализации с параметрами по умолчанию"""
        config = HHAPIConfig()

        assert config.area == 1
        assert config.per_page == 50
        assert config.only_with_salary is False
        assert config.custom_params is None

    def test_custom_initialization(self):
        """Тест инициализации с кастомными параметрами"""
        custom_params = {"test": "value"}
        config = HHAPIConfig(area=2, per_page=100, only_with_salary=True, custom_params=custom_params)

        assert config.area == 2
        assert config.per_page == 100
        assert config.only_with_salary is True
        assert config.custom_params == custom_params

    def test_get_params_default(self):
        """Тест получения параметров по умолчанию"""
        config = HHAPIConfig()
        params = config.get_params()

        expected = {"area": 1, "per_page": 50, "only_with_salary": False}
        assert params == expected

    def test_get_params_with_overrides(self):
        """Тест получения параметров с переопределением"""
        config = HHAPIConfig()
        params = config.get_params(area=2, per_page=25, custom_param="test")

        expected = {"area": 2, "per_page": 25, "only_with_salary": False, "custom_param": "test"}
        assert params == expected

    def test_get_params_with_custom_params(self):
        """Тест получения параметров с кастомными параметрами"""
        custom_params = {"param1": "value1", "param2": "value2"}
        config = HHAPIConfig(custom_params=custom_params)
        params = config.get_params(param3="value3")

        expected = {
            "area": 1,
            "per_page": 50,
            "only_with_salary": False,
            "param1": "value1",
            "param2": "value2",
            "param3": "value3",
        }
        assert params == expected

    def test_get_params_kwargs_override_custom(self):
        """Тест переопределения кастомных параметров через kwargs"""
        custom_params = {"param1": "old_value"}
        config = HHAPIConfig(custom_params=custom_params)
        params = config.get_params(param1="new_value")

        assert params["param1"] == "new_value"


class TestAPIConfig:
    """Тест основной конфигурации API"""

    def test_default_initialization(self):
        """Тест инициализации с параметрами по умолчанию"""
        config = APIConfig()

        assert config.user_agent == "MyVacancyApp/1.0"
        assert config.timeout == 15
        assert config.request_delay == 0.5
        assert isinstance(config.hh_config, HHAPIConfig)
        assert config.max_pages == 20

    def test_custom_initialization(self):
        """Тест инициализации с кастомными параметрами"""
        hh_config = HHAPIConfig(area=2)
        config = APIConfig(
            user_agent="CustomApp/2.0", timeout=30, request_delay=1.0, hh_config=hh_config, max_pages=50
        )

        assert config.user_agent == "CustomApp/2.0"
        assert config.timeout == 30
        assert config.request_delay == 1.0
        assert config.hh_config == hh_config
        assert config.max_pages == 50

    def test_initialization_without_hh_config(self):
        """Тест инициализации без передачи hh_config"""
        config = APIConfig(user_agent="TestApp/1.0")

        assert config.user_agent == "TestApp/1.0"
        assert isinstance(config.hh_config, HHAPIConfig)
        assert config.hh_config.area == 1  # Значение по умолчанию

    def test_get_pagination_params_default(self):
        """Тест получения параметров пагинации по умолчанию"""
        config = APIConfig()
        params = config.get_pagination_params()

        expected = {"max_pages": 20}
        assert params == expected

    def test_get_pagination_params_with_override(self):
        """Тест получения параметров пагинации с переопределением"""
        config = APIConfig(max_pages=10)
        params = config.get_pagination_params(max_pages=5)

        expected = {"max_pages": 5}
        assert params == expected

    def test_get_pagination_params_kwargs_priority(self):
        """Тест приоритета kwargs над значениями по умолчанию"""
        config = APIConfig(max_pages=20)
        params = config.get_pagination_params(max_pages=100)

        expected = {"max_pages": 100}
        assert params == expected

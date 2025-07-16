
import pytest
from src.config.api_config import HHAPIConfig, APIConfig


class TestHHAPIConfig:
    """Tests for HHAPIConfig class"""

    def test_default_initialization(self):
        """Test HHAPIConfig with default values"""
        config = HHAPIConfig()
        assert config.area == 1
        assert config.per_page == 50
        assert config.only_with_salary is False
        assert config.custom_params is None

    def test_custom_initialization(self):
        """Test HHAPIConfig with custom values"""
        custom_params = {"experience": "between1And3"}
        config = HHAPIConfig(
            area=2,
            per_page=100,
            only_with_salary=True,
            custom_params=custom_params
        )
        assert config.area == 2
        assert config.per_page == 100
        assert config.only_with_salary is True
        assert config.custom_params == custom_params

    def test_get_params_without_overrides(self):
        """Test get_params without any overrides"""
        config = HHAPIConfig(area=5, per_page=25, only_with_salary=True)
        params = config.get_params()
        
        expected = {
            "area": 5,
            "per_page": 25,
            "only_with_salary": True
        }
        assert params == expected

    def test_get_params_with_overrides(self):
        """Test get_params with keyword argument overrides"""
        config = HHAPIConfig(area=1, per_page=50)
        params = config.get_params(area=113, per_page=100, experience="noExperience")
        
        expected = {
            "area": 113,
            "per_page": 100,
            "only_with_salary": False,
            "experience": "noExperience"
        }
        assert params == expected

    def test_get_params_with_custom_params(self):
        """Test get_params with custom_params"""
        custom_params = {"schedule": "remote", "employment": "full"}
        config = HHAPIConfig(custom_params=custom_params)
        params = config.get_params()
        
        assert params["schedule"] == "remote"
        assert params["employment"] == "full"
        assert params["area"] == 1  # default value

    def test_get_params_custom_params_override(self):
        """Test that kwargs override custom_params"""
        custom_params = {"schedule": "remote", "area": 2}
        config = HHAPIConfig(custom_params=custom_params)
        params = config.get_params(area=113, schedule="office")
        
        assert params["area"] == 113  # kwargs override custom_params
        assert params["schedule"] == "office"  # kwargs override custom_params

    def test_get_params_with_none_custom_params(self):
        """Test get_params when custom_params is None"""
        config = HHAPIConfig(custom_params=None)
        params = config.get_params(area=5)
        
        expected = {
            "area": 5,
            "per_page": 50,
            "only_with_salary": False
        }
        assert params == expected


class TestAPIConfig:
    """Tests for APIConfig class"""

    def test_default_initialization(self):
        """Test APIConfig with default values"""
        config = APIConfig()
        assert config.user_agent == "MyVacancyApp/1.0"
        assert config.timeout == 15
        assert config.request_delay == 0.5
        assert config.max_pages == 20
        assert isinstance(config.hh_config, HHAPIConfig)

    def test_custom_initialization(self):
        """Test APIConfig with custom values"""
        custom_hh_config = HHAPIConfig(area=113, per_page=100)
        config = APIConfig(
            user_agent="TestApp/2.0",
            timeout=30,
            request_delay=1.0,
            hh_config=custom_hh_config,
            max_pages=50
        )
        
        assert config.user_agent == "TestApp/2.0"
        assert config.timeout == 30
        assert config.request_delay == 1.0
        assert config.hh_config == custom_hh_config
        assert config.max_pages == 50

    def test_hh_config_default_creation(self):
        """Test that HHAPIConfig is created by default when None is passed"""
        config = APIConfig(hh_config=None)
        assert isinstance(config.hh_config, HHAPIConfig)
        assert config.hh_config.area == 1  # default HHAPIConfig values

    def test_get_pagination_params_default(self):
        """Test get_pagination_params without overrides"""
        config = APIConfig(max_pages=25)
        params = config.get_pagination_params()
        
        expected = {"max_pages": 25}
        assert params == expected

    def test_get_pagination_params_with_overrides(self):
        """Test get_pagination_params with keyword argument overrides"""
        config = APIConfig(max_pages=20)
        params = config.get_pagination_params(max_pages=100)
        
        expected = {"max_pages": 100}
        assert params == expected

    def test_get_pagination_params_additional_kwargs(self):
        """Test get_pagination_params with additional keyword arguments"""
        config = APIConfig()
        params = config.get_pagination_params(max_pages=15, extra_param="value")
        
        expected = {"max_pages": 15}
        assert params == expected
        # Additional kwargs are not included in pagination params

    def test_integration_with_hh_config(self):
        """Test integration between APIConfig and HHAPIConfig"""
        hh_config = HHAPIConfig(area=113, only_with_salary=True)
        api_config = APIConfig(hh_config=hh_config, max_pages=10)
        
        # Test that hh_config methods work
        hh_params = api_config.hh_config.get_params(per_page=25)
        assert hh_params["area"] == 113
        assert hh_params["only_with_salary"] is True
        assert hh_params["per_page"] == 25
        
        # Test that pagination params work
        pagination_params = api_config.get_pagination_params()
        assert pagination_params["max_pages"] == 10

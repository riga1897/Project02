
import pytest
from src.config.hh_api_config import HHAPIConfig


class TestHHAPIConfig:
    """Tests for HHAPIConfig class from hh_api_config.py"""

    def test_default_initialization(self):
        """Test HHAPIConfig with default parameters"""
        config = HHAPIConfig()
        
        expected_params = {
            "area": 113,  # Russia
            "period": 7,
            "only_with_salary": True,
            "per_page": 50
        }
        
        assert config._default_hh_params == expected_params

    def test_custom_initialization(self):
        """Test HHAPIConfig with custom default parameters"""
        custom_params = {
            "area": 1,  # Moscow
            "period": 14,
            "only_with_salary": False,
            "per_page": 100,
            "experience": "between1And3"
        }
        
        config = HHAPIConfig(default_hh_params=custom_params)
        assert config._default_hh_params == custom_params

    def test_initialization_with_none(self):
        """Test HHAPIConfig initialization when None is passed"""
        config = HHAPIConfig(default_hh_params=None)
        
        expected_params = {
            "area": 113,
            "period": 7,
            "only_with_salary": True,
            "per_page": 50
        }
        
        assert config._default_hh_params == expected_params

    def test_get_hh_params_no_overrides(self):
        """Test get_hh_params without any overrides"""
        config = HHAPIConfig()
        params = config.get_hh_params()
        
        expected = {
            "area": 113,
            "period": 7,
            "only_with_salary": True,
            "per_page": 50
        }
        
        assert params == expected

    def test_get_hh_params_with_overrides(self):
        """Test get_hh_params with keyword argument overrides"""
        config = HHAPIConfig()
        params = config.get_hh_params(area=1, per_page=25, text="Python")
        
        expected = {
            "area": 1,  # overridden
            "period": 7,  # default
            "only_with_salary": True,  # default
            "per_page": 25,  # overridden
            "text": "Python"  # new parameter
        }
        
        assert params == expected

    def test_get_hh_params_custom_defaults_with_overrides(self):
        """Test get_hh_params with custom defaults and overrides"""
        custom_params = {
            "area": 2,
            "period": 30,
            "only_with_salary": False,
            "per_page": 20
        }
        
        config = HHAPIConfig(default_hh_params=custom_params)
        params = config.get_hh_params(area=113, text="Java")
        
        expected = {
            "area": 113,  # overridden
            "period": 30,  # from custom defaults
            "only_with_salary": False,  # from custom defaults
            "per_page": 20,  # from custom defaults
            "text": "Java"  # new parameter
        }
        
        assert params == expected

    def test_get_hh_params_preserves_defaults(self):
        """Test that get_hh_params doesn't modify the original defaults"""
        config = HHAPIConfig()
        original_defaults = config._default_hh_params.copy()
        
        # Call get_hh_params with overrides
        config.get_hh_params(area=999, new_param="test")
        
        # Verify defaults are unchanged
        assert config._default_hh_params == original_defaults

    def test_get_hh_params_empty_kwargs(self):
        """Test get_hh_params with empty kwargs"""
        custom_params = {"test": "value"}
        config = HHAPIConfig(default_hh_params=custom_params)
        params = config.get_hh_params()
        
        assert params == custom_params
        assert params is not config._default_hh_params  # Should be a copy

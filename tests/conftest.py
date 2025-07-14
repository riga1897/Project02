import pytest
from src.api_modules.hh_api import HeadHunterAPI
from src.config.api_config import APIConfig
from src.decorators.cache import simple_cache


@pytest.fixture
def default_hh_api():
    """Fixture providing default HeadHunterAPI instance."""
    return HeadHunterAPI()


@pytest.fixture
def custom_config():
    """Fixture providing custom APIConfig."""
    return APIConfig(
        user_agent="TestAgent/1.0",
        timeout=10,
        request_delay=0.1,
        default_hh_params={
            "area": 1,
            "period": 1,
            "per_page": 10
        }
    )


@pytest.fixture
def custom_hh_api(custom_config):
    """Fixture providing HeadHunterAPI with custom config."""
    return HeadHunterAPI(custom_config)


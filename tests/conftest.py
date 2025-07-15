import pytest
from src.api_modules.hh_api import HeadHunterAPI
from src.config.api_config import APIConfig
from src.decorators.cache import simple_cache
from pathlib import Path
import tempfile
from src.vacancies.models import Vacancy




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


@pytest.fixture
def temp_json_file():
    """Фикстура: создает временный JSON-файл"""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        yield Path(tmp.name)
    Path(tmp.name).unlink(missing_ok=True)


@pytest.fixture
def sample_vacancy():
    """Фикстура: возвращает тестовую вакансию"""
    return Vacancy("Python Dev", "http://test.com", "100000", "Test desc")


@pytest.fixture
def sample_vacancies():
    """Фикстура: возвращает список тестовых вакансий"""
    return [
        Vacancy("Python Dev", "http://test.com", "100000", "Test desc"),
        Vacancy("Data Scientist", "http://test.com", "150000", "ML"),
        Vacancy("Java Dev", "http://test.com", None, "Java coding")
    ]
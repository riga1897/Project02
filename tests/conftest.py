import pytest
from src.api_modules.hh_api import HeadHunterAPI
from src.config.api_config import APIConfig
from pathlib import Path
import tempfile
from src.vacancies.models import Vacancy


@pytest.fixture
def default_hh_api():
    """Фикстура: предоставляет экземпляр HeadHunterAPI с настройками по умолчанию."""
    # Создаем временную директорию для кэша
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cache_dir = HeadHunterAPI.DEFAULT_CACHE_DIR
        HeadHunterAPI.DEFAULT_CACHE_DIR = temp_dir
        HeadHunterAPI.ensure_cache_dir()
        yield HeadHunterAPI()
        HeadHunterAPI.DEFAULT_CACHE_DIR = original_cache_dir


@pytest.fixture
def custom_config():
    """Фикстура: предоставляет пользовательскую конфигурацию для API."""
    return APIConfig(
        user_agent="TestAgent/1.0",
        timeout=10
    )


@pytest.fixture
def temp_json_file():
    """Фикстура: создает временный JSON-файл для тестирования."""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        yield Path(tmp.name)
    Path(tmp.name).unlink(missing_ok=True)


@pytest.fixture
def initialized_json_file(tmp_path):
    """Фикстура: создает и инициализирует JSON-файл с пустым списком."""
    file_path = tmp_path / "test_vacancies.json"
    file_path.write_text("[]")
    return file_path


@pytest.fixture
def sample_vacancy():
    """Фикстура: возвращает тестовую вакансию."""
    vacancy = Vacancy(
        "Python Dev",
        "http://test.com",
        "100000",
        "Test desc"
    )
    vacancy.id = "test_id_1"
    return vacancy


@pytest.fixture
def sample_vacancies(sample_vacancy):
    """Фикстура: возвращает список тестовых вакансий."""
    vacancy2 = Vacancy(
        "Java Developer",
        "http://test.com",
        "90000",
        "Test description"
    )
    vacancy2.id = "test_id_2"

    vacancy3 = Vacancy(
        "Python Dev",
        "http://another.com",
        "110000",
        "Senior position"
    )
    vacancy3.id = "test_id_3"

    return [sample_vacancy, vacancy2, vacancy3]

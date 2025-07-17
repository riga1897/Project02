import os
import pytest
from src.api_modules.hh_api import HeadHunterAPI

# Автоматически отключаем прогресс-бары для всех тестов
os.environ['DISABLE_TQDM'] = '1'
from src.config.api_config import APIConfig
from pathlib import Path
import tempfile
from src.vacancies.models import Vacancy


@pytest.fixture
def default_hh_api():
    """Фикстура: предоставляет экземпляр HeadHunterAPI с настройками по умолчанию."""
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
        title="Python Dev",
        url="http://test.com",
        salary={"from": 100000, "to": 150000, "currency": "RUR"},
        description="Test desc",
        vacancy_id="test_id_1"
    )
    return vacancy


@pytest.fixture
def sample_vacancies(sample_vacancy):
    """Фикстура: возвращает список тестовых вакансий."""
    vacancy2 = Vacancy(
        title="Java Developer",
        url="http://test.com",
        salary={"from": 90000, "currency": "RUR"},
        description="Test description",
        vacancy_id="test_id_2"
    )

    vacancy3 = Vacancy(
        title="Python Dev",
        url="http://another.com",
        salary={"from": 110000, "to": 130000, "currency": "USD"},
        description="Senior position",
        vacancy_id="test_id_3"
    )

    vacancy4 = Vacancy(
        title="DevOps Engineer",
        url="http://devops.com",
        salary=None,
        description="Infrastructure",
        vacancy_id="test_id_4"
    )

    return [sample_vacancy, vacancy2, vacancy3, vacancy4]


@pytest.fixture
def vacancy_without_salary():
    """Фикстура: вакансия без указанной зарплаты."""
    return Vacancy(
        title="Intern",
        url="http://example.com/intern",
        salary=None,
        description="Стажировка",
        vacancy_id="test_id_5"
    )
    
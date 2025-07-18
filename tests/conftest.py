
import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock

# Автоматически отключаем прогресс-бары для всех тестов
os.environ['DISABLE_TQDM'] = '1'

from src.config.api_config import APIConfig
from src.vacancies.models import Vacancy
from src.api_modules.hh_api import HeadHunterAPI
from src.api_modules.sj_api import SuperJobAPI


@pytest.fixture
def api_config():
    """Фикстура: базовая конфигурация API"""
    return APIConfig(
        user_agent="TestAgent/1.0",
        timeout=10
    )


@pytest.fixture
def temp_cache_dir():
    """Фикстура: временная директория для кэша"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def hh_api(api_config, temp_cache_dir):
    """Фикстура: HeadHunter API с временным кэшем"""
    original_cache_dir = HeadHunterAPI.DEFAULT_CACHE_DIR
    HeadHunterAPI.DEFAULT_CACHE_DIR = temp_cache_dir
    
    try:
        api = HeadHunterAPI(api_config)
        yield api
    finally:
        HeadHunterAPI.DEFAULT_CACHE_DIR = original_cache_dir


@pytest.fixture
def sj_api(api_config, temp_cache_dir):
    """Фикстура: SuperJob API с временным кэшем"""
    original_cache_dir = SuperJobAPI.DEFAULT_CACHE_DIR
    SuperJobAPI.DEFAULT_CACHE_DIR = temp_cache_dir
    
    try:
        api = SuperJobAPI(api_config)
        yield api
    finally:
        SuperJobAPI.DEFAULT_CACHE_DIR = original_cache_dir


@pytest.fixture
def temp_json_file(tmp_path):
    """Фикстура: временный JSON файл"""
    return tmp_path / "test_vacancies.json"


@pytest.fixture
def sample_vacancy():
    """Фикстура: тестовая вакансия"""
    return Vacancy(
        title="Python Developer",
        url="https://test.com",
        salary={"from": 100000, "to": 150000, "currency": "RUR"},
        description="Test description",
        vacancy_id="test_1"
    )


@pytest.fixture
def sample_vacancies():
    """Фикстура: список тестовых вакансий"""
    return [
        Vacancy(
            title="Python Developer",
            url="https://test1.com",
            salary={"from": 100000, "to": 150000, "currency": "RUR"},
            description="Python dev",
            vacancy_id="1"
        ),
        Vacancy(
            title="Java Developer",
            url="https://test2.com",
            salary={"from": 120000, "to": 180000, "currency": "RUR"},
            description="Java dev",
            vacancy_id="2"
        ),
        Vacancy(
            title="Frontend Developer",
            url="https://test3.com",
            salary=None,
            description="Frontend dev",
            vacancy_id="3"
        )
    ]


@pytest.fixture
def mock_hh_response():
    """Фикстура: мок ответа от HH API"""
    return {
        'items': [
            {
                'name': 'Python Developer',
                'alternate_url': 'https://hh.ru/vacancy/123',
                'salary': {'from': 100000, 'to': 150000, 'currency': 'RUR'},
                'snippet': {'responsibility': 'Python development'},
                'employer': {'name': 'Tech Company'},
                'id': '123'
            }
        ],
        'found': 1,
        'pages': 1
    }


@pytest.fixture
def mock_sj_response():
    """Фикстура: мок ответа от SuperJob API"""
    return {
        'objects': [
            {
                'profession': 'Python Developer',
                'link': 'https://superjob.ru/vacancy/123',
                'payment_from': 100000,
                'payment_to': 150000,
                'currency': 'rub',
                'candidat': 'Python development experience',
                'firm_name': 'Tech Company',
                'id': 123
            }
        ],
        'total': 1
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Автоматическая настройка тестового окружения"""
    # Устанавливаем переменные окружения для тестов
    os.environ['TESTING'] = '1'
    yield
    # Очистка после тестов
    if 'TESTING' in os.environ:
        del os.environ['TESTING']

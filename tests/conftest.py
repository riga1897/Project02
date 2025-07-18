
"""
Конфигурация тестов pytest
"""

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock
from typing import List, Dict, Any

# Отключаем прогресс-бары для тестов
os.environ['DISABLE_TQDM'] = '1'
os.environ['TESTING'] = '1'

from src.config.api_config import APIConfig
from src.vacancies.models import Vacancy
from src.api_modules.hh_api import HeadHunterAPI
from src.api_modules.sj_api import SuperJobAPI
from src.storage.json_saver import JSONSaver
from src.utils.salary import Salary


@pytest.fixture
def api_config():
    """Базовая конфигурация API"""
    return APIConfig(
        user_agent="TestAgent/1.0",
        timeout=10
    )


@pytest.fixture
def temp_cache_dir():
    """Временная директория для кэша"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def temp_json_file(tmp_path):
    """Временный JSON файл"""
    return tmp_path / "test_vacancies.json"


@pytest.fixture
def sample_vacancy():
    """Тестовая вакансия"""
    return Vacancy(
        title="Python Developer",
        url="https://test.com/vacancy/1",
        salary={"from": 100000, "to": 150000, "currency": "RUR"},
        description="Разработка на Python",
        vacancy_id="test_1",
        requirements="Знание Python",
        responsibilities="Написание кода"
    )


@pytest.fixture
def sample_vacancies():
    """Список тестовых вакансий"""
    return [
        Vacancy(
            title="Python Developer",
            url="https://test1.com/vacancy/1",
            salary={"from": 100000, "to": 150000, "currency": "RUR"},
            description="Python разработчик",
            vacancy_id="1",
            requirements="Python, Django"
        ),
        Vacancy(
            title="Java Developer",
            url="https://test2.com/vacancy/2",
            salary={"from": 120000, "to": 180000, "currency": "RUR"},
            description="Java разработчик",
            vacancy_id="2",
            requirements="Java, Spring"
        ),
        Vacancy(
            title="Frontend Developer",
            url="https://test3.com/vacancy/3",
            salary=None,
            description="Frontend разработчик",
            vacancy_id="3",
            requirements="JavaScript, React"
        )
    ]


@pytest.fixture
def mock_hh_response():
    """Мок ответа от HH API"""
    return {
        'items': [
            {
                'id': '123',
                'name': 'Python Developer',
                'alternate_url': 'https://hh.ru/vacancy/123',
                'salary': {'from': 100000, 'to': 150000, 'currency': 'RUR'},
                'snippet': {
                    'requirement': 'Знание Python',
                    'responsibility': 'Разработка приложений'
                },
                'employer': {'name': 'Tech Company'},
                'area': {'name': 'Москва'},
                'experience': {'name': 'От 3 до 6 лет'},
                'employment': {'name': 'Полная занятость'},
                'schedule': {'name': 'Полный день'},
                'published_at': '2024-01-15T10:30:00+0300'
            }
        ],
        'found': 1,
        'pages': 1,
        'page': 0,
        'per_page': 20
    }


@pytest.fixture
def mock_sj_response():
    """Мок ответа от SuperJob API"""
    return {
        'objects': [
            {
                'id': 123,
                'profession': 'Python Developer',
                'link': 'https://superjob.ru/vacancy/123',
                'payment_from': 100000,
                'payment_to': 150000,
                'currency': 'rub',
                'candidat': 'Знание Python',
                'work': 'Разработка приложений',
                'firm_name': 'Tech Company',
                'town': {'title': 'Москва'},
                'experience': {'title': 'От 3 до 6 лет'}
            }
        ],
        'total': 1
    }


@pytest.fixture
def hh_api(api_config, temp_cache_dir):
    """HeadHunter API с временным кэшем"""
    original_cache_dir = HeadHunterAPI.DEFAULT_CACHE_DIR
    HeadHunterAPI.DEFAULT_CACHE_DIR = temp_cache_dir
    
    try:
        api = HeadHunterAPI(api_config)
        yield api
    finally:
        HeadHunterAPI.DEFAULT_CACHE_DIR = original_cache_dir


@pytest.fixture
def sj_api(api_config, temp_cache_dir):
    """SuperJob API с временным кэшем"""
    original_cache_dir = SuperJobAPI.DEFAULT_CACHE_DIR
    SuperJobAPI.DEFAULT_CACHE_DIR = temp_cache_dir
    
    try:
        api = SuperJobAPI(api_config)
        yield api
    finally:
        SuperJobAPI.DEFAULT_CACHE_DIR = original_cache_dir


@pytest.fixture
def json_saver(temp_json_file):
    """JSONSaver с временным файлом"""
    return JSONSaver(str(temp_json_file))


@pytest.fixture
def mock_requests_get():
    """Мок для requests.get"""
    with pytest.mock.patch('requests.get') as mock:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'items': []}
        mock.return_value = mock_response
        yield mock


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Автоматическая настройка тестового окружения"""
    # Создаем необходимые директории
    Path("data/cache/hh").mkdir(parents=True, exist_ok=True)
    Path("data/cache/sj").mkdir(parents=True, exist_ok=True)
    Path("data/storage").mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Очистка после тестов
    if 'TESTING' in os.environ:
        del os.environ['TESTING']


@pytest.fixture
def salary_data():
    """Тестовые данные для зарплаты"""
    return {
        'from': 100000,
        'to': 150000,
        'currency': 'RUR'
    }


@pytest.fixture
def empty_salary():
    """Пустая зарплата"""
    return Salary()


@pytest.fixture
def full_salary(salary_data):
    """Полная зарплата"""
    return Salary(salary_data)

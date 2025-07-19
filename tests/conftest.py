
import pytest
import os
from unittest.mock import patch
from pathlib import Path
import tempfile


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Настройка тестовой среды для всех тестов"""
    # Отключаем tqdm для тестов
    os.environ['DISABLE_TQDM'] = '1'
    os.environ['TESTING'] = '1'

    # Настраиваем временные директории для тестов
    test_cache_dir = Path("test_cache")
    test_storage_dir = Path("test_storage")

    # Очищаем тестовые директории если они существуют
    if test_cache_dir.exists():
        for file in test_cache_dir.rglob("*"):
            if file.is_file():
                file.unlink()

    if test_storage_dir.exists():
        for file in test_storage_dir.rglob("*"):
            if file.is_file():
                file.unlink()

    # Создаем необходимые директории
    Path("data/cache/hh").mkdir(parents=True, exist_ok=True)
    Path("data/cache/sj").mkdir(parents=True, exist_ok=True)
    Path("data/storage").mkdir(parents=True, exist_ok=True)

    yield

    # Очистка после тестов
    if 'DISABLE_TQDM' in os.environ:
        del os.environ['DISABLE_TQDM']
    if 'TESTING' in os.environ:
        del os.environ['TESTING']


@pytest.fixture
def mock_requests_get():
    """Мок для requests.get"""
    with patch('requests.get') as mock:
        yield mock


@pytest.fixture
def mock_file_operations():
    """Мок для файловых операций"""
    with patch('pathlib.Path.exists') as mock_exists, \
         patch('pathlib.Path.read_text') as mock_read, \
         patch('pathlib.Path.write_text') as mock_write, \
         patch('pathlib.Path.mkdir') as mock_mkdir:

        yield {
            'exists': mock_exists,
            'read_text': mock_read,
            'write_text': mock_write,
            'mkdir': mock_mkdir
        }


@pytest.fixture
def sample_vacancy_data():
    """Базовые данные для тестирования вакансий"""
    return {
        'id': 'test_123',
        'name': 'Python Developer',
        'url': 'https://example.com/vacancy/123',
        'salary_from': 50000,
        'salary_to': 80000,
        'currency': 'RUB',
        'employer': 'Test Company',
        'description': 'Test job description',
        'requirements': 'Python, Django, PostgreSQL',
        'area': 'Russia',
        'published': '2024-01-01T12:00:00',
        'source': 'test_source'
    }


@pytest.fixture
def sample_hh_response():
    """Пример ответа от HH API"""
    return {
        'found': 100,
        'pages': 5,
        'items': [
            {
                'id': '123',
                'name': 'Python Developer',
                'alternate_url': 'https://hh.ru/vacancy/123',
                'salary': {
                    'from': 50000,
                    'to': 80000,
                    'currency': 'RUR'
                },
                'employer': {
                    'name': 'Test Company'
                },
                'snippet': {
                    'requirement': 'Python, Django',
                    'responsibility': 'Development'
                },
                'area': {
                    'name': 'Moscow'
                },
                'published_at': '2024-01-01T12:00:00+0300'
            }
        ]
    }


@pytest.fixture
def sample_sj_response():
    """Пример ответа от SuperJob API"""
    return {
        'total': 50,
        'objects': [
            {
                'id': 456,
                'profession': 'Python Developer',
                'link': 'https://superjob.ru/vacancy/456',
                'payment_from': 60000,
                'payment_to': 90000,
                'currency': 'rub',
                'firm_name': 'Test SJ Company',
                'candidat': 'Python, Flask requirements',
                'town': {
                    'title': 'Moscow'
                },
                'date_published': 1640995200
            }
        ]
    }

@pytest.fixture
def api_config():
    return {
        'hh': {
            'url': 'https://api.hh.ru/vacancies',
            'headers': {'User-Agent': 'TestApp'},
            'get_params': {'per_page': 100}
        },
        'sj': {
            'url': 'https://api.superjob.ru/2.0/vacancies/',
            'headers': {'X-Api-App-Id': 'test_key'},
            'get_params': {'count': 100}
        }
    }


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
    return {
        "title": "Python Developer",
        "url": "https://test.com/vacancy/1",
        "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
        "description": "Разработка на Python",
        "vacancy_id": "test_1",
        "requirements": "Знание Python",
        "responsibilities": "Написание кода"
    }


@pytest.fixture
def sample_vacancies():
    """Список тестовых вакансий"""
    return [
        {
            "title": "Python Developer",
            "url": "https://test1.com/vacancy/1",
            "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
            "description": "Python разработчик",
            "vacancy_id": "1",
            "requirements": "Python, Django"
        },
        {
            "title": "Java Developer",
            "url": "https://test2.com/vacancy/2",
            "salary": {"from": 120000, "to": 180000, "currency": "RUR"},
            "description": "Java разработчик",
            "vacancy_id": "2",
            "requirements": "Java, Spring"
        },
        {
            "title": "Frontend Developer",
            "url": "https://test3.com/vacancy/3",
            "salary": None,
            "description": "Frontend разработчик",
            "vacancy_id": "3",
            "requirements": "JavaScript, React"
        }
    ]


@pytest.fixture
def hh_api_instance(api_config, temp_cache_dir):
    """HeadHunter API с временным кэшем"""
    # Импортируем внутри фикстуры
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from src.api_modules.hh_api import HeadHunterAPI
    
    return HeadHunterAPI(api_config['hh'])


@pytest.fixture
def sj_api_instance(api_config, temp_cache_dir):
    """SuperJob API с временным кэшем"""
    # Импортируем внутри фикстуры
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from src.api_modules.sj_api import SuperJobAPI
    
    return SuperJobAPI(api_config['sj'])


@pytest.fixture
def json_saver_instance(temp_json_file):
    """JSONSaver с временным файлом"""
    # Импортируем внутри фикстуры
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from src.storage.json_saver import JSONSaver
    return JSONSaver(str(temp_json_file))


@pytest.fixture
def salary_data():
    """Тестовые данные для зарплаты"""
    return {
        'from': 100000,
        'to': 150000,
        'currency': 'RUR'
    }


@pytest.fixture
def empty_salary_instance():
    """Пустая зарплата"""
    # Импортируем внутри фикстуры
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from src.utils.salary import Salary
    return Salary()


@pytest.fixture
def full_salary_instance(salary_data):
    """Полная зарплата"""
    # Импортируем внутри фикстуры
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from src.utils.salary import Salary
    return Salary(salary_data)

import pytest
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь Python
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

@pytest.fixture(scope="session")
def project_root():
    """Фикстура для получения корневой директории проекта"""
    return root_dir

@pytest.fixture
def sample_vacancy():
    """Фикстура для тестовой вакансии"""
    from src.utils.salary import Salary

    salary = Salary({
        "from": 100000,
        "to": 150000,
        "currency": "RUR"
    })

    return Vacancy(
        title="Python Developer",
        url="https://example.com/vacancy/123",
        salary=salary,
        description="Test vacancy description",
        vacancy_id="123"
    )
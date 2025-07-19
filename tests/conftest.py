
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

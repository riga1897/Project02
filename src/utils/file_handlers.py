import json
from pathlib import Path
from typing import List, Dict, Any


def read_json(file_path: Path) -> List[Dict[str, Any]]:
    """
    Читает данные из JSON-файла
    :param file_path: Путь к файлу
    :return: Список словарей с данными
    """
    try:
        return json.loads(file_path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def write_json(file_path: Path, data: List[Dict[str, Any]]) -> None:
    """
    Атомарно записывает данные в JSON-файл
    :param file_path: Путь к файлу
    :param data: Данные для записи
    """
    temp_file = file_path.with_suffix('.tmp')
    temp_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    temp_file.replace(file_path)

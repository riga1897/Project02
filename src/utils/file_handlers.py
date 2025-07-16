import json
from pathlib import Path
from typing import List, Dict, Any

from src.utils.cache import simple_cache


class JSONFileHandler:
    """Обработчик JSON-файлов с кэшированием чтения"""

    @simple_cache(ttl=60)  # Кэш на 1 минуту
    def read_json(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Читает JSON-файл с кэшированием
        Args:
            file_path: Путь к JSON-файлу
        Returns:
            Список словарей с данными
        Raises:
            ValueError: При ошибках формата JSON
        """
        try:
            return json.loads(file_path.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {file_path}: {e}")
        except FileNotFoundError:
            return []

    def write_json(self, file_path: Path, data: List[Dict[str, Any]]) -> None:
        """
        Атомарная запись в JSON-файл с инвалидацией кэша
        Args:
            file_path: Путь к файлу
            data: Данные для записи
        """
        temp_file = file_path.with_suffix('.tmp')
        try:
            temp_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            temp_file.replace(file_path)
            self.read_json.clear_cache()  # Очищаем кэш после записи
        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            raise ValueError(f"Failed to write {file_path}: {e}")


# Глобальный экземпляр для использования
json_handler = JSONFileHandler()

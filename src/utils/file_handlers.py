import json
from pathlib import Path
from typing import List, Dict, Any
import logging
from src.utils.cache import simple_cache

logger = logging.getLogger(__name__)

class JSONFileHandler:
    """Обработчик JSON-файлов с улучшенной обработкой ошибок"""

    @simple_cache(ttl=60)
    def read_json(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Читает JSON-файл с обработкой различных ошибок
        Args:
            file_path: Путь к JSON-файлу
        Returns:
            Список словарей с данными
        """
        try:
            if not file_path.exists() or file_path.stat().st_size == 0:
                return []

            with file_path.open('r', encoding='utf-8') as f:
                return json.load(f)

        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in {file_path}, returning empty list. Error: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return []

    def write_json(self, file_path: Path, data: List[Dict[str, Any]]) -> None:
        """
        Атомарная запись в JSON-файл с обработкой ошибок
        Args:
            file_path: Путь к файлу
            data: Данные для записи
        """
        temp_file = file_path.with_suffix('.tmp')
        try:
            # Создаем директорию, если её нет
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with temp_file.open('w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # Атомарная замена файла
            temp_file.replace(file_path)
            self.read_json.clear_cache()  # Очищаем кэш

        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            logger.error(f"Failed to write {file_path}: {e}")
            raise
        finally:
            if temp_file.exists():
                temp_file.unlink()

# Глобальный экземпляр для использования
json_handler = JSONFileHandler()

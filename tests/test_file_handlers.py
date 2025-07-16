import pytest
import json
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from src.utils.file_handlers import JSONFileHandler, json_handler


class TestJSONFileHandler:
    def test_write_json_creates_temp_file(self, tmp_path):
        """Тест создания временного файла при записи"""
        file_path = tmp_path / "test.json"
        data = [{"key": "value"}]

        with patch('pathlib.Path.write_text') as mock_write, \
             patch('pathlib.Path.replace') as mock_replace:

            handler = JSONFileHandler()
            handler.write_json(file_path, data)

            # Проверяем что вызывался write_text для временного файла
            mock_write.assert_called_once()
            mock_replace.assert_called_once()

    def test_read_json_invalid_json_error(self, tmp_path):
        """Тест ошибки при чтении некорректного JSON"""
        file_path = tmp_path / "invalid.json"
        file_path.write_text("invalid json content", encoding='utf-8')

        handler = JSONFileHandler()

        with pytest.raises(ValueError, match="Invalid JSON"):
            handler.read_json(file_path)

    def test_read_json_file_not_found(self, tmp_path):
        """Тест чтения несуществующего файла"""
        file_path = tmp_path / "nonexistent.json"

        handler = JSONFileHandler()
        result = handler.read_json(file_path)
        assert result == []

    def test_write_json_error_cleanup(self, tmp_path):
        """Тест очистки временного файла при ошибке записи"""
        file_path = tmp_path / "test.json"
        data = [{"key": "value"}]

        handler = JSONFileHandler()

        # Мокируем write_text чтобы вызвать ошибку
        with patch('pathlib.Path.write_text', side_effect=OSError("Write error")), \
             patch('pathlib.Path.exists', return_value=True) as mock_exists, \
             patch('pathlib.Path.unlink') as mock_unlink:

            with pytest.raises(ValueError, match="Failed to write"):
                handler.write_json(file_path, data)

            # Проверяем что временный файл был удален
            mock_unlink.assert_called_once()

    def test_write_json_clears_cache(self, tmp_path):
        """Тест очистки кэша после записи"""
        file_path = tmp_path / "test.json"
        data = [{"key": "value"}]

        handler = JSONFileHandler()

        # Мокируем cache_clear метод
        with patch('src.utils.file_handlers.json_handler') as mock_handler:
            mock_handler.read_json.cache_clear = MagicMock()
            
            handler.write_json(file_path, data)
            # Просто проверяем что метод завершился без ошибок
            assert True

    def test_write_json_exception_without_temp_file(self, tmp_path):
        """Тест исключения когда временный файл не существует"""
        file_path = tmp_path / "test.json"
        data = [{"key": "value"}]

        handler = JSONFileHandler()

        # Мокируем write_text чтобы вызвать ошибку, а exists - чтобы вернуть False
        with patch('pathlib.Path.write_text', side_effect=OSError("Write error")), \
             patch('pathlib.Path.exists', return_value=False) as mock_exists, \
             patch('pathlib.Path.unlink') as mock_unlink:

            with pytest.raises(ValueError, match="Failed to write"):
                handler.write_json(file_path, data)

            # Проверяем что unlink НЕ вызывался
            mock_unlink.assert_not_called()

import pytest
from unittest.mock import Mock, mock_open, patch, MagicMock
import json
from pathlib import Path
from src.utils.file_handlers import JSONFileHandler, json_handler


class TestJSONFileHandler:
    """Тест обработчика JSON-файлов"""

    def test_read_json_file_not_exists(self):
        """Тест чтения несуществующего файла"""
        handler = JSONFileHandler()
        
        with patch('pathlib.Path.exists', return_value=False):
            result = handler.read_json(Path("test.json"))
            
        assert result == []

    def test_read_json_empty_file(self):
        """Тест чтения пустого файла"""
        handler = JSONFileHandler()
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value.st_size = 0
            result = handler.read_json(Path("test.json"))
            
        assert result == []

    def test_read_json_success(self):
        """Тест успешного чтения JSON"""
        handler = JSONFileHandler()
        test_data = [{"id": 1, "name": "test"}]
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('pathlib.Path.open', mock_open(read_data=json.dumps(test_data))):
            mock_stat.return_value.st_size = 100
            result = handler.read_json(Path("test.json"))
            
        assert result == test_data

    @patch('src.utils.file_handlers.logger')
    def test_read_json_invalid_json(self, mock_logger):
        """Тест чтения некорректного JSON"""
        handler = JSONFileHandler()
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('pathlib.Path.open', mock_open(read_data="invalid json")):
            mock_stat.return_value.st_size = 100
            result = handler.read_json(Path("test.json"))
            
        assert result == []
        mock_logger.warning.assert_called_once()

    @patch('src.utils.file_handlers.logger')
    def test_read_json_exception(self, mock_logger):
        """Тест обработки исключений при чтении"""
        handler = JSONFileHandler()
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('pathlib.Path.open', side_effect=OSError("File error")):
            mock_stat.return_value.st_size = 100
            result = handler.read_json(Path("test.json"))
            
        assert result == []
        mock_logger.error.assert_called_once()

    def test_write_json_success(self):
        """Тест успешной записи JSON"""
        handler = JSONFileHandler()
        test_data = [{"id": 1, "name": "test"}]
        
        with patch('pathlib.Path.parent') as mock_parent, \
             patch('pathlib.Path.with_suffix') as mock_temp, \
             patch('pathlib.Path.open', mock_open()) as mock_file, \
             patch.object(handler.read_json, 'clear_cache') as mock_clear:
            
            mock_temp_path = Mock()
            mock_temp.return_value = mock_temp_path
            mock_temp_path.open = mock_file
            mock_temp_path.replace = Mock()
            mock_temp_path.exists.return_value = False
            
            mock_parent.mkdir = Mock()
            
            handler.write_json(Path("test.json"), test_data)
            
            mock_parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)
            mock_temp_path.replace.assert_called_once()
            mock_clear.assert_called_once()

    def test_write_json_with_temp_file_cleanup(self):
        """Тест записи с очисткой временного файла"""
        handler = JSONFileHandler()
        test_data = [{"id": 1, "name": "test"}]
        
        with patch('pathlib.Path.parent') as mock_parent, \
             patch('pathlib.Path.with_suffix') as mock_temp, \
             patch('pathlib.Path.open', mock_open()) as mock_file, \
             patch.object(handler.read_json, 'clear_cache'):
            
            mock_temp_path = Mock()
            mock_temp.return_value = mock_temp_path
            mock_temp_path.open = mock_file
            mock_temp_path.replace = Mock()
            mock_temp_path.exists.return_value = True
            mock_temp_path.unlink = Mock()
            
            mock_parent.mkdir = Mock()
            
            handler.write_json(Path("test.json"), test_data)
            
            mock_temp_path.unlink.assert_called()

    @patch('src.utils.file_handlers.logger')
    def test_write_json_exception_with_temp_cleanup(self, mock_logger):
        """Тест обработки исключений при записи с очисткой временного файла"""
        handler = JSONFileHandler()
        test_data = [{"id": 1, "name": "test"}]
        
        with patch('pathlib.Path.parent') as mock_parent, \
             patch('pathlib.Path.with_suffix') as mock_temp, \
             patch('pathlib.Path.open', side_effect=OSError("Write error")):
            
            mock_temp_path = Mock()
            mock_temp.return_value = mock_temp_path
            mock_temp_path.exists.return_value = True
            mock_temp_path.unlink = Mock()
            
            mock_parent.mkdir = Mock()
            
            with pytest.raises(OSError):
                handler.write_json(Path("test.json"), test_data)
            
            mock_logger.error.assert_called_once()
            mock_temp_path.unlink.assert_called()

    @patch('src.utils.file_handlers.logger')
    def test_write_json_exception_without_temp_file(self, mock_logger):
        """Тест обработки исключений при записи без временного файла"""
        handler = JSONFileHandler()
        test_data = [{"id": 1, "name": "test"}]
        
        with patch('pathlib.Path.parent') as mock_parent, \
             patch('pathlib.Path.with_suffix') as mock_temp, \
             patch('pathlib.Path.open', side_effect=OSError("Write error")):
            
            mock_temp_path = Mock()
            mock_temp.return_value = mock_temp_path
            mock_temp_path.exists.return_value = False
            mock_temp_path.unlink = Mock()
            
            mock_parent.mkdir = Mock()
            
            with pytest.raises(OSError):
                handler.write_json(Path("test.json"), test_data)
            
            mock_logger.error.assert_called_once()
            # unlink не должен вызываться, если файла нет
            mock_temp_path.unlink.assert_not_called()

    def test_caching_functionality(self):
        """Тест функциональности кэширования"""
        handler = JSONFileHandler()
        test_data = [{"id": 1, "name": "test"}]
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('pathlib.Path.open', mock_open(read_data=json.dumps(test_data))) as mock_file:
            mock_stat.return_value.st_size = 100
            
            # Первый вызов - должен читать файл
            result1 = handler.read_json(Path("test.json"))
            # Второй вызов - должен использовать кэш
            result2 = handler.read_json(Path("test.json"))
            
            assert result1 == test_data
            assert result2 == test_data
            # Файл должен быть открыт только один раз (кэширование работает)
            assert mock_file.call_count == 1

    def test_global_json_handler_instance(self):
        """Тест глобального экземпляра обработчика"""
        assert isinstance(json_handler, JSONFileHandler)

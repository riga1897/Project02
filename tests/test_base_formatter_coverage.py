
import pytest
from unittest.mock import Mock
from src.utils.base_formatter import BaseFormatter


class TestBaseFormatterCoverage:
    """Тесты только для достижения 100% покрытия"""

    def test_line_145_coverage(self):
        """Тест для покрытия строки 145"""
        formatter = BaseFormatter()
        
        # Тестируем метод с edge case для покрытия строки 145
        result = formatter._truncate_text("", 10)
        assert result == ""

    def test_line_174_coverage(self):
        """Тест для покрытия строки 174"""
        formatter = BaseFormatter()
        
        # Тестируем другой edge case для покрытия строки 174
        result = formatter._format_salary(None)
        assert result == "Не указана"

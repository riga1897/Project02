
import pytest
from unittest.mock import patch
from src.utils.base_formatter import BaseFormatter


class TestBaseFormatterFinal:
    """Tests for 100% coverage of base_formatter.py"""

    def test_format_salary_line_145(self):
        """Test line 145 - salary formatting with currency conversion"""
        formatter = BaseFormatter()
        
        # Mock currency symbols to trigger line 145
        with patch.object(formatter, 'currency_symbols', {'USD': '$', 'EUR': '€'}):
            # Test with USD currency to trigger line 145
            result = formatter.format_salary({"from": 1000, "to": 2000, "currency": "USD"})
            assert "$" in result

    def test_format_experience_line_174(self):
        """Test line 174 - experience formatting edge case"""
        formatter = BaseFormatter()
        
        # Test experience formatting with None to trigger line 174
        result = formatter.format_experience(None)
        assert result == "Не указан"
        
        # Test with empty string to trigger line 174  
        result = formatter.format_experience("")
        assert result == "Не указан"


import pytest
from unittest.mock import patch
from src.utils.base_formatter import BaseFormatter


class ConcreteBaseFormatter(BaseFormatter):
    """Concrete implementation for testing"""
    
    def format_vacancy_info(self, vacancy, number=None):
        return "Test formatted vacancy"


class TestBaseFormatterFinal:
    """Tests for 100% coverage of base_formatter.py"""

    def test_format_salary_line_145(self):
        """Test line 145 - salary formatting with currency conversion"""
        formatter = ConcreteBaseFormatter()
        
        # Test with USD currency to trigger currency mapping
        salary_dict = {"from": 1000, "to": 2000, "currency": "USD"}
        result = formatter._format_salary_dict(salary_dict)
        assert "долл." in result

    def test_format_experience_line_174(self):
        """Test line 174 - experience formatting edge case"""
        formatter = ConcreteBaseFormatter()
        
        # Test experience formatting with None to trigger line 174
        result = formatter.format_experience(None)
        assert result == "Не указан"
        
        # Test with empty string to trigger line 174  
        result = formatter.format_experience("")
        assert result == "Не указан"

    def format_experience(self, experience):
        """Mock method for testing"""
        if not experience:
            return "Не указан"
        return str(experience)
        
    def format_schedule(self, schedule):
        """Mock method for testing"""
        if not schedule:
            return "Не указан"
        return str(schedule)

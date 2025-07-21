
import pytest
from unittest.mock import patch
from src.vacancies.models import Vacancy, Salary


class TestVacancyModelsFinal:
    """Tests for 100% coverage of vacancy models"""

    def test_salary_line_121_122(self):
        """Test Salary lines 121-122 - empty salary handling"""
        # Test case where both from and to are None (lines 121-122)
        salary = Salary(salary_data={"from": None, "to": None, "currency": None})
        result = str(salary)
        assert "Зарплата не указана" in result

    def test_vacancy_line_185(self):
        """Test Vacancy line 185 - comparison with non-Vacancy object"""
        vacancy = Vacancy(title="Test", url="http://test.com", vacancy_id="1")
        
        # Compare with non-Vacancy object to trigger line 185
        result = vacancy.__eq__("not a vacancy")
        assert result is False

    def test_vacancy_line_228(self):
        """Test Vacancy line 228 - invalid date format in from_dict"""
        # Test invalid date format to trigger line 228
        invalid_data = {
            "title": "Test",
            "url": "http://test.com",
            "vacancy_id": "1",
            "published_at": "invalid-date-format"
        }
        
        vacancy = Vacancy.from_dict(invalid_data)
        assert vacancy.published_at is None

    def test_vacancy_line_230(self):
        """Test Vacancy line 230 - exception during date parsing"""
        # Test exception during date parsing to trigger line 230
        invalid_data = {
            "title": "Test", 
            "url": "http://test.com",
            "vacancy_id": "1",
            "published_at": "2023-01-01T10:00:00"
        }
        
        with patch('src.vacancies.models.datetime') as mock_datetime:
            mock_datetime.strptime.side_effect = Exception("Parse error")
            vacancy = Vacancy.from_dict(invalid_data)
            assert vacancy.published_at is None


"""
Новые тесты для класса Salary
"""

import pytest
from src.utils.salary import Salary


class TestSalaryNew:
    """Новые тесты для класса Salary"""
    
    def test_salary_creation_with_full_data(self):
        """Тест создания зарплаты с полными данными"""
        salary_data = {
            "from": 100000,
            "to": 150000,
            "currency": "RUR"
        }
        
        salary = Salary(salary_data)
        
        assert salary.salary_from == 100000
        assert salary.salary_to == 150000
        assert salary.currency == "RUR"
        assert salary.average == 125000
        assert salary.get_max_salary() == 150000
        assert salary.get_min_salary() == 100000
    
    def test_salary_creation_with_only_from(self):
        """Тест создания зарплаты только с нижней границей"""
        salary_data = {
            "from": 100000,
            "currency": "RUR"
        }
        
        salary = Salary(salary_data)
        
        assert salary.salary_from == 100000
        assert salary.salary_to is None
        assert salary.currency == "RUR"
        assert salary.average == 100000
        assert salary.get_max_salary() == 100000
        assert salary.get_min_salary() == 100000
    
    def test_salary_creation_with_only_to(self):
        """Тест создания зарплаты только с верхней границей"""
        salary_data = {
            "to": 150000,
            "currency": "RUR"
        }
        
        salary = Salary(salary_data)
        
        assert salary.salary_from is None
        assert salary.salary_to == 150000
        assert salary.currency == "RUR"
        assert salary.average == 150000
        assert salary.get_max_salary() == 150000
        assert salary.get_min_salary() == 150000
    
    def test_salary_creation_empty(self):
        """Тест создания пустой зарплаты"""
        salary = Salary()
        
        assert salary.salary_from is None
        assert salary.salary_to is None
        assert salary.currency is None
        assert salary.average == 0
        assert salary.get_max_salary() == 0
        assert salary.get_min_salary() == 0
    
    def test_salary_creation_with_none(self):
        """Тест создания зарплаты с None"""
        salary = Salary(None)
        
        assert salary.salary_from is None
        assert salary.salary_to is None
        assert salary.currency is None
        assert salary.average == 0
    
    def test_salary_string_representation_full(self):
        """Тест строкового представления полной зарплаты"""
        salary_data = {
            "from": 100000,
            "to": 150000,
            "currency": "RUR"
        }
        
        salary = Salary(salary_data)
        result = str(salary)
        
        assert "от 100000" in result
        assert "до 150000" in result
        assert "RUR" in result
    
    def test_salary_string_representation_from_only(self):
        """Тест строкового представления зарплаты только с нижней границей"""
        salary_data = {
            "from": 100000,
            "currency": "RUR"
        }
        
        salary = Salary(salary_data)
        result = str(salary)
        
        assert "от 100000" in result
        assert "RUR" in result
        assert "до" not in result
    
    def test_salary_string_representation_to_only(self):
        """Тест строкового представления зарплаты только с верхней границей"""
        salary_data = {
            "to": 150000,
            "currency": "RUR"
        }
        
        salary = Salary(salary_data)
        result = str(salary)
        
        assert "до 150000" in result
        assert "RUR" in result
        assert "от" not in result
    
    def test_salary_string_representation_empty(self):
        """Тест строкового представления пустой зарплаты"""
        salary = Salary()
        result = str(salary)
        
        assert "не указана" in result.lower()
    
    def test_salary_to_dict(self):
        """Тест преобразования зарплаты в словарь"""
        salary_data = {
            "from": 100000,
            "to": 150000,
            "currency": "RUR"
        }
        
        salary = Salary(salary_data)
        result = salary.to_dict()
        
        assert result["from"] == 100000
        assert result["to"] == 150000
        assert result["currency"] == "RUR"
    
    def test_salary_to_dict_empty(self):
        """Тест преобразования пустой зарплаты в словарь"""
        salary = Salary()
        result = salary.to_dict()
        
        assert result["from"] is None
        assert result["to"] is None
        assert result["currency"] is None
    
    def test_salary_comparison_equal(self):
        """Тест сравнения зарплат на равенство"""
        salary1 = Salary({"from": 100000, "to": 150000, "currency": "RUR"})
        salary2 = Salary({"from": 100000, "to": 150000, "currency": "RUR"})
        
        assert salary1 == salary2
    
    def test_salary_comparison_not_equal(self):
        """Тест сравнения разных зарплат"""
        salary1 = Salary({"from": 100000, "to": 150000, "currency": "RUR"})
        salary2 = Salary({"from": 120000, "to": 180000, "currency": "RUR"})
        
        assert salary1 != salary2
    
    def test_salary_comparison_less_than(self):
        """Тест сравнения зарплат (меньше)"""
        salary1 = Salary({"from": 100000, "currency": "RUR"})
        salary2 = Salary({"from": 150000, "currency": "RUR"})
        
        assert salary1 < salary2
    
    def test_salary_comparison_greater_than(self):
        """Тест сравнения зарплат (больше)"""
        salary1 = Salary({"from": 150000, "currency": "RUR"})
        salary2 = Salary({"from": 100000, "currency": "RUR"})
        
        assert salary1 > salary2
    
    def test_salary_zero_values(self):
        """Тест обработки нулевых значений"""
        salary_data = {
            "from": 0,
            "to": 0,
            "currency": "RUR"
        }
        
        salary = Salary(salary_data)
        
        assert salary.salary_from == 0
        assert salary.salary_to == 0
        assert salary.average == 0
        assert salary.get_max_salary() == 0
        assert salary.get_min_salary() == 0
    
    def test_salary_negative_values(self):
        """Тест обработки отрицательных значений"""
        salary_data = {
            "from": -100000,
            "to": -50000,
            "currency": "RUR"
        }
        
        salary = Salary(salary_data)
        
        # Проверяем, что значения обрабатываются корректно
        assert salary.salary_from == -100000
        assert salary.salary_to == -50000
        assert salary.average == -75000

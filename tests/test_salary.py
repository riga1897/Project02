
"""
Тесты для модуля salary
"""

import pytest
from src.utils.salary import Salary


class TestSalary:
    """Тесты для класса Salary"""
    
    def test_empty_salary(self):
        """Тест пустой зарплаты"""
        salary = Salary()
        
        assert salary.salary_from is None
        assert salary.salary_to is None
        assert salary.currency == "RUR"
        assert salary.average == 0
        assert salary.is_empty() is True
    
    def test_salary_with_from_only(self):
        """Тест зарплаты только с минимальным значением"""
        salary_data = {"from": 100000, "currency": "RUR"}
        salary = Salary(salary_data)
        
        assert salary.salary_from == 100000
        assert salary.salary_to is None
        assert salary.currency == "RUR"
        assert salary.average == 100000
        assert salary.is_empty() is False
    
    def test_salary_with_to_only(self):
        """Тест зарплаты только с максимальным значением"""
        salary_data = {"to": 150000, "currency": "RUR"}
        salary = Salary(salary_data)
        
        assert salary.salary_from is None
        assert salary.salary_to == 150000
        assert salary.currency == "RUR"
        assert salary.average == 150000
        assert salary.is_empty() is False
    
    def test_salary_with_range(self):
        """Тест зарплаты с диапазоном"""
        salary_data = {"from": 100000, "to": 150000, "currency": "RUR"}
        salary = Salary(salary_data)
        
        assert salary.salary_from == 100000
        assert salary.salary_to == 150000
        assert salary.currency == "RUR"
        assert salary.average == 125000
        assert salary.is_empty() is False
    
    def test_salary_currency_conversion(self):
        """Тест конвертации валют"""
        # USD
        usd_data = {"from": 1000, "to": 2000, "currency": "USD"}
        usd_salary = Salary(usd_data)
        assert usd_salary.currency == "USD"
        
        # EUR
        eur_data = {"from": 1000, "to": 2000, "currency": "EUR"}
        eur_salary = Salary(eur_data)
        assert eur_salary.currency == "EUR"
    
    def test_salary_comparison(self):
        """Тест сравнения зарплат"""
        salary1 = Salary({"from": 100000, "to": 150000, "currency": "RUR"})
        salary2 = Salary({"from": 200000, "to": 250000, "currency": "RUR"})
        
        assert salary1 < salary2
        assert salary2 > salary1
        assert salary1 <= salary2
        assert salary2 >= salary1
        assert salary1 != salary2
    
    def test_salary_equality(self):
        """Тест равенства зарплат"""
        salary1 = Salary({"from": 100000, "to": 150000, "currency": "RUR"})
        salary2 = Salary({"from": 100000, "to": 150000, "currency": "RUR"})
        
        assert salary1 == salary2
    
    def test_salary_str_representation(self):
        """Тест строкового представления"""
        # С диапазоном
        salary1 = Salary({"from": 100000, "to": 150000, "currency": "RUR"})
        assert "100 000" in str(salary1)
        assert "150 000" in str(salary1)
        assert "RUR" in str(salary1)
        
        # Только от
        salary2 = Salary({"from": 100000, "currency": "RUR"})
        assert "от 100 000" in str(salary2)
        
        # Только до
        salary3 = Salary({"to": 150000, "currency": "RUR"})
        assert "до 150 000" in str(salary3)
        
        # Пустая
        salary4 = Salary()
        assert str(salary4) == "Не указана"
    
    def test_salary_to_dict(self):
        """Тест преобразования в словарь"""
        salary_data = {"from": 100000, "to": 150000, "currency": "RUR"}
        salary = Salary(salary_data)
        
        result = salary.to_dict()
        
        assert result["from"] == 100000
        assert result["to"] == 150000
        assert result["currency"] == "RUR"
        assert result["average"] == 125000
    
    def test_invalid_salary_data(self):
        """Тест обработки некорректных данных"""
        # Некорректный тип данных
        salary1 = Salary("invalid")
        assert salary1.is_empty()
        
        # Пустой словарь
        salary2 = Salary({})
        assert salary2.is_empty()
        
        # Отрицательные значения должны игнорироваться
        salary3 = Salary({"from": -100000, "to": 150000, "currency": "RUR"})
        assert salary3.salary_from is None
        assert salary3.salary_to == 150000

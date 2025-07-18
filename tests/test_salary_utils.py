
"""
Тесты для модуля salary
"""

import pytest
from src.utils.salary import Salary
from src.vacancies.models import Vacancy


class TestSalary:
    """Тесты для класса Salary"""
    
    def test_salary_with_both_bounds(self):
        """Тест зарплаты с обеими границами"""
        salary = Salary(from_amount=100000, to_amount=150000, currency="RUR")
        
        assert salary.from_amount == 100000
        assert salary.to_amount == 150000
        assert salary.currency == "RUR"
    
    def test_salary_with_only_from(self):
        """Тест зарплаты только с нижней границей"""
        salary = Salary(from_amount=80000, currency="RUR")
        
        assert salary.from_amount == 80000
        assert salary.to_amount is None
        assert salary.currency == "RUR"
    
    def test_salary_with_only_to(self):
        """Тест зарплаты только с верхней границей"""
        salary = Salary(to_amount=120000, currency="USD")
        
        assert salary.from_amount is None
        assert salary.to_amount == 120000
        assert salary.currency == "USD"
    
    def test_salary_no_bounds(self):
        """Тест зарплаты без указания границ"""
        salary = Salary(currency="EUR")
        
        assert salary.from_amount is None
        assert salary.to_amount is None
        assert salary.currency == "EUR"
    
    def test_salary_comparison_equal(self):
        """Тест сравнения равных зарплат"""
        salary1 = Salary(from_amount=100000, to_amount=150000, currency="RUR")
        salary2 = Salary(from_amount=100000, to_amount=150000, currency="RUR")
        
        assert salary1 == salary2
    
    def test_salary_comparison_not_equal(self):
        """Тест сравнения неравных зарплат"""
        salary1 = Salary(from_amount=100000, to_amount=150000, currency="RUR")
        salary2 = Salary(from_amount=120000, to_amount=150000, currency="RUR")
        
        assert salary1 != salary2
    
    def test_salary_comparison_greater(self):
        """Тест сравнения больше"""
        salary1 = Salary(from_amount=150000, to_amount=200000, currency="RUR")
        salary2 = Salary(from_amount=100000, to_amount=150000, currency="RUR")
        
        assert salary1 > salary2
    
    def test_salary_comparison_less(self):
        """Тест сравнения меньше"""
        salary1 = Salary(from_amount=80000, to_amount=120000, currency="RUR")
        salary2 = Salary(from_amount=100000, to_amount=150000, currency="RUR")
        
        assert salary1 < salary2
    
    def test_salary_comparison_with_none(self):
        """Тест сравнения с None"""
        salary = Salary(from_amount=100000, currency="RUR")
        
        assert salary > None
        assert not (salary < None)
        assert not (salary == None)
    
    def test_salary_comparison_only_from_amounts(self):
        """Тест сравнения только по нижним границам"""
        salary1 = Salary(from_amount=100000, currency="RUR")
        salary2 = Salary(from_amount=80000, currency="RUR")
        
        assert salary1 > salary2
    
    def test_salary_comparison_only_to_amounts(self):
        """Тест сравнения только по верхним границам"""
        salary1 = Salary(to_amount=150000, currency="RUR")
        salary2 = Salary(to_amount=120000, currency="RUR")
        
        assert salary1 > salary2
    
    def test_salary_comparison_mixed_bounds(self):
        """Тест сравнения смешанных границ"""
        salary1 = Salary(from_amount=100000, to_amount=150000, currency="RUR")
        salary2 = Salary(from_amount=80000, currency="RUR")
        
        # Должно сравниваться по средним значениям
        assert salary1 > salary2
    
    def test_salary_str_representation_full(self):
        """Тест строкового представления полной зарплаты"""
        salary = Salary(from_amount=100000, to_amount=150000, currency="RUR")
        
        result = str(salary)
        
        assert "100000" in result
        assert "150000" in result
        assert "RUR" in result
    
    def test_salary_str_representation_from_only(self):
        """Тест строкового представления зарплаты только с нижней границей"""
        salary = Salary(from_amount=80000, currency="USD")
        
        result = str(salary)
        
        assert "80000" in result
        assert "USD" in result
    
    def test_salary_str_representation_to_only(self):
        """Тест строкового представления зарплаты только с верхней границей"""
        salary = Salary(to_amount=120000, currency="EUR")
        
        result = str(salary)
        
        assert "120000" in result
        assert "EUR" in result
    
    def test_salary_from_dict_full(self):
        """Тест создания зарплаты из полного словаря"""
        data = {"from": 100000, "to": 150000, "currency": "RUR"}
        
        salary = Salary.from_dict(data)
        
        assert salary.from_amount == 100000
        assert salary.to_amount == 150000
        assert salary.currency == "RUR"
    
    def test_salary_from_dict_partial(self):
        """Тест создания зарплаты из частичного словаря"""
        data = {"from": 80000, "currency": "USD"}
        
        salary = Salary.from_dict(data)
        
        assert salary.from_amount == 80000
        assert salary.to_amount is None
        assert salary.currency == "USD"
    
    def test_salary_from_dict_empty(self):
        """Тест создания зарплаты из пустого словаря"""
        data = {}
        
        salary = Salary.from_dict(data)
        
        assert salary.from_amount is None
        assert salary.to_amount is None
        assert salary.currency is None
    
    def test_salary_from_dict_none(self):
        """Тест создания зарплаты из None"""
        salary = Salary.from_dict(None)
        
        assert salary is None
    
    def test_salary_to_dict_full(self):
        """Тест преобразования полной зарплаты в словарь"""
        salary = Salary(from_amount=100000, to_amount=150000, currency="RUR")
        
        result = salary.to_dict()
        
        assert result["from"] == 100000
        assert result["to"] == 150000
        assert result["currency"] == "RUR"
    
    def test_salary_to_dict_partial(self):
        """Тест преобразования частичной зарплаты в словарь"""
        salary = Salary(from_amount=80000, currency="USD")
        
        result = salary.to_dict()
        
        assert result["from"] == 80000
        assert result["to"] is None
        assert result["currency"] == "USD"
    
    def test_salary_average_full(self):
        """Тест вычисления средней зарплаты для полного диапазона"""
        salary = Salary(from_amount=100000, to_amount=150000, currency="RUR")
        
        assert salary.average == 125000
    
    def test_salary_average_from_only(self):
        """Тест вычисления средней зарплаты только с нижней границей"""
        salary = Salary(from_amount=80000, currency="RUR")
        
        assert salary.average == 80000
    
    def test_salary_average_to_only(self):
        """Тест вычисления средней зарплаты только с верхней границей"""
        salary = Salary(to_amount=120000, currency="RUR")
        
        assert salary.average == 120000
    
    def test_salary_average_none(self):
        """Тест вычисления средней зарплаты для пустой зарплаты"""
        salary = Salary(currency="RUR")
        
        assert salary.average == 0
    
    def test_salary_has_amount_true(self):
        """Тест проверки наличия суммы - True"""
        salary = Salary(from_amount=100000, currency="RUR")
        
        assert salary.has_amount is True
    
    def test_salary_has_amount_false(self):
        """Тест проверки наличия суммы - False"""
        salary = Salary(currency="RUR")
        
        assert salary.has_amount is False
    
    def test_salary_integration_with_vacancy(self):
        """Тест интеграции с вакансией"""
        vacancy = Vacancy(
            title="Test Job",
            url="https://test.com",
            salary={"from": 100000, "to": 150000, "currency": "RUR"},
            description="Test description",
            vacancy_id="test"
        )
        
        salary = Salary.from_dict(vacancy.salary)
        
        assert salary.from_amount == 100000
        assert salary.to_amount == 150000
        assert salary.currency == "RUR"

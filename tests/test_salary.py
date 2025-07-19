
import pytest
from typing import Dict, Any

from src.utils.salary import Salary


class TestSalary:
    """Тесты для класса Salary"""

    def test_salary_initialization_empty(self):
        """Тест инициализации с пустыми данными"""
        salary = Salary()
        assert salary.amount_from == 0
        assert salary.amount_to == 0
        assert salary.currency == 'RUR'
        assert salary.gross is False
        assert salary.period == 'month'

    def test_salary_initialization_with_data(self):
        """Тест инициализации с данными"""
        salary_data = {
            'from': 50000,
            'to': 80000,
            'currency': 'USD',
            'gross': True
        }
        salary = Salary(salary_data)
        assert salary.amount_from == 50000
        assert salary.amount_to == 80000
        assert salary.currency == 'USD'
        assert salary.gross is True

    def test_salary_properties(self):
        """Тест свойств зарплаты"""
        salary_data = {'from': 60000, 'to': 90000, 'currency': 'EUR'}
        salary = Salary(salary_data)
        
        assert salary.salary_from == 60000
        assert salary.salary_to == 90000
        assert salary.currency == 'EUR'

    def test_average_calculation(self):
        """Тест расчета средней зарплаты"""
        # Обе границы указаны
        salary = Salary({'from': 50000, 'to': 70000})
        assert salary.average == 60000
        
        # Только нижняя граница
        salary_from_only = Salary({'from': 50000, 'to': 0})
        assert salary_from_only.average == 50000
        
        # Только верхняя граница
        salary_to_only = Salary({'from': 0, 'to': 70000})
        assert salary_to_only.average == 70000
        
        # Нет данных
        salary_empty = Salary({'from': 0, 'to': 0})
        assert salary_empty.average == 0

    def test_get_max_salary(self):
        """Тест получения максимальной зарплаты"""
        # Обе границы
        salary = Salary({'from': 50000, 'to': 70000})
        assert salary.get_max_salary() == 70000
        
        # Только нижняя граница
        salary_from = Salary({'from': 50000, 'to': 0})
        assert salary_from.get_max_salary() == 50000
        
        # Только верхняя граница
        salary_to = Salary({'from': 0, 'to': 70000})
        assert salary_to.get_max_salary() == 70000
        
        # Нет данных
        salary_empty = Salary({'from': 0, 'to': 0})
        assert salary_empty.get_max_salary() is None

    def test_to_dict(self):
        """Тест преобразования в словарь"""
        salary_data = {
            'from': 40000,
            'to': 60000,
            'currency': 'USD',
            'gross': True
        }
        salary = Salary(salary_data)
        result = salary.to_dict()
        
        expected = {
            'from': 40000,
            'to': 60000,
            'currency': 'USD',
            'gross': True,
            'period': 'month'
        }
        assert result == expected

    def test_str_representation(self):
        """Тест строкового представления"""
        # Полные данные
        salary = Salary({'from': 50000, 'to': 70000, 'currency': 'RUR'})
        result = str(salary)
        assert "от 50,000" in result
        assert "до 70,000" in result
        assert "руб." in result
        
        # Только нижняя граница
        salary_from = Salary({'from': 50000, 'to': 0})
        result_from = str(salary_from)
        assert "от 50,000" in result_from
        assert "до" not in result_from or "до 0" not in result_from
        
        # Пустая зарплата
        salary_empty = Salary({'from': 0, 'to': 0})
        assert str(salary_empty) == "Зарплата не указана"

    def test_salary_validation(self):
        """Тест валидации данных зарплаты"""
        # Некорректные типы данных
        salary_invalid = Salary({'from': 'invalid', 'to': None})
        assert salary_invalid.salary_from is None
        assert salary_invalid.salary_to is None
        
        # Отрицательные значения
        salary_negative = Salary({'from': -1000, 'to': -2000})
        assert salary_negative.salary_from is None
        assert salary_negative.salary_to is None

    def test_currency_validation(self):
        """Тест валидации валюты"""
        # Корректная валюта
        salary = Salary({'currency': 'usd'})
        assert salary.currency == 'USD'
        
        # Некорректная валюта
        salary_invalid = Salary({'currency': None})
        assert salary_invalid.currency == 'RUR'
        
        # Пустая строка
        salary_empty = Salary({'currency': ''})
        assert salary_empty.currency == 'RUR'

    def test_superjob_format_compatibility(self):
        """Тест совместимости с форматом SuperJob"""
        # Формат SuperJob использует salary_range
        sj_data = {
            'salary_range': {
                'from': 80000,
                'to': 120000,
                'mode': {'id': 'month'}
            }
        }
        salary = Salary(sj_data)
        assert salary.amount_from == 80000
        assert salary.amount_to == 120000
        assert salary.period == 'month'

    def test_no_get_method(self):
        """Тест отсутствия метода get (для проверки ошибки из теста)"""
        salary = Salary({'from': 50000, 'to': 70000})
        
        # Убеждаемся, что у Salary нет метода get
        assert not hasattr(salary, 'get')
        
        # Проверяем, что при попытке вызвать get будет ошибка
        with pytest.raises(AttributeError):
            salary.get('some_key')

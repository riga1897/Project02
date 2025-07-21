from src.utils.salary import Salary


class TestSalary:
    """Тест класса Salary"""

    def test_init_empty(self):
        """Тест инициализации с пустыми данными"""
        salary = Salary()

        assert salary.amount_from == 0
        assert salary.amount_to == 0
        assert salary.gross is False
        assert salary.period == "month"
        assert salary.salary_from is None
        assert salary.salary_to is None
        assert salary.currency == "RUR"

    def test_init_none_data(self):
        """Тест инициализации с None"""
        salary = Salary(None)

        assert salary.amount_from == 0
        assert salary.amount_to == 0
        assert salary.gross is False
        assert salary.period == "month"

    def test_init_with_basic_data(self):
        """Тест инициализации с базовыми данными"""
        data = {"from": 100000, "to": 150000, "currency": "USD", "gross": True}
        salary = Salary(data)

        assert salary.amount_from == 100000
        assert salary.amount_to == 150000
        assert salary.currency == "USD"
        assert salary.gross is True
        assert salary.salary_from == 100000
        assert salary.salary_to == 150000

    def test_init_with_salary_range(self):
        """Тест инициализации с salary_range"""
        data = {"from": 50000, "to": 60000, "salary_range": {"from": 100000, "to": 150000, "mode": {"id": "week"}}}
        salary = Salary(data)

        assert salary.amount_from == 100000
        assert salary.amount_to == 150000
        assert salary.period == "week"

    def test_init_with_salary_range_empty_mode(self):
        """Тест инициализации с пустым mode в salary_range"""
        data = {"salary_range": {"from": 100000, "to": 150000, "mode": {"id": ""}}}
        salary = Salary(data)

        assert salary.period == "month"

    def test_init_with_salary_range_no_mode_id(self):
        """Тест инициализации без id в mode"""
        data = {"salary_range": {"from": 100000, "to": 150000, "mode": {}}}
        salary = Salary(data)

        assert salary.period == "month"

    def test_init_with_salary_range_invalid_mode(self):
        """Тест инициализации с невалидным mode"""
        data = {"salary_range": {"from": 100000, "to": 150000, "mode": "invalid"}}
        salary = Salary(data)

        assert salary.period == "month"

    def test_validate_and_set_non_dict(self):
        """Тест _validate_and_set с не-словарем"""
        salary = Salary()
        salary._validate_and_set("not a dict")

        assert salary.amount_from == 0
        assert salary.amount_to == 0

    def test_validate_salary_value_none(self):
        """Тест валидации None значения"""
        result = Salary._validate_salary_value(None)
        assert result is None

    def test_validate_salary_value_valid_int(self):
        """Тест валидации валидного int"""
        result = Salary._validate_salary_value(100000)
        assert result == 100000

    def test_validate_salary_value_valid_str(self):
        """Тест валидации валидной строки"""
        result = Salary._validate_salary_value("100000")
        assert result == 100000

    def test_validate_salary_value_zero(self):
        """Тест валидации нулевого значения"""
        result = Salary._validate_salary_value(0)
        assert result is None

    def test_validate_salary_value_negative(self):
        """Тест валидации отрицательного значения"""
        result = Salary._validate_salary_value(-1000)
        assert result is None

    def test_validate_salary_value_invalid_string(self):
        """Тест валидации невалидной строки"""
        result = Salary._validate_salary_value("invalid")
        assert result is None

    def test_validate_salary_value_invalid_type(self):
        """Тест валидации невалидного типа"""
        result = Salary._validate_salary_value([])
        assert result is None

    def test_validate_currency_none(self):
        """Тест валидации None валюты"""
        result = Salary._validate_currency(None)
        assert result == "RUR"

    def test_validate_currency_empty_string(self):
        """Тест валидации пустой строки валюты"""
        result = Salary._validate_currency("")
        assert result == "RUR"

    def test_validate_currency_non_string(self):
        """Тест валидации не-строки валюты"""
        result = Salary._validate_currency(123)
        assert result == "RUR"

    def test_validate_currency_valid(self):
        """Тест валидации валидной валюты"""
        result = Salary._validate_currency("usd")
        assert result == "USD"

    def test_validate_currency_with_spaces(self):
        """Тест валидации валюты с пробелами"""
        result = Salary._validate_currency("  eur  ")
        assert result == "EUR"

    def test_average_both_values(self):
        """Тест среднего значения с обеими границами"""
        data = {"from": 100000, "to": 200000}
        salary = Salary(data)

        assert salary.average == 150000

    def test_average_only_from(self):
        """Тест среднего значения только с нижней границей"""
        data = {"from": 100000}
        salary = Salary(data)

        assert salary.average == 100000

    def test_average_only_to(self):
        """Тест среднего значения только с верхней границей"""
        data = {"to": 100000}
        salary = Salary(data)

        assert salary.average == 100000

    def test_average_no_values(self):
        """Тест среднего значения без значений"""
        salary = Salary()

        assert salary.average == 0

    def test_to_dict(self):
        """Тест преобразования в словарь"""
        data = {"from": 100000, "to": 150000, "currency": "USD", "gross": True}
        salary = Salary(data)

        result = salary.to_dict()
        expected = {"from": 100000, "to": 150000, "currency": "USD", "gross": True, "period": "month"}

        assert result == expected

    def test_get_max_salary_with_to(self):
        """Тест получения максимальной зарплаты с верхней границей"""
        data = {"from": 100000, "to": 200000}
        salary = Salary(data)

        assert salary.get_max_salary() == 200000

    def test_get_max_salary_only_from(self):
        """Тест получения максимальной зарплаты только с нижней границей"""
        data = {"from": 100000}
        salary = Salary(data)

        assert salary.get_max_salary() == 100000

    def test_get_max_salary_no_values(self):
        """Тест получения максимальной зарплаты без значений"""
        salary = Salary()

        assert salary.get_max_salary() is None

    def test_str_no_salary(self):
        """Тест строкового представления без зарплаты"""
        salary = Salary()

        assert str(salary) == "Зарплата не указана"

    def test_str_both_values_rur(self):
        """Тест строкового представления с обеими границами в рублях"""
        data = {"from": 100000, "to": 150000, "currency": "RUR"}
        salary = Salary(data)

        result = str(salary)
        assert result == "от 100,000 до 150,000 руб. в месяц"

    def test_str_only_from_usd(self):
        """Тест строкового представления только с нижней границей в долларах"""
        data = {"from": 100000, "currency": "USD"}
        salary = Salary(data)

        result = str(salary)
        assert result == "от 100,000 $ в месяц"

    def test_str_only_to_eur(self):
        """Тест строкового представления только с верхней границей в евро"""
        data = {"to": 150000, "currency": "EUR"}
        salary = Salary(data)

        result = str(salary)
        assert result == "до 150,000 € в месяц"

    def test_str_with_gross(self):
        """Тест строкового представления с gross"""
        data = {"from": 100000, "gross": True}
        salary = Salary(data)

        result = str(salary)
        assert result == "от 100,000 руб. в месяц до вычета налогов"

    def test_str_with_custom_period(self):
        """Тест строкового представления с кастомным периодом"""
        data = {"from": 100000, "salary_range": {"from": 100000, "mode": {"id": "week"}}}
        salary = Salary(data)

        result = str(salary)
        assert result == "от 100,000 руб. в week"

    def test_str_with_month_period_russian(self):
        """Тест строкового представления с русским периодом месяц"""
        data = {"from": 100000, "salary_range": {"from": 100000, "mode": {"id": "месяц"}}}
        salary = Salary(data)

        result = str(salary)
        assert result == "от 100,000 руб. в месяц"

    def test_str_unknown_currency(self):
        """Тест строкового представления с неизвестной валютой"""
        data = {"from": 100000, "currency": "BTC"}
        salary = Salary(data)

        result = str(salary)
        assert result == "от 100,000 BTC в месяц"

    def test_salary_properties(self):
        """Тест свойств salary_from, salary_to, currency"""
        data = {"from": 100000, "to": 150000, "currency": "USD"}
        salary = Salary(data)

        assert salary.salary_from == 100000
        assert salary.salary_to == 150000
        assert salary.currency == "USD"

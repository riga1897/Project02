from typing import Dict, Any, Optional

class Salary:
    """Класс для обработки зарплатных данных HH.ru"""

    __slots__ = ('_salary_from', '_salary_to', '_currency', 'gross', 'period', 'amount_from', 'amount_to')

    def __init__(self, salary_data: Optional[Dict[str, Any]] = None):
        if salary_data is None:
            salary_data = {}

        self.amount_from = 0
        self.amount_to = 0
        self.gross = False
        self.period = 'month'

        self._salary_from = self._validate_salary_value(salary_data.get('from'))
        self._salary_to = self._validate_salary_value(salary_data.get('to'))
        self._currency = self._validate_currency(salary_data.get('currency', 'RUR'))

        if salary_data:
            self._validate_and_set(salary_data)

    def _validate_and_set(self, data: Dict[str, Any]) -> None:
        """Приватный метод валидации данных"""
        if not isinstance(data, dict):
            return

        self.amount_from = data.get('from') or 0
        self.amount_to = data.get('to') or 0
        self.gross = data.get('gross', False)

        if 'salary_range' in data and isinstance(data['salary_range'], dict):
            salary_range = data['salary_range']
            self.amount_from = salary_range.get('from') or self.amount_from
            self.amount_to = salary_range.get('to') or self.amount_to
            if salary_range.get('mode') and isinstance(salary_range['mode'], dict):
                mode_id = salary_range['mode'].get('id', '').lower()
                if mode_id:
                    self.period = mode_id

    def _validate_salary_value(self, value: Any) -> Optional[int]:
        """Валидация значения зарплаты"""
        if value is None:
            return None
        try:
            salary_val = int(value)
            return salary_val if salary_val > 0 else None
        except (ValueError, TypeError):
            return None

    def _validate_currency(self, value: Any) -> str:
        """Валидация валюты"""
        if not value or not isinstance(value, str):
            return 'RUR'
        return value.upper().strip()

    @property
    def salary_from(self) -> Optional[int]:
        return self._salary_from

    @property
    def salary_to(self) -> Optional[int]:
        return self._salary_to

    @property
    def currency(self) -> str:
        return self._currency

    @property
    def average(self) -> int:
        """Среднее значение зарплаты"""
        if self.amount_from and self.amount_to:
            return (self.amount_from + self.amount_to) // 2
        return self.amount_from or self.amount_to or 0

    @property
    def salary_from(self) -> int:
        """Alias for amount_from for backward compatibility"""
        return self.amount_from

    @property
    def salary_to(self) -> int:
        """Alias for amount_to for backward compatibility"""
        return self.amount_to

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'from': self.amount_from,
            'to': self.amount_to,
            'currency': self.currency,
            'gross': self.gross,
            'period': self.period
        }

    def get_max_salary(self) -> Optional[int]:
        """Возвращает максимальную зарплату для сортировки"""
        if self.amount_to:
            return self.amount_to
        elif self.amount_from:
            return self.amount_from
        return None

    def __str__(self) -> str:
        if not any([self.amount_from, self.amount_to]):
            return "Зарплата не указана"

        components = []
        if self.amount_from:
            components.append(f"от {self.amount_from}")
        if self.amount_to:
            components.append(f"до {self.amount_to}")

        currency = {
            'RUR': 'руб.',
            'USD': '$',
            'EUR': '€'
        }.get(self.currency, self.currency)

        period = {
            'month': 'в месяц',
            'year': 'в год',
            'day': 'в день'
        }.get(self.period, '')

        gross = " до вычета налогов" if self.gross else ""

        return f"{' '.join(components)} {currency}{period}{gross}".strip()
from typing import Dict, Any, Optional

class Salary:
    """Класс для обработки зарплатных данных HH.ru"""

    __slots__ = ('amount_from', 'amount_to', 'currency', 'gross', 'period')

    def __init__(self, salary_data: Optional[Dict[str, Any]] = None):
        self.amount_from = 0
        self.amount_to = 0
        self.currency = 'RUR'
        self.gross = False
        self.period = 'month'

        if salary_data:
            self._validate_and_set(salary_data)

    def _validate_and_set(self, data: Dict[str, Any]) -> None:
        """Приватный метод валидации данных"""
        self.amount_from = data.get('from') or 0
        self.amount_to = data.get('to') or 0
        self.currency = data.get('currency', 'RUR')
        self.gross = data.get('gross', False)

        if 'salary_range' in data:
            self.amount_from = data['salary_range'].get('from') or self.amount_from
            self.amount_to = data['salary_range'].get('to') or self.amount_to
            if data['salary_range'].get('mode'):
                self.period = data['salary_range']['mode']['id'].lower()

    @property
    def average(self) -> int:
        """Среднее значение зарплаты"""
        if self.amount_from and self.amount_to:
            return (self.amount_from + self.amount_to) // 2
        return self.amount_from or self.amount_to or 0

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'from': self.amount_from,
            'to': self.amount_to,
            'currency': self.currency,
            'gross': self.gross,
            'period': self.period
        }

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
        
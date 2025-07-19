from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class HHAPIConfig:
    """Конфигурация специфичных параметров HH API"""
    area: int = 113  # Россия по умолчанию
    per_page: int = 50  # Количество элементов на странице
    only_with_salary: bool = False
    period: int = 15  # Период 15 дней по умолчанию
    custom_params: Dict[str, Any] = None

    def __post_init__(self):
        if self.custom_params is None:
            self.custom_params = {}

    def get_params(self, **kwargs) -> Dict[str, Any]:
        """Генерация параметров запроса с учетом переопределений"""
        params = {
            "area": kwargs.get("area", self.area),
            "per_page": kwargs.get("per_page", self.per_page),
            "only_with_salary": kwargs.get("only_with_salary", self.only_with_salary),
            "period": kwargs.get("period", self.period)
        }
        if self.custom_params:
            params.update(self.custom_params)
        params.update(kwargs)
        return params

    def get_hh_params(self, **kwargs) -> Dict[str, Any]:
        """Get HH API params with overrides (для совместимости со старым интерфейсом)."""
        return self.get_params(**kwargs)

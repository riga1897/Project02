from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SJAPIConfig:
    """Конфигурация специфичных параметров SuperJob API"""
    town: int = 4  # Москва по умолчанию
    count: int = 100  # Увеличиваем количество элементов на странице
    no_agreement: int = 1  # Исключить вакансии без указания зарплаты
    custom_params: Dict[str, Any] = None

    def get_params(self, **kwargs) -> Dict[str, Any]:
        """Генерация параметров запроса с учетом переопределений"""
        params = {
            "town": kwargs.get("town", self.town),
            "count": kwargs.get("count", self.count),
            "no_agreement": self.no_agreement,
            "published": kwargs.get("published", 1),  # За последний месяц
            "order_field": kwargs.get("order_field", "date"),  # Сортировка по дате
            "order_direction": kwargs.get("order_direction", "desc")  # Сначала новые
        }
        if self.custom_params:
            params.update(self.custom_params)
        params.update(kwargs)
        return params
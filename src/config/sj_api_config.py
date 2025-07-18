from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SJAPIConfig:
    """Конфигурация специфичных параметров SuperJob API"""
    town: int = 4  # Москва по умолчанию
    count: int = 500  # Максимальное количество элементов на странице (до 500 по API)
    no_agreement: int = 0  # Включаем ВСЕ вакансии (с зарплатой и без)
    custom_params: Dict[str, Any] = None

    def get_params(self, **kwargs) -> Dict[str, Any]:
        """Генерация параметров запроса с учетом переопределений"""
        params = {
            "town": kwargs.get("town", self.town),
            "count": kwargs.get("count", self.count),
            "no_agreement": kwargs.get("no_agreement", self.no_agreement),
            "published": kwargs.get("published", 1),  # За последний месяц
            "order_field": kwargs.get("order_field", "date"),  # Сортировка по дате
            "order_direction": kwargs.get("order_direction", "desc"),  # Сначала новые
            "type_of_work": kwargs.get("type_of_work", 1),  # Полная занятость
            "period": kwargs.get("period", 0),  # За весь период
            "education": kwargs.get("education", 0)  # Любое образование
        }
        if self.custom_params:
            params.update(self.custom_params)
        params.update(kwargs)
        return params
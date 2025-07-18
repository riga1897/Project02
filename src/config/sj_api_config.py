from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SJAPIConfig:
    """Конфигурация специфичных параметров SuperJob API"""
    town: int = 4  # Москва по умолчанию
    count: int = 500  # Максимальное количество элементов на странице (до 500 по API)
    no_agreement: int = 1  # Убираем вакансии без указания зарплаты для начала
    custom_params: Dict[str, Any] = None

    def get_params(self, **kwargs) -> Dict[str, Any]:
        """Генерация параметров запроса с учетом переопределений"""
        params = {
            "count": kwargs.get("count", self.count),
            "no_agreement": kwargs.get("no_agreement", self.no_agreement),
            "order_field": kwargs.get("order_field", "date"),  # Сортировка по дате
            "order_direction": kwargs.get("order_direction", "desc"),  # Сначала новые
        }
        
        # Добавляем город только если он указан явно
        if "town" in kwargs or self.town != 4:
            params["town"] = kwargs.get("town", self.town)
            
        # Добавляем фильтр по времени публикации только если указан
        if "published" in kwargs:
            params["published"] = kwargs["published"]
            
        if self.custom_params:
            params.update(self.custom_params)
        params.update(kwargs)
        return params
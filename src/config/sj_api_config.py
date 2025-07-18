
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SJAPIConfig:
    """Конфигурация специфичных параметров SuperJob API"""
    town: int = 4  # Москва по умолчанию
    count: int = 50  # Количество элементов на странице
    no_agreement: int = 1  # Не показывать вакансии без указания зарплаты
    custom_params: Dict[str, Any] = None

    def get_params(self, **kwargs) -> Dict[str, Any]:
        """Генерация параметров запроса с учетом переопределений"""
        params = {
            "town": kwargs.get("town", self.town),
            "count": kwargs.get("count", self.count),
            "no_agreement": kwargs.get("no_agreement", self.no_agreement)
        }
        if self.custom_params:
            params.update(self.custom_params)
        params.update(kwargs)
        return params

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class HHAPIConfig:
    """Конфигурация специфичных параметров HH API"""
    area: int = 113  # Россия по умолчанию
    per_page: int = 100  # Количество элементов на странице
    only_with_salary: bool = False
    custom_params: Dict[str, Any] = None

    def get_params(self, **kwargs) -> Dict[str, Any]:
        """Генерация параметров запроса с учетом переопределений"""
        params = {
            "area": kwargs.get("area", self.area),
            "per_page": kwargs.get("per_page", self.per_page),
            "only_with_salary": kwargs.get("only_with_salary", self.only_with_salary)
        }
        if self.custom_params:
            params.update(self.custom_params)
        params.update(kwargs)
        return params


class APIConfig:
    """Основная конфигурация API"""

    def __init__(
            self,
            user_agent: str = "MyVacancyApp/1.0",
            timeout: int = 15,
            request_delay: float = 0.15,
            hh_config: Optional[HHAPIConfig] = None,
            max_pages: int = 100
    ):
        self.user_agent = user_agent
        self.timeout = timeout
        self.request_delay = request_delay
        self.hh_config = hh_config or HHAPIConfig()
        self.max_pages = max_pages

    def get_pagination_params(self, **kwargs) -> Dict[str, Any]:
        """Получение параметров пагинации"""
        return {
            "max_pages": kwargs.get("max_pages", self.max_pages)
        }

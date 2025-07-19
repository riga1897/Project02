from typing import Dict, Any, Optional
from .hh_api_config import HHAPIConfig


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

from abc import ABC, abstractmethod
from typing import Optional
from src.config.api_config import APIConfig
from .get_api import APIConnector


class BaseAPI(ABC):
    """Абстрактный базовый класс для всех API"""

    def __init__(self, config: Optional[APIConfig] = None):
        """
        Инициализация базового API

        Args:
            config: Конфигурация API
        """
        self.config = config or APIConfig()
        self.connector = APIConnector(self.config)

    @abstractmethod
    def get_vacancies(self, search_query: str, **kwargs):
        """Абстрактный метод получения вакансий"""
        pass

    @abstractmethod
    def clear_cache(self):
        """Абстрактный метод очистки кэша"""
        pass

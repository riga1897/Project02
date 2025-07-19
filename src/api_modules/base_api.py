
from abc import ABC, abstractmethod
from typing import Any, Optional
from src.config.api_config import APIConfig
from .get_api import APIConnector


class BaseAPI(ABC):
    """
    Абстрактный базовый класс для всех API
    
    Определяет общий интерфейс и базовую функциональность
    для всех реализаций API поиска вакансий.
    """

    def __init__(self, config: Optional[APIConfig] = None):
        """
        Инициализация базового API

        Args:
            config: Конфигурация API (если None, используется конфигурация по умолчанию)
        """
        self.config = config or APIConfig()
        self.connector = APIConnector(self.config)

    @abstractmethod
    def get_vacancies(self, search_query: str, **kwargs) -> Any:
        """
        Абстрактный метод получения вакансий
        
        Args:
            search_query: Поисковый запрос
            **kwargs: Дополнительные параметры поиска
            
        Returns:
            Any: Список найденных вакансий
        """

    @abstractmethod
    def clear_cache(self, api_prefix: str):
        """
        Абстрактный метод очистки кэша
        
        Должен быть реализован в наследующих классах
        для очистки кэшированных данных API.
        """

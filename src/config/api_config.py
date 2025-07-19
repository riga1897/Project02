from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class HHAPIConfig:
    """
    Конфигурация специфичных параметров HH API
    
    Содержит настройки по умолчанию для запросов к API HeadHunter
    с возможностью переопределения через параметры.
    """
    area: int = 1  # Москва по умолчанию
    per_page: int = 50  # Количество элементов на странице
    only_with_salary: bool = False  # Только вакансии с указанной зарплатой
    custom_params: Dict[str, Any] = None  # Дополнительные параметры

    def get_params(self, **kwargs) -> Dict[str, Any]:
        """
        Генерация параметров запроса с учетом переопределений
        
        Args:
            **kwargs: Параметры для переопределения значений по умолчанию
            
        Returns:
            Dict[str, Any]: Словарь параметров для API запроса
        """
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
    """
    Основная конфигурация API
    
    Центральная точка конфигурации для всех API-модулей.
    Содержит общие настройки подключения, таймауты и лимиты.
    """

    def __init__(
            self,
            user_agent: str = "MyVacancyApp/1.0",
            timeout: int = 15,
            request_delay: float = 0.5,
            hh_config: Optional[HHAPIConfig] = None,
            max_pages: int = 20
    ):
        """
        Инициализация конфигурации API
        
        Args:
            user_agent: User-Agent для HTTP запросов
            timeout: Таймаут запросов в секундах
            request_delay: Задержка между запросами в секундах
            hh_config: Специфичная конфигурация для HH API
            max_pages: Максимальное количество страниц для обработки
        """
        self.user_agent = user_agent
        self.timeout = timeout
        self.request_delay = request_delay
        self.hh_config = hh_config or HHAPIConfig()
        self.max_pages = max_pages

    def get_pagination_params(self, **kwargs) -> Dict[str, Any]:
        """
        Получение параметров пагинации
        
        Args:
            **kwargs: Параметры для переопределения значений по умолчанию
            
        Returns:
            Dict[str, Any]: Словарь параметров пагинации
        """
        return {
            "max_pages": kwargs.get("max_pages", self.max_pages)
        }

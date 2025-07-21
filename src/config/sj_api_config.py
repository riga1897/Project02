from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class SJAPIConfig:
    """Конфигурация специфичных параметров SuperJob API"""
    count: int = 500  # Максимальное количество элементов на странице (до 500 по API)
    published: int = 15  # Период публикации в днях (по умолчанию 15 дней)
    custom_params: Dict[str, Any] = None

    def get_params(self, **kwargs) -> Dict[str, Any]:
        """Генерация параметров запроса с учетом переопределений"""
        params = {
            "count": kwargs.get("count", self.count),
            "order_field": kwargs.get("order_field", "date"),  # Сортировка по дате
            "order_direction": kwargs.get("order_direction", "desc"),  # Сначала новые
            "published": kwargs.get("published", self.published),  # Период публикации (15 дней по умолчанию)
        }

        # Обрабатываем пагинацию (SuperJob использует page, начиная с 0)
        if "page" in kwargs:
            params["page"] = kwargs["page"]

        # Город добавляем только если указан явно (по умолчанию поиск по всей России)
        if "town" in kwargs:
            params["town"] = kwargs["town"]

        if self.custom_params:
            params.update(self.custom_params)
        params.update(kwargs)
        return params
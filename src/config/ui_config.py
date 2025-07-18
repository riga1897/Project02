
"""
Конфигурация пользовательского интерфейса
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class UIPaginationConfig:
    """Конфигурация для пагинации в UI"""
    
    # Основные настройки пагинации
    default_items_per_page: int = 10
    search_results_per_page: int = 5  # Для результатов поиска
    saved_vacancies_per_page: int = 10  # Для сохраненных вакансий
    
    # Настройки для топ-списков
    top_vacancies_per_page: int = 10
    
    # Максимальные значения
    max_items_per_page: int = 50
    min_items_per_page: int = 1
    
    def get_items_per_page(self, context: Optional[str] = None) -> int:
        """
        Получить количество элементов на странице для конкретного контекста
        
        Args:
            context: Контекст использования ('search', 'saved', 'top', None)
            
        Returns:
            Количество элементов на странице
        """
        context_mapping = {
            'search': self.search_results_per_page,
            'saved': self.saved_vacancies_per_page,
            'top': self.top_vacancies_per_page,
        }
        
        return context_mapping.get(context, self.default_items_per_page)
    
    def validate_items_per_page(self, value: int) -> int:
        """
        Валидация количества элементов на странице
        
        Args:
            value: Предполагаемое количество элементов
            
        Returns:
            Валидное количество элементов
        """
        if value < self.min_items_per_page:
            return self.min_items_per_page
        elif value > self.max_items_per_page:
            return self.max_items_per_page
        return value


# Глобальный экземпляр конфигурации
ui_pagination_config = UIPaginationConfig()

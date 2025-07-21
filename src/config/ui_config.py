from dataclasses import dataclass
from typing import Optional


@dataclass
class UIPaginationConfig:
    """
    Конфигурация для пагинации в пользовательском интерфейсе

    Определяет настройки отображения элементов на страницах
    для различных контекстов использования в UI.
    """

    # Основные настройки пагинации
    default_items_per_page: int = 10  # Количество элементов по умолчанию
    search_results_per_page: int = 5  # Для результатов поиска вакансий
    saved_vacancies_per_page: int = 10  # Для просмотра сохраненных вакансий

    # Настройки для специальных списков
    top_vacancies_per_page: int = 10  # Для топ-списков по зарплате

    # Ограничения значений
    max_items_per_page: int = 50  # Максимальное количество элементов на странице
    min_items_per_page: int = 1  # Минимальное количество элементов на странице

    def get_items_per_page(self, context: Optional[str] = None) -> int:
        """
        Получить количество элементов на странице для конкретного контекста

        Args:
            context: Контекст использования ('search', 'saved', 'top', None)

        Returns:
            Количество элементов на странице
        """
        context_mapping = {
            "search": self.search_results_per_page,
            "saved": self.saved_vacancies_per_page,
            "top": self.top_vacancies_per_page,
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


@dataclass
class UIConfig:
    """
    Основная конфигурация пользовательского интерфейса

    Содержит базовые настройки отображения для консольного интерфейса.
    """

    items_per_page: int = 5  # Количество элементов на странице по умолчанию
    max_display_items: int = 20  # Максимальное количество отображаемых элементов

    def get_pagination_settings(self, **kwargs) -> dict:
        """
        Получить настройки пагинации

        Returns:
            Словарь с настройками пагинации
        """
        return {
            "items_per_page": kwargs.get("items_per_page", self.items_per_page),
            "max_display_items": kwargs.get("max_display_items", self.max_display_items),
        }


# Глобальные экземпляры конфигурации для использования во всем приложении
ui_pagination_config = UIPaginationConfig()  # Конфигурация пагинации UI
ui_config = UIConfig()  # Основная конфигурация UI

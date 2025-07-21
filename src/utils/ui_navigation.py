import logging
import math
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class UINavigation:
    """Класс для унифицированной навигации по спискам данных"""

    def __init__(self, items_per_page: int = 10):
        """
        Инициализация навигации

        Args:
            items_per_page: Количество элементов на странице
        """
        self.items_per_page = items_per_page

    def paginate_display(
        self,
        items: List[Any],
        formatter: Callable[[Any, Optional[int]], str],
        header: str = "Данные",
        show_numbers: bool = True,
        custom_actions: Optional[Dict[str, Callable]] = None,
    ) -> None:
        """
        Отображение данных с пагинацией и навигацией

        Args:
            items: Список элементов для отображения
            formatter: Функция для форматирования элементов
            header: Заголовок для отображения
            show_numbers: Показывать ли нумерацию элементов
            custom_actions: Дополнительные действия {клавиша: функция}
        """
        if not items:
            print("Нет данных для отображения")
            return

        total_pages = math.ceil(len(items) / self.items_per_page)
        current_page = 1

        while True:
            # Отображение текущей страницы
            self._display_page(items, current_page, total_pages, formatter, header, show_numbers)

            # Если только одна страница, просто ждем Enter и выходим
            if total_pages == 1:
                input("\nНажмите Enter для продолжения...")
                break

            # Отображение меню навигации
            self._display_navigation_menu(current_page, total_pages, custom_actions)

            # Обработка пользовательского ввода
            choice = input("\nВыберите действие: ").strip().lower()

            # Обработка навигационных команд
            new_page = self._handle_navigation_choice(choice, current_page, total_pages, custom_actions)

            if new_page == -1:  # Выход
                break
            elif new_page == -2:  # Некорректный ввод
                print("Некорректный ввод")
                input("Нажмите Enter для продолжения...")
            else:
                current_page = new_page

    def _display_page(
        self,
        items: List[Any],
        current_page: int,
        total_pages: int,
        formatter: Callable[[Any, Optional[int]], str],
        header: str,
        show_numbers: bool,
    ) -> None:
        """Отображение текущей страницы"""
        # Вычисление индексов для текущей страницы
        start_idx = (current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(items))
        current_items = items[start_idx:end_idx]

        print(f"\n\n{header}")
        print("=" * len(header))

        # Отображение элементов
        for i, item in enumerate(current_items, start_idx + 1):
            if show_numbers:
                formatted_item = formatter(item, i)
            else:
                formatted_item = formatter(item, None)
            print(formatted_item)

        # Информация о пагинации
        print("\n" + "=" * 20)
        print("Навигация:")
        print(f"Страница {current_page} из {total_pages}")
        print(f"Показано элементов: {start_idx + 1}-{end_idx} из {len(items)}")
        print("-" * 20)

    @staticmethod
    def _display_navigation_menu(
        current_page: int, total_pages: int, custom_actions: Optional[Dict[str, Callable]] = None
    ) -> None:
        """Отображение меню навигации"""
        # Основные навигационные команды
        if current_page > 1:
            print("'p' или 'prev' - предыдущая страница")
        if current_page < total_pages:
            print("'n' или 'next' - следующая страница")

        print("'q' или 'quit' - выход")
        print("Номер страницы - переход к странице")

        # Дополнительные действия
        if custom_actions:
            for key, action in custom_actions.items():
                if hasattr(action, "__doc__") and action.__doc__:
                    print(f"'{key}' - {action.__doc__}")
                else:
                    print(f"'{key}' - дополнительное действие")

    @staticmethod
    def _handle_navigation_choice(
        choice: str, current_page: int, total_pages: int, custom_actions: Optional[Dict[str, Callable]] = None
    ) -> int:
        """
        Обработка выбора пользователя

        Returns:
            int: Новая страница, -1 для выхода, -2 для некорректного ввода
        """
        # Выход
        if choice in ["q", "quit"]:
            return -1

        # Навигация по страницам
        if choice in ["n", "next"] and current_page < total_pages:
            return current_page + 1
        elif choice in ["p", "prev"] and current_page > 1:
            return current_page - 1

        # Переход к конкретной странице
        if choice.isdigit():
            page_num = int(choice)
            if 1 <= page_num <= total_pages:
                return page_num
            else:
                print(f"Некорректный номер страницы. Доступно: 1-{total_pages}")
                input("Нажмите Enter для продолжения...")
                return current_page

        # Дополнительные действия
        if custom_actions and choice in custom_actions:
            try:
                custom_actions[choice]()
                return current_page  # Остаемся на той же странице
            except Exception as e:
                logger.error(f"Ошибка при выполнении действия '{choice}': {e}")
                print(f"Ошибка при выполнении действия: {e}")
                input("Нажмите Enter для продолжения...")
                return current_page

        # Некорректный ввод
        return -2

    def get_page_data(self, items: List[Any], page: int = 1) -> tuple[List[Any], Dict]:
        """
        Получение данных для конкретной страницы

        Args:
            items: Список элементов
            page: Номер страницы

        Returns:
            Кортеж (элементы_страницы, информация_о_пагинации)
        """
        if not items:
            return [], {
                "total_items": 0,
                "total_pages": 0,
                "current_page": 1,
                "items_per_page": self.items_per_page,
                "has_prev": False,
                "has_next": False,
            }

        total_items = len(items)
        total_pages = math.ceil(total_items / self.items_per_page)

        # Валидация номера страницы
        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages

        # Вычисление индексов
        start_idx = (page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_items)

        # Получение элементов для текущей страницы
        page_items = items[start_idx:end_idx]

        # Информация о пагинации
        pagination_info = {
            "total_items": total_items,
            "total_pages": total_pages,
            "current_page": page,
            "items_per_page": self.items_per_page,
            "has_prev": page > 1,
            "has_next": page < total_pages,
            "start_idx": start_idx + 1,
            "end_idx": end_idx,
        }

        return page_items, pagination_info


# Глобальный экземпляр навигации
ui_navigation = UINavigation()


def quick_paginate(
    items: List[Any],
    formatter: Callable[[Any, Optional[int]], str],
    header: str = "Данные",
    items_per_page: int = 10,
    show_numbers: bool = True,
    custom_actions: Optional[Dict[str, Callable]] = None,
) -> None:
    """
    Быстрая функция для пагинации с настройками по умолчанию

    Args:
        items: Список элементов
        formatter: Функция форматирования
        header: Заголовок
        items_per_page: Элементов на странице
        show_numbers: Показывать номера
        custom_actions: Дополнительные действия
    """
    navigator = UINavigation(items_per_page)
    navigator.paginate_display(items, formatter, header, show_numbers, custom_actions)

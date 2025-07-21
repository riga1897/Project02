from typing import Dict, List, Tuple, Callable
import logging

logger = logging.getLogger(__name__)


class MenuManager:
    """
    Класс для управления меню пользовательского интерфейса
    
    Предоставляет функциональность для создания, управления и отображения
    интерактивных меню с динамической структурой пунктов.
    """
    
    def __init__(self):
        """
        Инициализация менеджера меню
        
        Создает пустую структуру меню с возможностью
        динамического добавления и удаления пунктов.
        """
        self.menu_items: Dict[str, Tuple[str, Callable]] = {}
        self.menu_order: List[str] = []
    
    def add_menu_item(self, key: str, title: str, handler: Callable | None, position: int = None) -> None:
        """
        Добавляет пункт меню
        
        Args:
            key: Ключ пункта меню
            title: Заголовок пункта меню
            handler: Функция-обработчик
            position: Позиция в меню (если None, добавляется в конец)
        """
        self.menu_items[key] = (title, handler)
        
        if position is not None and 0 <= position <= len(self.menu_order):
            self.menu_order.insert(position, key)
        else:
            self.menu_order.append(key)
    
    def remove_menu_item(self, key: str) -> bool:
        """
        Удаляет пункт меню
        
        Args:
            key: Ключ пункта меню
            
        Returns:
            bool: True если пункт удален, False если не найден
        """
        if key in self.menu_items:
            del self.menu_items[key]
            self.menu_order.remove(key)
            return True
        return False
    
    def get_menu_items(self) -> List[Tuple[str, str]]:
        """
        Возвращает упорядоченный список пунктов меню
        
        Returns:
            List[Tuple[str, str]]: Список кортежей (ключ, заголовок)
        """
        return [(key, self.menu_items[key][0]) for key in self.menu_order if key in self.menu_items]
    
    def get_handler(self, key: str) -> Callable:
        """
        Возвращает обработчик для пункта меню
        
        Args:
            key: Ключ пункта меню
            
        Returns:
            Callable: Функция-обработчик или None если не найден
        """
        return self.menu_items.get(key, (None, None))[1]
    
    def display_menu(self) -> None:
        """
        Отображает меню в консоли
        
        Выводит все пункты меню в установленном порядке
        с разделителями и опцией выхода.
        """
        # from src.utils.ui_helpers import print_menu_separator
        
        print("\n")
        print_menu_separator()
        print("Выберите действие:")
        
        for key, title in self.get_menu_items():
            print(f"{key}. {title}")
        
        print("0. Выход")
        print_menu_separator()


def create_main_menu() -> MenuManager:
    """
    Создает главное меню приложения
    
    Returns:
        MenuManager: Настроенный менеджер меню
    """
    menu = MenuManager()
    
    # Группа поиска и получения данных
    menu.add_menu_item("1", "Поиск вакансий по запросу (запрос к API)", None)
    
    # Группа просмотра сохраненных данных
    menu.add_menu_item("2", "Показать все сохраненные вакансии", None)
    menu.add_menu_item("3", "Топ N сохраненных вакансий по зарплате", None)
    
    # Группа поиска в сохраненных данных
    menu.add_menu_item("4", "Поиск в сохраненных вакансиях по ключевому слову", None)
    menu.add_menu_item("5", "Расширенный поиск (несколько ключевых слов)", None)
    menu.add_menu_item("6", "Фильтр сохраненных вакансий по зарплате", None)
    
    # Группа управления данными
    menu.add_menu_item("7", "Удалить сохраненные вакансии", None)
    menu.add_menu_item("8", "Очистить кэш API", None)
    menu.add_menu_item("9", "Настройка SuperJob API", None)
    
    return menu


def print_menu_separator(width: int = 40) -> None:
    """
    Печать разделителя меню
    
    Args:
        width: Ширина разделителя
    """
    print("-" * width)


def print_section_header(title: str, width: int = 50) -> None:
    """
    Печать заголовка секции с декоративным оформлением
    
    Args:
        title: Текст заголовка
        width: Ширина декоративной линии
    """
    print("=" * width)
    print(title)
    print("=" * width)

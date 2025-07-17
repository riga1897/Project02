
"""
Модуль для пагинации пользовательского интерфейса
"""

from typing import List, Any, Callable, Optional
import math


def paginate_display(
    items: List[Any],
    items_per_page: int = 10,
    formatter: Optional[Callable[[Any], str]] = None,
    header: Optional[str] = None,
    show_numbers: bool = True
) -> None:
    """
    Отображает элементы с пагинацией в консоли
    
    Args:
        items: Список элементов для отображения
        items_per_page: Количество элементов на странице
        formatter: Функция для форматирования элементов
        header: Заголовок для отображения
        show_numbers: Показывать ли нумерацию элементов
    """
    if not items:
        print("Нет данных для отображения")
        return
    
    total_pages = math.ceil(len(items) / items_per_page)
    current_page = 1
    
    while True:
        # Очистка экрана (для консоли)
        print("\n" * 2)
        
        # Отображение заголовка
        if header:
            print(f"\n{header}")
            print("=" * len(header))
        
        # Вычисление индексов для текущей страницы
        start_idx = (current_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(items))
        
        # Отображение элементов текущей страницы
        for i, item in enumerate(items[start_idx:end_idx], start=start_idx + 1):
            if formatter:
                formatted_item = formatter(item)
            else:
                formatted_item = str(item)
            
            if show_numbers:
                print(f"{i}. {formatted_item}")
            else:
                print(formatted_item)
            print("-" * 50)
        
        # Информация о пагинации
        print(f"\nСтраница {current_page} из {total_pages}")
        print(f"Показано элементов: {start_idx + 1}-{end_idx} из {len(items)}")
        
        # Навигация
        if total_pages > 1:
            print("\nНавигация:")
            if current_page < total_pages:
                print("'n' или 'next' - следующая страница")
            if current_page > 1:
                print("'p' или 'prev' - предыдущая страница")
            print("'q' или 'quit' - выход")
            print("Номер страницы - переход к странице")
            
            choice = input("\nВыберите действие: ").strip().lower()
            
            if choice in ['q', 'quit']:
                break
            elif choice in ['n', 'next'] and current_page < total_pages:
                current_page += 1
            elif choice in ['p', 'prev'] and current_page > 1:
                current_page -= 1
            elif choice.isdigit():
                page_num = int(choice)
                if 1 <= page_num <= total_pages:
                    current_page = page_num
                else:
                    print(f"Некорректный номер страницы. Доступно: 1-{total_pages}")
                    input("Нажмите Enter для продолжения...")
            else:
                print("Некорректный ввод")
                input("Нажмите Enter для продолжения...")
        else:
            input("\nНажмите Enter для продолжения...")
            break


def paginate_list(
    items: List[Any],
    page: int = 1,
    items_per_page: int = 10
) -> tuple[List[Any], dict]:
    """
    Возвращает элементы для указанной страницы и информацию о пагинации
    
    Args:
        items: Список элементов
        page: Номер страницы (начиная с 1)
        items_per_page: Количество элементов на странице
        
    Returns:
        Кортеж (элементы_страницы, информация_о_пагинации)
    """
    if not items:
        return [], {
            'total_items': 0,
            'total_pages': 0,
            'current_page': 1,
            'items_per_page': items_per_page,
            'has_prev': False,
            'has_next': False
        }
    
    total_items = len(items)
    total_pages = math.ceil(total_items / items_per_page)
    
    # Валидация номера страницы
    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages
    
    # Вычисление индексов
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    # Получение элементов для текущей страницы
    page_items = items[start_idx:end_idx]
    
    # Информация о пагинации
    pagination_info = {
        'total_items': total_items,
        'total_pages': total_pages,
        'current_page': page,
        'items_per_page': items_per_page,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'start_idx': start_idx + 1,
        'end_idx': end_idx
    }
    
    return page_items, pagination_info


def format_pagination_info(pagination_info: dict) -> str:
    """
    Форматирует информацию о пагинации для отображения
    
    Args:
        pagination_info: Словарь с информацией о пагинации
        
    Returns:
        Отформатированная строка с информацией о пагинации
    """
    return (
        f"Страница {pagination_info['current_page']} из {pagination_info['total_pages']} "
        f"({pagination_info['start_idx']}-{pagination_info['end_idx']} "
        f"из {pagination_info['total_items']} элементов)"
    )


def get_page_navigation_menu() -> str:
    """
    Возвращает меню навигации по страницам
    
    Returns:
        Строка с меню навигации
    """
    return """
Навигация:
'n' или 'next' - следующая страница
'p' или 'prev' - предыдущая страница  
'f' или 'first' - первая страница
'l' или 'last' - последняя страница
'q' или 'quit' - выход
Номер страницы - переход к странице
"""

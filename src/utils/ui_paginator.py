
from typing import List, Callable, Any
from src.vacancies.models import Vacancy


def paginate_display(
    items: List[Any],
    display_func: Callable[[List[Any], int], None],
    page_size: int = 10,
    title: str = "Элементы"
) -> None:
    """
    Утилита для постраничного отображения элементов в пользовательском интерфейсе
    
    Args:
        items: Список элементов для отображения
        display_func: Функция для отображения элементов (принимает список и начальный номер)
        page_size: Количество элементов на странице
        title: Заголовок для отображения
    """
    if not items:
        print(f"Нет {title.lower()} для отображения.")
        return
        
    total_pages = (len(items) + page_size - 1) // page_size
    current_page = 1
    
    while True:
        # Вычисляем индексы для текущей страницы
        start_idx = (current_page - 1) * page_size
        end_idx = min(start_idx + page_size, len(items))
        
        print(f"\n--- Страница {current_page} из {total_pages} ---")
        print(f"Показываем {title.lower()} {start_idx + 1}-{end_idx} из {len(items)}:")
        
        # Отображаем элементы текущей страницы
        display_func(items[start_idx:end_idx], start_idx + 1)
        
        # Меню навигации
        print("\n" + "=" * 50)
        print("Навигация:")
        if current_page > 1:
            print("p - Предыдущая страница")
        if current_page < total_pages:
            print("n - Следующая страница")
        print("q - Завершить просмотр")
        print("=" * 50)
        
        choice = input("Ваш выбор: ").strip().lower()
        
        if choice == 'q':
            break
        elif choice == 'n' and current_page < total_pages:
            current_page += 1
        elif choice == 'p' and current_page > 1:
            current_page -= 1
        else:
            print("Неверный выбор. Попробуйте снова.")


def get_user_choice_menu(options: List[str], title: str = "Выберите действие") -> str:
    """
    Утилита для отображения меню и получения выбора пользователя
    
    Args:
        options: Список опций меню
        title: Заголовок меню
        
    Returns:
        Выбор пользователя
    """
    print(f"\n{title}:")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    print("0. Назад")
    
    while True:
        try:
            choice = input("Ваш выбор: ").strip()
            choice_num = int(choice)
            if 0 <= choice_num <= len(options):
                return choice
            else:
                print(f"Введите число от 0 до {len(options)}")
        except ValueError:
            print("Введите корректное число")

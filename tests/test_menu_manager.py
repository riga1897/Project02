
"""
Тесты для модуля menu_manager
"""

import pytest
from unittest.mock import patch, MagicMock
from src.utils.menu_manager import MenuManager, create_main_menu, print_section_header, print_menu_separator


class TestMenuManager:
    """Тесты для класса MenuManager"""
    
    def test_init(self):
        """Тест инициализации MenuManager"""
        menu = MenuManager()
        assert menu.menu_items == {}
        assert menu.menu_order == []
    
    def test_add_menu_item(self):
        """Тест добавления пункта меню"""
        menu = MenuManager()
        handler = MagicMock()
        
        menu.add_menu_item("1", "Test Item", handler)
        
        assert "1" in menu.menu_items
        assert menu.menu_items["1"] == ("Test Item", handler)
        assert menu.menu_order == ["1"]
    
    def test_add_menu_item_with_position(self):
        """Тест добавления пункта меню с указанием позиции"""
        menu = MenuManager()
        handler1 = MagicMock()
        handler2 = MagicMock()
        
        menu.add_menu_item("1", "First", handler1)
        menu.add_menu_item("2", "Second", handler2, position=0)
        
        assert menu.menu_order == ["2", "1"]
    
    def test_remove_menu_item(self):
        """Тест удаления пункта меню"""
        menu = MenuManager()
        handler = MagicMock()
        
        menu.add_menu_item("1", "Test Item", handler)
        assert menu.remove_menu_item("1") is True
        assert "1" not in menu.menu_items
        assert "1" not in menu.menu_order
    
    def test_remove_nonexistent_menu_item(self):
        """Тест удаления несуществующего пункта меню"""
        menu = MenuManager()
        assert menu.remove_menu_item("nonexistent") is False
    
    def test_get_menu_items(self):
        """Тест получения списка пунктов меню"""
        menu = MenuManager()
        handler1 = MagicMock()
        handler2 = MagicMock()
        
        menu.add_menu_item("1", "First", handler1)
        menu.add_menu_item("2", "Second", handler2)
        
        items = menu.get_menu_items()
        assert items == [("1", "First"), ("2", "Second")]
    
    def test_get_handler(self):
        """Тест получения обработчика пункта меню"""
        menu = MenuManager()
        handler = MagicMock()
        
        menu.add_menu_item("1", "Test Item", handler)
        
        assert menu.get_handler("1") == handler
        assert menu.get_handler("nonexistent") is None
    
    @patch('builtins.print')
    def test_display_menu(self, mock_print):
        """Тест отображения меню"""
        menu = MenuManager()
        handler = MagicMock()
        
        menu.add_menu_item("1", "Test Item", handler)
        menu.display_menu()
        
        # Проверяем, что print был вызван с нужными аргументами
        mock_print.assert_any_call("Выберите действие:")
        mock_print.assert_any_call("1. Test Item")
        mock_print.assert_any_call("0. Выход")


class TestMenuFunctions:
    """Тесты для функций модуля menu_manager"""
    
    def test_create_main_menu(self):
        """Тест создания главного меню"""
        menu = create_main_menu()
        
        assert isinstance(menu, MenuManager)
        items = menu.get_menu_items()
        assert len(items) > 0
        
        # Проверяем наличие основных пунктов
        item_titles = [item[1] for item in items]
        assert "Поиск вакансий по запросу (запрос к API)" in item_titles
        assert "Показать все сохраненные вакансии" in item_titles
        assert "Удалить сохраненные вакансии" in item_titles
    
    @patch('builtins.print')
    def test_print_section_header(self, mock_print):
        """Тест печати заголовка секции"""
        print_section_header("Test Header", 20)
        
        mock_print.assert_any_call("=" * 20)
        mock_print.assert_any_call("Test Header")
    
    @patch('builtins.print')
    def test_print_menu_separator(self, mock_print):
        """Тест печати разделителя меню"""
        print_menu_separator(30)
        
        mock_print.assert_called_with("-" * 30)

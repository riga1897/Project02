
import pytest
from unittest.mock import Mock, patch
from src.utils.menu_manager import MenuManager, create_main_menu, print_menu_separator, print_section_header


class TestMenuManager:
    """Тест менеджера меню"""

    def test_init(self):
        """Тест инициализации"""
        manager = MenuManager()
        
        assert manager.menu_items == {}
        assert manager.menu_order == []

    def test_add_menu_item_without_position(self):
        """Тест добавления пункта меню без указания позиции"""
        manager = MenuManager()
        handler = Mock()
        
        manager.add_menu_item("1", "Test Item", handler)
        
        assert "1" in manager.menu_items
        assert manager.menu_items["1"] == ("Test Item", handler)
        assert manager.menu_order == ["1"]

    def test_add_menu_item_with_position(self):
        """Тест добавления пункта меню с указанием позиции"""
        manager = MenuManager()
        handler1 = Mock()
        handler2 = Mock()
        
        manager.add_menu_item("1", "First", handler1)
        manager.add_menu_item("2", "Second", handler2, position=0)
        
        assert manager.menu_order == ["2", "1"]

    def test_add_menu_item_with_invalid_position(self):
        """Тест добавления пункта меню с неверной позицией"""
        manager = MenuManager()
        handler = Mock()
        
        manager.add_menu_item("1", "Test", handler, position=10)
        
        assert manager.menu_order == ["1"]

    def test_add_menu_item_with_none_handler(self):
        """Тест добавления пункта меню с None обработчиком"""
        manager = MenuManager()
        
        manager.add_menu_item("1", "Test", None)
        
        assert manager.menu_items["1"] == ("Test", None)

    def test_remove_menu_item_existing(self):
        """Тест удаления существующего пункта меню"""
        manager = MenuManager()
        handler = Mock()
        
        manager.add_menu_item("1", "Test", handler)
        result = manager.remove_menu_item("1")
        
        assert result is True
        assert "1" not in manager.menu_items
        assert "1" not in manager.menu_order

    def test_remove_menu_item_non_existing(self):
        """Тест удаления несуществующего пункта меню"""
        manager = MenuManager()
        
        result = manager.remove_menu_item("1")
        
        assert result is False

    def test_get_menu_items(self):
        """Тест получения пунктов меню"""
        manager = MenuManager()
        handler1 = Mock()
        handler2 = Mock()
        
        manager.add_menu_item("1", "First", handler1)
        manager.add_menu_item("2", "Second", handler2)
        
        items = manager.get_menu_items()
        
        assert items == [("1", "First"), ("2", "Second")]

    def test_get_menu_items_with_missing_key(self):
        """Тест получения пунктов меню с отсутствующим ключом в order"""
        manager = MenuManager()
        handler = Mock()
        
        manager.add_menu_item("1", "Test", handler)
        manager.menu_order.append("2")  # Добавляем несуществующий ключ
        
        items = manager.get_menu_items()
        
        assert items == [("1", "Test")]

    def test_get_handler_existing(self):
        """Тест получения обработчика для существующего пункта"""
        manager = MenuManager()
        handler = Mock()
        
        manager.add_menu_item("1", "Test", handler)
        result = manager.get_handler("1")
        
        assert result == handler

    def test_get_handler_non_existing(self):
        """Тест получения обработчика для несуществующего пункта"""
        manager = MenuManager()
        
        result = manager.get_handler("1")
        
        assert result is None

    @patch('builtins.print')
    @patch('src.utils.menu_manager.print_menu_separator')
    def test_display_menu(self, mock_separator, mock_print):
        """Тест отображения меню"""
        manager = MenuManager()
        manager.add_menu_item("1", "First Item", Mock())
        manager.add_menu_item("2", "Second Item", Mock())
        
        manager.display_menu()
        
        mock_separator.assert_called()
        mock_print.assert_any_call("\n")
        mock_print.assert_any_call("Выберите действие:")
        mock_print.assert_any_call("1. First Item")
        mock_print.assert_any_call("2. Second Item")
        mock_print.assert_any_call("0. Выход")


class TestCreateMainMenu:
    """Тест создания главного меню"""

    def test_create_main_menu(self):
        """Тест создания главного меню"""
        menu = create_main_menu()
        
        assert isinstance(menu, MenuManager)
        assert len(menu.menu_items) == 9
        assert "1" in menu.menu_items
        assert "9" in menu.menu_items
        assert menu.menu_items["1"][0] == "Поиск вакансий по запросу (запрос к API)"
        assert menu.menu_items["9"][0] == "Настройка SuperJob API"


class TestPrintMenuSeparator:
    """Тест печати разделителя меню"""

    @patch('builtins.print')
    def test_print_menu_separator_default_width(self, mock_print):
        """Тест печати разделителя с шириной по умолчанию"""
        print_menu_separator()
        
        mock_print.assert_called_once_with("-" * 40)

    @patch('builtins.print')
    def test_print_menu_separator_custom_width(self, mock_print):
        """Тест печати разделителя с кастомной шириной"""
        print_menu_separator(20)
        
        mock_print.assert_called_once_with("-" * 20)


class TestPrintSectionHeader:
    """Тест печати заголовка секции"""

    @patch('builtins.print')
    def test_print_section_header_default_width(self, mock_print):
        """Тест печати заголовка с шириной по умолчанию"""
        print_section_header("Test Header")
        
        expected_calls = [
            ("=" * 50,),
            ("Test Header",),
            ("=" * 50,)
        ]
        
        assert mock_print.call_count == 3
        for i, expected_call in enumerate(expected_calls):
            assert mock_print.call_args_list[i][0] == expected_call

    @patch('builtins.print')
    def test_print_section_header_custom_width(self, mock_print):
        """Тест печати заголовка с кастомной шириной"""
        print_section_header("Test", 10)
        
        expected_calls = [
            ("=" * 10,),
            ("Test",),
            ("=" * 10,)
        ]
        
        assert mock_print.call_count == 3
        for i, expected_call in enumerate(expected_calls):
            assert mock_print.call_args_list[i][0] == expected_call

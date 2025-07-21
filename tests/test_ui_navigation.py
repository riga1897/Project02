from unittest.mock import Mock, patch, call

from src.utils.ui_navigation import UINavigation, ui_navigation, quick_paginate


class TestUINavigation:
    """Тест класса UINavigation"""

    def test_init_default(self):
        """Тест инициализации с параметрами по умолчанию"""
        nav = UINavigation()
        assert nav.items_per_page == 10

    def test_init_custom(self):
        """Тест инициализации с кастомными параметрами"""
        nav = UINavigation(items_per_page=5)
        assert nav.items_per_page == 5

    @patch('builtins.print')
    @patch('builtins.input', return_value='')
    def test_paginate_display_empty_list(self, mock_input, mock_print):
        """Тест отображения пустого списка"""
        nav = UINavigation()
        formatter = Mock(return_value="test")
        
        nav.paginate_display([], formatter)
        
        mock_print.assert_called_once_with("Нет данных для отображения")

    @patch('builtins.print')
    @patch('builtins.input', return_value='')
    def test_paginate_display_single_page(self, mock_input, mock_print):
        """Тест отображения одной страницы"""
        nav = UINavigation(items_per_page=10)
        items = ["item1", "item2", "item3"]
        formatter = Mock(side_effect=lambda item, idx: f"{idx}: {item}" if idx else item)
        
        nav.paginate_display(items, formatter, "Test Header", True)
        
        # Проверяем что formatter вызывался с правильными параметрами
        expected_calls = [call("item1", 1), call("item2", 2), call("item3", 3)]
        formatter.assert_has_calls(expected_calls)
        
        # Проверяем что был вызван input для продолжения
        mock_input.assert_called_once_with("\nНажмите Enter для продолжения...")

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['q'])
    def test_paginate_display_multiple_pages_quit(self, mock_input, mock_print):
        """Тест отображения множественных страниц с выходом"""
        nav = UINavigation(items_per_page=2)
        items = ["item1", "item2", "item3", "item4", "item5"]
        formatter = Mock(side_effect=lambda item, idx: f"{idx}: {item}" if idx else item)
        
        nav.paginate_display(items, formatter, "Test Header", True)
        
        # Проверяем что были показаны первые 2 элемента
        expected_calls = [call("item1", 1), call("item2", 2)]
        formatter.assert_has_calls(expected_calls)

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['n', 'q'])
    def test_paginate_display_next_page(self, mock_input, mock_print):
        """Тест навигации на следующую страницу"""
        nav = UINavigation(items_per_page=2)
        items = ["item1", "item2", "item3", "item4"]
        formatter = Mock(side_effect=lambda item, idx: f"{idx}: {item}" if idx else item)
        
        nav.paginate_display(items, formatter, "Test Header", True)
        
        # Должны быть вызовы для первой и второй страницы
        expected_calls = [
            call("item1", 1), call("item2", 2),  # первая страница
            call("item3", 3), call("item4", 4)   # вторая страница
        ]
        formatter.assert_has_calls(expected_calls)

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['next', 'prev', 'quit'])
    def test_paginate_display_navigation_commands(self, mock_input, mock_print):
        """Тест навигационных команд next/prev"""
        nav = UINavigation(items_per_page=2)
        items = ["item1", "item2", "item3", "item4"]
        formatter = Mock(side_effect=lambda item, idx: f"{idx}: {item}" if idx else item)
        
        nav.paginate_display(items, formatter, "Test Header", True)
        
        # Проверяем что отображались разные страницы
        assert formatter.call_count >= 4  # минимум 2 страницы

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['2', 'q'])
    def test_paginate_display_page_number_navigation(self, mock_input, mock_print):
        """Тест навигации по номеру страницы"""
        nav = UINavigation(items_per_page=2)
        items = ["item1", "item2", "item3", "item4"]
        formatter = Mock(side_effect=lambda item, idx: f"{idx}: {item}" if idx else item)
        
        nav.paginate_display(items, formatter, "Test Header", True)
        
        # Проверяем что были показаны элементы второй страницы
        expected_calls = [
            call("item1", 1), call("item2", 2),  # первая страница
            call("item3", 3), call("item4", 4)   # вторая страница
        ]
        formatter.assert_has_calls(expected_calls)

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['invalid', '', 'q'])
    def test_paginate_display_invalid_input(self, mock_input, mock_print):
        """Тест обработки некорректного ввода"""
        nav = UINavigation(items_per_page=2)
        items = ["item1", "item2", "item3", "item4"]
        formatter = Mock(side_effect=lambda item, idx: f"{idx}: {item}" if idx else item)
        
        nav.paginate_display(items, formatter, "Test Header", True)
        
        # Проверяем что было сообщение о некорректном вводе
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert "Некорректный ввод" in print_calls

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['custom', 'q'])
    def test_paginate_display_custom_actions(self, mock_input, mock_print):
        """Тест кастомных действий"""
        nav = UINavigation(items_per_page=2)
        items = ["item1", "item2", "item3", "item4"]
        formatter = Mock(side_effect=lambda item, idx: f"{idx}: {item}" if idx else item)
        
        custom_action = Mock()
        custom_action.__doc__ = "Custom action"
        custom_actions = {"custom": custom_action}
        
        nav.paginate_display(items, formatter, "Test Header", True, custom_actions)
        
        # Проверяем что кастомное действие было вызвано
        custom_action.assert_called_once()

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['custom', '', 'q'])
    @patch('src.utils.ui_navigation.logger')
    def test_paginate_display_custom_actions_exception(self, mock_logger, mock_input, mock_print):
        """Тест обработки исключений в кастомных действиях"""
        nav = UINavigation(items_per_page=2)
        items = ["item1", "item2", "item3", "item4"]
        formatter = Mock(side_effect=lambda item, idx: f"{idx}: {item}" if idx else item)
        
        custom_action = Mock(side_effect=Exception("Test error"))
        custom_actions = {"custom": custom_action}
        
        nav.paginate_display(items, formatter, "Test Header", True, custom_actions)
        
        # Проверяем что была залогирована ошибка
        mock_logger.error.assert_called_once()

    @patch('builtins.print')
    def test_display_page(self, mock_print):
        """Тест метода _display_page"""
        nav = UINavigation(items_per_page=2)
        items = ["item1", "item2", "item3"]
        formatter = Mock(side_effect=lambda item, idx: f"{idx}: {item}" if idx else item)
        
        nav._display_page(items, 1, 2, formatter, "Test Header", True)
        
        # Проверяем что formatter был вызван для первых двух элементов
        expected_calls = [call("item1", 1), call("item2", 2)]
        formatter.assert_has_calls(expected_calls)

    @patch('builtins.print')
    def test_display_page_without_numbers(self, mock_print):
        """Тест метода _display_page без нумерации"""
        nav = UINavigation(items_per_page=2)
        items = ["item1", "item2"]
        formatter = Mock(side_effect=lambda item, idx: f"{item}")
        
        nav._display_page(items, 1, 1, formatter, "Test Header", False)
        
        # Проверяем что formatter был вызван без индексов
        expected_calls = [call("item1", None), call("item2", None)]
        formatter.assert_has_calls(expected_calls)

    @patch('builtins.print')
    def test_display_navigation_menu_first_page(self, mock_print):
        """Тест меню навигации на первой странице"""
        UINavigation._display_navigation_menu(1, 3)
        
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert "'n' или 'next' - следующая страница" in print_calls
        assert "'p' или 'prev' - предыдущая страница" not in print_calls

    @patch('builtins.print')
    def test_display_navigation_menu_middle_page(self, mock_print):
        """Тест меню навигации на средней странице"""
        UINavigation._display_navigation_menu(2, 3)
        
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert "'n' или 'next' - следующая страница" in print_calls
        assert "'p' или 'prev' - предыдущая страница" in print_calls

    @patch('builtins.print')
    def test_display_navigation_menu_last_page(self, mock_print):
        """Тест меню навигации на последней странице"""
        UINavigation._display_navigation_menu(3, 3)
        
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert "'n' или 'next' - следующая страница" not in print_calls
        assert "'p' или 'prev' - предыдущая страница" in print_calls

    @patch('builtins.print')
    def test_display_navigation_menu_with_custom_actions(self, mock_print):
        """Тест меню навигации с кастомными действиями"""
        custom_action = Mock()
        custom_action.__doc__ = "Custom action"
        custom_actions = {"custom": custom_action}
        
        UINavigation._display_navigation_menu(1, 2, custom_actions)
        
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert "'custom' - Custom action" in print_calls

    @patch('builtins.print')
    def test_display_navigation_menu_with_custom_actions_no_doc(self, mock_print):
        """Тест меню навигации с кастомными действиями без документации"""
        custom_action = Mock()
        custom_action.__doc__ = None
        custom_actions = {"custom": custom_action}
        
        UINavigation._display_navigation_menu(1, 2, custom_actions)
        
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert "'custom' - дополнительное действие" in print_calls

    def test_handle_navigation_choice_quit_q(self):
        """Тест команды выхода 'q'"""
        result = UINavigation._handle_navigation_choice('q', 1, 3)
        assert result == -1

    def test_handle_navigation_choice_quit_full(self):
        """Тест команды выхода 'quit'"""
        result = UINavigation._handle_navigation_choice('quit', 1, 3)
        assert result == -1

    def test_handle_navigation_choice_next_valid(self):
        """Тест команды 'next' когда возможно"""
        result = UINavigation._handle_navigation_choice('n', 1, 3)
        assert result == 2
        
        result = UINavigation._handle_navigation_choice('next', 1, 3)
        assert result == 2

    def test_handle_navigation_choice_next_invalid(self):
        """Тест команды 'next' когда невозможно"""
        result = UINavigation._handle_navigation_choice('n', 3, 3)
        assert result == -2

    def test_handle_navigation_choice_prev_valid(self):
        """Тест команды 'prev' когда возможно"""
        result = UINavigation._handle_navigation_choice('p', 2, 3)
        assert result == 1
        
        result = UINavigation._handle_navigation_choice('prev', 2, 3)
        assert result == 1

    def test_handle_navigation_choice_prev_invalid(self):
        """Тест команды 'prev' когда невозможно"""
        result = UINavigation._handle_navigation_choice('p', 1, 3)
        assert result == -2

    def test_handle_navigation_choice_page_number_valid(self):
        """Тест перехода по валидному номеру страницы"""
        result = UINavigation._handle_navigation_choice('2', 1, 3)
        assert result == 2

    @patch('builtins.print')
    @patch('builtins.input', return_value='')
    def test_handle_navigation_choice_page_number_invalid(self, mock_input, mock_print):
        """Тест перехода по невалидному номеру страницы"""
        result = UINavigation._handle_navigation_choice('5', 1, 3)
        assert result == 1  # возвращается текущая страница
        
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("Некорректный номер страницы" in call for call in print_calls)

    def test_handle_navigation_choice_custom_action(self):
        """Тест кастомного действия"""
        custom_action = Mock()
        custom_actions = {"custom": custom_action}
        
        result = UINavigation._handle_navigation_choice('custom', 1, 3, custom_actions)
        
        custom_action.assert_called_once()
        assert result == 1  # остаемся на той же странице

    @patch('builtins.print')
    @patch('builtins.input', return_value='')
    @patch('src.utils.ui_navigation.logger')
    def test_handle_navigation_choice_custom_action_exception(self, mock_logger, mock_input, mock_print):
        """Тест исключения в кастомном действии"""
        custom_action = Mock(side_effect=Exception("Test error"))
        custom_actions = {"custom": custom_action}
        
        result = UINavigation._handle_navigation_choice('custom', 1, 3, custom_actions)
        
        assert result == 1
        mock_logger.error.assert_called_once()

    def test_handle_navigation_choice_invalid(self):
        """Тест некорректного ввода"""
        result = UINavigation._handle_navigation_choice('invalid', 1, 3)
        assert result == -2

    def test_get_page_data_empty_list(self):
        """Тест получения данных пустой страницы"""
        nav = UINavigation()
        items, info = nav.get_page_data([])
        
        assert items == []
        expected_info = {
            'total_items': 0,
            'total_pages': 0,
            'current_page': 1,
            'items_per_page': 10,
            'has_prev': False,
            'has_next': False
        }
        assert info == expected_info

    def test_get_page_data_first_page(self):
        """Тест получения данных первой страницы"""
        nav = UINavigation(items_per_page=3)
        items = ["item1", "item2", "item3", "item4", "item5"]
        
        page_items, info = nav.get_page_data(items, 1)
        
        assert page_items == ["item1", "item2", "item3"]
        expected_info = {
            'total_items': 5,
            'total_pages': 2,
            'current_page': 1,
            'items_per_page': 3,
            'has_prev': False,
            'has_next': True,
            'start_idx': 1,
            'end_idx': 3
        }
        assert info == expected_info

    def test_get_page_data_last_page(self):
        """Тест получения данных последней страницы"""
        nav = UINavigation(items_per_page=3)
        items = ["item1", "item2", "item3", "item4", "item5"]
        
        page_items, info = nav.get_page_data(items, 2)
        
        assert page_items == ["item4", "item5"]
        expected_info = {
            'total_items': 5,
            'total_pages': 2,
            'current_page': 2,
            'items_per_page': 3,
            'has_prev': True,
            'has_next': False,
            'start_idx': 4,
            'end_idx': 5
        }
        assert info == expected_info

    def test_get_page_data_page_validation_low(self):
        """Тест валидации номера страницы (слишком низкий)"""
        nav = UINavigation(items_per_page=2)
        items = ["item1", "item2", "item3"]
        
        page_items, info = nav.get_page_data(items, -1)
        
        assert info['current_page'] == 1

    def test_get_page_data_page_validation_high(self):
        """Тест валидации номера страницы (слишком высокий)"""
        nav = UINavigation(items_per_page=2)
        items = ["item1", "item2", "item3"]
        
        page_items, info = nav.get_page_data(items, 10)
        
        assert info['current_page'] == 2  # максимальная страница

    def test_get_page_data_single_page(self):
        """Тест получения данных единственной страницы"""
        nav = UINavigation(items_per_page=10)
        items = ["item1", "item2"]
        
        page_items, info = nav.get_page_data(items, 1)
        
        assert page_items == ["item1", "item2"]
        assert info['total_pages'] == 1
        assert info['has_prev'] == False
        assert info['has_next'] == False


class TestGlobalUINavigation:
    """Тест глобального экземпляра UINavigation"""

    def test_global_instance_exists(self):
        """Тест существования глобального экземпляра"""
        assert ui_navigation is not None
        assert isinstance(ui_navigation, UINavigation)

    def test_global_instance_default_config(self):
        """Тест конфигурации глобального экземпляра"""
        assert ui_navigation.items_per_page == 10


class TestQuickPaginate:
    """Тест функции quick_paginate"""

    @patch('src.utils.ui_navigation.UINavigation')
    def test_quick_paginate_default_params(self, mock_ui_nav_class):
        """Тест quick_paginate с параметрами по умолчанию"""
        mock_navigator = Mock()
        mock_ui_nav_class.return_value = mock_navigator
        
        items = ["item1", "item2"]
        formatter = Mock()
        
        quick_paginate(items, formatter)
        
        # Проверяем создание навигатора с правильными параметрами
        mock_ui_nav_class.assert_called_once_with(10)
        
        # Проверяем вызов paginate_display
        mock_navigator.paginate_display.assert_called_once_with(
            items, formatter, "Данные", True, None
        )

    @patch('src.utils.ui_navigation.UINavigation')
    def test_quick_paginate_custom_params(self, mock_ui_nav_class):
        """Тест quick_paginate с кастомными параметрами"""
        mock_navigator = Mock()
        mock_ui_nav_class.return_value = mock_navigator
        
        items = ["item1", "item2"]
        formatter = Mock()
        custom_actions = {"test": Mock()}
        
        quick_paginate(
            items=items,
            formatter=formatter,
            header="Custom Header",
            items_per_page=5,
            show_numbers=False,
            custom_actions=custom_actions
        )
        
        # Проверяем создание навигатора с правильными параметрами
        mock_ui_nav_class.assert_called_once_with(5)
        
        # Проверяем вызов paginate_display
        mock_navigator.paginate_display.assert_called_once_with(
            items, formatter, "Custom Header", False, custom_actions
        )

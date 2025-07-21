
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.ui_interfaces.console_interface import UserInterface


class TestUserInterface:
    """Тесты для класса UserInterface"""

    @pytest.fixture
    def interface(self):
        """Фикстура для создания экземпляра UserInterface"""
        with patch('src.ui_interfaces.console_interface.HeadHunterAPI'), \
             patch('src.ui_interfaces.console_interface.SuperJobAPI'), \
             patch('src.ui_interfaces.console_interface.UnifiedAPI'), \
             patch('src.ui_interfaces.console_interface.JSONSaver'), \
             patch('src.ui_interfaces.console_interface.create_main_menu'), \
             patch('src.ui_interfaces.console_interface.VacancyOperations'), \
             patch('src.ui_interfaces.console_interface.SourceSelector'), \
             patch('src.ui_interfaces.console_interface.VacancySearchHandler'), \
             patch('src.ui_interfaces.console_interface.VacancyDisplayHandler'):
            return UserInterface()

    @patch('builtins.print')
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=['0'])
    def test_run_exit(self, mock_input, mock_header, mock_print, interface):
        """Тест выхода из программы"""
        interface.run()
        mock_print.assert_any_call("Спасибо за использование! До свидания!")

    @patch('builtins.print')
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=['1', '0'])
    def test_run_search_vacancies(self, mock_input, mock_header, mock_print, interface):
        """Тест вызова поиска вакансий"""
        interface.search_handler.search_vacancies = Mock()
        interface.run()
        interface.search_handler.search_vacancies.assert_called_once()

    @patch('builtins.print')
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=['2', '0'])
    def test_run_show_saved_vacancies(self, mock_input, mock_header, mock_print, interface):
        """Тест показа сохраненных вакансий"""
        interface.display_handler.show_all_saved_vacancies = Mock()
        interface.run()
        interface.display_handler.show_all_saved_vacancies.assert_called_once()

    @patch('builtins.print')
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=['3', '0'])
    def test_run_get_top_saved_vacancies(self, mock_input, mock_header, mock_print, interface):
        """Тест получения топ вакансий по зарплате"""
        interface.display_handler.show_top_vacancies_by_salary = Mock()
        interface.run()
        interface.display_handler.show_top_vacancies_by_salary.assert_called_once()

    @patch('builtins.print')
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=['4', '0'])
    def test_run_search_saved_by_keyword(self, mock_input, mock_header, mock_print, interface):
        """Тест поиска в сохраненных вакансиях по ключевому слову"""
        interface.display_handler.search_saved_vacancies_by_keyword = Mock()
        interface.run()
        interface.display_handler.search_saved_vacancies_by_keyword.assert_called_once()

    @patch('builtins.print')
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=['8', '0'])
    def test_run_clear_api_cache(self, mock_input, mock_header, mock_print, interface):
        """Тест очистки кэша API"""
        with patch.object(interface, '_clear_api_cache') as mock_clear:
            interface.run()
            mock_clear.assert_called_once()

    @patch('builtins.print')
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=['9', '0'])
    def test_run_setup_superjob_api(self, mock_input, mock_header, mock_print, interface):
        """Тест настройки SuperJob API"""
        with patch.object(interface, '_setup_superjob_api') as mock_setup:
            interface.run()
            mock_setup.assert_called_once()

    @patch('builtins.print')
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=['invalid', '0'])
    def test_run_invalid_choice(self, mock_input, mock_header, mock_print, interface):
        """Тест неверного выбора"""
        interface.run()
        mock_print.assert_any_call("Неверный выбор. Попробуйте снова.")

    @patch('builtins.print')
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=KeyboardInterrupt)
    def test_run_keyboard_interrupt(self, mock_input, mock_header, mock_print, interface):
        """Тест прерывания пользователем"""
        interface.run()
        mock_print.assert_any_call("\n\nРабота прервана пользователем. До свидания!")

    @patch('builtins.print')
    @patch('src.ui_interfaces.console_interface.print_section_header')
    @patch('builtins.input', side_effect=Exception("Test error"))
    def test_run_exception_handling(self, mock_input, mock_header, mock_print, interface):
        """Тест обработки исключений"""
        with patch('src.ui_interfaces.console_interface.logger') as mock_logger:
            interface.run()
            mock_logger.error.assert_called()

    @patch('builtins.input', return_value='1')
    @patch('src.ui_interfaces.console_interface.print_menu_separator')
    @patch('builtins.print')
    def test_show_menu(self, mock_print, mock_separator, mock_input, interface):
        """Тест отображения меню"""
        result = interface._show_menu()
        assert result == '1'
        mock_print.assert_any_call("Выберите действие:")

    @patch('src.ui_interfaces.console_interface.get_user_input', return_value='python')
    @patch('src.ui_interfaces.console_interface.quick_paginate')
    @patch('builtins.print')
    def test_advanced_search_vacancies_with_commas(self, mock_print, mock_paginate, mock_input, interface):
        """Тест расширенного поиска с запятыми"""
        mock_vacancy = Mock()
        mock_vacancy.title = "Python Developer"
        interface.json_saver.get_vacancies.return_value = [mock_vacancy]
        interface.vacancy_ops.filter_vacancies_by_multiple_keywords.return_value = [mock_vacancy]
        
        with patch('src.ui_interfaces.console_interface.get_user_input', return_value='python, django'):
            interface._advanced_search_vacancies()
        
        interface.vacancy_ops.filter_vacancies_by_multiple_keywords.assert_called_once()

    @patch('src.ui_interfaces.console_interface.get_user_input', return_value='python AND django')
    @patch('src.ui_interfaces.console_interface.quick_paginate')
    @patch('builtins.print')
    def test_advanced_search_vacancies_with_operators(self, mock_print, mock_paginate, mock_input, interface):
        """Тест расширенного поиска с операторами"""
        mock_vacancy = Mock()
        interface.json_saver.get_vacancies.return_value = [mock_vacancy]
        interface.vacancy_ops.search_vacancies_advanced.return_value = [mock_vacancy]
        
        interface._advanced_search_vacancies()
        interface.vacancy_ops.search_vacancies_advanced.assert_called_once()

    @patch('src.ui_interfaces.console_interface.get_user_input', return_value='')
    @patch('builtins.print')
    def test_advanced_search_vacancies_empty_query(self, mock_print, mock_input, interface):
        """Тест расширенного поиска с пустым запросом"""
        interface.json_saver.get_vacancies.return_value = []
        interface._advanced_search_vacancies()

    @patch('builtins.print')
    def test_advanced_search_vacancies_no_saved(self, mock_print, interface):
        """Тест расширенного поиска без сохраненных вакансий"""
        interface.json_saver.get_vacancies.return_value = []
        interface._advanced_search_vacancies()
        mock_print.assert_any_call("Нет сохраненных вакансий.")

    @patch('src.ui_interfaces.console_interface.get_user_input', return_value='python')
    @patch('builtins.print')
    def test_advanced_search_vacancies_no_results(self, mock_print, mock_input, interface):
        """Тест расширенного поиска без результатов"""
        mock_vacancy = Mock()
        interface.json_saver.get_vacancies.return_value = [mock_vacancy]
        interface.vacancy_ops.search_vacancies_advanced.return_value = []
        
        interface._advanced_search_vacancies()
        mock_print.assert_any_call("Вакансии по указанным критериям не найдены.")

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_filter_saved_vacancies_by_salary_min(self, mock_print, mock_input, interface):
        """Тест фильтрации по минимальной зарплате"""
        mock_vacancy = Mock()
        interface.json_saver.get_vacancies.return_value = [mock_vacancy]
        interface.vacancy_ops.filter_vacancies_by_min_salary.return_value = [mock_vacancy]
        interface.vacancy_ops.sort_vacancies_by_salary.return_value = [mock_vacancy]
        
        with patch('builtins.input', side_effect=['1', '100000']):
            with patch('src.ui_interfaces.console_interface.quick_paginate'):
                interface._filter_saved_vacancies_by_salary()
        
        interface.vacancy_ops.filter_vacancies_by_min_salary.assert_called_once()

    @patch('builtins.input', return_value='2')
    @patch('builtins.print')
    def test_filter_saved_vacancies_by_salary_max(self, mock_print, mock_input, interface):
        """Тест фильтрации по максимальной зарплате"""
        mock_vacancy = Mock()
        interface.json_saver.get_vacancies.return_value = [mock_vacancy]
        interface.vacancy_ops.filter_vacancies_by_max_salary.return_value = [mock_vacancy]
        interface.vacancy_ops.sort_vacancies_by_salary.return_value = [mock_vacancy]
        
        with patch('builtins.input', side_effect=['2', '150000']):
            with patch('src.ui_interfaces.console_interface.quick_paginate'):
                interface._filter_saved_vacancies_by_salary()
        
        interface.vacancy_ops.filter_vacancies_by_max_salary.assert_called_once()

    @patch('builtins.input', return_value='3')
    @patch('src.ui_interfaces.console_interface.parse_salary_range', return_value=(100000, 150000))
    @patch('builtins.print')
    def test_filter_saved_vacancies_by_salary_range(self, mock_print, mock_parse, mock_input, interface):
        """Тест фильтрации по диапазону зарплат"""
        mock_vacancy = Mock()
        interface.json_saver.get_vacancies.return_value = [mock_vacancy]
        interface.vacancy_ops.filter_vacancies_by_salary_range.return_value = [mock_vacancy]
        interface.vacancy_ops.sort_vacancies_by_salary.return_value = [mock_vacancy]
        
        with patch('builtins.input', side_effect=['3', '100000 - 150000']):
            with patch('src.ui_interfaces.console_interface.quick_paginate'):
                interface._filter_saved_vacancies_by_salary()
        
        interface.vacancy_ops.filter_vacancies_by_salary_range.assert_called_once()

    @patch('builtins.input', return_value='invalid')
    @patch('builtins.print')
    def test_filter_saved_vacancies_by_salary_invalid_choice(self, mock_print, mock_input, interface):
        """Тест фильтрации с неверным выбором"""
        interface.json_saver.get_vacancies.return_value = [Mock()]
        interface._filter_saved_vacancies_by_salary()
        mock_print.assert_any_call("Неверный выбор.")

    @patch('builtins.input', side_effect=['1', 'invalid'])
    @patch('builtins.print')
    def test_filter_saved_vacancies_by_salary_invalid_min(self, mock_print, mock_input, interface):
        """Тест фильтрации с неверной минимальной зарплатой"""
        interface.json_saver.get_vacancies.return_value = [Mock()]
        interface._filter_saved_vacancies_by_salary()
        mock_print.assert_any_call("Введите корректное число!")

    @patch('builtins.input', side_effect=['2', 'invalid'])
    @patch('builtins.print')
    def test_filter_saved_vacancies_by_salary_invalid_max(self, mock_print, mock_input, interface):
        """Тест фильтрации с неверной максимальной зарплатой"""
        interface.json_saver.get_vacancies.return_value = [Mock()]
        interface._filter_saved_vacancies_by_salary()
        mock_print.assert_any_call("Введите корректное число!")

    @patch('builtins.input', return_value='1')
    @patch('src.ui_interfaces.console_interface.confirm_action', return_value=True)
    @patch('builtins.print')
    def test_delete_saved_vacancies_all(self, mock_print, mock_confirm, mock_input, interface):
        """Тест удаления всех вакансий"""
        interface.json_saver.get_vacancies.return_value = [Mock()]
        interface.json_saver.delete_all_vacancies.return_value = True
        
        interface._delete_saved_vacancies()
        interface.json_saver.delete_all_vacancies.assert_called_once()

    @patch('builtins.input', return_value='1')
    @patch('src.ui_interfaces.console_interface.confirm_action', return_value=False)
    @patch('builtins.print')
    def test_delete_saved_vacancies_all_cancelled(self, mock_print, mock_confirm, mock_input, interface):
        """Тест отмены удаления всех вакансий"""
        interface.json_saver.get_vacancies.return_value = [Mock()]
        
        interface._delete_saved_vacancies()
        mock_print.assert_any_call("Удаление отменено.")

    @patch('builtins.input', return_value='2')
    @patch('src.ui_interfaces.console_interface.get_user_input', return_value='python')
    @patch('src.ui_interfaces.console_interface.filter_vacancies_by_keyword')
    @patch('builtins.print')
    def test_delete_saved_vacancies_by_keyword(self, mock_print, mock_filter, mock_get_input, mock_input, interface):
        """Тест удаления вакансий по ключевому слову"""
        mock_vacancy = Mock()
        interface.json_saver.get_vacancies.return_value = [mock_vacancy]
        mock_filter.return_value = [mock_vacancy]
        
        with patch.object(interface, '_show_vacancies_for_deletion') as mock_show:
            interface._delete_saved_vacancies()
            mock_show.assert_called_once()

    @patch('builtins.input', return_value='2')
    @patch('src.ui_interfaces.console_interface.get_user_input', return_value='')
    @patch('builtins.print')
    def test_delete_saved_vacancies_by_keyword_empty(self, mock_print, mock_get_input, mock_input, interface):
        """Тест удаления вакансий с пустым ключевым словом"""
        interface.json_saver.get_vacancies.return_value = [Mock()]
        interface._delete_saved_vacancies()

    @patch('builtins.input', return_value='3')
    @patch('src.ui_interfaces.console_interface.get_user_input', return_value='123')
    @patch('src.ui_interfaces.console_interface.confirm_action', return_value=True)
    @patch('builtins.print')
    def test_delete_saved_vacancies_by_id(self, mock_print, mock_confirm, mock_get_input, mock_input, interface):
        """Тест удаления вакансии по ID"""
        mock_vacancy = Mock()
        mock_vacancy.vacancy_id = '123'
        mock_vacancy.title = 'Test Job'
        mock_vacancy.employer = {'name': 'Test Company'}
        mock_vacancy.salary = '100000'
        mock_vacancy.experience = '3-6 лет'
        mock_vacancy.url = 'http://test.com'
        
        interface.json_saver.get_vacancies.return_value = [mock_vacancy]
        interface.json_saver.delete_vacancy_by_id.return_value = True
        
        interface._delete_saved_vacancies()
        interface.json_saver.delete_vacancy_by_id.assert_called_once_with('123')

    @patch('builtins.input', return_value='0')
    @patch('builtins.print')
    def test_delete_saved_vacancies_cancel(self, mock_print, mock_input, interface):
        """Тест отмены удаления вакансий"""
        interface.json_saver.get_vacancies.return_value = [Mock()]
        interface._delete_saved_vacancies()
        mock_print.assert_any_call("Назад в предыдущее меню.")

    @patch('builtins.print')
    def test_delete_saved_vacancies_no_vacancies(self, mock_print, interface):
        """Тест удаления при отсутствии вакансий"""
        interface.json_saver.get_vacancies.return_value = []
        interface._delete_saved_vacancies()
        mock_print.assert_any_call("Нет сохраненных вакансий для удаления.")

    @patch('src.ui_interfaces.console_interface.confirm_action', return_value=True)
    @patch('builtins.print')
    def test_clear_api_cache(self, mock_print, mock_confirm, interface):
        """Тест очистки кэша API"""
        interface.source_selector.get_user_source_choice.return_value = {'hh'}
        interface.source_selector.display_sources_info = Mock()
        interface.unified_api.clear_cache = Mock()
        
        interface._clear_api_cache()
        interface.unified_api.clear_cache.assert_called_once()

    @patch('src.ui_interfaces.console_interface.confirm_action', return_value=False)
    @patch('builtins.print')
    def test_clear_api_cache_cancelled(self, mock_print, mock_confirm, interface):
        """Тест отмены очистки кэша"""
        interface.source_selector.get_user_source_choice.return_value = {'hh'}
        interface.source_selector.display_sources_info = Mock()
        
        interface._clear_api_cache()
        mock_print.assert_any_call("Очистка кэша отменена.")

    def test_clear_api_cache_no_sources(self, interface):
        """Тест очистки кэша без выбранных источников"""
        interface.source_selector.get_user_source_choice.return_value = None
        interface._clear_api_cache()

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_get_period_choice_1_day(self, mock_print, mock_input, interface):
        """Тест выбора периода 1 день"""
        result = interface._get_period_choice()
        assert result == 1

    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    def test_get_period_choice_default(self, mock_print, mock_input, interface):
        """Тест выбора периода по умолчанию"""
        result = interface._get_period_choice()
        assert result == 15

    @patch('builtins.input', return_value='0')
    @patch('builtins.print')
    def test_get_period_choice_cancel(self, mock_print, mock_input, interface):
        """Тест отмены выбора периода"""
        result = interface._get_period_choice()
        assert result is None

    @patch('builtins.input', side_effect=['6', '30'])
    @patch('builtins.print')
    def test_get_period_choice_custom(self, mock_print, mock_input, interface):
        """Тест выбора пользовательского периода"""
        result = interface._get_period_choice()
        assert result == 30

    @patch('builtins.input', side_effect=['6', '999'])
    @patch('builtins.print')
    def test_get_period_choice_custom_invalid_range(self, mock_print, mock_input, interface):
        """Тест выбора пользовательского периода вне диапазона"""
        result = interface._get_period_choice()
        assert result == 15

    @patch('builtins.input', side_effect=['6', 'invalid'])
    @patch('builtins.print')
    def test_get_period_choice_custom_invalid_input(self, mock_print, mock_input, interface):
        """Тест выбора пользовательского периода с неверным вводом"""
        result = interface._get_period_choice()
        assert result == 15

    @patch('builtins.input', return_value='invalid')
    @patch('builtins.print')
    def test_get_period_choice_invalid(self, mock_print, mock_input, interface):
        """Тест неверного выбора периода"""
        result = interface._get_period_choice()
        assert result == 15

    @patch('builtins.input', side_effect=KeyboardInterrupt)
    @patch('builtins.print')
    def test_get_period_choice_keyboard_interrupt(self, mock_print, mock_input, interface):
        """Тест прерывания выбора периода"""
        result = interface._get_period_choice()
        assert result is None

    @patch('os.getenv', return_value='real_key')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_setup_superjob_api_configured(self, mock_print, mock_input, mock_getenv, interface):
        """Тест настройки SuperJob API когда ключ уже настроен"""
        interface._setup_superjob_api()
        mock_print.assert_any_call("✅ SuperJob API ключ уже настроен")

    @patch('os.getenv', return_value='v3.r.137440105.example.test_tool')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_setup_superjob_api_test_key(self, mock_print, mock_input, mock_getenv, interface):
        """Тест настройки SuperJob API с тестовым ключом"""
        interface._setup_superjob_api()
        mock_print.assert_any_call("❌ SuperJob API ключ не настроен или используется тестовый")

    @patch('src.ui_interfaces.console_interface.display_vacancy_info')
    @patch('builtins.print')
    def test_display_vacancies(self, mock_print, mock_display, interface):
        """Тест отображения списка вакансий"""
        mock_vacancy = Mock()
        vacancies = [mock_vacancy]
        
        interface._display_vacancies(vacancies, 1)
        mock_display.assert_called_once_with(mock_vacancy, 1)

    @patch('src.ui_interfaces.console_interface.quick_paginate')
    def test_display_vacancies_with_pagination(self, mock_paginate, interface):
        """Тест отображения вакансий с пагинацией"""
        vacancies = [Mock()]
        interface._display_vacancies_with_pagination(vacancies)
        mock_paginate.assert_called_once()

    @patch('builtins.input', side_effect=['q'])
    @patch('builtins.print')
    def test_show_vacancies_for_deletion_quit(self, mock_print, mock_input, interface):
        """Тест выхода из меню удаления вакансий"""
        mock_vacancy = Mock()
        mock_vacancy.vacancy_id = '123'
        mock_vacancy.title = 'Test'
        mock_vacancy.employer = {'name': 'Test'}
        mock_vacancy.salary = '100000'
        mock_vacancy.url = 'http://test.com'
        
        interface._show_vacancies_for_deletion([mock_vacancy], 'python')

    @patch('builtins.input', side_effect=['a'])
    @patch('src.ui_interfaces.console_interface.confirm_action', return_value=True)
    @patch('builtins.print')
    def test_show_vacancies_for_deletion_all(self, mock_print, mock_confirm, mock_input, interface):
        """Тест удаления всех вакансий из списка"""
        mock_vacancy = Mock()
        mock_vacancy.vacancy_id = '123'
        mock_vacancy.title = 'Test'
        mock_vacancy.employer = {'name': 'Test'}
        mock_vacancy.salary = '100000'
        mock_vacancy.url = 'http://test.com'
        
        interface.json_saver.delete_vacancies_by_keyword.return_value = 1
        interface._show_vacancies_for_deletion([mock_vacancy], 'python')

    @patch('os.getenv', return_value=None)
    @patch('builtins.input')
    @patch('builtins.print')
    def test_configure_superjob_api_no_key(self, mock_print, mock_input, mock_getenv, interface):
        """Тест настройки SuperJob API без ключа"""
        interface._configure_superjob_api()
        mock_print.assert_any_call("❌ SuperJob API ключ не настроен или используется тестовый")

    @patch('builtins.input', return_value='5')
    @patch('builtins.print')
    def test_run_advanced_search(self, mock_print, mock_input, interface):
        """Тест расширенного поиска из меню"""
        with patch.object(interface, '_advanced_search_vacancies') as mock_advanced:
            with patch('builtins.input', side_effect=['5', '0']):
                interface.run()
                mock_advanced.assert_called_once()

    @patch('builtins.input', return_value='6')
    @patch('builtins.print')
    def test_run_filter_by_salary(self, mock_print, mock_input, interface):
        """Тест фильтрации по зарплате из меню"""
        with patch.object(interface, '_filter_saved_vacancies_by_salary') as mock_filter:
            with patch('builtins.input', side_effect=['6', '0']):
                interface.run()
                mock_filter.assert_called_once()

    @patch('builtins.input', return_value='7')
    @patch('builtins.print')
    def test_run_delete_vacancies(self, mock_print, mock_input, interface):
        """Тест удаления вакансий из меню"""
        with patch.object(interface, '_delete_saved_vacancies') as mock_delete:
            with patch('builtins.input', side_effect=['7', '0']):
                interface.run()
                mock_delete.assert_called_once()

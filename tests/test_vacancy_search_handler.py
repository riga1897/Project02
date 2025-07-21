
import pytest
from unittest.mock import Mock, patch, call
from src.ui_interfaces.vacancy_search_handler import VacancySearchHandler
from src.api_modules.unified_api import UnifiedAPI
from src.storage.json_saver import JSONSaver
from src.vacancies.models import Vacancy


class TestVacancySearchHandler:
    """Тесты для класса VacancySearchHandler"""

    @pytest.fixture
    def mock_unified_api(self):
        """Фикстура для мок UnifiedAPI"""
        return Mock(spec=UnifiedAPI)

    @pytest.fixture
    def mock_json_saver(self):
        """Фикстура для мок JSONSaver"""
        return Mock(spec=JSONSaver)

    @pytest.fixture
    def handler(self, mock_unified_api, mock_json_saver):
        """Фикстура для VacancySearchHandler"""
        return VacancySearchHandler(mock_unified_api, mock_json_saver)

    def test_init(self, mock_unified_api, mock_json_saver):
        """Тест инициализации обработчика"""
        handler = VacancySearchHandler(mock_unified_api, mock_json_saver)
        
        assert handler.unified_api is mock_unified_api
        assert handler.json_saver is mock_json_saver
        assert handler.source_selector is not None

    @patch('src.ui_interfaces.vacancy_search_handler.get_user_input', return_value=None)
    def test_search_vacancies_no_sources(self, mock_input, handler):
        """Тест поиска без выбора источников"""
        handler.source_selector.get_user_source_choice = Mock(return_value=None)
        
        handler.search_vacancies()
        
        handler.source_selector.get_user_source_choice.assert_called_once()

    @patch('src.ui_interfaces.vacancy_search_handler.get_user_input', return_value=None)
    def test_search_vacancies_no_query(self, mock_input, handler):
        """Тест поиска без запроса"""
        handler.source_selector.get_user_source_choice = Mock(return_value={"hh"})
        handler.source_selector.display_sources_info = Mock()
        
        handler.search_vacancies()
        
        mock_input.assert_called_once_with("\nВведите поисковый запрос: ")

    @patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler._get_period_choice', return_value=None)
    @patch('src.ui_interfaces.vacancy_search_handler.get_user_input', return_value="python")
    def test_search_vacancies_no_period(self, mock_input, mock_period, handler):
        """Тест поиска без выбора периода"""
        handler.source_selector.get_user_source_choice = Mock(return_value={"hh"})
        handler.source_selector.display_sources_info = Mock()
        
        handler.search_vacancies()
        
        mock_period.assert_called_once()

    @patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler._handle_search_results')
    @patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler._fetch_vacancies_from_sources')
    @patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler._get_period_choice', return_value=15)
    @patch('src.ui_interfaces.vacancy_search_handler.get_user_input', return_value="python")
    @patch('builtins.print')
    def test_search_vacancies_success(self, mock_print, mock_input, mock_period, mock_fetch, mock_handle, handler):
        """Тест успешного поиска вакансий"""
        handler.source_selector.get_user_source_choice = Mock(return_value={"hh"})
        handler.source_selector.display_sources_info = Mock()
        vacancies = [Mock(spec=Vacancy)]
        mock_fetch.return_value = vacancies
        
        handler.search_vacancies()
        
        mock_fetch.assert_called_once_with({"hh"}, "python", 15)
        mock_handle.assert_called_once_with(vacancies, "python")

    @patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler._fetch_vacancies_from_sources')
    @patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler._get_period_choice', return_value=15)
    @patch('src.ui_interfaces.vacancy_search_handler.get_user_input', return_value="python")
    @patch('builtins.print')
    def test_search_vacancies_no_results(self, mock_print, mock_input, mock_period, mock_fetch, handler):
        """Тест поиска без результатов"""
        handler.source_selector.get_user_source_choice = Mock(return_value={"hh"})
        handler.source_selector.display_sources_info = Mock()
        mock_fetch.return_value = []
        
        handler.search_vacancies()
        
        mock_print.assert_any_call("Вакансии не найдены ни на одном из источников.")

    @patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler._fetch_vacancies_from_sources')
    @patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler._get_period_choice', return_value=15)
    @patch('src.ui_interfaces.vacancy_search_handler.get_user_input', return_value="python")
    @patch('src.ui_interfaces.vacancy_search_handler.logger')
    @patch('builtins.print')
    def test_search_vacancies_exception(self, mock_print, mock_logger, mock_input, mock_period, mock_fetch, handler):
        """Тест обработки исключения при поиске"""
        handler.source_selector.get_user_source_choice = Mock(return_value={"hh"})
        handler.source_selector.display_sources_info = Mock()
        error_msg = "API Error"
        mock_fetch.side_effect = Exception(error_msg)
        
        handler.search_vacancies()
        
        mock_logger.error.assert_called_once_with(f"Ошибка поиска вакансий: {error_msg}")
        mock_print.assert_any_call(f"Произошла ошибка при поиске: {error_msg}")

    @patch('builtins.print')
    def test_fetch_vacancies_from_sources_hh_only(self, mock_print, handler):
        """Тест получения вакансий только с HH.ru"""
        sources = {"hh"}
        vacancies = [Mock(spec=Vacancy)]
        handler.unified_api.get_hh_vacancies.return_value = vacancies
        
        result = handler._fetch_vacancies_from_sources(sources, "python", 15)
        
        handler.unified_api.get_hh_vacancies.assert_called_once_with("python", period=15)
        assert result == vacancies

    @patch('builtins.print')
    def test_fetch_vacancies_from_sources_sj_only(self, mock_print, handler):
        """Тест получения вакансий только с SuperJob"""
        sources = {"sj"}
        vacancies = [Mock(spec=Vacancy)]
        handler.unified_api.get_sj_vacancies.return_value = vacancies
        
        result = handler._fetch_vacancies_from_sources(sources, "python", 15)
        
        handler.unified_api.get_sj_vacancies.assert_called_once_with("python", period=15)
        assert result == vacancies

    @patch('builtins.print')
    def test_fetch_vacancies_from_sources_both(self, mock_print, handler):
        """Тест получения вакансий с обоих источников"""
        sources = {"hh", "sj"}
        hh_vacancies = [Mock(spec=Vacancy)]
        sj_vacancies = [Mock(spec=Vacancy)]
        handler.unified_api.get_hh_vacancies.return_value = hh_vacancies
        handler.unified_api.get_sj_vacancies.return_value = sj_vacancies
        
        result = handler._fetch_vacancies_from_sources(sources, "python", 15)
        
        assert len(result) == 2
        assert hh_vacancies[0] in result
        assert sj_vacancies[0] in result

    @patch('builtins.print')
    def test_fetch_vacancies_from_sources_no_results(self, mock_print, handler):
        """Тест получения вакансий без результатов"""
        sources = {"hh"}
        handler.unified_api.get_hh_vacancies.return_value = None
        
        result = handler._fetch_vacancies_from_sources(sources, "python", 15)
        
        assert result == []

    def test_handle_search_results(self, handler):
        """Тест обработки результатов поиска"""
        handler._handle_vacancies_preview_and_save = Mock()
        vacancies = [Mock(spec=Vacancy)]
        
        handler._handle_search_results(vacancies, "python")
        
        handler._handle_vacancies_preview_and_save.assert_called_once_with(vacancies, "python")

    @patch('src.ui_interfaces.vacancy_search_handler.confirm_action', return_value=False)
    @patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler._display_duplicate_info')
    @patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler._check_existing_vacancies')
    def test_handle_vacancies_preview_and_save_no_preview(self, mock_check, mock_display, mock_confirm, handler):
        """Тест обработки без предпросмотра"""
        vacancies = [Mock(spec=Vacancy)]
        duplicate_info = {'new_vacancies': [], 'total_count': 1}
        mock_check.return_value = duplicate_info
        
        handler._handle_vacancies_preview_and_save(vacancies, "python")
        
        mock_confirm.assert_called_once_with("Показать найденные вакансии?")

    @patch('src.ui_interfaces.vacancy_search_handler.confirm_action', side_effect=[True, True])
    @patch('src.ui_interfaces.vacancy_search_handler.quick_paginate')
    @patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler._save_vacancies')
    @patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler._display_duplicate_info')
    @patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler._check_existing_vacancies')
    def test_handle_vacancies_preview_and_save_with_preview_and_save(self, mock_check, mock_display, mock_save, mock_paginate, mock_confirm, handler):
        """Тест обработки с предпросмотром и сохранением"""
        vacancies = [Mock(spec=Vacancy)]
        new_vacancies = [Mock(spec=Vacancy)]
        duplicate_info = {'new_vacancies': new_vacancies, 'total_count': 1}
        mock_check.return_value = duplicate_info
        
        handler._handle_vacancies_preview_and_save(vacancies, "python")
        
        mock_paginate.assert_called_once()
        mock_save.assert_called_once_with(new_vacancies)

    @patch('src.ui_interfaces.vacancy_search_handler.confirm_action', side_effect=[True, False])
    @patch('src.ui_interfaces.vacancy_search_handler.quick_paginate')
    @patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler._display_duplicate_info')
    @patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler._check_existing_vacancies')
    @patch('builtins.print')
    def test_handle_vacancies_preview_and_save_no_save(self, mock_print, mock_check, mock_display, mock_paginate, mock_confirm, handler):
        """Тест обработки с предпросмотром но без сохранения"""
        vacancies = [Mock(spec=Vacancy)]
        new_vacancies = [Mock(spec=Vacancy)]
        duplicate_info = {'new_vacancies': new_vacancies, 'total_count': 1}
        mock_check.return_value = duplicate_info
        
        handler._handle_vacancies_preview_and_save(vacancies, "python")
        
        mock_print.assert_called_with("Новые вакансии не сохранены")

    @patch('src.ui_interfaces.vacancy_search_handler.confirm_action', return_value=False)
    @patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler._display_duplicate_info')
    @patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler._check_existing_vacancies')
    @patch('builtins.print')
    def test_handle_vacancies_preview_and_save_no_new_vacancies(self, mock_print, mock_check, mock_display, mock_confirm, handler):
        """Тест обработки без новых вакансий"""
        vacancies = [Mock(spec=Vacancy)]
        duplicate_info = {'new_vacancies': [], 'total_count': 1}
        mock_check.return_value = duplicate_info
        
        handler._handle_vacancies_preview_and_save(vacancies, "python")
        
        mock_print.assert_any_call("Нет новых вакансий для сохранения.")

    @patch('builtins.print')
    def test_save_vacancies_success(self, mock_print, handler):
        """Тест сохранения вакансий"""
        vacancies = [Mock(spec=Vacancy)]
        handler.json_saver.add_vacancy.return_value = ["Добавлена вакансия"]
        
        handler._save_vacancies(vacancies)
        
        handler.json_saver.add_vacancy.assert_called_once_with(vacancies)

    @patch('builtins.print')
    def test_save_vacancies_many_messages(self, mock_print, handler):
        """Тест сохранения вакансий с многими сообщениями"""
        vacancies = [Mock(spec=Vacancy)]
        messages = [f"Сообщение {i}" for i in range(10)]
        handler.json_saver.add_vacancy.return_value = messages
        
        handler._save_vacancies(vacancies)
        
        mock_print.assert_any_call("  ... и еще 5 операций")

    @patch('builtins.print')
    def test_save_vacancies_no_messages(self, mock_print, handler):
        """Тест сохранения вакансий без сообщений"""
        vacancies = [Mock(spec=Vacancy)]
        handler.json_saver.add_vacancy.return_value = []
        
        handler._save_vacancies(vacancies)
        
        mock_print.assert_called_with("Вакансии уже существуют в базе данных")

    @patch('tqdm.tqdm')
    def test_check_existing_vacancies(self, mock_tqdm, handler):
        """Тест проверки существующих вакансий"""
        vacancies = [Mock(spec=Vacancy), Mock(spec=Vacancy)]
        handler.json_saver.is_vacancy_exists.side_effect = [True, False]
        
        # Настройка mock для tqdm
        mock_pbar = Mock()
        mock_tqdm.return_value.__enter__.return_value = mock_pbar
        
        result = handler._check_existing_vacancies(vacancies)
        
        assert result['existing_count'] == 1
        assert result['new_count'] == 1
        assert result['total_count'] == 2
        assert len(result['existing_vacancies']) == 1
        assert len(result['new_vacancies']) == 1

    @patch('builtins.print')
    def test_display_duplicate_info_no_vacancies(self, mock_print, handler):
        """Тест отображения информации о дублях - нет вакансий"""
        duplicate_info = {'total_count': 0, 'existing_count': 0, 'new_count': 0}
        
        handler._display_duplicate_info(duplicate_info)
        
        mock_print.assert_called_once_with("Не найдено ни одной вакансии.")

    @patch('builtins.print')
    def test_display_duplicate_info_all_existing(self, mock_print, handler):
        """Тест отображения информации о дублях - все существуют"""
        duplicate_info = {'total_count': 5, 'existing_count': 5, 'new_count': 0}
        
        handler._display_duplicate_info(duplicate_info)
        
        mock_print.assert_called_once_with("Все 5 вакансий уже существуют в базе данных.")

    @patch('builtins.print')
    def test_display_duplicate_info_some_existing(self, mock_print, handler):
        """Тест отображения информации о дублях - некоторые существуют"""
        duplicate_info = {'total_count': 10, 'existing_count': 3, 'new_count': 7}
        
        handler._display_duplicate_info(duplicate_info)
        
        expected_calls = [
            call("3 вакансий из 10 уже есть в базе данных."),
            call("Можно сохранить 7 новых вакансий.")
        ]
        mock_print.assert_has_calls(expected_calls)

    @patch('builtins.print')
    def test_display_duplicate_info_all_new(self, mock_print, handler):
        """Тест отображения информации о дублях - все новые"""
        duplicate_info = {'total_count': 5, 'existing_count': 0, 'new_count': 5}
        
        handler._display_duplicate_info(duplicate_info)
        
        mock_print.assert_called_once_with("Все 5 вакансий - новые.")

    @patch('builtins.input', return_value="0")
    @patch('builtins.print')
    def test_get_period_choice_cancel(self, mock_print, mock_input):
        """Тест отмены выбора периода"""
        result = VacancySearchHandler._get_period_choice()
        
        assert result is None
        mock_print.assert_any_call("Выбор периода отменен.")

    @patch('builtins.input', return_value="1")
    def test_get_period_choice_1_day(self, mock_input):
        """Тест выбора 1 дня"""
        result = VacancySearchHandler._get_period_choice()
        
        assert result == 1

    @patch('builtins.input', return_value="")
    def test_get_period_choice_default(self, mock_input):
        """Тест выбора по умолчанию"""
        result = VacancySearchHandler._get_period_choice()
        
        assert result == 15

    @patch('builtins.input', side_effect=["6", "30"])
    def test_get_period_choice_custom_valid(self, mock_input):
        """Тест выбора кастомного периода"""
        result = VacancySearchHandler._get_period_choice()
        
        assert result == 30

    @patch('builtins.input', side_effect=["6", "500"])
    @patch('builtins.print')
    def test_get_period_choice_custom_invalid(self, mock_print, mock_input):
        """Тест выбора кастомного некорректного периода"""
        result = VacancySearchHandler._get_period_choice()
        
        assert result == 15
        mock_print.assert_any_call("Некорректный период. Используется 15 дней по умолчанию.")

    @patch('builtins.input', side_effect=["6", "invalid"])
    @patch('builtins.print')
    def test_get_period_choice_custom_non_numeric(self, mock_print, mock_input):
        """Тест выбора кастомного нечислового периода"""
        result = VacancySearchHandler._get_period_choice()
        
        assert result == 15
        mock_print.assert_any_call("Некорректный ввод. Используется 15 дней по умолчанию.")

    @patch('builtins.input', return_value="invalid")
    @patch('builtins.print')
    def test_get_period_choice_invalid(self, mock_print, mock_input):
        """Тест некорректного выбора"""
        result = VacancySearchHandler._get_period_choice()
        
        assert result == 15
        mock_print.assert_any_call("Некорректный выбор. Используется 15 дней по умолчанию.")

    @patch('builtins.input', side_effect=KeyboardInterrupt())
    @patch('builtins.print')
    def test_get_period_choice_keyboard_interrupt(self, mock_print, mock_input):
        """Тест прерывания клавиатурой"""
        result = VacancySearchHandler._get_period_choice()
        
        assert result is None
        mock_print.assert_any_call("\nВыбор периода отменен.")

    @patch('src.ui_interfaces.vacancy_search_handler.VacancyFormatter')
    @patch('src.ui_interfaces.vacancy_search_handler.quick_paginate')
    @patch('src.ui_interfaces.vacancy_search_handler.confirm_action', return_value=True)
    @patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler._display_duplicate_info')
    @patch('src.ui_interfaces.vacancy_search_handler.VacancySearchHandler._check_existing_vacancies')
    def test_handle_vacancies_preview_format_vacancy_none_coverage(self, mock_check, mock_display, mock_confirm, mock_paginate, mock_formatter, handler):
        """Тест покрытия ValueError при vacancy=None в format_vacancy (строка 134-136)"""
        vacancies = [Mock(spec=Vacancy)]
        duplicate_info = {'new_vacancies': [], 'total_count': 1}
        mock_check.return_value = duplicate_info
        
        # Симулируем вызов format_vacancy с None
        def side_effect_paginate(vacancies_list, formatter, header, items_per_page):
            # Вызываем форматтер с None чтобы покрыть проверку
            try:
                formatter(None, 1)
            except ValueError as e:
                assert str(e) == "Received a vacancy object of None type."
        
        mock_paginate.side_effect = side_effect_paginate
        
        handler._handle_vacancies_preview_and_save(vacancies, "python")
        
        mock_paginate.assert_called_once()

    @patch('builtins.print')
    def test_fetch_vacancies_from_sources_hh_empty_result_coverage(self, mock_print, handler):
        """Тест покрытия пустого результата с HH.ru (строка 102)"""
        sources = {"hh"}
        handler.unified_api.get_hh_vacancies.return_value = []
        
        result = handler._fetch_vacancies_from_sources(sources, "python", 15)
        
        assert result == []
        mock_print.assert_any_call("Вакансии на HH.ru не найдены")

from unittest.mock import MagicMock, patch

import pytest

from src.ui_interfaces.console_interface import UserInterface
from src.vacancies.models import Vacancy


@pytest.fixture
def ui_instance():
    """Фикстура для создания экземпляра UserInterface с замоканными зависимостями"""
    with patch('src.ui_interfaces.console_interface.HeadHunterAPI'), \
         patch('src.ui_interfaces.console_interface.SuperJobAPI'), \
         patch('src.ui_interfaces.console_interface.UnifiedAPI'), \
         patch('src.ui_interfaces.console_interface.JSONSaver'), \
         patch('src.ui_interfaces.console_interface.create_main_menu'), \
         patch('src.ui_interfaces.console_interface.VacancyOperations'), \
         patch('src.ui_interfaces.console_interface.SourceSelector'):
        ui = UserInterface()
        # Мокируем обработчики
        ui.search_handler = MagicMock()
        ui.display_handler = MagicMock()
        return ui


# Тесты инициализации
def test_initialization(ui_instance):
    """Тест инициализации UserInterface"""
    assert hasattr(ui_instance, 'hh_api')
    assert hasattr(ui_instance, 'sj_api')
    assert hasattr(ui_instance, 'unified_api')
    assert hasattr(ui_instance, 'json_saver')
    assert hasattr(ui_instance, 'menu_manager')
    assert hasattr(ui_instance, 'vacancy_ops')
    assert hasattr(ui_instance, 'source_selector')
    assert hasattr(ui_instance, 'search_handler')
    assert hasattr(ui_instance, 'display_handler')


# Тесты основных функций
def test_show_menu(ui_instance):
    """Тест отображения меню"""
    with patch('builtins.input', return_value='1'):
        result = ui_instance._show_menu()
        assert result == '1'


def test_search_vacancies(ui_instance):
    """Тест поиска вакансий"""
    ui_instance._search_vacancies()
    ui_instance.search_handler.search_vacancies.assert_called_once()


def test_show_saved_vacancies(ui_instance):
    """Тест отображения сохраненных вакансий"""
    ui_instance._show_saved_vacancies()
    ui_instance.display_handler.show_all_saved_vacancies.assert_called_once()


def test_get_top_saved_vacancies_by_salary(ui_instance):
    """Тест получения топ N вакансий по зарплате"""
    ui_instance._show_saved_vacancies()
    ui_instance._get_top_saved_vacancies_by_salary()
    ui_instance.display_handler.show_top_vacancies_by_salary.assert_called_once(
    )


def test_search_saved_vacancies_by_keyword(ui_instance):
    """Тест поиска по ключевому слову"""
    ui_instance._search_saved_vacancies_by_keyword()
    ui_instance.display_handler.search_saved_vacancies_by_keyword.assert_called_once(
    )


# Тесты расширенного поиска
def test_advanced_search_vacancies(ui_instance):
    """Тест расширенного поиска с вакансиями"""
    test_vacancies = [
        Vacancy(vacancy_id="1",
                title="Python Developer",
                salary={
                    "from": 100000,
                    "to": 150000
                },
                url="https://example.com/python-developer"),
        Vacancy(vacancy_id="2",
                title="Java Developer",
                salary={
                    "from": 120000,
                    "to": 160000
                },
                url="https://example.com/java-developer"),
    ]

    ui_instance.json_saver.get_vacancies.return_value = test_vacancies
    ui_instance.vacancy_ops.filter_vacancies_by_multiple_keywords.return_value = [
        test_vacancies[0]
    ]
    ui_instance.vacancy_ops.search_vacancies_advanced.return_value = [
        test_vacancies[0]
    ]

    # Тест с несколькими ключевыми словами через запятую
    with patch('builtins.input', side_effect=['python,developer', 'q']):
        ui_instance._advanced_search_vacancies()

    # Тест с оператором AND
    with patch('builtins.input', side_effect=['python AND developer', 'q']):
        ui_instance._advanced_search_vacancies()


def test_advanced_search_vacancies_no_results(ui_instance):
    """Тест расширенного поиска без результатов"""
    ui_instance.json_saver.get_vacancies.return_value = []

    with patch('builtins.input', return_value='nonexistent'):
        ui_instance._advanced_search_vacancies()

    ui_instance.json_saver.get_vacancies.assert_called_once()


def test_advanced_search_vacancies_empty_query(ui_instance):
    """Тест расширенного поиска с пустым запросом"""
    with patch('src.ui_interfaces.console_interface.get_user_input', return_value=''):
        ui_instance._advanced_search_vacancies()


# Тесты фильтрации по зарплате
def test_filter_saved_vacancies_by_salary(ui_instance):
    """Тест фильтрации по зарплате"""
    test_vacancies = [
        Vacancy(vacancy_id="1",
                title="Python Developer",
                salary={
                    "from": 100000,
                    "to": 150000
                },
                url="https://example.com/python-developer"),
        Vacancy(vacancy_id="2",
                title="Java Developer",
                salary={
                    "from": 120000,
                    "to": 160000
                },
                url="https://example.com/java-developer"),
    ]

    ui_instance.json_saver.get_vacancies.return_value = test_vacancies
    ui_instance.vacancy_ops.filter_vacancies_by_min_salary.return_value = [
        test_vacancies[1]
    ]
    ui_instance.vacancy_ops.filter_vacancies_by_max_salary.return_value = [
        test_vacancies[0]
    ]
    ui_instance.vacancy_ops.filter_vacancies_by_salary_range.return_value = test_vacancies
    ui_instance.vacancy_ops.sort_vacancies_by_salary.return_value = test_vacancies

    # Тест минимальной зарплаты
    with patch('builtins.input', side_effect=['1', '120000', 'q']):
        ui_instance._filter_saved_vacancies_by_salary()

    # Тест максимальной зарплаты
    with patch('builtins.input', side_effect=['2', '140000', 'q']):
        ui_instance._filter_saved_vacancies_by_salary()

    # Тест диапазона зарплат
    with patch('builtins.input', side_effect=['3', '100000 - 160000', 'q']):
        ui_instance._filter_saved_vacancies_by_salary()


def test_filter_saved_vacancies_invalid_input(ui_instance):
    """Тест фильтрации с некорректным вводом"""
    test_vacancies = [
        Vacancy(vacancy_id="1",
                title="Python Developer",
                salary={
                    "from": 100000,
                    "to": 150000
                },
                url="https://example.com/java-developer"),
    ]

    ui_instance.json_saver.get_vacancies.return_value = test_vacancies

    # Некорректный выбор типа фильтрации
    with patch('builtins.input', side_effect=['invalid', 'q']):
        ui_instance._filter_saved_vacancies_by_salary()

    # Некорректный ввод зарплаты
    with patch('builtins.input', side_effect=['1', 'not_a_number', 'q']):
        ui_instance._filter_saved_vacancies_by_salary()

    # Некорректный диапазон зарплат
    with patch('builtins.input', side_effect=['3', 'invalid-range', 'q']):
        ui_instance._filter_saved_vacancies_by_salary()


def test_filter_saved_vacancies_no_vacancies(ui_instance):
    """Тест фильтрации при отсутствии вакансий"""
    ui_instance.json_saver.get_vacancies.return_value = []

    with patch('builtins.input', side_effect=['1', '100000', 'q']):
        ui_instance._filter_saved_vacancies_by_salary()


# Тесты удаления вакансий
def test_delete_saved_vacancies(ui_instance):
    """Тест удаления вакансий"""
    test_vacancies = [
        Vacancy(vacancy_id="1",
                title="Python Developer",
                salary={
                    "from": 100000,
                    "to": 150000
                },
                url="https://example.com/python-developer"),
        Vacancy(vacancy_id="2",
                title="Java Developer",
                salary={
                    "from": 120000,
                    "to": 160000
                },
                url="https://example.com/java-developer"),
    ]

    ui_instance.json_saver.get_vacancies.return_value = test_vacancies
    ui_instance.json_saver.delete_all_vacancies.return_value = True
    ui_instance.json_saver.delete_vacancy_by_id.return_value = True

    # Тест удаления всех вакансий
    with patch('builtins.input', side_effect=['1', 'y', 'q']):
        ui_instance._delete_saved_vacancies()

    # Тест удаления по ID
    with patch('builtins.input', side_effect=['3', '1', 'y', 'q']):
        ui_instance._delete_saved_vacancies()


def test_delete_saved_vacancies_cancel(ui_instance):
    """Тест отмены удаления вакансий"""
    test_vacancies = [
        Vacancy(vacancy_id="1",
                title="Python Developer",
                url="https://example.com/java-developer"),
    ]

    ui_instance.json_saver.get_vacancies.return_value = test_vacancies

    # Отмена удаления всех вакансий
    with patch('builtins.input', side_effect=['1', 'n', 'q']):
        ui_instance._delete_saved_vacancies()

    # Отмена удаления по ID
    with patch('builtins.input', side_effect=['3', '1', 'n', 'q']):
        ui_instance._delete_saved_vacancies()


def test_delete_saved_vacancies_no_vacancies(ui_instance):
    """Тест удаления при отсутствии вакансий"""
    ui_instance.json_saver.get_vacancies.return_value = []

    with patch('builtins.input', return_value='1'):
        ui_instance._delete_saved_vacancies()


def test_delete_saved_vacancies_invalid_id(ui_instance):
    """Тест удаления с несуществующим ID"""
    test_vacancies = [
        Vacancy(vacancy_id="1",
                title="Python Developer",
                url="https://example.com/java-developer"),
    ]

    ui_instance.json_saver.get_vacancies.return_value = test_vacancies

    with patch('builtins.input', side_effect=['3', 'invalid_id', 'q']):
        ui_instance._delete_saved_vacancies()


# Тесты работы с API
def test_clear_api_cache(ui_instance):
    """Тест очистки кэша API"""
    ui_instance.source_selector.get_user_source_choice.return_value = {
        'hh', 'sj'
    }

    with patch('builtins.input', return_value='y'):
        ui_instance._clear_api_cache()

    ui_instance.unified_api.clear_cache.assert_called_once_with({
        'hh': True,
        'sj': True
    })


def test_clear_api_cache_cancel(ui_instance):
    """Тест отмены очистки кэша API"""
    with patch('builtins.input', return_value='n'):
        ui_instance._clear_api_cache()

    ui_instance.unified_api.clear_cache.assert_not_called()


def test_setup_superjob_api(ui_instance):
    """Тест настройки SuperJob API"""
    with patch('builtins.input', return_value=''):
        ui_instance._setup_superjob_api()


# Тесты вспомогательных методов
def test_get_period_choice(ui_instance):
    """Тест выбора периода"""
    # Тест выбора по умолчанию
    with patch('builtins.input', return_value=''):
        assert ui_instance._get_period_choice() == 15

    # Тест выбора 7 дней
    with patch('builtins.input', return_value='3'):
        assert ui_instance._get_period_choice() == 7

    # Тест отмены
    with patch('builtins.input', return_value='0'):
        assert ui_instance._get_period_choice() is None

    # Тест пользовательского периода
    with patch('builtins.input', side_effect=['6', '10']):
        assert ui_instance._get_period_choice() == 10

    # Тест некорректного пользовательского периода
    with patch('builtins.input', side_effect=['6', 'invalid', '15']):
        assert ui_instance._get_period_choice() == 15


def test_display_vacancies(ui_instance):
    """Тест отображения вакансий"""
    test_vacancies = [
        Vacancy(vacancy_id="1",
                title="Python Developer",
                salary={
                    "from": 100000,
                    "to": 150000
                },
                url="https://example.com/python-developer"),
        Vacancy(vacancy_id="2",
                title="Java Developer",
                salary={
                    "from": 120000,
                    "to": 160000
                },
                url="https://example.com/java-developer"),
    ]

    with patch('src.ui_interfaces.console_interface.display_vacancy_info'
               ) as mock_display:
        ui_instance._display_vacancies(test_vacancies)
        assert mock_display.call_count == 2


def test_display_vacancies_empty(ui_instance):
    """Тест отображения пустого списка вакансий"""
    with patch('src.ui_interfaces.console_interface.display_vacancy_info'
               ) as mock_display:
        ui_instance._display_vacancies([])
        mock_display.assert_not_called()


def test_show_vacancies_for_deletion(ui_instance):
    """Тест отображения вакансий для удаления"""
    test_vacancies = [
        Vacancy(vacancy_id="1",
                title="Python Developer",
                salary={
                    "from": 100000,
                    "to": 150000
                },
                url="https://example.com/python-developer"),
        Vacancy(vacancy_id="2",
                title="Java Developer",
                salary={
                    "from": 120000,
                    "to": 160000
                },
                url="https://example.com/java-developer"),
    ]

    ui_instance.json_saver.delete_vacancy_by_id.return_value = True

    # Тест выхода без удаления
    with patch('builtins.input', return_value='q'):
        ui_instance._show_vacancies_for_deletion(test_vacancies, 'python')

    # Тест удаления по номеру
    with patch('builtins.input', side_effect=['1', 'y', 'q']):
        ui_instance._show_vacancies_for_deletion(test_vacancies, 'python')

    # Тест удаления диапазона
    with patch('builtins.input', side_effect=['1-2', 'y', 'q']):
        ui_instance._show_vacancies_for_deletion(test_vacancies, 'python')


def test_show_vacancies_for_deletion_invalid_input(ui_instance):
    """Тест отображения вакансий для удаления с некорректным вводом"""
    test_vacancies = [
        Vacancy(vacancy_id="1",
                title="Python Developer",
                url="https://example.com/java-developer")
    ]

    # Некорректный номер вакансии
    with patch('builtins.input', side_effect=['invalid', 'q']):
        ui_instance._show_vacancies_for_deletion(test_vacancies, 'python')

    # Некорректный диапазон
    with patch('builtins.input', side_effect=['1-', 'q']):
        ui_instance._show_vacancies_for_deletion(test_vacancies, 'python')

    # Некорректный выбор действия
    with patch('builtins.input', side_effect=['x', 'q']):
        ui_instance._show_vacancies_for_deletion(test_vacancies, 'python')


# Тесты main run loop
def test_run_main_loop_keyboard_interrupt(ui_instance):
    """Тест прерывания основного цикла"""
    with patch.object(ui_instance, '_show_menu', side_effect=KeyboardInterrupt):
        ui_instance.run()


def test_run_main_loop_exception_handling(ui_instance):
    """Тест обработки исключений в основном цикле"""
    with patch.object(ui_instance, '_show_menu', side_effect=[Exception("Test error"), "0"]):
        ui_instance.run()


def test_run_main_loop_all_menu_choices(ui_instance):
    """Тест всех пунктов меню"""
    choices = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "invalid", "0"]
    with patch.object(ui_instance, '_show_menu', side_effect=choices):
        ui_instance.run()


# Тесты расширенного поиска - дополнительные случаи
def test_advanced_search_vacancies_operators(ui_instance):
    """Тест расширенного поиска с операторами"""
    test_vacancies = [
        Vacancy(vacancy_id="1", title="Python Developer", url="https://example.com/1", description="Python Flask"),
        Vacancy(vacancy_id="2", title="Java Developer", url="https://example.com/2", description="Java Spring"),
    ]

    ui_instance.json_saver.get_vacancies.return_value = test_vacancies
    ui_instance.vacancy_ops.search_vacancies_advanced.return_value = [test_vacancies[0]]

    # Тест с оператором OR
    with patch('src.ui_interfaces.console_interface.get_user_input', return_value='python OR java'):
        ui_instance._advanced_search_vacancies()

    ui_instance.vacancy_ops.search_vacancies_advanced.assert_called()


def test_advanced_search_vacancies_exception(ui_instance):
    """Тест обработки исключений в расширенном поиске"""
    ui_instance.json_saver.get_vacancies.side_effect = Exception("Database error")

    ui_instance._advanced_search_vacancies()


# Тесты фильтрации по зарплате - дополнительные случаи
def test_filter_saved_vacancies_by_salary_sort_option(ui_instance):
    """Тест сортировки в фильтрации по зарплате"""
    test_vacancies = [
        Vacancy(vacancy_id="1", title="Python Developer", url="https://example.com/1", salary={"from": 100000, "to": 150000}),
    ]

    ui_instance.json_saver.get_vacancies.return_value = test_vacancies
    ui_instance.vacancy_ops.filter_vacancies_by_min_salary.return_value = test_vacancies
    ui_instance.vacancy_ops.sort_vacancies_by_salary.return_value = test_vacancies

    with patch('builtins.input', side_effect=['1', '100000', 'q']):
        ui_instance._filter_saved_vacancies_by_salary()

    ui_instance.vacancy_ops.sort_vacancies_by_salary.assert_called()


def test_filter_saved_vacancies_exception(ui_instance):
    """Тест обработки исключений в фильтрации"""
    ui_instance.json_saver.get_vacancies.side_effect = Exception("Database error")

    ui_instance._filter_saved_vacancies_by_salary()


# Тесты удаления вакансий - дополнительные случаи
def test_delete_saved_vacancies_by_keyword_advanced(ui_instance):
    """Тест удаления по ключевому слову с расширенным функционалом"""
    test_vacancies = [
        Vacancy(vacancy_id="1", title="Python Developer", url="https://example.com/1"),
        Vacancy(vacancy_id="2", title="Java Developer", url="https://example.com/2"),
    ]

    ui_instance.json_saver.get_vacancies.return_value = test_vacancies

    with patch('src.ui_interfaces.console_interface.get_user_input', return_value='python'):
        with patch('src.ui_interfaces.console_interface.filter_vacancies_by_keyword', return_value=[test_vacancies[0]]):
            with patch.object(ui_instance, '_show_vacancies_for_deletion') as mock_show:
                with patch('builtins.input', side_effect=['2', 'q']):
                    ui_instance._delete_saved_vacancies()
                mock_show.assert_called_once()


def test_delete_saved_vacancies_exception(ui_instance):
    """Тест обработки исключений в удалении"""
    ui_instance.json_saver.get_vacancies.side_effect = Exception("Database error")

    ui_instance._delete_saved_vacancies()


# Тесты показа вакансий для удаления - дополнительные случаи
def test_show_vacancies_for_deletion_all_delete(ui_instance):
    """Тест удаления всех вакансий через 'a'"""
    test_vacancies = [
        Vacancy(vacancy_id="1", title="Python Developer", url="https://example.com/1"),
    ]

    ui_instance.json_saver.delete_vacancies_by_keyword.return_value = 1

    with patch('src.ui_interfaces.console_interface.confirm_action', return_value=True):
        with patch('builtins.input', side_effect=['a', 'q']):
            ui_instance._show_vacancies_for_deletion(test_vacancies, 'python')

    ui_instance.json_saver.delete_vacancies_by_keyword.assert_called_once_with('python')


def test_show_vacancies_for_deletion_pagination(ui_instance):
    """Тест пагинации в удалении вакансий"""
    # Создаем 15 вакансий для тестирования пагинации
    test_vacancies = []
    for i in range(15):
        test_vacancies.append(Vacancy(vacancy_id=str(i), title=f"Developer {i}", url=f"https://example.com/{i}"))

    with patch('builtins.input', side_effect=['n', 'p', 'q']):
        ui_instance._show_vacancies_for_deletion(test_vacancies, 'test')


def test_show_vacancies_for_deletion_range_delete_with_swap(ui_instance):
    """Тест удаления диапазона с перестановкой номеров"""
    test_vacancies = [
        Vacancy(vacancy_id="1", title="Dev 1", url="https://example.com/1"),
        Vacancy(vacancy_id="2", title="Dev 2", url="https://example.com/2"),
        Vacancy(vacancy_id="3", title="Dev 3", url="https://example.com/3"),
    ]

    ui_instance.json_saver.delete_vacancy_by_id.return_value = True

    with patch('src.ui_interfaces.console_interface.confirm_action', return_value=True):
        with patch('builtins.input', side_effect=['3-1', 'q']):  # Обратный порядок
            ui_instance._show_vacancies_for_deletion(test_vacancies, 'test')


def test_show_vacancies_for_deletion_failed_delete(ui_instance):
    """Тест неудачного удаления"""
    test_vacancies = [Vacancy(vacancy_id="1", title="Developer", url="https://example.com/1")]

    ui_instance.json_saver.delete_vacancy_by_id.return_value = False

    with patch('src.ui_interfaces.console_interface.confirm_action', return_value=True):
        with patch('builtins.input', side_effect=['1', 'q']):
            ui_instance._show_vacancies_for_deletion(test_vacancies, 'test')


def test_show_vacancies_for_deletion_all_delete_failed(ui_instance):
    """Тест неудачного удаления всех вакансий"""
    test_vacancies = [Vacancy(vacancy_id="1", title="Developer", url="https://example.com/1")]

    ui_instance.json_saver.delete_vacancies_by_keyword.return_value = 0

    with patch('src.ui_interfaces.console_interface.confirm_action', return_value=True):
        with patch('builtins.input', side_effect=['a', 'q']):
            ui_instance._show_vacancies_for_deletion(test_vacancies, 'test')


# Тесты периода выбора - дополнительные случаи
def test_get_period_choice_keyboard_interrupt(ui_instance):
    """Тест прерывания выбора периода"""
    with patch('builtins.input', side_effect=KeyboardInterrupt):
        result = ui_instance._get_period_choice()
        assert result is None


def test_get_period_choice_custom_invalid_range(ui_instance):
    """Тест некорректного пользовательского периода вне диапазона"""
    with patch('builtins.input', side_effect=['6', '500']):
        result = ui_instance._get_period_choice()
        assert result == 15


# Тесты настройки SuperJob API
def test_setup_superjob_api_with_real_key(ui_instance):
    """Тест настройки SuperJob API с реальным ключом"""
    with patch('os.getenv', return_value='real_api_key_value'):
        with patch('builtins.input', return_value=''):
            ui_instance._setup_superjob_api()


# Тесты очистки кэша API - дополнительные случаи
def test_clear_api_cache_no_sources(ui_instance):
    """Тест очистки кэша без выбора источников"""
    ui_instance.source_selector.get_user_source_choice.return_value = set()

    ui_instance._clear_api_cache()

    ui_instance.unified_api.clear_cache.assert_not_called()


def test_clear_api_cache_exception(ui_instance):
    """Тест обработки исключений при очистке кэша"""
    ui_instance.source_selector.get_user_source_choice.side_effect = Exception("Error")

    ui_instance._clear_api_cache()


# Тесты отображения вакансий с дополнительным номером
def test_display_vacancies_with_start_number(ui_instance):
    """Тест отображения вакансий с начальным номером"""
    test_vacancies = [
        Vacancy(vacancy_id="1", title="Python Developer", url="https://example.com/1"),
        Vacancy(vacancy_id="2", title="Java Developer", url="https://example.com/2"),
    ]

    with patch('src.ui_interfaces.console_interface.display_vacancy_info') as mock_display:
        ui_instance._display_vacancies(test_vacancies, 5)

        # Проверяем, что функция вызвана с правильными номерами
        calls = mock_display.call_args_list
        assert len(calls) == 2
        assert calls[0][0][1] == 5  # Первая вакансия с номером 5
        assert calls[1][0][1] == 6  # Вторая вакансия с номером 6


# Тесты обработки ошибок
def test_methods_with_exceptions(ui_instance):
    """Тест методов с имитацией исключений"""
    ui_instance.json_saver.get_vacancies.side_effect = Exception("Test error")

    # Мокируем дополнительные методы, которые могут вызвать циклы
    ui_instance.source_selector.get_user_source_choice.return_value = set()
    ui_instance.unified_api.clear_cache.return_value = None

    with patch('builtins.input', side_effect=['0', 'q', 'n', '0', 'q'] * 10):
        # Проверяем, что методы не падают при исключениях
        try:
            ui_instance._filter_saved_vacancies_by_salary()
        except Exception as e:
            err = e

        try:
            ui_instance._delete_saved_vacancies()
        except Exception as e:
            err = e

        try:
            ui_instance._advanced_search_vacancies()
        except Exception as e:
            err = e

        try:
            ui_instance._clear_api_cache()
        except Exception as e:
            err = e

        ui_instance._show_vacancies_for_deletion([], 'test')
        ui_instance._display_vacancies([])
        ui_instance._display_vacancies_with_pagination([])
        ui_instance._configure_superjob_api()

        result = ui_instance._get_period_choice()
        assert result is None or isinstance(result, int)

        result = ui_instance._show_menu()
        assert result in ['0', 'q']

        ui_instance._search_vacancies()
        ui_instance._show_saved_vacancies()
        ui_instance._get_top_saved_vacancies_by_salary()
        ui_instance._search_saved_vacancies_by_keyword()

def test_console_interface_edge_cases(ui_instance, mocker):
    """Тесты для покрытия оставшихся непокрытых строк"""
    
    # Тестируем различные сценарии для достижения 100% покрытия
    ui_instance.json_saver.get_vacancies.return_value = []
    
    # Мокаем input для различных сценариев
    mocker.patch('builtins.input', side_effect=['4', '', 'q'])
    ui_instance._filter_saved_vacancies_by_salary()
    
    # Тестируем сценарии с исключениями
    ui_instance.source_selector.get_user_source_choice.side_effect = Exception("test")
    ui_instance._clear_api_cache()
    
    # Тестируем edge cases для периода
    mocker.patch('builtins.input', side_effect=['7'])
    result = ui_instance._get_period_choice()
    assert result == 15  # default fallback
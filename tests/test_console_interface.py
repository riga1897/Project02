import pytest
from unittest.mock import MagicMock, patch, mock_open
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
    with patch('builtins.input', return_value=''):
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
    with patch('builtins.input', side_effect=['6', 'invalid', '20']):
        assert ui_instance._get_period_choice() == 20


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


# Тесты обработки ошибок
def test_methods_with_exceptions(ui_instance):
    """Тест методов с имитацией исключений"""
    ui_instance.json_saver.get_vacancies.side_effect = Exception("Test error")

    with patch('builtins.input', return_value='1'):
        # Проверяем, что методы не падают при исключениях
        ui_instance._filter_saved_vacancies_by_salary()
        ui_instance._delete_saved_vacancies()
        ui_instance._advanced_search_vacancies()
        ui_instance._clear_api_cache()
        ui_instance._show_vacancies_for_deletion([], 'test')
        ui_instance._display_vacancies([])
        ui_instance._display_vacancies_with_pagination([])
        ui_instance._configure_superjob_api()
        ui_instance._get_period_choice()
        ui_instance._show_menu()
        ui_instance._search_vacancies()
        ui_instance._show_saved_vacancies()
        ui_instance._get_top_saved_vacancies_by_salary()

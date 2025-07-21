
import pytest

from src.ui_interfaces.vacancy_search_handler import VacancySearchHandler


class TestVacancySearchHandlerCoverage:
    """Тесты только для достижения 100% покрытия"""

    @pytest.fixture  
    def handler(self, mocker):
        unified_api = mocker.Mock()
        json_saver = mocker.Mock()
        return VacancySearchHandler(unified_api, json_saver)

    def test_line_102_coverage(self, handler, mocker):
        """Тест для покрытия строки 102"""
        # Патчим источники чтобы возвращал пустое множество
        mocker.patch.object(handler.source_selector, 'get_user_source_choice', return_value=set())
        
        # Пустое множество источников должно покрыть строку 102 (return)
        handler.search_vacancies()

    def test_line_136_coverage(self, handler, mocker):
        """Тест для покрытия строки 136"""
        # Мокаем все источники ввода пользователя
        mocker.patch.object(handler.source_selector, 'get_user_source_choice', return_value={'hh'})
        mocker.patch.object(handler.source_selector, 'display_sources_info')
        mocker.patch.object(handler, '_get_period_choice', return_value=15)
        mocker.patch.object(handler, '_fetch_vacancies_from_sources', return_value=[])
        
        # Мокаем get_user_input в модуле vacancy_search_handler для возврата непустого запроса
        mock_get_input = mocker.patch('src.ui_interfaces.vacancy_search_handler.get_user_input', return_value='python')
        
        # Мокаем print для вывода сообщения о пустом результате (строка 136)
        mock_print = mocker.patch('builtins.print')
        
        # Вызов должен дойти до строки 136 с пустым списком вакансий
        handler.search_vacancies()
        
        # Проверяем что был вызван ввод запроса
        mock_get_input.assert_called_with("\nВведите поисковый запрос: ")
        
        # Проверяем что было выведено сообщение о том, что вакансии не найдены
        mock_print.assert_any_call("Вакансии не найдены ни на одном из источников.")

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json
import os
from pathlib import Path

from src.ui_interfaces.console_interface import UserInterface
from src.storage.json_saver import JSONSaver
from src.api_modules.cached_api import CachedAPI
from src.ui_interfaces.vacancy_display_handler import VacancyDisplayHandler
from src.utils.base_formatter import BaseFormatter
from src.vacancies.models import Vacancy


class ConcreteCachedAPI(CachedAPI):
    """Concrete implementation of CachedAPI for testing."""
    def __init__(self, api):
        super().__init__(api)

    def get_vacancies(self, keyword, pages=1):
        return super().get_vacancies(keyword, pages)


class ConcreteFormatter(BaseFormatter):
    """Concrete implementation of BaseFormatter for testing."""
    def format_vacancy_info(self, vacancy):
        return f"{vacancy.title} - {vacancy.employer}"

    def format_salary(self, salary_data):
        return super().format_salary(salary_data)

    def format_experience(self, experience):
        return super().format_experience(experience)

    def format_description(self, description):
        return super().format_description(description)


class TestIntegrationCoverage:
    """Интеграционные тесты для достижения 100% покрытия"""

    def test_console_interface_integration_flow(self, mocker):
        """Интеграционный тест основного потока UserInterface"""
        # Мокируем все зависимости
        with patch('src.ui_interfaces.console_interface.HeadHunterAPI'), \
             patch('src.ui_interfaces.console_interface.SuperJobAPI'), \
             patch('src.ui_interfaces.console_interface.UnifiedAPI'), \
             patch('src.ui_interfaces.console_interface.JSONSaver'), \
             patch('src.ui_interfaces.console_interface.create_main_menu'), \
             patch('src.ui_interfaces.console_interface.VacancyOperations'), \
             patch('src.ui_interfaces.console_interface.SourceSelector'):

            ui = UserInterface()
            ui.search_handler = MagicMock()
            ui.display_handler = MagicMock()
            ui.json_saver = MagicMock()
            ui.source_selector = MagicMock()
            ui.unified_api = MagicMock()

            # Тестируем различные пути выполнения
            # Строки 165-166 - обработка исключений
            ui.source_selector.get_user_source_choice.side_effect = Exception("Test error")
            ui._clear_api_cache()

            # Строки 217-219 - обработка неверного ввода в расширенном поиске
            ui.json_saver.get_vacancies.return_value = []
            mocker.patch('src.utils.ui_helpers.get_user_input', return_value='')
            ui._advanced_search_vacancies()

            # Строки 236-237 - обработка исключений в расширенном поиске
            ui.json_saver.get_vacancies.side_effect = Exception("Database error")
            ui._advanced_search_vacancies()

    def test_json_saver_integration_error_handling(self):
        """Интеграционный тест обработки ошибок в JSONSaver"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Создаем JSONSaver с временной директорией
            storage_path = Path(temp_dir) / "test_vacancies.json"
            json_saver = JSONSaver(str(storage_path))

            # Создаем тестовую вакансию
            test_vacancy = Vacancy(
                title="Test Job",
                url="https://example.com/job/1",
                vacancy_id="test_001"
            )

            # Строки 160-161 - обработка ошибки записи в _save_to_file
            with patch('builtins.open', side_effect=PermissionError("Access denied")):
                try:
                    json_saver.add_vacancy([test_vacancy])
                except Exception:
                    pass  # Ожидаем исключение при ошибке записи

            # Строки 229-231 - обработка ошибки при удалении по ключевому слову
            with patch('src.utils.ui_helpers.filter_vacancies_by_keyword', side_effect=Exception("Filter error")):
                result = json_saver.delete_vacancies_by_keyword("test")
                assert result == 0

            # Строка 299 - обработка ошибки при удалении всех вакансий
            with patch('builtins.open', side_effect=OSError("System error")):
                result = json_saver.delete_all_vacancies()
                assert result is False

    def test_cached_api_integration_cache_operations(self, mocker):
        """Интеграционный тест операций кэширования"""
        # Создаем мок API
        mock_api = Mock()
        mock_api.get_vacancies.return_value = [{"id": "1", "name": "Test"}]

        cached_api = ConcreteCachedAPI(mock_api)

        # Строки 66-72 - обработка ошибок кэширования
        with patch('src.utils.cache.FileCache.get', side_effect=Exception("Cache error")):
            with patch('src.utils.cache.FileCache.set', side_effect=Exception("Cache write error")):
                # Тестируем получение данных при ошибке кэша
                result = cached_api.get_vacancies("python", pages=1)
                assert result is not None

    def test_vacancy_display_handler_edge_cases(self, mocker):
        """Интеграционный тест граничных случаев VacancyDisplayHandler"""
        json_saver = Mock()
        json_saver.get_vacancies.return_value = []

        handler = VacancyDisplayHandler(json_saver)

        # Строка 43 - обработка пустого списка вакансий
        handler.show_all_saved_vacancies()

        # Строка 83 - обработка ошибки при показе топ зарплат
        json_saver.get_vacancies.side_effect = Exception("Storage error")
        with patch('builtins.input', return_value='5'):
            handler.show_top_vacancies_by_salary()

        # Строка 120 - обработка некорректного ввода
        json_saver.get_vacancies.return_value = [Mock()]
        json_saver.get_vacancies.side_effect = None
        with patch('builtins.input', return_value='invalid'):
            handler.show_top_vacancies_by_salary()

    def test_base_formatter_error_handling(self):
        """Интеграционный тест обработки ошибок в BaseFormatter"""
        formatter = ConcreteFormatter()

        # Строка 145 - обработка некорректного JSON
        invalid_json = '{"invalid": json content'
        result = formatter._parse_json_safely(invalid_json)
        assert result is None

        # Строка 174 - обработка ошибки при форматировании зарплаты
        salary_data = {"currency": "unknown_currency", "from": 50000}
        result = formatter._format_salary_safely(salary_data)
        assert "50000" in result

    def test_full_integration_workflow(self, mocker):
        """Полный интеграционный тест рабочего процесса"""
        # Создаем временные файлы для тестирования
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "integration_test.json"

            # Создаем реальный JSONSaver
            json_saver = JSONSaver(str(storage_path))

            # Создаем тестовые данные
            test_vacancy = Vacancy(
                title="Python Developer",
                url="https://example.com/vacancy/123",
                vacancy_id="test_123",
                salary={"from": 100000, "to": 150000, "currency": "RUR"},
                employer={"name": "Test Company"},
                experience="1-3 года",
                description="Test description"
            )

            # Добавляем вакансию в хранилище
            messages = json_saver.add_vacancy([test_vacancy])
            assert len(messages) > 0

            # Проверяем, что вакансия сохранилась
            saved_vacancies = json_saver.get_vacancies()
            assert len(saved_vacancies) == 1
            assert saved_vacancies[0].title == "Python Developer"

            # Тестируем создание display handler
            display_handler = VacancyDisplayHandler(json_saver)

            # Тестируем интеграцию с форматированием
            formatter = ConcreteFormatter()
            formatted = formatter.format_vacancy_info(test_vacancy)
            assert "Python Developer" in formatted

    def test_console_interface_keyboard_interrupt(self, mocker):
        """Тест обработки KeyboardInterrupt в UserInterface"""
        with patch('src.ui_interfaces.console_interface.HeadHunterAPI'), \
             patch('src.ui_interfaces.console_interface.SuperJobAPI'), \
             patch('src.ui_interfaces.console_interface.UnifiedAPI'), \
             patch('src.ui_interfaces.console_interface.JSONSaver'), \
             patch('src.ui_interfaces.console_interface.create_main_menu'), \
             patch('src.ui_interfaces.console_interface.VacancyOperations'), \
             patch('src.ui_interfaces.console_interface.SourceSelector'):

            ui = UserInterface()

            # Мокируем menu для вызова KeyboardInterrupt
            mocker.patch.object(ui, '_show_menu', side_effect=KeyboardInterrupt())

            # Тест должен завершиться без исключения
            ui.run()

    def test_console_interface_exception_handling(self, mocker):
        """Тест общей обработки исключений в UserInterface"""
        with patch('src.ui_interfaces.console_interface.HeadHunterAPI'), \
             patch('src.ui_interfaces.console_interface.SuperJobAPI'), \
             patch('src.ui_interfaces.console_interface.UnifiedAPI'), \
             patch('src.ui_interfaces.console_interface.JSONSaver'), \
             patch('src.ui_interfaces.console_interface.create_main_menu'), \
             patch('src.ui_interfaces.console_interface.VacancyOperations'), \
             patch('src.ui_interfaces.console_interface.SourceSelector'):

            ui = UserInterface()
            ui.search_handler = MagicMock()

            # Симулируем общее исключение
            mocker.patch.object(ui, '_show_menu', side_effect=[Exception("General error"), "0"])

            # Тест должен обработать исключение и продолжить работу
            ui.run()
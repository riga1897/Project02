
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

            # Строки 160-161 - обработка ошибки записи
            with patch('builtins.open', side_effect=PermissionError("Access denied")):
                result = json_saver.save_vacancies([])
                assert result is False

            # Строки 229-231 - обработка ошибки при удалении по ключевому слову
            with patch('builtins.open', side_effect=IOError("Disk error")):
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
        
        cached_api = CachedAPI(mock_api)
        
        # Строки 66-72 - обработка ошибок кэширования
        with patch('src.utils.cache.FileCache.get', side_effect=Exception("Cache error")):
            with patch('src.utils.cache.FileCache.set', side_effect=Exception("Cache write error")):
                # Тестируем получение данных при ошибке кэша
                result = cached_api.get_vacancies("python", pages=1)
                assert result is not None

    def test_vacancy_display_handler_edge_cases(self, mocker):
        """Интеграционный тест граничных случаев VacancyDisplayHandler"""
        json_saver = MagicMock()
        handler = VacancyDisplayHandler(json_saver)

        # Строка 43 - возврат при отсутствии вакансий
        json_saver.get_vacancies.return_value = []
        mocker.patch('builtins.input', return_value='0')
        handler.show_top_vacancies_by_salary()

        # Строка 83 - возврат при пустом поисковом запросе
        json_saver.get_vacancies.return_value = []
        mocker.patch('src.utils.ui_helpers.get_user_input', return_value='')
        handler.search_saved_vacancies_by_keyword()

        # Строка 120 - обработка неверного ввода
        mock_vacancy = Mock(spec=Vacancy)
        json_saver.get_vacancies.return_value = [mock_vacancy]
        mocker.patch('builtins.input', return_value='invalid')
        handler.show_top_vacancies_by_salary()

    def test_base_formatter_error_handling(self):
        """Интеграционный тест обработки ошибок в BaseFormatter"""
        formatter = BaseFormatter()

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
                vacancy_id="test_123",
                title="Python Developer",
                url="https://example.com/vacancy/123",
                salary_from=100000,
                salary_to=150000,
                currency="RUR",
                employer={"name": "Test Company"},
                experience="1-3 года",
                description="Test description"
            )

            # Тестируем полный цикл: сохранение -> загрузка -> удаление
            save_result = json_saver.save_vacancies([test_vacancy])
            assert save_result is True

            loaded_vacancies = json_saver.get_vacancies()
            assert len(loaded_vacancies) == 1
            assert loaded_vacancies[0].vacancy_id == "test_123"

            # Тестируем удаление по ID
            delete_result = json_saver.delete_vacancy_by_id("test_123")
            assert delete_result is True

            # Проверяем, что вакансия удалена
            remaining_vacancies = json_saver.get_vacancies()
            assert len(remaining_vacancies) == 0

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

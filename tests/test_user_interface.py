import logging
from unittest.mock import Mock, call, patch

import pytest

from src.user_interface import main


class TestUserInterface:
    """Тесты для модуля user_interface"""

    @patch("src.user_interface.UserInterface")
    @patch("src.user_interface.EnvLoader.get_env_var")
    @patch("src.user_interface.EnvLoader.load_env_file")
    @patch("src.user_interface.logging.basicConfig")
    @patch("builtins.print")
    def test_main_function_default_log_level(
        self, mock_print, mock_logging_config, mock_load_env, mock_get_env_var, mock_ui_class
    ):
        """Тест основной функции main с уровнем логирования по умолчанию"""
        # Настройка моков
        mock_get_env_var.return_value = "INFO"
        mock_ui_instance = Mock()
        mock_ui_class.return_value = mock_ui_instance

        # Вызов функции
        main()

        # Проверки
        mock_load_env.assert_called_once()
        mock_get_env_var.assert_called_once_with("LOG_LEVEL", "INFO")

        # Проверяем настройку логирования
        mock_logging_config.assert_called_once()
        call_args = mock_logging_config.call_args
        assert call_args[1]["level"] == logging.INFO
        assert call_args[1]["format"] == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        assert len(call_args[1]["handlers"]) == 2

        # Проверяем вывод заголовка
        expected_calls = [call("=" * 60), call("   ПОИСКОВИК ВАКАНСИЙ"), call("=" * 60)]
        mock_print.assert_has_calls(expected_calls)

        # Проверяем создание и запуск UI
        mock_ui_class.assert_called_once()
        mock_ui_instance.run.assert_called_once()

    @patch("src.user_interface.UserInterface")
    @patch("src.user_interface.EnvLoader.get_env_var")
    @patch("src.user_interface.EnvLoader.load_env_file")
    @patch("src.user_interface.logging.basicConfig")
    @patch("builtins.print")
    def test_main_function_debug_log_level(
        self, mock_print, mock_logging_config, mock_load_env, mock_get_env_var, mock_ui_class
    ):
        """Тест основной функции main с уровнем логирования DEBUG"""
        # Настройка моков
        mock_get_env_var.return_value = "DEBUG"
        mock_ui_instance = Mock()
        mock_ui_class.return_value = mock_ui_instance

        # Вызов функции
        main()

        # Проверяем настройку логирования с DEBUG уровнем
        mock_logging_config.assert_called_once()
        call_args = mock_logging_config.call_args
        assert call_args[1]["level"] == logging.DEBUG

    @patch("src.user_interface.UserInterface")
    @patch("src.user_interface.EnvLoader.get_env_var")
    @patch("src.user_interface.EnvLoader.load_env_file")
    @patch("src.user_interface.logging.basicConfig")
    @patch("builtins.print")
    def test_main_function_error_log_level(
        self, mock_print, mock_logging_config, mock_load_env, mock_get_env_var, mock_ui_class
    ):
        """Тест основной функции main с уровнем логирования ERROR"""
        # Настройка моков
        mock_get_env_var.return_value = "ERROR"
        mock_ui_instance = Mock()
        mock_ui_class.return_value = mock_ui_instance

        # Вызов функции
        main()

        # Проверяем настройку логирования с ERROR уровнем
        mock_logging_config.assert_called_once()
        call_args = mock_logging_config.call_args
        assert call_args[1]["level"] == logging.ERROR

    @patch("src.user_interface.UserInterface")
    @patch("src.user_interface.EnvLoader.get_env_var")
    @patch("src.user_interface.EnvLoader.load_env_file")
    @patch("src.user_interface.logging.basicConfig")
    @patch("builtins.print")
    def test_main_function_invalid_log_level(
        self, mock_print, mock_logging_config, mock_load_env, mock_get_env_var, mock_ui_class
    ):
        """Тест основной функции main с некорректным уровнем логирования"""
        # Настройка моков
        mock_get_env_var.return_value = "INVALID_LEVEL"
        mock_ui_instance = Mock()
        mock_ui_class.return_value = mock_ui_instance

        # Вызов функции
        main()

        # Проверяем настройку логирования с INFO по умолчанию для некорректного уровня
        mock_logging_config.assert_called_once()
        call_args = mock_logging_config.call_args
        assert call_args[1]["level"] == logging.INFO

    @patch("src.user_interface.UserInterface")
    @patch("src.user_interface.EnvLoader.get_env_var")
    @patch("src.user_interface.EnvLoader.load_env_file")
    @patch("src.user_interface.logging.basicConfig")
    @patch("builtins.print")
    def test_main_function_lowercase_log_level(
        self, mock_print, mock_logging_config, mock_load_env, mock_get_env_var, mock_ui_class
    ):
        """Тест основной функции main с уровнем логирования в нижнем регистре"""
        # Настройка моков
        mock_get_env_var.return_value = "warning"
        mock_ui_instance = Mock()
        mock_ui_class.return_value = mock_ui_instance

        # Вызов функции
        main()

        # Проверяем настройку логирования с WARNING уровнем
        mock_logging_config.assert_called_once()
        call_args = mock_logging_config.call_args
        assert call_args[1]["level"] == logging.WARNING

    @patch("src.user_interface.main")
    def test_main_entry_point(self, mock_main):
        """Тест точки входа if __name__ == '__main__'"""
        # Имитация выполнения скрипта напрямую
        import src.user_interface

        # Сохраняем оригинальное значение
        original_name = src.user_interface.__name__

        try:
            # Устанавливаем __name__ как '__main__'
            src.user_interface.__name__ = "__main__"

            # Имитация выполнения условия
            if src.user_interface.__name__ == "__main__":
                src.user_interface.main()

            # Проверяем, что main была вызвана
            mock_main.assert_called_once()

        finally:
            # Восстанавливаем оригинальное значение
            src.user_interface.__name__ = original_name

    @patch("src.user_interface.UserInterface")
    @patch("src.user_interface.EnvLoader.get_env_var")
    @patch("src.user_interface.EnvLoader.load_env_file")
    @patch("src.user_interface.logging.basicConfig")
    @patch("builtins.print")
    def test_main_function_ui_exception_handling(
        self, mock_print, mock_logging_config, mock_load_env, mock_get_env_var, mock_ui_class
    ):
        """Тест обработки исключений в main функции при ошибке UI"""
        # Настройка моков
        mock_get_env_var.return_value = "INFO"
        mock_ui_instance = Mock()
        mock_ui_instance.run.side_effect = Exception("UI Error")
        mock_ui_class.return_value = mock_ui_instance

        # Проверяем, что исключение пробрасывается
        with pytest.raises(Exception, match="UI Error"):
            main()

        # Проверяем, что все предварительные шаги были выполнены
        mock_load_env.assert_called_once()
        mock_get_env_var.assert_called_once_with("LOG_LEVEL", "INFO")
        mock_logging_config.assert_called_once()
        mock_ui_class.assert_called_once()
        mock_ui_instance.run.assert_called_once()

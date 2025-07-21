from unittest.mock import patch

from src.ui_interfaces.source_selector import SourceSelector


class TestSourceSelector:
    """Тесты для класса SourceSelector"""

    def test_available_sources_constant(self):
        """Тест константы доступных источников"""
        expected = {"hh": "HH.ru", "sj": "SuperJob.ru"}
        assert SourceSelector.AVAILABLE_SOURCES == expected

    @patch("builtins.print")
    @patch("builtins.input", return_value="1")
    def test_get_user_source_choice_hh(self, mock_input, mock_print):
        """Тест выбора источника HH.ru"""
        result = SourceSelector.get_user_source_choice()

        assert result == {"hh"}
        mock_print.assert_called()

    @patch("builtins.print")
    @patch("builtins.input", return_value="2")
    def test_get_user_source_choice_sj(self, mock_input, mock_print):
        """Тест выбора источника SuperJob.ru"""
        result = SourceSelector.get_user_source_choice()

        assert result == {"sj"}
        mock_print.assert_called()

    @patch("builtins.print")
    @patch("builtins.input", return_value="3")
    def test_get_user_source_choice_both(self, mock_input, mock_print):
        """Тест выбора обоих источников"""
        result = SourceSelector.get_user_source_choice()

        assert result == {"hh", "sj"}
        mock_print.assert_called()

    @patch("builtins.print")
    @patch("builtins.input", return_value="0")
    def test_get_user_source_choice_cancel(self, mock_input, mock_print):
        """Тест отмены выбора источников"""
        result = SourceSelector.get_user_source_choice()

        assert result is None
        mock_print.assert_called()

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["invalid", "1"])
    def test_get_user_source_choice_invalid_then_valid(self, mock_input, mock_print):
        """Тест некорректного ввода, затем корректного"""
        result = SourceSelector.get_user_source_choice()

        assert result == {"hh"}
        mock_print.assert_called()

    def test_get_source_display_name_existing(self):
        """Тест получения имени существующего источника"""
        assert SourceSelector.get_source_display_name("hh") == "HH.ru"
        assert SourceSelector.get_source_display_name("sj") == "SuperJob.ru"

    def test_get_source_display_name_non_existing(self):
        """Тест получения имени несуществующего источника"""
        result = SourceSelector.get_source_display_name("unknown")
        assert result == "unknown"

    @patch("builtins.print")
    def test_display_sources_info_empty(self, mock_print):
        """Тест отображения информации о пустом множестве источников"""
        SourceSelector.display_sources_info(set())

        mock_print.assert_called_with("Источники не выбраны")

    @patch("builtins.print")
    def test_display_sources_info_single_source(self, mock_print):
        """Тест отображения информации об одном источнике"""
        SourceSelector.display_sources_info({"hh"})

        mock_print.assert_called_with("Выбранные источники: HH.ru")

    @patch("builtins.print")
    def test_display_sources_info_multiple_sources(self, mock_print):
        """Тест отображения информации о нескольких источниках"""
        SourceSelector.display_sources_info({"hh", "sj"})

        # Проверяем что print был вызван с строкой содержащей оба источника
        call_args = mock_print.call_args[0][0]
        assert "Выбранные источники:" in call_args
        assert "HH.ru" in call_args
        assert "SuperJob.ru" in call_args

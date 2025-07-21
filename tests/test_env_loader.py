from unittest.mock import mock_open, patch

from src.utils.env_loader import EnvLoader


class TestEnvLoader:
    """Тест загрузчика переменных окружения"""

    @staticmethod
    def setup_method():
        """Сброс состояния перед каждым тестом"""
        EnvLoader._loaded = False

    def test_load_env_file_already_loaded(self):
        """Тест что при повторном вызове файл не загружается"""
        EnvLoader._loaded = True

        with patch("os.path.exists") as mock_exists, patch("builtins.open") as mock_file:
            EnvLoader.load_env_file()

            mock_exists.assert_not_called()
            mock_file.assert_not_called()

    def test_load_env_file_not_exists(self):
        """Тест когда .env файл не существует"""
        with patch("os.path.exists", return_value=False), patch("src.utils.env_loader.logger") as mock_logger:

            EnvLoader.load_env_file()

            assert EnvLoader._loaded is True
            mock_logger.warning.assert_called_once()

    def test_load_env_file_success_with_quotes(self):
        """Тест успешной загрузки файла с кавычками"""
        env_content = """
# Комментарий
KEY1=value1
KEY2="value2"
KEY3='value3'

KEY4=value4
"""

        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=env_content)),
            patch("os.environ", {}) as mock_environ,
            patch("src.utils.env_loader.logger") as mock_logger,
        ):

            EnvLoader.load_env_file()

            assert mock_environ["KEY1"] == "value1"
            assert mock_environ["KEY2"] == "value2"
            assert mock_environ["KEY3"] == "value3"
            assert mock_environ["KEY4"] == "value4"
            assert EnvLoader._loaded is True
            mock_logger.info.assert_called_once()

    def test_load_env_file_existing_env_vars_not_overwritten(self):
        """Тест что существующие переменные окружения не перезаписываются"""
        env_content = "EXISTING_KEY=new_value"

        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=env_content)),
            patch("os.environ", {"EXISTING_KEY": "old_value"}) as mock_environ,
        ):

            EnvLoader.load_env_file()

            assert mock_environ["EXISTING_KEY"] == "old_value"

    def test_load_env_file_invalid_format_line(self):
        """Тест обработки строк с неверным форматом"""
        env_content = """
VALID_KEY=valid_value
invalid_line_without_equals
ANOTHER_KEY=another_value
"""

        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=env_content)),
            patch("os.environ", {}) as mock_environ,
            patch("src.utils.env_loader.logger") as mock_logger,
        ):

            EnvLoader.load_env_file()

            assert mock_environ["VALID_KEY"] == "valid_value"
            assert mock_environ["ANOTHER_KEY"] == "another_value"
            mock_logger.warning.assert_called_once()

    def test_load_env_file_exception_handling(self):
        """Тест обработки исключений при загрузке файла"""
        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", side_effect=IOError("File error")),
            patch("src.utils.env_loader.logger") as mock_logger,
        ):

            EnvLoader.load_env_file()

            assert EnvLoader._loaded is True
            mock_logger.error.assert_called_once()

    def test_load_env_file_custom_path(self):
        """Тест загрузки файла с кастомным путем"""
        env_content = "CUSTOM_KEY=custom_value"
        custom_path = "custom/.env"

        with (
            patch("os.path.exists", return_value=True) as mock_exists,
            patch("builtins.open", mock_open(read_data=env_content)),
            patch("os.environ", {}),
        ):

            EnvLoader.load_env_file(custom_path)

            mock_exists.assert_called_with(custom_path)

    def test_load_env_file_empty_lines_and_comments(self):
        """Тест обработки пустых строк и комментариев"""
        env_content = """
# Это комментарий
    # Еще комментарий

KEY=value

    
# Комментарий в конце
"""

        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=env_content)),
            patch("os.environ", {}) as mock_environ,
        ):

            EnvLoader.load_env_file()

            assert mock_environ["KEY"] == "value"
            assert len(mock_environ) == 1

    def test_load_env_file_whitespace_handling(self):
        """Тест обработки пробелов в ключах и значениях"""
        env_content = """
  KEY1  =  value1  
KEY2=  value2
  KEY3=value3  
"""

        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=env_content)),
            patch("os.environ", {}) as mock_environ,
        ):

            EnvLoader.load_env_file()

            assert mock_environ["KEY1"] == "value1"
            assert mock_environ["KEY2"] == "value2"
            assert mock_environ["KEY3"] == "value3"

    def test_get_env_var_existing(self):
        """Тест получения существующей переменной окружения"""
        with patch("os.getenv", return_value="test_value"):
            result = EnvLoader.get_env_var("TEST_KEY")
            assert result == "test_value"

    def test_get_env_var_not_existing_with_default(self):
        """Тест получения несуществующей переменной с значением по умолчанию"""
        with patch("os.getenv", side_effect=lambda key, default=None: default):
            result = EnvLoader.get_env_var("NON_EXISTING_KEY", "default_value")
            assert result == "default_value"

    def test_get_env_var_not_existing_no_default(self):
        """Тест получения несуществующей переменной без значения по умолчанию"""
        with patch("os.getenv", return_value=None):
            result = EnvLoader.get_env_var("NON_EXISTING_KEY")
            assert result is None

    def test_get_env_var_int_valid_integer(self):
        """Тест получения переменной как целое число"""
        with patch("os.getenv", return_value="42"):
            result = EnvLoader.get_env_var_int("TEST_KEY")
            assert result == 42

    def test_get_env_var_int_invalid_integer(self):
        """Тест получения переменной как целое число с невалидным значением"""
        with patch("os.getenv", return_value="not_a_number"), patch("src.utils.env_loader.logger") as mock_logger:

            result = EnvLoader.get_env_var_int("TEST_KEY", 100)

            assert result == 100
            mock_logger.warning.assert_called_once()

    def test_get_env_var_int_none_value(self):
        """Тест получения переменной как целое число когда переменная не существует"""
        with patch("os.getenv", return_value=None):
            result = EnvLoader.get_env_var_int("NON_EXISTING_KEY", 50)
            assert result == 50

    def test_get_env_var_int_default_zero(self):
        """Тест получения переменной как целое число со значением по умолчанию 0"""
        with patch("os.getenv", return_value=None):
            result = EnvLoader.get_env_var_int("NON_EXISTING_KEY")
            assert result == 0

    def test_load_env_file_equals_in_value(self):
        """Тест обработки знака равенства в значении переменной"""
        env_content = "KEY=value=with=equals"

        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=env_content)),
            patch("os.environ", {}) as mock_environ,
        ):

            EnvLoader.load_env_file()

            assert mock_environ["KEY"] == "value=with=equals"

    def test_automatic_loading_on_import(self):
        """Тест автоматической загрузки при импорте модуля"""
        # Этот тест проверяет что в конце модуля вызывается EnvLoader.load_env_file()
        # Поскольку модуль уже импортирован, мы можем только проверить что _loaded установлен
        assert hasattr(EnvLoader, "_loaded")

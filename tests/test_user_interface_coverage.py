
import pytest
from unittest.mock import Mock
from src.user_interface import main


def test_line_39_coverage(mocker):
    """Тест для покрытия строки 39 в main()"""
    # Мокаем UserInterface чтобы покрыть строку 39
    mock_ui_class = mocker.patch('src.user_interface.UserInterface')
    mock_ui = mock_ui_class.return_value
    
    main()
    
    mock_ui_class.assert_called_once()
    mock_ui.run.assert_called_once()

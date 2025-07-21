
import pytest
from unittest.mock import patch, MagicMock
from src.user_interface import UserInterface


class TestUserInterfaceFinal:
    """Tests for 100% coverage of user_interface.py"""

    @patch('src.user_interface.UserInterface')
    def test_main_function_line_39(self, mock_ui_class):
        """Test line 39 in user_interface.py main function"""
        # Mock the UserInterface class and its run method
        mock_ui_instance = MagicMock()
        mock_ui_class.return_value = mock_ui_instance
        
        # Import and call main to cover line 39
        from src.user_interface import main
        main()
        
        # Verify that UserInterface was instantiated and run was called
        mock_ui_class.assert_called_once()
        mock_ui_instance.run.assert_called_once()

    def test_userinterface_import_coverage(self):
        """Test UserInterface import and basic structure"""
        # This covers the import and class definition
        ui = UserInterface()
        assert hasattr(ui, 'run')
        assert callable(getattr(ui, 'run'))

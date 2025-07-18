
"""
Тесты для модуля source_selector
"""

import pytest
from unittest.mock import patch, MagicMock
from src.ui_interfaces.source_selector import SourceSelector


class TestSourceSelector:
    """Тесты для класса SourceSelector"""
    
    @pytest.fixture
    def source_selector(self):
        """Фикстура для создания экземпляра селектора источников"""
        return SourceSelector()
    
    @patch('src.ui_interfaces.source_selector.get_user_input')
    def test_select_sources_single_hh(self, mock_input, source_selector):
        """Тест выбора только HH.ru"""
        mock_input.return_value = '1'
        
        result = source_selector.select_sources()
        
        assert result == ['hh']
        mock_input.assert_called_once()
    
    @patch('src.ui_interfaces.source_selector.get_user_input')
    def test_select_sources_single_sj(self, mock_input, source_selector):
        """Тест выбора только SuperJob"""
        mock_input.return_value = '2'
        
        result = source_selector.select_sources()
        
        assert result == ['sj']
        mock_input.assert_called_once()
    
    @patch('src.ui_interfaces.source_selector.get_user_input')
    def test_select_sources_both(self, mock_input, source_selector):
        """Тест выбора обоих источников"""
        mock_input.return_value = '3'
        
        result = source_selector.select_sources()
        
        assert result == ['hh', 'sj']
        mock_input.assert_called_once()
    
    @patch('src.ui_interfaces.source_selector.get_user_input')
    def test_select_sources_cancel(self, mock_input, source_selector):
        """Тест отмены выбора"""
        mock_input.return_value = '0'
        
        result = source_selector.select_sources()
        
        assert result == []
        mock_input.assert_called_once()
    
    @patch('src.ui_interfaces.source_selector.get_user_input')
    @patch('builtins.print')
    def test_select_sources_invalid_input(self, mock_print, mock_input, source_selector):
        """Тест обработки неверного ввода"""
        mock_input.side_effect = ['invalid', '1']
        
        result = source_selector.select_sources()
        
        assert result == ['hh']
        assert mock_input.call_count == 2
        mock_print.assert_called()
    
    @patch('src.ui_interfaces.source_selector.get_user_input')
    @patch('builtins.print')
    def test_select_sources_empty_input(self, mock_print, mock_input, source_selector):
        """Тест обработки пустого ввода"""
        mock_input.side_effect = ['', '2']
        
        result = source_selector.select_sources()
        
        assert result == ['sj']
        assert mock_input.call_count == 2
    
    @patch('src.ui_interfaces.source_selector.get_user_input')
    @patch('builtins.print')
    def test_select_sources_out_of_range(self, mock_print, mock_input, source_selector):
        """Тест обработки ввода вне диапазона"""
        mock_input.side_effect = ['5', '3']
        
        result = source_selector.select_sources()
        
        assert result == ['hh', 'sj']
        assert mock_input.call_count == 2
        mock_print.assert_called()
    
    @patch('src.ui_interfaces.source_selector.get_user_input')
    def test_select_sources_for_cache_clearing_hh(self, mock_input, source_selector):
        """Тест выбора источников для очистки кэша - HH"""
        mock_input.return_value = '1'
        
        result = source_selector.select_sources_for_cache_clearing()
        
        assert result == {'hh': True, 'sj': False}
        mock_input.assert_called_once()
    
    @patch('src.ui_interfaces.source_selector.get_user_input')
    def test_select_sources_for_cache_clearing_sj(self, mock_input, source_selector):
        """Тест выбора источников для очистки кэша - SuperJob"""
        mock_input.return_value = '2'
        
        result = source_selector.select_sources_for_cache_clearing()
        
        assert result == {'hh': False, 'sj': True}
        mock_input.assert_called_once()
    
    @patch('src.ui_interfaces.source_selector.get_user_input')
    def test_select_sources_for_cache_clearing_both(self, mock_input, source_selector):
        """Тест выбора источников для очистки кэша - оба"""
        mock_input.return_value = '3'
        
        result = source_selector.select_sources_for_cache_clearing()
        
        assert result == {'hh': True, 'sj': True}
        mock_input.assert_called_once()
    
    @patch('src.ui_interfaces.source_selector.get_user_input')
    def test_select_sources_for_cache_clearing_cancel(self, mock_input, source_selector):
        """Тест отмены выбора источников для очистки кэша"""
        mock_input.return_value = '0'
        
        result = source_selector.select_sources_for_cache_clearing()
        
        assert result == {}
        mock_input.assert_called_once()
    
    @patch('src.ui_interfaces.source_selector.get_user_input')
    @patch('builtins.print')
    def test_select_sources_for_cache_clearing_invalid(self, mock_print, mock_input, source_selector):
        """Тест обработки неверного ввода при выборе источников для очистки кэша"""
        mock_input.side_effect = ['invalid', '1']
        
        result = source_selector.select_sources_for_cache_clearing()
        
        assert result == {'hh': True, 'sj': False}
        assert mock_input.call_count == 2
        mock_print.assert_called()
    
    @patch('builtins.print')
    def test_display_sources_menu(self, mock_print, source_selector):
        """Тест отображения меню выбора источников"""
        source_selector._display_sources_menu()
        
        mock_print.assert_called()
        # Проверяем, что вызов print содержит ожидаемый текст меню
        printed_text = ''.join([call[0][0] for call in mock_print.call_args_list])
        assert "HH.ru" in printed_text
        assert "SuperJob" in printed_text
    
    @patch('builtins.print')
    def test_display_cache_clearing_menu(self, mock_print, source_selector):
        """Тест отображения меню очистки кэша"""
        source_selector._display_cache_clearing_menu()
        
        mock_print.assert_called()
        # Проверяем, что вызов print содержит ожидаемый текст меню
        printed_text = ''.join([call[0][0] for call in mock_print.call_args_list])
        assert "кэш" in printed_text.lower()
    
    def test_validate_choice_valid(self, source_selector):
        """Тест валидации корректного выбора"""
        assert source_selector._validate_choice('1') is True
        assert source_selector._validate_choice('2') is True
        assert source_selector._validate_choice('3') is True
        assert source_selector._validate_choice('0') is True
    
    def test_validate_choice_invalid(self, source_selector):
        """Тест валидации некорректного выбора"""
        assert source_selector._validate_choice('4') is False
        assert source_selector._validate_choice('invalid') is False
        assert source_selector._validate_choice('') is False
        assert source_selector._validate_choice('-1') is False
    
    def test_get_sources_from_choice(self, source_selector):
        """Тест получения источников из выбора"""
        assert source_selector._get_sources_from_choice('1') == ['hh']
        assert source_selector._get_sources_from_choice('2') == ['sj']
        assert source_selector._get_sources_from_choice('3') == ['hh', 'sj']
        assert source_selector._get_sources_from_choice('0') == []
    
    def test_get_cache_sources_from_choice(self, source_selector):
        """Тест получения источников кэша из выбора"""
        assert source_selector._get_cache_sources_from_choice('1') == {'hh': True, 'sj': False}
        assert source_selector._get_cache_sources_from_choice('2') == {'hh': False, 'sj': True}
        assert source_selector._get_cache_sources_from_choice('3') == {'hh': True, 'sj': True}
        assert source_selector._get_cache_sources_from_choice('0') == {}

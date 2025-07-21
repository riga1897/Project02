from unittest.mock import Mock, patch

import pytest

from src.utils.paginator import Paginator


class TestPaginator:
    """Тест пагинатора"""

    @patch("src.utils.paginator.tqdm")
    def test_paginate_basic_functionality(self, mock_tqdm):
        """Тест базовой функциональности пагинации"""
        # Настройка mock для tqdm
        mock_progress = Mock()
        mock_tqdm.return_value.__enter__.return_value = mock_progress

        # Создаем mock функцию для получения данных
        fetch_func = Mock()
        fetch_func.side_effect = [
            [{"id": 1}, {"id": 2}],  # page 0
            [{"id": 3}, {"id": 4}],  # page 1
        ]

        result = Paginator.paginate(fetch_func, total_pages=2)

        expected = [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}]
        assert result == expected

        # Проверяем что функция вызывалась для каждой страницы
        assert fetch_func.call_count == 2
        fetch_func.assert_any_call(0)
        fetch_func.assert_any_call(1)

        # Проверяем что tqdm был настроен правильно
        mock_tqdm.assert_called_once_with(total=2, desc="Fetching pages", unit="page", dynamic_ncols=True)

    @patch("src.utils.paginator.tqdm")
    def test_paginate_with_start_page(self, mock_tqdm):
        """Тест пагинации с начальной страницы"""
        mock_progress = Mock()
        mock_tqdm.return_value.__enter__.return_value = mock_progress

        fetch_func = Mock()
        fetch_func.side_effect = [
            [{"id": 3}, {"id": 4}],  # page 1
            [{"id": 5}, {"id": 6}],  # page 2
        ]

        result = Paginator.paginate(fetch_func, total_pages=3, start_page=1)

        expected = [{"id": 3}, {"id": 4}, {"id": 5}, {"id": 6}]
        assert result == expected

        assert fetch_func.call_count == 2
        fetch_func.assert_any_call(1)
        fetch_func.assert_any_call(2)

        mock_tqdm.assert_called_once_with(
            total=2, desc="Fetching pages", unit="page", dynamic_ncols=True  # 3 - 1 = 2 pages to process
        )

    @patch("src.utils.paginator.tqdm")
    def test_paginate_with_max_pages(self, mock_tqdm):
        """Тест пагинации с ограничением максимального количества страниц"""
        mock_progress = Mock()
        mock_tqdm.return_value.__enter__.return_value = mock_progress

        fetch_func = Mock()
        fetch_func.side_effect = [
            [{"id": 1}, {"id": 2}],  # page 0
            [{"id": 3}, {"id": 4}],  # page 1
        ]

        result = Paginator.paginate(fetch_func, total_pages=5, max_pages=2)

        expected = [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}]
        assert result == expected

        assert fetch_func.call_count == 2

        mock_tqdm.assert_called_once_with(
            total=2, desc="Fetching pages", unit="page", dynamic_ncols=True  # min(5, 2) = 2
        )

    @patch("src.utils.paginator.tqdm")
    @patch("src.utils.paginator.logger")
    def test_paginate_with_no_pages_to_process(self, mock_logger, mock_tqdm):
        """Тест когда нет страниц для обработки"""
        fetch_func = Mock()

        result = Paginator.paginate(fetch_func, total_pages=2, start_page=3)

        assert result == []
        fetch_func.assert_not_called()
        mock_tqdm.assert_not_called()
        mock_logger.warning.assert_called_once_with("No pages to process (start_page >= total_pages)")

    @patch("src.utils.paginator.tqdm")
    @patch("src.utils.paginator.logger")
    def test_paginate_with_non_list_response(self, mock_logger, mock_tqdm):
        """Тест обработки ответа не в формате списка"""
        mock_progress = Mock()
        mock_tqdm.return_value.__enter__.return_value = mock_progress

        fetch_func = Mock()
        fetch_func.side_effect = [
            {"not": "a list"},  # Не список
            [{"id": 2}],  # Нормальный список
        ]

        result = Paginator.paginate(fetch_func, total_pages=2)

        expected = [{"id": 2}]
        assert result == expected

        mock_logger.warning.assert_called_once_with("Page 0 returned <class 'dict'> instead of list")

    @patch("src.utils.paginator.tqdm")
    @patch("src.utils.paginator.logger")
    def test_paginate_with_exception(self, mock_logger, mock_tqdm):
        """Тест обработки исключений"""
        mock_progress = Mock()
        mock_tqdm.return_value.__enter__.return_value = mock_progress

        fetch_func = Mock()
        fetch_func.side_effect = [
            Exception("Network error"),  # Первая страница с ошибкой
            [{"id": 2}],  # Вторая страница нормально
        ]

        result = Paginator.paginate(fetch_func, total_pages=2)

        expected = [{"id": 2}]
        assert result == expected

        mock_logger.error.assert_called_once_with("Error on page 0: Network error")

    @patch("src.utils.paginator.tqdm")
    def test_paginate_keyboard_interrupt(self, mock_tqdm):
        """Тест обработки прерывания пользователем"""
        mock_progress = Mock()
        mock_tqdm.return_value.__enter__.return_value = mock_progress

        fetch_func = Mock()
        fetch_func.side_effect = KeyboardInterrupt("User interrupted")

        with pytest.raises(KeyboardInterrupt):
            Paginator.paginate(fetch_func, total_pages=2)

    @patch("src.utils.paginator.tqdm")
    @patch("src.utils.paginator.logger")
    def test_paginate_keyboard_interrupt_with_logging(self, mock_logger, mock_tqdm):
        """Тест логирования при прерывании пользователем"""
        mock_progress = Mock()
        mock_tqdm.return_value.__enter__.return_value = mock_progress

        fetch_func = Mock()
        fetch_func.side_effect = KeyboardInterrupt("User interrupted")

        with pytest.raises(KeyboardInterrupt):
            Paginator.paginate(fetch_func, total_pages=2)

        mock_logger.info.assert_called_once_with("Прервано пользователем")

    @patch("src.utils.paginator.tqdm")
    def test_paginate_progress_bar_updates(self, mock_tqdm):
        """Тест обновления прогресс-бара"""
        mock_progress = Mock()
        mock_tqdm.return_value.__enter__.return_value = mock_progress

        fetch_func = Mock()
        fetch_func.side_effect = [
            [{"id": 1}, {"id": 2}],
            [{"id": 3}],
        ]

        result = Paginator.paginate(fetch_func, total_pages=2)

        # Проверяем что set_postfix вызывался с правильными значениями
        expected_calls = [
            ({"vacancies": 2},),  # После первой страницы
            ({"vacancies": 3},),  # После второй страницы
        ]

        assert mock_progress.set_postfix.call_count == 2
        for i, expected_call in enumerate(expected_calls):
            assert mock_progress.set_postfix.call_args_list[i][1] == expected_call[0]

        # Проверяем что update вызывался для каждой страницы
        assert mock_progress.update.call_count == 2
        mock_progress.update.assert_any_call(1)

    @patch("src.utils.paginator.tqdm")
    def test_paginate_default_parameters(self, mock_tqdm):
        """Тест пагинации с параметрами по умолчанию"""
        mock_progress = Mock()
        mock_tqdm.return_value.__enter__.return_value = mock_progress

        fetch_func = Mock()
        fetch_func.return_value = [{"id": 1}]

        result = Paginator.paginate(fetch_func)

        expected = [{"id": 1}]
        assert result == expected

        fetch_func.assert_called_once_with(0)

        mock_tqdm.assert_called_once_with(
            total=1, desc="Fetching pages", unit="page", dynamic_ncols=True  # total_pages=1 по умолчанию
        )

    @patch("src.utils.paginator.tqdm")
    def test_paginate_empty_page_data(self, mock_tqdm):
        """Тест обработки пустых данных страницы"""
        mock_progress = Mock()
        mock_tqdm.return_value.__enter__.return_value = mock_progress

        fetch_func = Mock()
        fetch_func.side_effect = [
            [],  # Пустой список
            [{"id": 1}],  # Непустой список
        ]

        result = Paginator.paginate(fetch_func, total_pages=2)

        expected = [{"id": 1}]
        assert result == expected

        # Проверяем обновления прогресс-бара
        expected_calls = [
            ({"vacancies": 0},),  # После пустой страницы
            ({"vacancies": 1},),  # После страницы с данными
        ]

        for i, expected_call in enumerate(expected_calls):
            assert mock_progress.set_postfix.call_args_list[i][1] == expected_call[0]

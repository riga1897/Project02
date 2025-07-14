from src.utils.paginator import Paginator
import pytest


class TestPaginator:


    def test_max_pages_limit(self):
        """Test pagination respects max_pages limit."""
        call_count = 0

        def mock_fetch(page):
            nonlocal call_count
            call_count += 1
            return [page] * 2

        result = Paginator.paginate(mock_fetch, max_pages=3, per_page=2)
        assert len(result) == 6
        assert call_count == 3

    def test_early_termination(self):
        """Test pagination stops when empty page is returned."""
        call_count = 0

        def mock_fetch(page):
            nonlocal call_count
            call_count += 1
            return [] if page > 0 else [1, 2]

        result = Paginator.paginate(mock_fetch, max_pages=5, per_page=2)
        assert result == [1, 2]
        assert call_count == 2  # page 0 and page 1

    def test_empty_initial_response(self):
        """Test when first page is empty."""
        call_count = 0

        def mock_fetch(page):
            nonlocal call_count
            call_count += 1
            return []

        result = Paginator.paginate(mock_fetch, max_pages=5, per_page=10)
        assert result == []
        assert call_count == 1  # Должен быть только один вызов

    def test_none_response_handling(self):
        """Test paginator handles None response from fetch_func."""

        def mock_fetch(page):
            return None if page > 0 else [1, 2]

        result = Paginator.paginate(mock_fetch, max_pages=3, per_page=2)
        assert result == [1, 2]  # Should ignore None and stop


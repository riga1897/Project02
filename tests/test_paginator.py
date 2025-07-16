from src.utils.paginator import Paginator
import pytest


class TestPaginator:
    def test_collects_multiple_pages(self):
        """Тест сбора данных с нескольких страниц"""
        def fetch(page):
            if page == 0:
                return ['a', 'b']
            elif page == 1:
                return ['c', 'd']
            return []

        result = Paginator.paginate(fetch, total_pages=3)
        assert result == ['a', 'b', 'c', 'd']

    def test_stops_at_empty_page(self):
        """Тест остановки при пустой странице"""
        def fetch(page):
            return ['data'] if page == 0 else []

        result = Paginator.paginate(fetch, total_pages=5)
        assert result == ['data']

    def test_empty_result(self):
        """Тест с пустым результатом"""
        def fetch(page):
            return []

        result = Paginator.paginate(fetch, total_pages=3)
        assert result == []

    def test_respects_total_pages(self):
        """Тест ограничения по total_pages"""
        def fetch(page):
            return [f'page{page}']

        result = Paginator.paginate(fetch, total_pages=2)
        assert result == ['page0', 'page1']

from typing import Callable, List, Dict


class Paginator:
    """Universal API paginator."""

    @staticmethod
    def paginate(
            fetch_func: Callable[[int], List[Dict]],
            max_pages: int = 20,
            per_page: int = 50,
            **kwargs
    ) -> List[Dict]:
        """
        Paginate through API using provided function.

        Args:
            fetch_func: Function that accepts page number and returns results
            max_pages: Maximum pages to fetch
            per_page: Items per page
            kwargs: Additional params

        Returns:
            Combined results from all pages
        """
        all_items = []
        for page in range(max_pages):
            items = fetch_func(page)
            if not items:
                break
            all_items.extend(items)

            if len(items) < per_page:
                break

        return all_items

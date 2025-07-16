from typing import List, Dict, Callable, Optional
from tqdm import tqdm


class Paginator:
    """Улучшенный пагинатор с прогресс-баром"""

    @staticmethod
    def paginate(
            fetch_func: Callable[[int], List[Dict]],
            total_pages: int = 1,
            start_page: int = 0,
            max_pages: Optional[int] = None,
            **kwargs
    ) -> List[Dict]:
        """
        Пагинация с прогресс-баром

        Args:
            fetch_func: Функция для получения страницы
            total_pages: Общее количество страниц
            start_page: Стартовая страница
            max_pages: Максимальное количество страниц
        """
        actual_max = min(total_pages, max_pages) if max_pages else total_pages
        results = []

        with tqdm(
                total=actual_max - start_page,
                desc="Fetching pages",
                unit="page",
                dynamic_ncols=True
        ) as pbar:
            for page in range(start_page, actual_max):
                results.extend(fetch_func(page))
                pbar.update(1)

        return results

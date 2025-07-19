from typing import List, Dict, Callable, Optional
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)


class Paginator:
    """
    Улучшенный пагинатор с обработкой ошибок и отслеживанием прогресса
    
    Предоставляет функциональность для постраничного получения данных
    с визуальным индикатором прогресса и обработкой ошибок.
    """

    @staticmethod
    def paginate(
            fetch_func: Callable[[int], List[Dict]],
            total_pages: int = 1,
            start_page: int = 0,
            max_pages: Optional[int] = None,
            **kwargs
    ) -> List[Dict]:
        """
        Надежная пагинация с функциями:
        - Отслеживание прогресса
        - Обработка ошибок
        - Ограничение запросов
        
        Args:
            fetch_func: Функция для получения данных страницы
            total_pages: Общее количество страниц
            start_page: Начальная страница
            max_pages: Максимальное количество страниц для обработки
            **kwargs: Дополнительные параметры
            
        Returns:
            List[Dict]: Объединенный список всех полученных данных
        """
        actual_max = min(total_pages, max_pages) if max_pages else total_pages
        results = []

        if actual_max <= start_page:
            logger.warning("No pages to process (start_page >= total_pages)")
            return results

        with tqdm(
                total=actual_max - start_page,
                desc="Fetching pages",
                unit="page",
                dynamic_ncols=True
        ) as pbar:
            for page in range(start_page, actual_max):
                try:
                    page_data = fetch_func(page)
                    if not isinstance(page_data, list):
                        logger.warning(
                            f"Page {page} returned {type(page_data)} instead of list"
                        )
                        page_data = []

                    results.extend(page_data)
                    pbar.set_postfix(vacancies=len(results))

                except KeyboardInterrupt:
                    logger.info("Прервано пользователем")
                    raise
                except Exception as e:
                    logger.error(f"Error on page {page}: {e}")
                finally:
                    pbar.update(1)

        return results
        
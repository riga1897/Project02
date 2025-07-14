from abc import ABC, abstractmethod
from typing import Dict, List


class BaseAPI(ABC):
    """Abstract base class for job search APIs."""

    @abstractmethod
    def _connect_to_api(self, url: str, params: dict) -> Dict:
        """Connect to API with error handling."""

    @abstractmethod
    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict]:
        """Get vacancies by search query."""

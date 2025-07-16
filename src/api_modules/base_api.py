from abc import ABC, abstractmethod
from typing import Dict, List, Union
import logging

logger = logging.getLogger(__name__)


class BaseAPI(ABC):
    """Abstract base class for job search APIs with enhanced error handling"""

    @abstractmethod
    def _connect_to_api(self, url: str, params: Dict) -> Union[Dict, str]:
        """
        Connect to API with comprehensive error handling
        Returns:
            Dict: API response as dictionary
            str: Error message if request fails
        """
        pass

    @abstractmethod
    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict]:
        """Get validated vacancies by search query"""
        pass

    @staticmethod
    def validate_response(response: Union[Dict, str]) -> bool:
        """Validate API response structure"""
        if isinstance(response, str):
            logger.error(f"API returned error: {response}")
            return False
        return True
        
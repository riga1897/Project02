from typing import Dict, Any, Optional
from .hh_api_config import HHAPIConfig


class APIConfig:
    """API configuration class."""

    def __init__(
        self,
        user_agent: str = "MyVacancyApp/1.0",
        timeout: int = 15,
        request_delay: float = 0.5,
        default_hh_params: Optional[Dict[str, Any]] = None,
        default_pagination_params: Optional[Dict[str, Any]] = None
    ):
        self.user_agent = user_agent
        self.timeout = timeout
        self.request_delay = request_delay
        self.hh_config = HHAPIConfig(default_hh_params)
        self._default_pagination_params = default_pagination_params or {
            "max_pages": 20
        }

    def get_pagination_params(self, **kwargs) -> Dict[str, Any]:
        """Get pagination params with overrides."""
        params = self._default_pagination_params.copy()
        params.update(kwargs)
        return params
        

from typing import Dict, Any, Optional


class HHAPIConfig:
    """HH.ru API configuration class."""

    def __init__(self, default_hh_params: Optional[Dict[str, Any]] = None):
        self._default_hh_params = default_hh_params or {
            "area": 113,  # Russia (исключая Казахстан)
            "period": 15,  # Период 15 дней по умолчанию
            "per_page": 100  # Максимальное значение для HH.ru API
        }

    def get_hh_params(self, **kwargs) -> Dict[str, Any]:
        """Get HH API params with overrides."""
        params = self._default_hh_params.copy()
        params.update(kwargs)
        return params
      

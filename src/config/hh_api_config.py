from typing import Dict, Any


class HHAPIConfig:
    """HH.ru API configuration class."""

    def __init__(self, default_hh_params: Optional[Dict[str, Any]] = None):
        self._default_hh_params = default_hh_params or {
            "area": 113,  # Russia
            "period": 7,
            "only_with_salary": True,
            "per_page": 50
        }

    def get_hh_params(self, **kwargs) -> Dict[str, Any]:
        """Get HH API params with overrides."""
        params = self._default_hh_params.copy()
        params.update(kwargs)
        return params
      

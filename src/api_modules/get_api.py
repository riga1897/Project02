import requests
from typing import Dict, Optional
from time import sleep
from src.config.api_config import APIConfig


class APIConnector:
    """General API connection handler."""

    def __init__(self, config: Optional[APIConfig] = None):
        self.config = config or APIConfig()
        self.headers = {'User-Agent': self.config.user_agent}

    def connect(self, url: str, params: Dict, delay: float = 0.5) -> Dict:
        """Make API request with error handling."""
        try:
            sleep(delay)
            response = requests.get(
                url,
                params={k: v for k, v in params.items() if v is not None},
                headers=self.headers,
                timeout=self.config.timeout
            )

            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 1))
                sleep(retry_after)
                return self.connect(url, params, delay)

            response.raise_for_status()
            return response.json()

        except requests.Timeout as e:
            raise ConnectionError(f"Timeout error: {str(e)}")
        except requests.HTTPError as e:
            error_msg = f"HTTP error {e.response.status_code}"
            if e.response.text:
                error_msg += f": {e.response.text[:200]}"
            raise ConnectionError(error_msg)
        except requests.RequestException as e:
            raise ConnectionError(f"Connection error: {str(e)}")
        except ValueError as e:
            raise ConnectionError(f"JSON decode error: {str(e)}")

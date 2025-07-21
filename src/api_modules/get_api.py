"""
Модуль для выполнения HTTP-запросов к внешним API.

Предоставляет низкоуровневый клиент для работы с API различных сервисов
поиска вакансий. Включает обработку ошибок, повторные попытки запросов
и визуализацию прогресса выполнения операций.
"""

import os
import requests
from typing import Dict, Optional
from time import sleep
from tqdm import tqdm
from src.config.api_config import APIConfig


class APIConnector:
    """
    Обработчик API-запросов с прогресс-баром

    Предоставляет функциональность для выполнения HTTP-запросов к API
    с визуальным отображением прогресса, обработкой ошибок и повторными попытками.
    """

    def __init__(self, config: Optional[APIConfig] = None):
        """
        Инициализация API-коннектора

        Args:
            config: Конфигурация API (если None, используется конфигурация по умолчанию)
        """
        self.config = config or APIConfig()
        self.headers = {
            'User-Agent': self.config.user_agent,
            'Accept': 'application/json'
        }
        self._progress = None

    def _init_progress(self, total: int, desc: str) -> None:
        """
        Инициализация прогресс-бара с автоматическим отключением в тестах

        Args:
            total: Общее количество операций
            desc: Описание операции
        """
        tqdm_params = {
            'total': total,
            'desc': desc,
            'unit': "req",
            'bar_format': "{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
            'dynamic_ncols': True,
            'disable': os.getenv('DISABLE_TQDM') == '1'  # Автоматическое отключение
        }
        self._progress = tqdm(**tqdm_params)

    def _update_progress(self, n: int = 1) -> None:
        """
        Обновление прогресс-бара

        Args:
            n: Количество шагов для обновления
        """
        if self._progress:
            self._progress.update(n)

    def _close_progress(self) -> None:
        """
        Закрытие прогресс-бара

        Безопасно закрывает и освобождает ресурсы прогресс-бара.
        """
        if self._progress:
            self._progress.close()
            self._progress = None

    def __connect(
            self,
            url: str,
            params: Dict,
            delay: float = 0.15,
            show_progress: bool = False,
            progress_desc: Optional[str] = None
    ) -> Dict:
        """
        Выполнение API-запроса с обработкой ошибок и прогрессом

        Args:
            url: URL для запроса
            params: Параметры запроса
            delay: Задержка между запросами в секундах
            show_progress: Показывать ли прогресс-бар
            progress_desc: Описание для прогресс-бара

        Returns:
            Dict: Ответ API в формате JSON

        Raises:
            ConnectionError: При ошибках сети или API
        """
        try:
            if show_progress:
                desc = progress_desc or f"Request to {url.split('/')[-1]}"
                self._init_progress(1, desc)

            sleep(delay)
            response = requests.get(
                url,
                params={k: v for k, v in params.items() if v is not None},
                headers=self.headers,
                timeout=self.config.timeout
            )

            self._update_progress()

            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 1))
                sleep(retry_after)
                return self.__connect(url, params, delay, show_progress, progress_desc)

            response.raise_for_status()
            return response.json()

        except requests.Timeout as e:
            raise ConnectionError(f"Timeout error: {str(e)}")
        except requests.HTTPError as e:
            if e.response is None:
                error_msg = "HTTP error (no response details)"
            else:
                error_msg = f"HTTP error {e.response.status_code}"
                if e.response.text:
                    error_msg += f": {e.response.text[:200]}"
            raise ConnectionError(error_msg)
        except requests.RequestException as e:
            raise ConnectionError(f"Connection error: {str(e)}")
        except ValueError as e:
            raise ConnectionError(f"JSON decode error: {str(e)}")
        except Exception as e:
            raise ConnectionError(f"Unexpected error: {str(e)}")
        finally:
            self._close_progress()

    def connect(self, url: str, params: Dict = None) -> Dict:
        """
        Выполнение HTTP-запроса

        Args:
            url: URL для запроса  
            params: Параметры запроса

        Returns:
            Dict: Ответ API
        """
        return self._APIConnector__connect(url, params)
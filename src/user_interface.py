#!/usr/bin/env python3
"""
Модуль для запуска пользовательского интерфейса
"""

import logging
from src.ui_interfaces.console_interface import UserInterface


def main() -> None:
    """Точка входа для пользовательского интерфейса"""
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("user_interface.log"),
            logging.StreamHandler()
        ]
    )

    ui = UserInterface()
    ui.run()


if __name__ == "__main__":
    main()
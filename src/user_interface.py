#!/usr/bin/env python3
"""
Модуль для запуска пользовательского интерфейса
"""

import logging

from src.ui_interfaces.console_interface import UserInterface
from src.utils.env_loader import EnvLoader


def main() -> None:
    """Точка входа для пользовательского интерфейса"""
    # Загружаем переменные окружения из .env файла
    EnvLoader.load_env_file()

    # Получаем уровень логирования из переменных окружения
    log_level = EnvLoader.get_env_var("LOG_LEVEL", "INFO").upper()
    log_level_value = getattr(logging, log_level, logging.INFO)

    # Настройка логирования
    logging.basicConfig(
        level=log_level_value,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("user_interface.log"), logging.StreamHandler()],
    )

    print("=" * 60)
    print("   ПОИСКОВИК ВАКАНСИЙ")
    print("=" * 60)

    ui = UserInterface()
    ui.run()


if __name__ == "__main__":
    main()

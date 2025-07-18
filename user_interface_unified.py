
#!/usr/bin/env python3
"""
Унифицированное приложение для поиска вакансий на HH.ru и SuperJob
"""

import logging
from src.ui_interfaces.console_interface import UserInterface


def main() -> None:
    """Точка входа для унифицированного пользовательского интерфейса"""
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("unified_interface.log"),
            logging.StreamHandler()
        ]
    )

    print("=" * 60)
    print("   ПОИСКОВИК ВАКАНСИЙ - HH.ru и SuperJob.ru")
    print("=" * 60)
    
    ui = UserInterface()
    ui.run()


if __name__ == "__main__":
    main()

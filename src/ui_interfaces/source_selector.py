import logging
from typing import Optional, Set

logger = logging.getLogger(__name__)


class SourceSelector:
    """Класс для выбора источников вакансий"""

    AVAILABLE_SOURCES = {"hh": "HH.ru", "sj": "SuperJob.ru"}

    @classmethod
    def get_user_source_choice(cls) -> Optional[Set[str]]:
        """
        Получение выбора пользователя по источникам

        Returns:
            Set[str]: Множество выбранных источников или None при отмене
        """
        print("\n" + "=" * 50)
        print("ВЫБОР ИСТОЧНИКОВ ВАКАНСИЙ")
        print("=" * 50)
        print("Выберите источники для поиска вакансий:")
        print("1. HH.ru")
        print("2. SuperJob.ru")
        print("3. Оба источника")
        print("0. Отмена")
        print("=" * 50)

        while True:
            choice = input("Ваш выбор: ").strip()

            if choice == "1":
                print("Выбран источник: HH.ru")
                return {"hh"}
            elif choice == "2":
                print("Выбран источник: SuperJob.ru")
                return {"sj"}
            elif choice == "3":
                print("Выбраны оба источника: HH.ru и SuperJob.ru")
                return {"hh", "sj"}
            elif choice == "0":
                print("Выбор источников отменен.")
                return None
            else:
                print("Неверный выбор. Пожалуйста, введите 1, 2, 3 или 0.")

    @classmethod
    def get_source_display_name(cls, source_key: str) -> str:
        """
        Получение отображаемого имени источника

        Args:
            source_key: Ключ источника

        Returns:
            str: Отображаемое имя источника
        """
        return cls.AVAILABLE_SOURCES.get(source_key, source_key)

    @classmethod
    def display_sources_info(cls, sources: Set[str]) -> None:
        """
        Отображение информации о выбранных источниках

        Args:
            sources: Множество выбранных источников
        """
        if not sources:
            print("Источники не выбраны")
            return

        source_names = [cls.get_source_display_name(source) for source in sources]
        print(f"Выбранные источники: {', '.join(source_names)}")

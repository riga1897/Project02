import logging
from typing import List, Optional
from src.vacancies.models import Vacancy
from src.utils.ui_helpers import get_user_input, confirm_action
from src.utils.vacancy_formatter import VacancyFormatter
from src.ui_interfaces.source_selector import SourceSelector
from src.api_modules.unified_api import UnifiedAPI
from src.storage.json_saver import JSONSaver
from src.utils.ui_navigation import quick_paginate

logger = logging.getLogger(__name__)


class VacancySearchHandler:
    """
    Обработчик операций поиска вакансий
    
    Отвечает за логику поиска вакансий через API,
    их отображение и сохранение.
    """
    
    def __init__(self, unified_api: UnifiedAPI, json_saver: JSONSaver):
        """
        Инициализация обработчика поиска
        
        Args:
            unified_api: Унифицированный API для получения вакансий
            json_saver: Сервис сохранения данных
        """
        self.unified_api = unified_api
        self.json_saver = json_saver
        self.source_selector = SourceSelector()
    
    def search_vacancies(self) -> None:
        """Поиск вакансий по запросу пользователя"""
        # Выбор источников
        sources = self.source_selector.get_user_source_choice()
        if not sources:
            return

        self.source_selector.display_sources_info(sources)

        # Ввод поискового запроса
        query = get_user_input("\nВведите поисковый запрос: ")
        if not query:
            return

        # Выбор периода
        period = self._get_period_choice()
        if period is None:
            return

        print(f"\nИщем вакансии по запросу: '{query}' за последние {period} дней...")

        # Получение вакансий
        try:
            all_vacancies = self._fetch_vacancies_from_sources(sources, query, period)
            
            if not all_vacancies:
                print("Вакансии не найдены ни на одном из источников.")
                return

            print(f"\nВсего найдено {len(all_vacancies)} вакансий")
            
            # Обработка результатов
            self._handle_search_results(all_vacancies, query)
            
        except Exception as e:
            logger.error(f"Ошибка поиска вакансий: {e}")
            print(f"Произошла ошибка при поиске: {e}")
    
    def _fetch_vacancies_from_sources(self, sources: set, query: str, period: int) -> List[Vacancy]:
        """
        Получение вакансий из выбранных источников
        
        Args:
            sources: Множество выбранных источников
            query: Поисковый запрос
            period: Период поиска в днях
            
        Returns:
            List[Vacancy]: Список найденных вакансий
        """
        all_vacancies = []

        if "hh" in sources:
            print("Получение вакансий с HH.ru...")
            hh_vacancies = self.unified_api.get_hh_vacancies(query, period=period)
            if hh_vacancies:
                all_vacancies.extend(hh_vacancies)
                print(f"Найдено {len(hh_vacancies)} вакансий на HH.ru")
            else:
                print("Вакансии на HH.ru не найдены")

        if "sj" in sources:
            print("Получение вакансий с SuperJob...")
            sj_vacancies = self.unified_api.get_sj_vacancies(query, period=period)
            if sj_vacancies:
                all_vacancies.extend(sj_vacancies)
                print(f"Найдено {len(sj_vacancies)} вакансий на SuperJob")
            else:
                print("Вакансии на SuperJob не найдены")

        return all_vacancies
    
    def _handle_search_results(self, vacancies: List[Vacancy], query: str) -> None:
        """
        Обработка результатов поиска - отображение и сохранение
        
        Args:
            vacancies: Список найденных вакансий
            query: Поисковый запрос
        """
        # Предпросмотр вакансий
        show_vacancies = confirm_action("Показать найденные вакансии?")
        if show_vacancies:
            def format_vacancy(vacancy: Vacancy, number: Optional[int] = None) -> str:
                if vacancy is None:
                    raise ValueError("Received a vacancy object of None type.")
                return VacancyFormatter.format_vacancy_info(vacancy, number)

            quick_paginate(
                vacancies,
                formatter=format_vacancy,
                header=f"Найденные вакансии по запросу '{query}' из всех источников",
                items_per_page=5
            )

            # Сохранение после просмотра
            if confirm_action("Сохранить просмотренные вакансии?"):
                self._save_vacancies(vacancies)
            else:
                print("Вакансии не сохранены")
        else:
            # Сохранение без просмотра
            if confirm_action("Сохранить найденные вакансии без просмотра?"):
                self._save_vacancies(vacancies)
            else:
                print("Вакансии не сохранены")
    
    def _save_vacancies(self, vacancies: List[Vacancy]) -> None:
        """
        Сохранение вакансий в хранилище
        
        Args:
            vacancies: Список вакансий для сохранения
        """
        update_messages = self.json_saver.add_vacancy(vacancies)
        if update_messages:
            print(f"Обработано {len(vacancies)} вакансий:")
            for message in update_messages[:5]:
                print(f"  • {message}")
            if len(update_messages) > 5:
                print(f"  ... и еще {len(update_messages) - 5} операций")
        else:
            print("Вакансии уже существуют в базе данных")
    
    @staticmethod
    def _get_period_choice() -> Optional[int]:
        """
        Выбор периода публикации вакансий
        
        Returns:
            Optional[int]: Количество дней для поиска или None при отмене
        """
        try:
            print("\nВыберите период публикации вакансий:")
            print("1. 1 день")
            print("2. 3 дня")
            print("3. 7 дней")
            print("4. 15 дней (по умолчанию)")
            print("5. 30 дней")
            print("6. Ввести свой период")
            print("0. Отмена")

            choice = input("Ваш выбор (по умолчанию 15 дней): ").strip()

            period_map = {
                "1": 1,
                "2": 3,
                "3": 7,
                "4": 15,
                "5": 30,
                "": 15
            }

            if choice == "0":
                print("Выбор периода отменен.")
                return None
            elif choice in period_map:
                return period_map[choice]
            elif choice == "6":
                try:
                    custom_period = int(input("Введите количество дней (1-365): "))
                    if 1 <= custom_period <= 365:
                        return custom_period
                    else:
                        print("Некорректный период. Используется 15 дней по умолчанию.")
                        return 15
                except ValueError:
                    print("Некорректный ввод. Используется 15 дней по умолчанию.")
                    return 15
            else:
                print("Некорректный выбор. Используется 15 дней по умолчанию.")
                return 15

        except KeyboardInterrupt:
            print("\nВыбор периода отменен.")
            return None

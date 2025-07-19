import logging

from src.config.ui_config import ui_pagination_config
from src.storage.json_saver import JSONSaver
from src.utils.ui_helpers import get_positive_integer, filter_vacancies_by_keyword
from src.utils.ui_navigation import quick_paginate
from src.utils.vacancy_formatter import VacancyFormatter
from src.utils.vacancy_operations import VacancyOperations

logger = logging.getLogger(__name__)


class VacancyDisplayHandler:
    """
    Обработчик операций отображения сохраненных вакансий
    
    Отвечает за логику отображения, фильтрации и сортировки
    сохраненных вакансий.
    """
    
    def __init__(self, json_saver: JSONSaver):
        """
        Инициализация обработчика отображения
        
        Args:
            json_saver: Сервис работы с сохраненными данными
        """
        self.json_saver = json_saver
        self.vacancy_ops = VacancyOperations()
    
    def show_all_saved_vacancies(self) -> None:
        """Отображение всех сохраненных вакансий с постраничным просмотром"""
        try:
            vacancies = self.json_saver.get_vacancies()

            if not vacancies:
                print("\nНет сохраненных вакансий.")
                return

            print(f"\nСохраненных вакансий: {len(vacancies)}")

            def format_vacancy(vacancy, number=None):
                return VacancyFormatter.format_vacancy_info(vacancy, number)

            quick_paginate(
                vacancies,
                formatter=format_vacancy,
                header="Сохраненные вакансии",
                items_per_page=ui_pagination_config.get_items_per_page('saved')
            )

        except Exception as e:
            logger.error(f"Ошибка при отображении сохраненных вакансий: {e}")
            print(f"Ошибка при загрузке вакансий: {e}")
    
    def show_top_vacancies_by_salary(self) -> None:
        """Получение топ N сохраненных вакансий по зарплате"""
        n = get_positive_integer("\nВведите количество вакансий для отображения: ")
        if n is None:
            return

        try:
            vacancies = self.json_saver.get_vacancies()

            if not vacancies:
                print("Нет сохраненных вакансий.")
                return

            # Фильтруем вакансии с зарплатой
            vacancies_with_salary = self.vacancy_ops.get_vacancies_with_salary(vacancies)

            if not vacancies_with_salary:
                print("Среди сохраненных вакансий нет ни одной с указанной зарплатой.")
                return

            # Сортируем по убыванию зарплаты
            sorted_vacancies = self.vacancy_ops.sort_vacancies_by_salary(vacancies_with_salary)
            top_vacancies = sorted_vacancies[:n]

            print(f"\nТоп {len(top_vacancies)} сохраненных вакансий по зарплате:")

            def format_vacancy(vacancy, number=None):
                return VacancyFormatter.format_vacancy_info(vacancy, number)

            quick_paginate(
                top_vacancies,
                formatter=format_vacancy,
                header=f"Топ {len(top_vacancies)} вакансий по зарплате",
                items_per_page=ui_pagination_config.get_items_per_page('top')
            )

        except Exception as e:
            logger.error(f"Ошибка при получении топ сохраненных вакансий: {e}")
            print(f"Ошибка при поиске: {e}")
    
    def search_saved_vacancies_by_keyword(self) -> None:
        """Поиск в сохраненных вакансиях с ключевым словом"""
        from src.utils.ui_helpers import get_user_input
        
        keyword = get_user_input("\nВведите ключевое слово для поиска в описании: ")
        if not keyword:
            return

        try:
            vacancies = self.json_saver.get_vacancies()

            if not vacancies:
                print("Нет сохраненных вакансий.")
                return

            filtered_vacancies = filter_vacancies_by_keyword(vacancies, keyword)

            if not filtered_vacancies:
                print(f"Среди сохраненных вакансий не найдено ни одной с ключевым словом '{keyword}'.")
                return

            print(f"\nНайдено {len(filtered_vacancies)} сохраненных вакансий с ключевым словом '{keyword}':")

            def format_vacancy(vacancy, number=None):
                return VacancyFormatter.format_vacancy_info(vacancy, number)

            quick_paginate(
                filtered_vacancies,
                formatter=format_vacancy,
                header=f"Вакансии с ключевым словом '{keyword}'",
                items_per_page=ui_pagination_config.get_items_per_page('search')
            )

        except Exception as e:
            logger.error(f"Ошибка при поиске по ключевому слову: {e}")
            print(f"Ошибка при поиске: {e}")

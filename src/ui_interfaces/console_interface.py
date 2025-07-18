import logging
from typing import List, Optional
from src.api_modules.unified_api import UnifiedVacancyAPI
from src.vacancies.models import Vacancy
from src.storage.json_saver import JSONSaver
from src.utils.ui_paginator import paginate_display
from src.utils.ui_helpers import (
    get_user_input, get_positive_integer, parse_salary_range, confirm_action,
    filter_vacancies_by_keyword, display_vacancy_info
)
from src.utils.vacancy_operations import VacancyOperations
from src.utils.menu_manager import create_main_menu, print_section_header, print_menu_separator
from src.ui_interfaces.source_selector import SourceSelector
from src.api_modules.hh_api import HeadHunterAPI
from src.api_modules.sj_api import SuperJobAPI
from src.api_modules.unified_api import UnifiedAPI

logger = logging.getLogger(__name__)


class UserInterface:
    """Класс для взаимодействия с пользователем через консоль"""

    def __init__(self):
        """Инициализация пользовательского интерфейса"""
        self.hh_api = HeadHunterAPI()
        self.sj_api = SuperJobAPI()
        self.unified_api = UnifiedAPI()
        self.json_saver = JSONSaver()
        self.menu_manager = create_main_menu()
        self.vacancy_ops = VacancyOperations()
        self.source_selector = SourceSelector()

    def run(self) -> None:
        """Основной цикл взаимодействия с пользователем"""
        print_section_header("Добро пожаловать в поисковик вакансий!")

        while True:
            try:
                choice = self._show_menu()

                if choice == "1":
                    self._search_vacancies()
                elif choice == "2":
                    self._show_saved_vacancies()
                elif choice == "3":
                    self._get_top_saved_vacancies_by_salary()
                elif choice == "4":
                    self._search_saved_vacancies_by_keyword()
                elif choice == "5":
                    self._advanced_search_vacancies()
                elif choice == "6":
                    self._filter_saved_vacancies_by_salary()
                elif choice == "7":
                    self._show_keywords_statistics()
                elif choice == "8":
                    self._delete_saved_vacancies()
                elif choice == "9":
                    self._clear_api_cache()
                elif choice == "10":
                    self._setup_superjob_api()
                elif choice == "0":
                    print("Спасибо за использование! До свидания!")
                    break
                else:
                    print("Неверный выбор. Попробуйте снова.")

            except KeyboardInterrupt:
                print("\n\nРабота прервана пользователем. До свидания!")
                break
            except Exception as e:
                logger.error(f"Ошибка в пользовательском интерфейсе: {e}")
                print(f"Произошла ошибка: {e}")

    def _show_menu(self) -> str:
        """
        Отображение главного меню

        Returns:
            str: Выбор пользователя
        """
        print("\n")
        print_menu_separator()
        print("Выберите действие:")
        print("1. Поиск вакансий по запросу (выбор источника + запрос к API)")
        print("2. Показать все сохраненные вакансии")
        print("3. Топ N сохраненных вакансий по зарплате")
        print("4. Поиск в сохраненных вакансиях по ключевому слову")
        print("5. Расширенный поиск (несколько ключевых слов)")
        print("6. Фильтр сохраненных вакансий по зарплате")
        print("7. Статистика по ключевым словам")
        print("8. Удалить сохраненные вакансии")
        print("9. Очистить кэш API")
        print("10. Настройка SuperJob API")
        print("0. Выход")
        print_menu_separator()

        return input("Ваш выбор: ").strip()

    def _search_vacancies(self) -> None:
        """Поиск вакансий по запросу пользователя"""
        # Сначала выбираем источники
        sources = self.source_selector.get_user_source_choice()
        if not sources:
            return

        self.source_selector.display_sources_info(sources)

        # Затем вводим поисковый запрос
        query = get_user_input("\nВведите поисковый запрос: ")

        if not query:
            return

        print(f"\nИщем вакансии по запросу: '{query}'...")

        # Получение вакансий с выбранных источников через UnifiedAPI
        try:
            print(f"Поиск вакансий по запросу: '{query}'...")

            # Определяем источники для поиска
            selected_sources = []
            if sources["hh"]:
                selected_sources.append("hh")
            if sources["sj"]:
                selected_sources.append("sj")

            if not selected_sources:
                print("Не выбран ни один источник для поиска.")
                return

            # Получаем и автоматически сохраняем вакансии
            all_vacancies = self.unified_api.get_vacancies_from_sources(query, selected_sources)

            if not all_vacancies:
                print("Вакансии не найдены.")
                return

            print(f"\nПоиск завершен. Всего найдено и сохранено: {len(all_vacancies)} вакансий")

            # Показываем статистику по источникам
            hh_count = sum(1 for v in all_vacancies if v.source == "hh.ru")
            sj_count = sum(1 for v in all_vacancies if v.source == "superjob.ru")

            if hh_count > 0:
                print(f"  • HH.ru: {hh_count} вакансий")
            if sj_count > 0:
                print(f"  • SuperJob: {sj_count} вакансий")

        except Exception as e:
            print(f"Ошибка при поиске вакансий: {e}")
            logger.error(f"Ошибка в search_vacancies: {e}")
            return

    def _show_saved_vacancies(self) -> None:
        """Отображение сохраненных вакансий с постраничным просмотром"""
        try:
            vacancies = self.json_saver.get_vacancies()

            if not vacancies:
                print("\nНет сохраненных вакансий.")
                return

            print(f"\nСохраненных вакансий: {len(vacancies)}")

            # Постраничный просмотр
            paginate_display(vacancies, self._display_vacancies, 10, "Сохраненные вакансии")

        except Exception as e:
            logger.error(f"Ошибка при отображении сохраненных вакансий: {e}")
            print(f"Ошибка при загрузке вакансий: {e}")

    def _get_top_saved_vacancies_by_salary(self) -> None:
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

            # Постраничный просмотр
            paginate_display(top_vacancies, self._display_vacancies, 10, f"Топ {len(top_vacancies)} вакансий по зарплате")

        except Exception as e:
            logger.error(f"Ошибка при получении топ сохраненных вакансий: {e}")
            print(f"Ошибка при поиске: {e}")

    def _search_saved_vacancies_by_keyword(self) -> None:
        """Поиск в сохраненных вакансиях с ключевым словом в описании"""
        keyword = get_user_input("\nВведите ключевое слово для поиска в описании: ")

        if not keyword:
            return

        try:
            vacancies = self.json_saver.get_vacancies()

            if not vacancies:
                print("Нет сохраненных вакансий.")
                return

            # Фильтруем по ключевому слову в описании
            filtered_vacancies = filter_vacancies_by_keyword(vacancies, keyword)

            if not filtered_vacancies:
                print(f"Среди сохраненных вакансий не найдено ни одной с ключевым словом '{keyword}'.")
                return

            print(f"\nНайдено {len(filtered_vacancies)} сохраненных вакансий с ключевым словом '{keyword}':")

            # Постраничный просмотр
            paginate_display(filtered_vacancies, self._display_vacancies, 10, f"Вакансии с ключевым словом '{keyword}'")

        except Exception as e:
            logger.error(f"Ошибка при поиске по ключевому слову: {e}")
            print(f"Ошибка при поиске: {e}")

    def _advanced_search_vacancies(self) -> None:
        """Расширенный поиск по вакансиям"""
        try:
            vacancies = self.json_saver.get_vacancies()

            if not vacancies:
                print("Нет сохраненных вакансий.")
                return

            print("\nРасширенный поиск:")
            print("Введите ключевые слова через запятую, пробел или используйте операторы AND/OR")
            print("Примеры:")
            print("  - python django postgresql (поиск по любому из слов)")
            print("  - python, django, postgresql (поиск по любому из слов)")
            print("  - python AND django (поиск по всем словам)")
            print("  - python OR java (поиск по любому из слов)")

            query = get_user_input("Введите поисковый запрос: ")

            if not query:
                return

            # Определяем тип поиска
            if ',' in query and ' AND ' not in query.upper() and ' OR ' not in query.upper():
                # Поиск по нескольким ключевым словам через запятую
                keywords = [kw.strip() for kw in query.split(',')]
                filtered_vacancies = self.vacancy_ops.filter_vacancies_by_multiple_keywords(vacancies, keywords)
                print(f"\nПоиск по ключевым словам: {', '.join(keywords)}")
            else:
                # Продвинутый поиск с операторами
                filtered_vacancies = self.vacancy_ops.search_vacancies_advanced(vacancies, query)
                print(f"\nРезультаты поиска по запросу: '{query}'")

            if not filtered_vacancies:
                print("Вакансии по указанным критериям не найдены.")
                return

            print(f"Найдено {len(filtered_vacancies)} вакансий:")

            # Постраничный просмотр
            paginate_display(filtered_vacancies, self._display_vacancies, 10, "Результаты расширенного поиска")

        except Exception as e:
            logger.error(f"Ошибка при расширенном поиске: {e}")
            print(f"Ошибка при поиске: {e}")

    def _filter_saved_vacancies_by_salary(self) -> None:
        """Фильтрация сохраненных вакансий по зарплате"""
        try:
            vacancies = self.json_saver.get_vacancies()

            if not vacancies:
                print("Нет сохраненных вакансий.")
                return

            print("\nВыберите тип фильтрации:")
            print("1. Минимальная зарплата")
            print("2. Максимальная зарплата")
            print("3. Диапазон зарплат")

            choice = input("Ваш выбор: ").strip()

            filtered_vacancies = []

            if choice == "1":
                try:
                    min_salary = int(input("Введите минимальную зарплату: "))
                    filtered_vacancies = self.vacancy_ops.filter_vacancies_by_min_salary(vacancies, min_salary)
                    print(f"\nВакансии с зарплатой от {min_salary} руб.:")
                except ValueError:
                    print("Введите корректное число!")
                    return

            elif choice == "2":
                try:
                    max_salary = int(input("Введите максимальную зарплату: "))
                    filtered_vacancies = self.vacancy_ops.filter_vacancies_by_max_salary(vacancies, max_salary)
                    print(f"\nВакансии с зарплатой до {max_salary} руб.:")
                except ValueError:
                    print("Введите корректное число!")
                    return

            elif choice == "3":
                salary_range = input("Введите диапазон зарплат (пример: 100000 - 150000): ").strip()
                parsed_range = parse_salary_range(salary_range)
                if parsed_range:
                    min_salary, max_salary = parsed_range
                    filtered_vacancies = self.vacancy_ops.filter_vacancies_by_salary_range(vacancies, min_salary, max_salary)
                    print(f"\nВакансии с зарплатой в диапазоне {min_salary} - {max_salary} руб.:")
                else:
                    return

            else:
                print("Неверный выбор.")
                return

            if not filtered_vacancies:
                print("Вакансии с указанными критериями зарплаты не найдены.")
                return

            # Сортируем по убыванию зарплаты
            sorted_vacancies = self.vacancy_ops.sort_vacancies_by_salary(filtered_vacancies)

            print(f"Найдено {len(sorted_vacancies)} вакансий:")

            # Постраничный просмотр
            paginate_display(sorted_vacancies, self._display_vacancies, 10, "Вакансии по зарплате")

        except Exception as e:
            logger.error(f"Ошибка при фильтрации по зарплате: {e}")
            print(f"Ошибка при фильтрации: {e}")

    def _show_keywords_statistics(self) -> None:
        """Показать статистику по ключевым словам"""
        try:
            vacancies = self.json_saver.get_vacancies()

            if not vacancies:
                print("Нет сохраненных вакансий.")
                return

            keywords_stats = self.vacancy_ops.get_vacancy_keywords_summary(vacancies)

            if not keywords_stats:
                print("Ключевые слова не найдены в сохраненных вакансиях.")
                return

            print(f"\nСтатистика по ключевым словам (всего вакансий: {len(vacancies)}):")
            print("-" * 50)

            # Показываем топ-20 ключевых слов
            for i, (keyword, count) in enumerate(list(keywords_stats.items())[:20], 1):
                percentage = (count / len(vacancies)) * 100
                print(f"{i:2}. {keyword:<20} - {count:3} вакансий ({percentage:.1f}%)")

            if len(keywords_stats) > 20:
                print(f"\n... и еще {len(keywords_stats) - 20} ключевых слов")

            # Предлагаем поиск по популярным ключевым словам
            print("\nВыберите ключевое слово для поиска (введите номер) или 0 для возврата:")
            try:
                choice = int(input("Ваш выбор: "))
                if 1 <= choice <= min(20, len(keywords_stats)):
                    keyword = list(keywords_stats.keys())[choice - 1]
                    filtered_vacancies = filter_vacancies_by_keyword(vacancies, keyword)
                    print(f"\nВакансии с ключевым словом '{keyword}':")

                    # Постраничный просмотр
                    paginate_display(filtered_vacancies, self._display_vacancies, 10, f"Вакансии с ключевым словом '{keyword}'")
            except ValueError:
                pass

        except Exception as e:
            logger.error(f"Ошибка при показе статистики: {e}")
            print(f"Ошибка при загрузке статистики: {e}")

    def _delete_saved_vacancies(self) -> None:
        """Удаление сохраненных вакансий"""
        try:
            vacancies = self.json_saver.get_vacancies()

            if not vacancies:
                print("Нет сохраненных вакансий для удаления.")
                return

            print(f"\nСохраненных вакансий: {len(vacancies)}")
            print("\nВыберите способ удаления:")
            print("1. Удалить все сохраненные вакансии")
            print("2. Удалить вакансии по ключевому слову")
            print("3. Удалить конкретную вакансию по ID")
            print("0. Отмена")

            choice = input("Ваш выбор: ").strip()

            if choice == "1":
                if confirm_action("Вы уверены, что хотите удалить ВСЕ сохраненные вакансии?"):
                    if self.json_saver.delete_all_vacancies():
                        print("Все сохраненные вакансии успешно удалены.")
                    else:
                        print("Ошибка при удалении вакансий.")
                else:
                    print("Удаление отменено.")

            elif choice == "2":
                keyword = get_user_input("Введите ключевое слово для удаления связанных вакансий: ")
                if keyword:
                    # Сначала покажем, что будет удалено
                    filtered_vacancies = filter_vacancies_by_keyword(vacancies, keyword)
                    if not filtered_vacancies:
                        print(f"Вакансии с ключевым словом '{keyword}' не найдены.")
                        return

                    print(f"\nНайдено {len(filtered_vacancies)} вакансий с ключевым словом '{keyword}':")

                    # Показываем список с постраничным просмотром
                    self._show_vacancies_for_deletion(filtered_vacancies, keyword)

            elif choice == "3":
                print("\nДля просмотра ID вакансий используйте пункт 2 (Показать все сохраненные вакансии)")
                vacancy_id = get_user_input("Введите полный ID вакансии для удаления: ")
                if vacancy_id:
                    # Найдем вакансию для подтверждения
                    vacancy_to_delete = None
                    for vacancy in vacancies:
                        if vacancy.vacancy_id == vacancy_id:
                            vacancy_to_delete = vacancy
                            break

                    if vacancy_to_delete:
                        print(f"\nВакансия для удаления:")
                        print(f"ID: {vacancy_to_delete.vacancy_id}")
                        print(f"Название: {vacancy_to_delete.title or 'Не указано'}")
                        if vacancy_to_delete.employer:
                            print(f"Компания: {vacancy_to_delete.employer.get('name', 'Не указана')}")
                        if vacancy_to_delete.salary:
                            print(f"Зарплата: {vacancy_to_delete.salary}")
                        else:
                            print("Зарплата: Не указана")
                        if vacancy_to_delete.experience:
                            print(f"Опыт: {vacancy_to_delete.experience}")
                        print(f"Ссылка: {vacancy_to_delete.url}")

                        if confirm_action("Удалить эту вакансию?"):
                            if self.json_saver.delete_vacancy_by_id(vacancy_id):
                                print("Вакансия успешно удалена.")
                            else:
                                print("Ошибка при удалении вакансии.")
                        else:
                            print("Удаление отменено.")
                    else:
                        print("Вакансия с указанным ID не найдена.")

            elif choice == "0":
                print("Назад в предыдущее меню.")

            else:
                print("Неверный выбор.")

        except Exception as e:
            logger.error(f"Ошибка при удалении вакансий: {e}")
            print(f"Ошибка при удалении: {e}")

    def _clear_api_cache(self) -> None:
        """Очистка кэша API"""
        try:
            sources = self.source_selector.get_user_source_choice()
            if not sources:
                return

            self.source_selector.display_sources_info(sources)
            if confirm_action("Вы уверены, что хотите очистить кэш выбранных источников?"):
                self.unified_api.clear_cache(sources)
                print("Кэш выбранных источников успешно очищен.")
            else:
                print("Очистка кэша отменена.")
        except Exception as e:
            logger.error(f"Ошибка при очистке кэша: {e}")
            print(f"Ошибка при очистке кэша: {e}")

    def _setup_superjob_api(self) -> None:
        """Настройка SuperJob API"""
        import os

        print("\n" + "="*60)
        print("НАСТРОЙКА SUPERJOB API")
        print("="*60)

        current_key = os.getenv('SUPERJOB_API_KEY')
        if current_key and current_key != 'v3.r.137440105.example.test_tool':
            print("✅ SuperJob API ключ уже настроен")
        else:
            print("❌ SuperJob API ключ не настроен или используется тестовый")

        print("\nДля получения API ключа SuperJob:")
        print("1. Перейдите на https://api.superjob.ru/register/")
        print("2. Зарегистрируйте ваше приложение")
        print("3. Получите Secret key")
        print("4. Добавьте его в Secrets как SUPERJOB_API_KEY")
        print("\nИнструкция по добавлению секретов:")
        print("• Откройте панель Secrets в левом меню")
        print("• Нажмите 'New Secret'")
        print("• Введите Key: SUPERJOB_API_KEY")
        print("• Введите Value: ваш настоящий API ключ")
        print("• Нажмите 'Add Secret'")
        print("• Перезапустите приложение")
        print("\n" + "="*60)

        input("\nНажмите Enter для продолжения...")

    def _display_vacancies(self, vacancies: List[Vacancy], start_number: int = 1) -> None:
        """
        Отображение списка вакансий

        Args:
            vacancies: Список вакансий для отображения
            start_number: Начальный номер для нумерации
        """
        for i, vacancy in enumerate(vacancies, start_number):
            display_vacancy_info(vacancy, i)

    def _display_vacancies_with_pagination(self, vacancies: List[Vacancy]) -> None:
        """
        Отображение вакансий с постраничным просмотром

        Args:
            vacancies: Список вакансий для отображения
        """
        paginate_display(vacancies, self._display_vacancies, 10, "Вакансии")

    def _show_vacancies_for_deletion(self, vacancies: List[Vacancy], keyword: str) -> None:
        """
        Отображение вакансий для удаления с возможностью выбора

        Args:
            vacancies: Список вакансий для удаления
            keyword: Ключевое слово для удаления
        """
        page_size = 10
        total_pages = (len(vacancies) + page_size - 1) // page_size
        current_page = 1

        while True:
            # Вычисляем индексы для текущей страницы
            start_idx = (current_page - 1) * page_size
            end_idx = min(start_idx + page_size, len(vacancies))
            current_vacancies = vacancies[start_idx:end_idx]

            print(f"\n--- Страница {current_page} из {total_pages} ---")
            print(f"Вакансии {start_idx + 1}-{end_idx} из {len(vacancies)} с ключевым словом '{keyword}':")
            print("-" * 80)

            # Отображаем вакансии с номерами
            for i, vacancy in enumerate(current_vacancies, start_idx + 1):
                print(f"{i}. ID: {vacancy.vacancy_id}")
                print(f"   Название: {vacancy.title or 'Не указано'}")
                if vacancy.employer:
                    print(f"   Компания: {vacancy.employer.get('name', 'Не указана')}")
                if vacancy.salary:
                    print(f"   Зарплата: {vacancy.salary}")
                else:
                    print("   Зарплата: Не указана")
                print(f"   Ссылка: {vacancy.url}")
                print("-" * 40)

            # Меню навигации и действий
            print("\n" + "=" * 60)
            print("Действия:")
            print("a - Удалить ВСЕ вакансии с этим ключевым словом")
            print("1-10 - Удалить конкретную вакансию по номеру на странице")
            print("8-9, 2-5 - Удалить диапазон вакансий (например: 8-9)")
            if current_page > 1:
                print("p - Предыдущая страница")
            if current_page < total_pages:
                print("n - Следующая страница")
            print("q - Назад в предыдущее меню.")
            print("=" * 60)

            choice = input("Ваш выбор: ").strip().lower()

            if choice == 'q':
                print("Удаление отменено.")
                break
            elif choice == 'a':
                if confirm_action(f"Удалить ВСЕ {len(vacancies)} вакансий с ключевым словом '{keyword}'?"):
                    deleted_count = self.json_saver.delete_vacancies_by_keyword(keyword)
                    if deleted_count > 0:
                        print(f"Удалено {deleted_count} вакансий.")
                    else:
                        print("Не удалось удалить вакансии.")
                break
            elif choice == 'n' and current_page < total_pages:
                current_page += 1
            elif choice == 'p' and current_page > 1:
                current_page -= 1
            elif '-' in choice and choice not in ['n', 'p']:
                # Обработка диапазона (например: 8-9)
                try:
                    start_str, end_str = choice.split('-', 1)
                    start_num = int(start_str.strip())
                    end_num = int(end_str.strip())

                    if start_num > end_num:
                        start_num, end_num = end_num, start_num

                    if 1 <= start_num <= len(vacancies) and 1 <= end_num <= len(vacancies):
                        # Получаем вакансии для удаления
                        vacancies_to_delete = []
                        for num in range(start_num, end_num + 1):
                            vacancies_to_delete.append(vacancies[num - 1])

                        print(f"\nВакансии для удаления (номера {start_num}-{end_num}):")
                        for i, vacancy in enumerate(vacancies_to_delete, start_num):
                            print(f"{i}. ID: {vacancy.vacancy_id}")
                            print(f"   Название: {vacancy.title or 'Не указано'}")
                            if vacancy.employer:
                                print(f"   Компания: {vacancy.employer.get('name', 'Не указана')}")
                            print(f"   Ссылка: {vacancy.url}")
                            print("-" * 40)

                        if confirm_action(f"Удалить {len(vacancies_to_delete)} вакансий?"):
                            deleted_count = 0
                            for vacancy in vacancies_to_delete:
                                if self.json_saver.delete_vacancy_by_id(vacancy.vacancy_id):
                                    vacancies.remove(vacancy)
                                    deleted_count += 1

                            if deleted_count > 0:
                                print(f"Удалено {deleted_count} вакансий.")
                                if not vacancies:
                                    print("Все вакансии с данным ключевым словом удалены.")
                                    break
                                # Пересчитываем страницы
                                total_pages = (len(vacancies) + page_size - 1) // page_size
                                if current_page > total_pages:
                                    current_page = total_pages
                            else:
                                print("Не удалось удалить вакансии.")
                        else:
                            print("Удаление отменено.")
                    else:
                        print(f"Введите диапазон в пределах от 1 до {len(vacancies)}")
                except ValueError:
                    print("Неверный формат диапазона. Используйте формат: 8-9")
            elif choice.isdigit():
                vacancy_num = int(choice)
                if 1 <= vacancy_num <= len(vacancies):
                    vacancy_to_delete = vacancies[vacancy_num - 1]
                    print(f"\nВакансия для удаления:")
                    print(f"ID: {vacancy_to_delete.vacancy_id}")
                    print(f"Название: {vacancy_to_delete.title or 'Не указано'}")
                    if vacancy_to_delete.employer:
                        print(f"Компания: {vacancy_to_delete.employer.get('name', 'Не указана')}")
                    if vacancy_to_delete.salary:
                        print(f"Зарплата: {vacancy_to_delete.salary}")
                    else:
                        print("Зарплата: Не указана")
                    print(f"Ссылка: {vacancy_to_delete.url}")

                    if confirm_action("Удалить эту вакансию?"):
                        if self.json_saver.delete_vacancy_by_id(vacancy_to_delete.vacancy_id):
                            print("Вакансия успешно удалена.")
                            # Удаляем из локального списка и обновляем отображение
                            vacancies.remove(vacancy_to_delete)
                            if not vacancies:
                                print("Все вакансии с данным ключевым словом удалены.")
                                break
                            # Пересчитываем страницы
                            total_pages = (len(vacancies) + page_size - 1) // page_size
                            if current_page > total_pages:
                                current_page = total_pages
                        else:
                            print("Ошибка при удалении вакансии.")
                    else:
                        print("Удаление отменено.")
                else:
                    print(f"Введите номер от 1 до {len(vacancies)}")
            else:
                print("Неверный выбор. Попробуйте снова.")
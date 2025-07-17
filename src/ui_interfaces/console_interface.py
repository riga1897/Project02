
import logging
from typing import List, Optional
from src.api_modules.hh_api import HeadHunterAPI
from src.vacancies.models import Vacancy
from src.storage.json_saver import JSONSaver
from src.utils.ui_paginator import paginate_display
from src.utils.ui_helpers import (
    get_user_input, get_positive_integer, parse_salary_range, confirm_action,
    filter_vacancies_by_keyword, filter_vacancies_by_min_salary,
    filter_vacancies_by_max_salary, filter_vacancies_by_salary_range,
    get_vacancies_with_salary, sort_vacancies_by_salary, display_vacancy_info,
    print_section_header, print_menu_separator, filter_vacancies_by_multiple_keywords,
    search_vacancies_advanced, get_vacancy_keywords_summary
)

logger = logging.getLogger(__name__)


class UserInterface:
    """Класс для взаимодействия с пользователем через консоль"""
    
    def __init__(self):
        self.hh_api = HeadHunterAPI()
        self.json_saver = JSONSaver()
    
    def run(self) -> None:
        """Основной цикл взаимодействия с пользователем"""
        print_section_header("Добро пожаловать в поисковик вакансий HH.ru!")
        
        while True:
            try:
                choice = self._show_menu()
                
                if choice == "1":
                    self._search_vacancies()
                elif choice == "2":
                    self._get_top_saved_vacancies_by_salary()
                elif choice == "3":
                    self._search_saved_vacancies_by_keyword()
                elif choice == "4":
                    self._advanced_search_vacancies()
                elif choice == "5":
                    self._filter_saved_vacancies_by_salary()
                elif choice == "6":
                    self._show_saved_vacancies()
                elif choice == "7":
                    self._show_keywords_statistics()
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
        """Отображение главного меню"""
        print("\n")
        print_menu_separator()
        print("Выберите действие:")
        print("1. Поиск вакансий по запросу (запрос к API)")
        print("2. Топ N сохраненных вакансий по зарплате")
        print("3. Поиск в сохраненных вакансиях с ключевым словом")
        print("4. Расширенный поиск (несколько ключевых слов)")
        print("5. Фильтр сохраненных вакансий по зарплате")
        print("6. Показать все сохраненные вакансии")
        print("7. Статистика по ключевым словам")
        print("0. Выход")
        print_menu_separator()
        
        return input("Ваш выбор: ").strip()
    
    def _search_vacancies(self) -> None:
        """Поиск вакансий по запросу пользователя"""
        query = get_user_input("\nВведите поисковый запрос: ")
        
        if not query:
            return
        
        print(f"\nИщем вакансии по запросу: '{query}'...")
        
        try:
            vacancies_data = self.hh_api.get_vacancies(query)
            
            if not vacancies_data:
                print("Вакансии не найдены.")
                return
            
            vacancies = Vacancy.cast_to_object_list(vacancies_data)
            
            print(f"\nНайдено {len(vacancies)} вакансий:")
            
            # Постраничный просмотр найденных вакансий
            self._display_vacancies_with_pagination(vacancies)
            
            if confirm_action("Сохранить найденные вакансии?"):
                self.json_saver.add_vacancy(vacancies)
                print(f"Сохранено {len(vacancies)} вакансий.")
                
        except Exception as e:
            logger.error(f"Ошибка при поиске вакансий: {e}")
            print(f"Ошибка при поиске: {e}")
    
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
            vacancies_with_salary = get_vacancies_with_salary(vacancies)
            
            if not vacancies_with_salary:
                print("Среди сохраненных вакансий нет ни одной с указанной зарплатой.")
                return
            
            # Сортируем по убыванию зарплаты
            sorted_vacancies = sort_vacancies_by_salary(vacancies_with_salary)
            
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
                    filtered_vacancies = [
                        v for v in vacancies 
                        if v.salary and v.salary.get_max_salary() and v.salary.get_max_salary() >= min_salary
                    ]
                    print(f"\nВакансии с зарплатой от {min_salary} руб.:")
                except ValueError:
                    print("Введите корректное число!")
                    return
                    
            elif choice == "2":
                try:
                    max_salary = int(input("Введите максимальную зарплату: "))
                    filtered_vacancies = [
                        v for v in vacancies 
                        if v.salary and (
                            (v.salary.salary_from and v.salary.salary_from <= max_salary) or
                            (v.salary.salary_to and v.salary.salary_to <= max_salary)
                        )
                    ]
                    print(f"\nВакансии с зарплатой до {max_salary} руб.:")
                except ValueError:
                    print("Введите корректное число!")
                    return
                    
            elif choice == "3":
                salary_range = input("Введите диапазон зарплат (пример: 100000 - 150000): ").strip()
                try:
                    # Парсим диапазон
                    if " - " in salary_range:
                        min_sal, max_sal = salary_range.split(" - ")
                        min_salary = int(min_sal.strip())
                        max_salary = int(max_sal.strip())
                    elif "-" in salary_range:
                        min_sal, max_sal = salary_range.split("-")
                        min_salary = int(min_sal.strip())
                        max_salary = int(max_sal.strip())
                    else:
                        print("Неверный формат диапазона. Используйте формат: 100000 - 150000")
                        return
                    
                    if min_salary > max_salary:
                        min_salary, max_salary = max_salary, min_salary
                    
                    filtered_vacancies = [
                        v for v in vacancies 
                        if v.salary and (
                            (v.salary.salary_from and min_salary <= v.salary.salary_from <= max_salary) or
                            (v.salary.salary_to and min_salary <= v.salary.salary_to <= max_salary) or
                            (v.salary.salary_from and v.salary.salary_to and 
                             v.salary.salary_from <= max_salary and v.salary.salary_to >= min_salary)
                        )
                    ]
                    print(f"\nВакансии с зарплатой в диапазоне {min_salary} - {max_salary} руб.:")
                except ValueError:
                    print("Введите корректные числа!")
                    return
                    
            else:
                print("Неверный выбор.")
                return
            
            if not filtered_vacancies:
                print("Вакансии с указанными критериями зарплаты не найдены.")
                return
            
            # Сортируем по убыванию зарплаты
            sorted_vacancies = sorted(
                filtered_vacancies,
                key=lambda x: x.salary.get_max_salary() or 0,
                reverse=True
            )
            
            print(f"Найдено {len(sorted_vacancies)} вакансий:")
            
            # Постраничный просмотр
            paginate_display(sorted_vacancies, self._display_vacancies, 10, "Вакансии по зарплате")
                
        except Exception as e:
            logger.error(f"Ошибка при фильтрации по зарплате: {e}")
            print(f"Ошибка при фильтрации: {e}")
    
    def _display_vacancies(self, vacancies: List[Vacancy], start_number: int = 1) -> None:
        """Отображение списка вакансий"""
        for i, vacancy in enumerate(vacancies, start_number):
            display_vacancy_info(vacancy, i)
    
    def _advanced_search_vacancies(self) -> None:
        """Расширенный поиск по вакансиям"""
        try:
            vacancies = self.json_saver.get_vacancies()
            
            if not vacancies:
                print("Нет сохраненных вакансий.")
                return
            
            print("\nРасширенный поиск:")
            print("Введите ключевые слова через запятую или используйте операторы AND/OR")
            print("Примеры:")
            print("  - python, django, postgresql")
            print("  - python AND django")
            print("  - python OR java")
            
            query = get_user_input("Введите поисковый запрос: ")
            
            if not query:
                return
            
            # Определяем тип поиска
            if ',' in query and ' AND ' not in query.upper() and ' OR ' not in query.upper():
                # Поиск по нескольким ключевым словам через запятую
                keywords = [kw.strip() for kw in query.split(',')]
                filtered_vacancies = filter_vacancies_by_multiple_keywords(vacancies, keywords)
                print(f"\nПоиск по ключевым словам: {', '.join(keywords)}")
            else:
                # Продвинутый поиск с операторами
                filtered_vacancies = search_vacancies_advanced(vacancies, query)
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
    
    def _show_keywords_statistics(self) -> None:
        """Показать статистику по ключевым словам"""
        try:
            vacancies = self.json_saver.get_vacancies()
            
            if not vacancies:
                print("Нет сохраненных вакансий.")
                return
            
            keywords_stats = get_vacancy_keywords_summary(vacancies)
            
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

    def _display_vacancies_with_pagination(self, vacancies: List[Vacancy]) -> None:
        """Отображение вакансий с постраничным просмотром"""
        paginate_display(vacancies, self._display_vacancies, 10, "Вакансии")

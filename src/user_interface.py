
import logging
from typing import List, Optional
from src.api_modules.hh_api import HeadHunterAPI
from src.vacancies.models import Vacancy
from src.storage.json_saver import JSONSaver
from src.utils.ui_paginator import paginate_display

logger = logging.getLogger(__name__)


class UserInterface:
    """Класс для взаимодействия с пользователем через консоль"""
    
    def __init__(self):
        self.hh_api = HeadHunterAPI()
        self.json_saver = JSONSaver()
    
    def run(self) -> None:
        """Основной цикл взаимодействия с пользователем"""
        print("=" * 50)
        print("Добро пожаловать в поисковик вакансий HH.ru!")
        print("=" * 50)
        
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
                    self._filter_saved_vacancies_by_salary()
                elif choice == "5":
                    self._show_saved_vacancies()
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
        print("\n" + "-" * 40)
        print("Выберите действие:")
        print("1. Поиск вакансий по запросу (запрос к API)")
        print("2. Топ N сохраненных вакансий по зарплате")
        print("3. Поиск в сохраненных вакансиях с ключевым словом")
        print("4. Фильтр сохраненных вакансий по зарплате")
        print("5. Показать все сохраненные вакансии")
        print("0. Выход")
        print("-" * 40)
        
        return input("Ваш выбор: ").strip()
    
    def _search_vacancies(self) -> None:
        """Поиск вакансий по запросу пользователя"""
        query = input("\nВведите поисковый запрос: ").strip()
        
        if not query:
            print("Запрос не может быть пустым!")
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
            
            if self._ask_save_vacancies():
                self.json_saver.add_vacancy(vacancies)
                print(f"Сохранено {len(vacancies)} вакансий.")
                
        except Exception as e:
            logger.error(f"Ошибка при поиске вакансий: {e}")
            print(f"Ошибка при поиске: {e}")
    
    def _get_top_saved_vacancies_by_salary(self) -> None:
        """Получение топ N сохраненных вакансий по зарплате"""
        try:
            n = int(input("\nВведите количество вакансий для отображения: "))
            if n <= 0:
                print("Количество должно быть положительным числом!")
                return
        except ValueError:
            print("Введите корректное число!")
            return
        
        try:
            vacancies = self.json_saver.get_vacancies()
            
            if not vacancies:
                print("Нет сохраненных вакансий.")
                return
            
            # Фильтруем вакансии с зарплатой
            vacancies_with_salary = [
                v for v in vacancies 
                if v.salary and (v.salary.salary_from or v.salary.salary_to)
            ]
            
            if not vacancies_with_salary:
                print("Среди сохраненных вакансий нет ни одной с указанной зарплатой.")
                return
            
            # Сортируем по убыванию зарплаты
            sorted_vacancies = sorted(
                vacancies_with_salary,
                key=lambda x: x.salary.get_max_salary() or 0,
                reverse=True
            )
            
            top_vacancies = sorted_vacancies[:n]
            
            print(f"\nТоп {len(top_vacancies)} сохраненных вакансий по зарплате:")
            self._display_vacancies(top_vacancies)
                
        except Exception as e:
            logger.error(f"Ошибка при получении топ сохраненных вакансий: {e}")
            print(f"Ошибка при поиске: {e}")
    
    def _search_saved_vacancies_by_keyword(self) -> None:
        """Поиск в сохраненных вакансиях с ключевым словом в описании"""
        keyword = input("\nВведите ключевое слово для поиска в описании: ").strip()
        
        if not keyword:
            print("Ключевое слово не может быть пустым!")
            return
        
        try:
            vacancies = self.json_saver.get_vacancies()
            
            if not vacancies:
                print("Нет сохраненных вакансий.")
                return
            
            # Фильтруем по ключевому слову в описании
            filtered_vacancies = []
            keyword_lower = keyword.lower()
            
            for vacancy in vacancies:
                description_text = ""
                if vacancy.title:
                    description_text += vacancy.title.lower()
                if vacancy.description:
                    description_text += " " + vacancy.description.lower()
                if vacancy.requirements:
                    description_text += " " + vacancy.requirements.lower()
                if vacancy.responsibilities:
                    description_text += " " + vacancy.responsibilities.lower()
                
                if keyword_lower in description_text:
                    filtered_vacancies.append(vacancy)
            
            if not filtered_vacancies:
                print(f"Среди сохраненных вакансий не найдено ни одной с ключевым словом '{keyword}'.")
                return
            
            print(f"\nНайдено {len(filtered_vacancies)} сохраненных вакансий с ключевым словом '{keyword}':")
            self._display_vacancies(filtered_vacancies[:10])  # Показываем первые 10
                
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
            self._display_vacancies(sorted_vacancies[:10])  # Показываем первые 10
            
            if len(sorted_vacancies) > 10:
                print(f"\n... и еще {len(sorted_vacancies) - 10} вакансий.")
                
        except Exception as e:
            logger.error(f"Ошибка при фильтрации по зарплате: {e}")
            print(f"Ошибка при фильтрации: {e}")
    
    def _display_vacancies(self, vacancies: List[Vacancy], start_number: int = 1) -> None:
        """Отображение списка вакансий"""
        for i, vacancy in enumerate(vacancies, start_number):
            print(f"\n{i}. {vacancy.title}")
            
            if vacancy.employer:
                company = vacancy.employer.get('name', 'Не указана')
                print(f"   Компания: {company}")
            
            if vacancy.salary:
                print(f"   Зарплата: {vacancy.salary}")
            else:
                print("   Зарплата: Не указана")
            
            if vacancy.experience:
                print(f"   Опыт: {vacancy.experience}")
            
            if vacancy.url:
                print(f"   Ссылка: {vacancy.url}")
            
            print("-" * 80)
    
    def _display_vacancies_with_pagination(self, vacancies: List[Vacancy]) -> None:
        """Отображение вакансий с постраничным просмотром"""
        paginate_display(vacancies, self._display_vacancies, 10, "Вакансии")

    def _ask_save_vacancies(self) -> bool:
        """Спрашивает пользователя, хочет ли он сохранить вакансии"""
        while True:
            answer = input("\nСохранить найденные вакансии? (y/n): ").strip().lower()
            if answer in ['y', 'yes', 'д', 'да']:
                return True
            elif answer in ['n', 'no', 'н', 'нет']:
                return False
            else:
                print("Введите 'y' для да или 'n' для нет.")


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

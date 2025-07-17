
import logging
from typing import List, Optional
from src.api_modules.hh_api import HeadHunterAPI
from src.vacancies.models import Vacancy
from src.storage.json_saver import JSONSaver

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
                    self._get_top_vacancies_by_salary()
                elif choice == "3":
                    self._search_vacancies_by_keyword()
                elif choice == "4":
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
        print("1. Поиск вакансий по запросу")
        print("2. Топ N вакансий по зарплате")
        print("3. Поиск вакансий с ключевым словом")
        print("4. Показать сохраненные вакансии")
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
            self._display_vacancies(vacancies[:10])  # Показываем первые 10
            
            if self._ask_save_vacancies():
                self.json_saver.add_vacancy(vacancies)
                print(f"Сохранено {len(vacancies)} вакансий.")
                
        except Exception as e:
            logger.error(f"Ошибка при поиске вакансий: {e}")
            print(f"Ошибка при поиске: {e}")
    
    def _get_top_vacancies_by_salary(self) -> None:
        """Получение топ N вакансий по зарплате"""
        try:
            n = int(input("\nВведите количество вакансий для отображения: "))
            if n <= 0:
                print("Количество должно быть положительным числом!")
                return
        except ValueError:
            print("Введите корректное число!")
            return
        
        query = input("Введите поисковый запрос: ").strip()
        
        if not query:
            print("Запрос не может быть пустым!")
            return
        
        print(f"\nИщем топ {n} вакансий по зарплате для запроса: '{query}'...")
        
        try:
            # Получаем вакансии только с указанной зарплатой
            vacancies_data = self.hh_api.get_vacancies(query, only_with_salary=True)
            
            if not vacancies_data:
                print("Вакансии с указанной зарплатой не найдены.")
                return
            
            vacancies = Vacancy.cast_to_object_list(vacancies_data)
            
            # Сортируем по максимальной зарплате
            vacancies_with_salary = [
                v for v in vacancies 
                if v.salary and (v.salary.salary_from or v.salary.salary_to)
            ]
            
            if not vacancies_with_salary:
                print("Не найдено вакансий с корректно указанной зарплатой.")
                return
            
            # Сортируем по убыванию зарплаты
            sorted_vacancies = sorted(
                vacancies_with_salary,
                key=lambda x: x.salary.get_max_salary() or 0,
                reverse=True
            )
            
            top_vacancies = sorted_vacancies[:n]
            
            print(f"\nТоп {len(top_vacancies)} вакансий по зарплате:")
            self._display_vacancies(top_vacancies)
            
            if self._ask_save_vacancies():
                self.json_saver.add_vacancy(top_vacancies)
                print(f"Сохранено {len(top_vacancies)} вакансий.")
                
        except Exception as e:
            logger.error(f"Ошибка при получении топ вакансий: {e}")
            print(f"Ошибка при поиске: {e}")
    
    def _search_vacancies_by_keyword(self) -> None:
        """Поиск вакансий с ключевым словом в описании"""
        base_query = input("\nВведите основной поисковый запрос: ").strip()
        keyword = input("Введите ключевое слово для поиска в описании: ").strip()
        
        if not base_query or not keyword:
            print("Запрос и ключевое слово не могут быть пустыми!")
            return
        
        print(f"\nИщем вакансии по запросу '{base_query}' с ключевым словом '{keyword}'...")
        
        try:
            vacancies_data = self.hh_api.get_vacancies(base_query)
            
            if not vacancies_data:
                print("Вакансии не найдены.")
                return
            
            vacancies = Vacancy.cast_to_object_list(vacancies_data)
            
            # Фильтруем по ключевому слову в описании
            filtered_vacancies = []
            keyword_lower = keyword.lower()
            
            for vacancy in vacancies:
                description_text = ""
                if vacancy.description:
                    description_text += vacancy.description.lower()
                if vacancy.requirements:
                    description_text += " " + vacancy.requirements.lower()
                if vacancy.responsibilities:
                    description_text += " " + vacancy.responsibilities.lower()
                
                if keyword_lower in description_text:
                    filtered_vacancies.append(vacancy)
            
            if not filtered_vacancies:
                print(f"Вакансии с ключевым словом '{keyword}' не найдены.")
                return
            
            print(f"\nНайдено {len(filtered_vacancies)} вакансий с ключевым словом '{keyword}':")
            self._display_vacancies(filtered_vacancies[:10])  # Показываем первые 10
            
            if self._ask_save_vacancies():
                self.json_saver.add_vacancy(filtered_vacancies)
                print(f"Сохранено {len(filtered_vacancies)} вакансий.")
                
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
            page_size = 10
            total_pages = (len(vacancies) + page_size - 1) // page_size
            current_page = 1
            
            while True:
                # Вычисляем индексы для текущей страницы
                start_idx = (current_page - 1) * page_size
                end_idx = min(start_idx + page_size, len(vacancies))
                
                print(f"\n--- Страница {current_page} из {total_pages} ---")
                print(f"Показываем вакансии {start_idx + 1}-{end_idx} из {len(vacancies)}:")
                
                self._display_vacancies(vacancies[start_idx:end_idx], start_idx + 1)
                
                # Меню навигации
                print("\n" + "=" * 50)
                print("Навигация:")
                if current_page > 1:
                    print("p - Предыдущая страница")
                if current_page < total_pages:
                    print("n - Следующая страница")
                print("q - Выход к главному меню")
                print("=" * 50)
                
                choice = input("Ваш выбор: ").strip().lower()
                
                if choice == 'q':
                    break
                elif choice == 'n' and current_page < total_pages:
                    current_page += 1
                elif choice == 'p' and current_page > 1:
                    current_page -= 1
                else:
                    print("Неверный выбор. Попробуйте снова.")
                
        except Exception as e:
            logger.error(f"Ошибка при отображении сохраненных вакансий: {e}")
            print(f"Ошибка при загрузке вакансий: {e}")
    
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

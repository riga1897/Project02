import logging
from typing import List
from src.api_modules.hh_api import HeadHunterAPI
from src.vacancies.models import Vacancy
from src.storage.json_saver import JSONSaver

def setup_logging() -> None:
    """Настройка логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )

def get_vacancies(hh_api: HeadHunterAPI, query: str) -> List[Vacancy]:
    """Получение вакансий с API"""
    try:
        vacancies_data = hh_api.get_vacancies(query)
        if not vacancies_data:
            logging.warning(f"Не найдено вакансий по запросу: {query}")
            return []
        return Vacancy.cast_to_object_list(vacancies_data)
    except Exception as e:
        logging.error(f"Ошибка при получении вакансий: {e}")
        return []

def main() -> None:
    """Основная функция приложения"""
    setup_logging()
    logging.info("Запуск приложения")

    try:
        hh_api = HeadHunterAPI()
        json_saver = JSONSaver()

        vacancies = get_vacancies(hh_api, "Python")
        if not vacancies:
            logging.warning("Нет вакансий для сохранения")
            return

        json_saver.add_vacancy(vacancies)
        logging.info(f"Сохранено {len(vacancies)} вакансий")

        print("\nПоследние вакансии:")
        for i, vacancy in enumerate(json_saver.get_vacancies(), 1):
            print(f"\n{i}. {vacancy}")
            if i >= 3:
                break

    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
    finally:
        logging.info("Завершение работы")

if __name__ == "__main__":
    main()
    
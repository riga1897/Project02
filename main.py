from src.vacancies.models import Vacancy
from src.storage.json_saver import JSONSaver

def main():
    """Пример использования классов для работы с вакансиями"""

    # Пример данных с HeadHunter API (с неожиданным полем 'id')
    hh_vacancies = [
        {
            "id": "123",
            "title": "Python Developer",
            "url": "https://hh.ru/vacancy/123",
            "salary": "100 000-150 000 руб.",
            "description": "Описание вакансии...",
            "extra_field": "some value"  # Дополнительное поле
        }
    ]

    # 1. Преобразование JSON в объекты (теперь работает с лишними полями)
    vacancies = Vacancy.cast_to_object_list(hh_vacancies)
    print(f"Преобразовано вакансий: {len(vacancies)}")
    print(f"Первая вакансия: {vacancies[0]}")

    # 2. Создание отдельной вакансии
    new_vacancy = Vacancy(
        "Java Developer",
        "https://hh.ru/vacancy/456",
        "120 000 руб.",
        "Требуется Java-разработчик"
    )

    # 3. Работа с хранилищем
    saver = JSONSaver('vacancies.json')

    # Добавление вакансий
    for v in vacancies:
        saver.add_vacancy(v)
    saver.add_vacancy(new_vacancy)

    # Получение и вывод всех вакансий
    print("\nВсе вакансии в хранилище:")
    for v in saver.get_vacancies():
        print(f"- {v.title}: {v.salary}")


    #api = HeadHunterAPI()

    # Первый запрос - идёт реальный запрос к API
    vacancies = api.get_vacancies("Python")

    # Повторный запрос - берётся из кэша
    cached_vacancies = api.get_vacancies("Python")

    # Принудительное обновление
    api.clear_cache()
    fresh_vacancies = api.get_vacancies("Python")

    # 1. Инициализация
    from src.api.hh_api import HeadHunterAPI
    api = HeadHunterAPI()

    # 2. Запрос с автоматическим сохранением
    results = api.get_vacancies("Python", area=1, per_page=100)

    # 3. Ручное чтение сырых данных
    from src.utils.cache import FileCache
    cache = FileCache("hh_cache")

    # Получить все файлы для запроса "Python"
    python_files = list(cache.cache_dir.glob("hh_text-Python*"))

    # Прочитать конкретный файл
    with open(python_files[0], 'r', encoding='utf-8') as f:
        raw_json = json.load(f)
        print(raw_json.keys())  # ['items', 'found', 'pages', 'per_page', ...]

    sj_cache = FileCache("data/cache/sj")

    from pathlib import Path

    def init_project_structure():
        """Создает необходимые директории при запуске"""
        Path("data/cache/hh").mkdir(parents=True, exist_ok=True)
        Path("data/cache/sj").mkdir(parents=True, exist_ok=True)  # Для будущих платформ

    if __name__ == "__main__":
        init_project_structure()
        # ... запуск приложения ...

if __name__ == "__main__":
    main()
    
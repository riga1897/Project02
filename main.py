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

if __name__ == "__main__":
    main()
    
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Union, Dict, Any

from src.vacancies.models import Vacancy

logger = logging.getLogger(__name__)


class JSONSaver:
    """
    Класс для работы с JSON хранилищем вакансий.
    
    Обеспечивает сохранение, загрузку, обновление и удаление вакансий
    в JSON формате с валидацией данных и обработкой ошибок.
    
    Attributes:
        _filename: Путь к файлу для хранения данных вакансий
    """

    __slots__ = ('_filename',)

    def __init__(self, filename: str = "data/storage/vacancies.json"):
        self._filename = self._validate_filename(filename)
        self._ensure_data_directory()
        self._ensure_file_exists()

    @staticmethod
    def _validate_filename(filename: str) -> str:
        """Валидация имени файла"""
        if not filename or not isinstance(filename, str):
            return "data/storage/vacancies.json"
        return filename.strip()

    @property
    def filename(self) -> str:
        """Получение имени файла"""
        return self._filename

    @staticmethod
    def _ensure_data_directory() -> None:
        """Создает директорию для хранения данных, если она не существует."""
        data_dir = Path("data/storage")
        data_dir.mkdir(parents=True, exist_ok=True)

    def _ensure_file_exists(self) -> None:
        """Создает файл, если он не существует"""
        file_path = Path(self.filename)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch(exist_ok=True)

    def _backup_corrupted_file(self) -> None:
        """Создает резервную копию поврежденного файла"""
        try:
            from datetime import datetime
            
            file_path = Path(self.filename)
            if file_path.exists():
                backup_name = f"{file_path.stem}_corrupted_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_path.suffix}"
                backup_path = file_path.parent / backup_name
                
                import shutil
                shutil.copy2(file_path, backup_path)
                logger.info(f"Создана резервная копия поврежденного файла: {backup_path}")
                
                # Создаем новый пустой файл
                with open(self.filename, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
                logger.info(f"Создан новый пустой файл: {self.filename}")
        except Exception as e:
            logger.error(f"Ошибка создания резервной копии: {e}")

    def add_vacancy(self, vacancies: Union[Vacancy, List[Vacancy]]) -> List[str]:
        """
        Добавляет вакансии в файл с выводом информационных сообщений об изменениях.
        Возвращает список сообщений об обновлениях.
        """
        if not isinstance(vacancies, list):
            vacancies = [vacancies]

        existing_vacancies = self.load_vacancies()
        existing_map = {v.vacancy_id: v for v in existing_vacancies}

        update_messages: List[str] = []
        new_count = 0

        for new_vac in vacancies:
            if new_vac.vacancy_id in existing_map:
                existing_vac = existing_map[new_vac.vacancy_id]
                changed_fields = []

                # Проверяем каждое поле на изменения
                for field in ['title', 'url', 'salary', 'description', 'updated_at']:
                    old_val = getattr(existing_vac, field, None)
                    new_val = getattr(new_vac, field, None)

                    if old_val != new_val:
                        changed_fields.append(field)

                if changed_fields:
                    # Обновляем только изменившиеся поля
                    for field in changed_fields:
                        setattr(existing_vac, field, getattr(new_vac, field))

                    message = (
                        f"Вакансия ID {new_vac.vacancy_id} обновлена. "
                        f"Измененные поля: {', '.join(changed_fields)}. "
                        f"Название: '{new_vac.title}'"
                    )
                    update_messages.append(message)
            else:
                existing_map[new_vac.vacancy_id] = new_vac
                message = f"Добавлена новая вакансия ID {new_vac.vacancy_id}: '{new_vac.title}'"
                update_messages.append(message)
                new_count += 1

        # Сохраняем все вакансии
        if update_messages:
            self._save_to_file(list(existing_map.values()))

        return update_messages

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """Парсит дату из строки в объект datetime"""
        try:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
        except (ValueError, TypeError):
            return datetime.min  # Возвращаем минимальную дату если парсинг не удался

    def load_vacancies(self) -> List[Vacancy]:
        """Загружает вакансии с улучшенной обработкой ошибок"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
                # Если файл пустой, возвращаем пустой список
                if not content:
                    logger.info("Файл пустой, возвращаем пустой список")
                    return []
                
                data = json.loads(content)

                if not isinstance(data, list):
                    logger.warning(f"Ожидался список, получен {type(data)}. Создаем резервную копию и возвращаем пустой список")
                    self._backup_corrupted_file()
                    return []

                vacancies = []
                for item in data:
                    try:
                        if not isinstance(item, dict):
                            logger.warning(f"Пропущен некорректный элемент типа {type(item)}")
                            continue

                        vacancy = Vacancy.from_dict(item)
                        vacancies.append(vacancy)
                    except Exception as e:
                        logger.error(f"Ошибка создания вакансии: {e}\nДанные: {item}")

                return vacancies

        except FileNotFoundError:
            logger.info("Файл не найден, будет создан новый")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка формата JSON файла: {e}. Создаем резервную копию и возвращаем пустой список")
            self._backup_corrupted_file()
            return []
        except Exception as e:
            logger.error(f"Ошибка загрузки файла: {e}. Создаем резервную копию и возвращаем пустой список")
            self._backup_corrupted_file()
            return []

    def get_vacancies(self) -> List[Vacancy]:
        """
        Возвращает список вакансий с учетом фильтров
        :return: Список вакансий
        """
        return self.load_vacancies()

    def delete_all_vacancies(self) -> bool:
        """
        Удаляет все сохраненные вакансии

        Returns:
            bool: True если операция успешна, False иначе
        """
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            logger.info("Все вакансии удалены")
            return True
        except Exception as e:
            logger.error(f"Ошибка при удалении всех вакансий: {e}")
            return False

    def delete_vacancy_by_id(self, vacancy_id: str) -> bool:
        """
        Удаляет вакансию по ID

        Args:
            vacancy_id: ID вакансии для удаления

        Returns:
            bool: True если вакансия найдена и удалена, False иначе
        """
        try:
            vacancies = self.load_vacancies()
            initial_count = len(vacancies)

            # Фильтруем вакансии, исключая нужную.
            # Проверяем vacancy_id и id для совместимости.
            filtered_vacancies = [
                v for v in vacancies 
                if v.vacancy_id != vacancy_id and getattr(v, 'id', None) != vacancy_id
            ]

            if len(filtered_vacancies) == initial_count:
                logger.warning(f"Вакансия с ID {vacancy_id} не найдена")
                return False

            self._save_to_file(filtered_vacancies)
            logger.info(f"Вакансия с ID {vacancy_id} удалена")
            return True

        except Exception as e:
            logger.error(f"Ошибка при удалении вакансии {vacancy_id}: {e}")
            return False

    def delete_vacancies_by_keyword(self, keyword: str) -> int:
        """
        Удаляет вакансии, содержащие указанное ключевое слово

        Args:
            keyword: Ключевое слово для поиска

        Returns:
            int: Количество удаленных вакансий
        """
        try:
            from src.utils.ui_helpers import filter_vacancies_by_keyword

            vacancies = self.load_vacancies()
            initial_count = len(vacancies)

            # Находим вакансии для удаления
            vacancies_to_delete = filter_vacancies_by_keyword(vacancies, keyword)
            delete_ids = {v.vacancy_id for v in vacancies_to_delete}

            # Фильтруем вакансии, исключая найденные
            filtered_vacancies = [v for v in vacancies if v.vacancy_id not in delete_ids]

            deleted_count = initial_count - len(filtered_vacancies)

            if deleted_count > 0:
                self._save_to_file(filtered_vacancies)
                logger.info(f"Удалено {deleted_count} вакансий по ключевому слову '{keyword}'")

            return deleted_count

        except Exception as e:
            logger.error(f"Ошибка при удалении вакансий по ключевому слову '{keyword}': {e}")
            return 0

    def _ensure_json_serializable(self, obj):
        """
        Обеспечивает JSON-преобразование объекта
        """
        if obj is None:
            return None
        elif isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, dict):
            return {key: self._ensure_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._ensure_json_serializable(item) for item in obj]
        else:
            # Преобразуем неподдерживаемые типы в строку
            return str(obj)

    def _save_to_file(self, vacancies: List[Vacancy]) -> None:
        """Сохраняет вакансии с дополнительной валидацией"""
        valid_data = []
        error_count = 0

        for vac in vacancies:
            try:
                if not isinstance(vac, Vacancy):
                    raise ValueError(f"Ожидался объект Vacancy, получен {type(vac)}")

                vac_dict = vac.to_dict()
                # Дополнительная проверка структуры.
                # Проверяем наличие ID (может быть как 'id', так и 'vacancy_id').
                has_id = 'id' in vac_dict or 'vacancy_id' in vac_dict
                if not (has_id and 'title' in vac_dict and 'url' in vac_dict):
                    raise ValueError("Отсутствуют обязательные поля")

                valid_data.append(vac_dict)
            except Exception as e:
                error_count += 1
                logger.error(f"Ошибка валидации вакансии: {e}\nВакансия: {vars(vac)}")

        if error_count:
            logger.warning(f"Пропущено {error_count} невалидных вакансий")

        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(valid_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Успешно сохранено {len(valid_data)} вакансий")
        except Exception as e:
            logger.critical(f"Ошибка записи в файл: {e}")
            raise

        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(valid_data, f, ensure_ascii=False, indent=2)

    def get_file_size(self) -> int:
        """
        Получает размер файла в байтах
        
        Returns:
            int: Размер файла в байтах, 0 если файл не существует
        """
        try:
            file_path = Path(self.filename)
            if file_path.exists():
                return file_path.stat().st_size
            return 0
        except Exception as e:
            logger.error(f"Ошибка получения размера файла: {e}")
            return 0

    @staticmethod
    def _vacancy_to_dict(vacancy: Vacancy) -> Dict[str, Any]:
        """Преобразование объекта Vacancy в словарь"""
        salary_dict = None
        if vacancy.salary:
            salary_dict = {
                'from': vacancy.salary.salary_from,
                'to': vacancy.salary.salary_to,
                'currency': vacancy.salary.currency
            }

        return {
            'title': vacancy.title,
            'url': vacancy.url,
            'salary': salary_dict,
            'description': vacancy.description,
            'requirements': vacancy.requirements,
            'responsibilities': vacancy.responsibilities,
            'experience': vacancy.experience,
            'employment': vacancy.employment,
            'schedule': vacancy.schedule,
            'employer': vacancy.employer,
            'area': vacancy.area,
            'vacancy_id': vacancy.vacancy_id,
            'published_at': vacancy.published_at
        }
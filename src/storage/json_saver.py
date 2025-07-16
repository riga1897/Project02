from datetime import datetime
from typing import List, Union, Dict, Any
import json
import logging
from pathlib import Path
from src.vacancies.models import Vacancy

logger = logging.getLogger(__name__)


class JSONSaver:
    """Класс для сохранения вакансий в JSON-файл с обновлением существующих"""

    def __init__(self, filename: str = "vacancies.json"):
        self.filename = filename
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Создает файл, если он не существует"""
        Path(self.filename).touch(exist_ok=True)

        from typing import List, Union, Optional

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

    def _parse_date(self, date_str: str) -> datetime:
        """Парсит дату из строки в объект datetime"""
        try:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
        except (ValueError, TypeError):
            return datetime.min  # Возвращаем минимальную дату если парсинг не удался

    def load_vacancies(self) -> List[Vacancy]:
        """Загружает вакансии с улучшенной обработкой ошибок"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

                if not isinstance(data, list):
                    raise ValueError(f"Ожидался список, получен {type(data)}")

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
        except json.JSONDecodeError:
            logger.error("Ошибка формата файла")
            return []
        except Exception as e:
            logger.critical(f"Критическая ошибка загрузки: {e}")
            raise

        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Ошибка загрузки файла: {e}")
            return []

    def _save_to_file(self, vacancies: List[Vacancy]) -> None:
        """Сохраняет вакансии с дополнительной валидацией"""
        valid_data = []
        error_count = 0

        for vac in vacancies:
            try:
                if not isinstance(vac, Vacancy):
                    raise ValueError(f"Ожидался объект Vacancy, получен {type(vac)}")

                vac_dict = vac.to_dict()
                # Дополнительная проверка структуры
                if not all(key in vac_dict for key in ['id', 'title', 'url']):
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
            
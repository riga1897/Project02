from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import logging
from .abstract import AbstractVacancy
from src.utils.salary import Salary

logger = logging.getLogger(__name__)


class SuperJobVacancy(AbstractVacancy):
    """Класс для представления вакансии SuperJob"""

    def __init__(
        self,
        title: str,
        url: str,
        salary: Optional[Dict[str, Any]],
        description: str,
        requirements: Optional[str] = None,
        responsibilities: Optional[str] = None,
        employer: Optional[Dict[str, Any]] = None,
        experience: Optional[str] = None,
        employment: Optional[str] = None,
        schedule: Optional[str] = None,
        published_at: Optional[str] = None,
        skills: Optional[List[Dict[str, str]]] = None,
        keywords: Optional[List[str]] = None,
        detailed_description: Optional[str] = None,
        benefits: Optional[str] = None,
        vacancy_id: Optional[str] = None,
        source: str = "superjob.ru"
    ):
        self.vacancy_id = vacancy_id or str(uuid.uuid4())
        self.title = title
        self.url = url
        self.salary = self._validate_salary(salary)
        self.description = description
        self.requirements = requirements
        self.responsibilities = responsibilities
        self.employer = employer
        self.experience = experience
        self.employment = employment
        self.schedule = schedule
        self.published_at = self._parse_datetime(published_at) if published_at else None
        self.skills = skills or []
        self.keywords = keywords or []
        self.detailed_description = detailed_description or description
        self.benefits = benefits
        self.source = source

    @staticmethod
    def _validate_salary(salary_data: Optional[Dict[str, Any]]) -> Optional[Salary]:
        """Валидация и создание объекта зарплаты"""
        if not salary_data:
            return None

        try:
            # Получаем значения зарплаты
            salary_from = salary_data.get("payment_from")
            salary_to = salary_data.get("payment_to")

            # Если оба значения равны 0, считаем что зарплата не указана
            if not salary_from and not salary_to:
                return None

            # Конвертируем 0 в None для корректного отображения
            if salary_from == 0:
                salary_from = None
            if salary_to == 0:
                salary_to = None

            return Salary({
                "from": salary_from,
                "to": salary_to,
                "currency": "RUB",
                "period": "месяц"
            })
        except Exception as e:
            logger.warning(f"Ошибка создания зарплаты: {e}")
            return None

    @staticmethod
    def _parse_datetime(timestamp) -> datetime:
        """Парсинг времени из timestamp или строки SuperJob"""
        if isinstance(timestamp, int):
            return datetime.fromtimestamp(timestamp)
        elif isinstance(timestamp, str):
            # Обработка строкового формата даты SuperJob
            try:
                # Попробуем несколько форматов
                for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S%z']:
                    try:
                        return datetime.strptime(timestamp, fmt)
                    except ValueError:
                        continue
                # Если не удалось распарсить, используем текущее время
                logger.warning(f"Не удалось распарсить дату: {timestamp}")
                return datetime.now()
            except Exception as e:
                logger.error(f"Ошибка парсинга даты {timestamp}: {e}")
                return datetime.now()
        else:
            return datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SuperJobVacancy':
        """Создает объект SuperJobVacancy из данных API"""
        try:
            if not isinstance(data, dict):
                raise ValueError("Данные должны быть словарем")

            # Обработка работодателя
            employer = None
            if data.get("firm_name"):
                employer = {"name": data.get("firm_name")}

            # Обработка зарплаты
            salary = None
            if data.get("payment_from") or data.get("payment_to"):
                salary = {
                    "payment_from": data.get("payment_from", 0),
                    "payment_to": data.get("payment_to", 0),
                    "currency": data.get("currency", "rub")
                }

            return cls(
                vacancy_id=str(data.get("id", "")),
                title=data.get("profession", ""),
                url=data.get("link", ""),
                salary=salary,
                description=data.get("vacancyRichText", ""),
                requirements=data.get("candidat", ""),
                responsibilities=data.get("work", ""),
                employer=employer,
                experience=data.get("experience", {}).get("title") if data.get("experience") else None,
                employment=data.get("type_of_work", {}).get("title") if data.get("type_of_work") else None,
                schedule=None,  # SuperJob не всегда предоставляет эту информацию
                published_at=data.get("date_published"),
                source="superjob.ru"
            )

        except Exception as e:
            logger.error(f"Ошибка создания SuperJob вакансии из данных: {data}\nОшибка: {e}")
            raise ValueError(f"Невозможно создать SuperJob вакансию: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "id": self.vacancy_id,
            "profession": self.title,
            "link": self.url,
            "payment_from": self.salary.salary_from if self.salary else None,
            "payment_to": self.salary.salary_to if self.salary else None,
            "currency": self.salary.currency if self.salary else None,
            "vacancyRichText": self.description,
            "candidat": self.requirements,
            "work": self.responsibilities,
            "firm_name": self.employer.get("name") if self.employer else None,
            "experience": self.experience,
            "type_of_work": self.employment,
            "date_published": int(self.published_at.timestamp()) if self.published_at else None,
            "source": self.source
        }
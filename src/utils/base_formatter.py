import logging
from abc import ABC, abstractmethod
from typing import Any, List, Optional

logger = logging.getLogger(__name__)


class BaseFormatter(ABC):
    """Базовый класс для форматирования вакансий"""

    @staticmethod
    def _build_vacancy_lines(vacancy: Any, number: Optional[int] = None) -> List[str]:
        """
        Формирование списка строк с информацией о вакансии в едином порядке

        Args:
            vacancy: Объект вакансии
            number: Порядковый номер (опционально)

        Returns:
            Список строк с информацией о вакансии
        """
        lines = []

        # Номер вакансии
        if number:
            lines.append(f"{number}.")

        # ID
        vacancy_id = getattr(vacancy, "vacancy_id", None) or getattr(vacancy, "id", None)
        if vacancy_id:
            lines.append(f"ID: {vacancy_id}")

        # Название
        title = getattr(vacancy, "title", None) or getattr(vacancy, "name", None)
        if title:
            lines.append(f"Название: {title}")

        # Компания
        company_name = BaseFormatter._extract_company_name(vacancy)
        if company_name and company_name != "Не указана":
            lines.append(f"Компания: {company_name}")

        # Зарплата
        salary_info = BaseFormatter._extract_salary_info(vacancy)
        if salary_info and salary_info != "Не указана":
            lines.append(f"Зарплата: {salary_info}")

        # Опыт
        experience = getattr(vacancy, "experience", None)
        if experience:
            lines.append(f"Опыт: {experience}")

        # Занятость
        employment = getattr(vacancy, "employment", None)
        if employment:
            lines.append(f"Занятость: {employment}")

        # Источник
        source = getattr(vacancy, "source", None)
        if source:
            lines.append(f"Источник: {source}")

        # Ссылка
        url = getattr(vacancy, "url", None) or getattr(vacancy, "alternate_url", None)
        if url:
            lines.append(f"Ссылка: {url}")

        # Обязанности
        responsibilities = BaseFormatter._extract_responsibilities(vacancy)
        if responsibilities:
            resp_text = str(responsibilities)
            if len(resp_text) > 150:
                resp_text = resp_text[:150] + "..."
            lines.append(f"Обязанности: {resp_text}")

        # Требования
        requirements = BaseFormatter._extract_requirements(vacancy)
        if requirements:
            req_text = str(requirements)
            if len(req_text) > 150:
                req_text = req_text[:150] + "..."
            lines.append(f"Требования: {req_text}")

        # Условия
        conditions = BaseFormatter._extract_conditions(vacancy)
        if conditions:
            cond_text = str(conditions)
            if len(cond_text) > 150:
                cond_text = cond_text[:150] + "..."
            lines.append(f"Условия: {cond_text}")

        return lines

    @staticmethod
    def _extract_company_name(vacancy: Any) -> Optional[str]:
        """Извлечение названия компании"""
        employer = getattr(vacancy, "employer", None)
        if employer:
            if isinstance(employer, dict):
                return employer.get("name")
            else:
                return str(employer)
        return None

    @staticmethod
    def _extract_salary_info(vacancy: Any) -> Optional[str]:
        """Извлечение информации о зарплате"""
        salary = getattr(vacancy, "salary", None)
        if not salary:
            return None

        if isinstance(salary, dict):
            return BaseFormatter._format_salary_dict(salary)
        else:
            return str(salary)

    @staticmethod
    def _format_salary_dict(salary_dict: dict) -> str:
        """Форматирование словаря зарплаты"""
        if not salary_dict:
            return "Не указана"

        from_salary = salary_dict.get("from")
        to_salary = salary_dict.get("to")
        currency = salary_dict.get("currency", "RUR")

        # Конвертация валют в читаемый формат
        currency_map = {"RUR": "руб.", "RUB": "руб.", "USD": "долл.", "EUR": "евро"}
        currency_display = currency_map.get(currency, currency)

        if from_salary and to_salary:
            return f"от {from_salary:,} до {to_salary:,} {currency_display} в месяц".replace(",", " ")
        elif from_salary:
            return f"от {from_salary:,} {currency_display} в месяц".replace(",", " ")
        elif to_salary:
            return f"до {to_salary:,} {currency_display} в месяц".replace(",", " ")
        else:
            return "Не указана"

    @staticmethod
    def _extract_responsibilities(vacancy: Any) -> Optional[str]:
        """Извлечение обязанностей (базовая реализация)"""
        # В базовом классе используем универсальные поля
        return getattr(vacancy, "responsibilities", None)

    @staticmethod
    def _extract_requirements(vacancy: Any) -> Optional[str]:
        """Извлечение требований (базовая реализация)"""
        # В базовом классе используем универсальные поля
        return getattr(vacancy, "requirements", None)

    @staticmethod
    def _extract_conditions(vacancy: Any) -> Optional[str]:
        """Извлечение условий (базовая реализация)"""
        # В базовом классе проверяем стандартные поля
        conditions = getattr(vacancy, "conditions", None)
        if not conditions:
            # Также можем использовать график работы как условие
            schedule = getattr(vacancy, "schedule", None)
            if schedule:
                conditions = f"График: {schedule}"
        return conditions

    @abstractmethod
    def format_vacancy_info(self, vacancy: Any, number: Optional[int] = None) -> str:
        """Форматирование информации о вакансии в строку"""
        pass

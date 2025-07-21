import logging
from typing import Optional, List

from .base_formatter import BaseFormatter
from ..vacancies.models import Vacancy

logger = logging.getLogger(__name__)


class VacancyFormatter(BaseFormatter):
    """Класс для форматирования и отображения вакансий с поддержкой маппинга полей"""

    @staticmethod
    def _extract_responsibilities(vacancy) -> Optional[str]:
        """Извлечение обязанностей (парсеры уже правильно маппят поля)"""
        return getattr(vacancy, 'responsibilities', None)

    @staticmethod
    def _extract_requirements(vacancy) -> Optional[str]:
        """Извлечение требований (парсеры уже правильно маппят поля)"""
        return getattr(vacancy, 'requirements', None)

    @staticmethod
    def _extract_conditions(vacancy) -> Optional[str]:
        """Извлечение условий с учетом источника"""
        conditions_parts = []

        # График работы
        schedule = getattr(vacancy, 'schedule', None)
        if schedule:
            conditions_parts.append(f"График: {schedule}")

        # Можно добавить другие условия специфичные для разных источников
        source = getattr(vacancy, 'source', '')

        if source == 'hh.ru':
            # Специфичные для HH условия
            pass
        elif source == 'superjob.ru':
            # Специфичные для SJ условия
            pass

        return "; ".join(conditions_parts) if conditions_parts else None

    @staticmethod
    def format_vacancy_info(vacancy: Vacancy, number: Optional[int] = None) -> str:
        """
        Форматирование информации о вакансии в строку

        Args:
            vacancy: Объект вакансии
            number: Порядковый номер (опционально)

        Returns:
            Отформатированная строка с информацией о вакансии
        """
        lines = VacancyFormatter._build_vacancy_lines(vacancy, number)
        return "\n".join(lines) + "\n"

    @staticmethod
    def display_vacancy_info(vacancy: Vacancy, number: Optional[int] = None) -> None:
        """
        Отображение информации о вакансии

        Args:
            vacancy: Объект вакансии
            number: Порядковый номер (опционально)
        """
        lines = VacancyFormatter._build_vacancy_lines(vacancy, number)

        for line in lines:
            print(line)

        print()  # Один перевод строки между вакансиями

    @staticmethod
    def format_salary(salary_info) -> str:
        """
        Форматирование информации о зарплате

        Args:
            salary_info: Информация о зарплате

        Returns:
            Отформатированная строка с зарплатой
        """
        if not salary_info:
            return "Зарплата не указана"

        if isinstance(salary_info, dict):
            return VacancyFormatter._format_salary_dict(salary_info)

        return str(salary_info)

    @staticmethod
    def _build_vacancy_lines(vacancy: Vacancy, number: Optional[int] = None) -> List[str]:
        """
        Формирование списка строк с информацией о вакансии

        Args:
            vacancy: Объект вакансии
            number: Порядковый номер (опционально)

        Returns:
            Список строк с информацией о вакансии
            :type vacancy: Vacancy
        """
        lines = []

        # Добавляем номер отдельной строкой
        if number:
            lines.append(f"{number}.")

        # ID
        lines.append(f"ID: {vacancy.vacancy_id}")

        # Название
        title = vacancy.title or getattr(vacancy, 'name', None) or 'Не указано'
        lines.append(f"Название: {title}")

        # Компания
        company_name = 'Не указана'
        if vacancy.employer:
            if isinstance(vacancy.employer, dict):
                company_name = vacancy.employer.get('name', 'Не указана')
            else:
                company_name = str(vacancy.employer)
        lines.append(f"Компания: {company_name}")

        # Зарплата
        if vacancy.salary:
            lines.append(f"Зарплата: {vacancy.salary}")
        else:
            lines.append("Зарплата: Не указана")

        # Опыт
        if vacancy.experience:
            lines.append(f"Опыт: {vacancy.experience}")

        # Занятость
        if vacancy.employment:
            lines.append(f"Занятость: {vacancy.employment}")

        # Источник
        lines.append(f"Источник: {getattr(vacancy, 'source', 'Не указан')}")

        # Ссылка с преобразованием API-ссылок в веб-ссылки
        url = vacancy.url
        if isinstance(url, str) and url != 'Не указана':
            # Преобразуем API-ссылки HH в веб-ссылки
            if 'api.hh.ru/vacancies/' in url:
                import re
                match = re.search(r'/vacancies/(\d+)', url)
                if match:
                    vacancy_web_id = match.group(1)
                    url = f"https://hh.ru/vacancy/{vacancy_web_id}"
        
        lines.append(f"Ссылка: {url}")

        # Описание вакансии (объединенное поле)
        description_parts = []

        # Основное описание - сначала пробуем description, потом detailed_description
        main_description = getattr(vacancy, 'description', None)
        if not main_description or not str(main_description).strip():
            main_description = getattr(vacancy, 'detailed_description', None)
            
        if main_description and str(main_description).strip() and str(main_description).strip() != "Не указано" and str(main_description).strip() != "":
            # Очищаем HTML-теги и ограничиваем длину
            import re
            clean_description = re.sub(r'<[^>]+>', '', str(main_description))
            clean_description = clean_description.strip()
            if clean_description:
                if len(clean_description) > 150:
                    clean_description = clean_description[:150] + "..."
                description_parts.append(clean_description)

        # Обязанности
        responsibilities = VacancyFormatter._extract_responsibilities(vacancy)
        if responsibilities and str(responsibilities).strip() and str(responsibilities).strip() != "Не указано" and str(responsibilities).strip() != "":
            resp_text = str(responsibilities).strip()
            if len(resp_text) > 150:
                resp_text = resp_text[:150] + "..."
            description_parts.append(f"Обязанности: {resp_text}")

        # Требования
        requirements = VacancyFormatter._extract_requirements(vacancy)
        if requirements and str(requirements).strip() and str(requirements).strip() != "Не указано" and str(requirements).strip() != "":
            req_text = str(requirements).strip()
            if len(req_text) > 150:
                req_text = req_text[:150] + "..."
            description_parts.append(f"Требования: {req_text}")

        # Условия
        conditions = VacancyFormatter._extract_conditions(vacancy)
        if conditions and str(conditions).strip():
            cond_text = str(conditions).strip()
            if len(cond_text) > 100:
                cond_text = cond_text[:100] + "..."
            description_parts.append(f"Условия: {cond_text}")

        # Если есть хотя бы одна из частей описания, показываем её
        if description_parts:
            combined_description = "; ".join(description_parts)
            # Ограничиваем общую длину описания
            if len(combined_description) > 400:
                combined_description = combined_description[:400] + "..."
            lines.append(f"Описание вакансии: {combined_description}")
        else:
            # Если нет никакого описания, показываем заглушку для отладки
            lines.append("Описание вакансии: Описание отсутствует")

        return lines

    @staticmethod
    def format_company_info(employer_info) -> str:
        """
        Форматирование информации о компании
        Args:
            employer_info: Информация о работодателе
        Returns:
            Отформатированная строка с информацией о компании
        """
        if not employer_info:
            return "Не указана"

        if isinstance(employer_info, dict):
            return employer_info.get('name', 'Не указана')

        return str(employer_info)

    @staticmethod
    def _format_salary_dict(salary_info: dict) -> str:
        """
        Форматирование информации о зарплате из словаря
        """
        salary_str = ""
        from_value = salary_info.get('from')
        to_value = salary_info.get('to')
        currency = salary_info.get('currency')

        if from_value:
            salary_str += f"от {from_value} "
        if to_value:
            salary_str += f"до {to_value} "
        if currency:
            salary_str += currency

        return salary_str.strip() if salary_str else "Зарплата не указана"

    

# Глобальный экземпляр форматтера
vacancy_formatter = VacancyFormatter()
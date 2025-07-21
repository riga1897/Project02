from typing import List, Dict, Any
import logging
from ..models import Vacancy

logger = logging.getLogger(__name__)


class SuperJobParser:
    """Парсер для обработки данных вакансий SuperJob"""

    @staticmethod
    def parse_vacancies(vacancies_data: List[Dict[str, Any]]) -> List[Vacancy]:
        """
        Парсинг списка вакансий SuperJob

        Args:
            vacancies_data: Данные вакансий от API SuperJob

        Returns:
            List[SuperJobVacancy]: Список объектов вакансий
        """
        parsed_vacancies = []

        for vacancy_data in vacancies_data:
            try:
                vacancy = Vacancy.from_dict(vacancy_data)
                parsed_vacancies.append(vacancy)
            except ValueError as e:
                logger.warning(f"Пропуск вакансии SuperJob из-за ошибки валидации: {e}")
                continue
            except Exception as e:
                logger.error(f"Неожиданная ошибка при парсинге вакансии SuperJob: {e}")
                continue

        logger.info(f"Успешно распарсено {len(parsed_vacancies)} вакансий SuperJob из {len(vacancies_data)}")
        return parsed_vacancies

    @staticmethod
    def convert_to_unified_format(sj_vacancy: Vacancy) -> Dict[str, Any]:
        """
        Конвертация SuperJob вакансии в унифицированный формат

        Args:
            sj_vacancy: Объект вакансии SuperJob

        Returns:
            Dict[str, Any]: Унифицированный словарь вакансии
        """
        # Обрабатываем зарплату для корректного отображения
        salary_dict = None
        if sj_vacancy.salary:
            salary_dict = sj_vacancy.salary.to_dict()
            # Исправляем период для SuperJob
            if salary_dict and 'period' in salary_dict:
                if salary_dict['period'] in ['месяц', 'month']:
                    salary_dict['period'] = 'месяц'

        return {
            "id": sj_vacancy.vacancy_id,
            "name": sj_vacancy.title,
            "title": sj_vacancy.title,
            "url": sj_vacancy.url,
            "alternate_url": sj_vacancy.url,
            "salary": salary_dict,
            "description": sj_vacancy.description,
            # Для SJ: обязанности = vacancyRichText (description), требования = candidat (requirements)
            "requirements": sj_vacancy.requirements,  # candidat
            "responsibilities": sj_vacancy.description,  # vacancyRichText  
            "employer": sj_vacancy.employer,
            "experience": sj_vacancy.experience,
            "employment": sj_vacancy.employment,
            "schedule": sj_vacancy.schedule,
            "published_at": sj_vacancy.published_at.isoformat() if sj_vacancy.published_at else None,
            "skills": [],
            "keywords": [],
            "detailed_description": sj_vacancy.detailed_description,
            "benefits": sj_vacancy.benefits,
            "source": sj_vacancy.source
        }
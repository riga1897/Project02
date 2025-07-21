import logging
from typing import List, Dict

from src.vacancies.models import Vacancy
from src.vacancies.parsers.sj_parser import SuperJobParser
from .hh_api import HeadHunterAPI
from .sj_api import SuperJobAPI

logger = logging.getLogger(__name__)


class UnifiedAPI:
    """Унифицированный API для работы с несколькими источниками вакансий"""

    def __init__(self):
        self.hh_api = HeadHunterAPI()
        self.sj_api = SuperJobAPI()
        self.parser = SuperJobParser()

    @staticmethod
    def _deduplicate_cross_platform(all_vacancies: List[Dict]) -> List[Dict]:
        """
        Межплатформенная дедупликация вакансий из разных источников

        Args:
            all_vacancies: Список всех вакансий из разных источников

        Returns:
            List[Dict]: Список вакансий без дублей между платформами
        """
        if not all_vacancies:
            return []
            
        from tqdm import tqdm
        
        seen = set()
        unique_vacancies = []

        print("Выполняется поиск дубликатов между платформами...")
        with tqdm(total=len(all_vacancies), desc="Поиск дубликатов", unit="вакансия") as pbar:
            for vacancy in all_vacancies:
                # Универсальная логика для дедупликации между источниками
                title = vacancy.get('name', vacancy.get('profession', '')).lower().strip()
                company = vacancy.get('employer', {}).get('name', 
                         vacancy.get('firm_name', '')).lower().strip()

                # Нормализуем зарплату для межплатформенного сравнения
                salary_key = ''
                if 'salary' in vacancy and vacancy['salary']:
                    salary = vacancy['salary']
                    salary_from = salary.get('from', 0) or 0
                    salary_to = salary.get('to', 0) or 0
                    salary_key = f"{salary_from}-{salary_to}"
                elif 'payment_from' in vacancy:
                    salary_key = f"{vacancy.get('payment_from', 0)}-{vacancy.get('payment_to', 0)}"

                dedup_key = (title, company, salary_key)

                if dedup_key not in seen:
                    seen.add(dedup_key)
                    unique_vacancies.append(vacancy)
                else:
                    logger.debug(f"Межплатформенный дубль отфильтрован: {title} в {company}")
                
                pbar.update(1)

        duplicates_found = len(all_vacancies) - len(unique_vacancies)
        if duplicates_found > 0:
            print(f"Найдено и удалено {duplicates_found} дубликатов между платформами")
        
        logger.info(f"Межплатформенная дедупликация: {len(all_vacancies)} -> {len(unique_vacancies)} вакансий")
        return unique_vacancies

    def get_vacancies_from_sources(self, search_query: str, sources: List[str] = None, **kwargs) -> List[Dict]:
        """
        Получение вакансий из выбранных источников с дедупликацией

        Args:
            search_query: Поисковый запрос
            sources: Список источников ['hh', 'sj']
            **kwargs: Дополнительные параметры для API

        Returns:
            List[Dict]: Список всех уникальных вакансий
        """
        if sources is None:
            sources = self.get_available_sources()
        else:
            sources = self.validate_sources(sources)

        all_vacancies = []

        # Получение из HeadHunter с дедупликацией
        if 'hh' in sources:
            try:
                logger.info(f"Получение вакансий с HH.ru по запросу: '{search_query}'")
                hh_data = self.hh_api.get_vacancies_with_deduplication(search_query, **kwargs)
                hh_vacancies = [Vacancy.from_dict(item).to_dict() for item in hh_data]

                if hh_vacancies:
                    logger.info(f"Найдено {len(hh_vacancies)} уникальных вакансий с HH.ru")
                    all_vacancies.extend(hh_vacancies)

            except Exception as e:
                logger.error(f"Ошибка получения вакансий с HH.ru: {e}")

        # Получение из SuperJob
        if 'sj' in sources:
            try:
                logger.info(f"Получение вакансий с SuperJob по запросу: '{search_query}'")
                # Синхронизируем параметры периода между API
                sj_kwargs = kwargs.copy()
                if 'period' in kwargs:
                    # HH использует 'period', SuperJob использует 'published'
                    sj_kwargs['published'] = kwargs['period']
                    sj_kwargs.pop('period', None)  # Удаляем исходный параметр
                sj_data = self.sj_api.get_vacancies_with_deduplication(search_query, **sj_kwargs)

                if sj_data:
                    from tqdm import tqdm
                    
                    # Парсим данные SuperJob в объекты SuperJobVacancy с прогресс-баром
                    print(f"Парсинг {len(sj_data)} вакансий SuperJob...")
                    sj_vacancies_raw = self.parser.parse_vacancies(sj_data)

                    # Конвертируем SuperJobVacancy в унифицированный формат с прогресс-баром
                    sj_vacancies = []
                    print("Конвертация вакансий SuperJob в унифицированный формат...")
                    
                    with tqdm(total=len(sj_vacancies_raw), desc="Конвертация SJ", unit="вакансия") as pbar:
                        for sj_vac in sj_vacancies_raw:
                            try:
                                # Конвертируем SuperJobVacancy в унифицированный формат
                                unified_data = self.parser.convert_to_unified_format(sj_vac)
                                vacancy = Vacancy.from_dict(unified_data)
                                sj_vacancies.append(vacancy.to_dict())
                            except Exception as e:
                                logger.warning(f"Ошибка конвертации вакансии SuperJob: {e}")
                            finally:
                                pbar.update(1)

                    if sj_vacancies:
                        logger.info(f"Найдено {len(sj_vacancies)} уникальных вакансий с SuperJob")
                        all_vacancies.extend(sj_vacancies)
                    else:
                        logger.warning("SuperJob API не вернул вакансий")

            except Exception as e:
                logger.error(f"Ошибка получения вакансий из SJ: {e}")

        # Выводим общую статистику и применяем межплатформенную дедупликацию
        if all_vacancies:
            print(f"\nВсего найдено {len(all_vacancies)} вакансий")
            return self._deduplicate_cross_platform(all_vacancies)
        else:
            return []

    def get_hh_vacancies(self, query: str, **kwargs) -> List[Vacancy]:
        """Получение вакансий только с HH.ru с дедупликацией"""
        try:
            hh_data = self.hh_api.get_vacancies_with_deduplication(query, **kwargs)
            return [Vacancy.from_dict(item) for item in hh_data]
        except Exception as e:
            logger.error(f"Ошибка получения вакансий HH: {e}")
            return []

    def get_sj_vacancies(self, query: str, **kwargs) -> List[Vacancy]:
        """Получение вакансий только с SuperJob с дедупликацией"""
        try:
            # Синхронизируем параметры периода
            sj_kwargs = kwargs.copy()
            if 'period' in kwargs:
                # HH использует 'period', SuperJob использует 'published'
                sj_kwargs['published'] = kwargs['period']
                sj_kwargs.pop('period', None)  # Удаляем исходный параметр

            sj_data = self.sj_api.get_vacancies_with_deduplication(query, **sj_kwargs)

            # Парсим данные SuperJob в объекты SuperJobVacancy
            if sj_data:
                from tqdm import tqdm
                
                print(f"Парсинг {len(sj_data)} вакансий SuperJob...")
                sj_vacancies_raw = self.parser.parse_vacancies(sj_data)

                # Конвертируем SuperJobVacancy в унифицированный формат
                sj_vacancies = []
                print("Конвертация вакансий SuperJob в унифицированный формат...")
                
                with tqdm(total=len(sj_vacancies_raw), desc="Конвертация SJ", unit="вакансия") as pbar:
                    for sj_vac in sj_vacancies_raw:
                        try:
                            unified_data = self.parser.convert_to_unified_format(sj_vac)
                            vacancy = Vacancy.from_dict(unified_data)
                            sj_vacancies.append(vacancy)
                        except Exception as e:
                            logger.warning(f"Ошибка конвертации вакансии SuperJob: {e}")
                        finally:
                            pbar.update(1)

                return sj_vacancies
            return []
        except Exception as e:
            logger.error(f"Ошибка получения вакансий SJ: {e}")
            return []

    def clear_cache(self, sources: Dict[str, bool]) -> None:
        """
        Очистка кэша выбранных источников

        Args:
            sources: Словарь источников {'hh': bool, 'sj': bool}
        """
        try:
            if sources.get('hh', False):
                self.hh_api.clear_cache("hh")
                logger.info("Кэш HH.ru очищен")

            if sources.get('sj', False):
                self.sj_api.clear_cache("sj")
                logger.info("Кэш SuperJob очищен")

        except Exception as e:
            logger.error(f"Ошибка очистки кэша: {e}")

    def clear_all_cache(self) -> None:
        """Очистка кэша всех API"""
        # Очищаем кэш каждого API отдельно, чтобы ошибка в одном не влияла на другой
        try:
            self.hh_api.clear_cache("hh")
            logger.info("Кэш HH.ru очищен")
        except Exception as e:
            logger.error(f"Ошибка очистки кэша HH.ru: {e}")

        try:
            self.sj_api.clear_cache("sj")
            logger.info("Кэш SuperJob очищен")
        except Exception as e:
            logger.error(f"Ошибка очистки кэша SuperJob: {e}")

    @staticmethod
    def get_available_sources() -> List[str]:
        """Получение списка доступных источников"""
        return ['hh', 'sj']

    def validate_sources(self, sources: List[str]) -> List[str]:
        """Валидация списка источников"""
        available = self.get_available_sources()
        valid_sources = [s for s in sources if s in available]

        if not valid_sources:
            logger.warning(f"Нет валидных источников в {sources}, используем все доступные")
            return available

        return valid_sources

"""
Базовый модуль для работы с API поиска вакансий.

Содержит абстрактный базовый класс, который определяет единый интерфейс
для всех API источников вакансий (HH.ru, SuperJob и т.д.).
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict

logger = logging.getLogger(__name__)


class BaseJobAPI(ABC):
    """
    Базовый абстрактный класс для всех API поиска вакансий.
    
    Определяет единый интерфейс для работы с различными источниками вакансий,
    включая методы для получения, валидации и дедупликации вакансий.

    """
    
    @abstractmethod
    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict]:
        """
        Получение списка вакансий из источника по поисковому запросу.
        
        Args:
            search_query: Поисковый запрос для поиска вакансий
            **kwargs: Дополнительные параметры поиска (зарплата, опыт и т.д.)
            
        Returns:
            List[Dict]: Список найденных вакансий в формате словарей
        """

    
    @abstractmethod
    def _validate_vacancy(self, vacancy: Dict) -> bool:
        """
        Валидация структуры данных вакансии.
        
        Проверяет, что вакансия содержит все необходимые поля
        и соответствует ожидаемой структуре данных.
        
        Args:
            vacancy: Словарь с данными вакансии для валидации
            
        Returns:
            bool: True если структура валидна, False иначе
        """

    
    @staticmethod
    def _create_dedup_key(vacancy: Dict, source: str) -> tuple:
        """
        Создание универсального ключа дедупликации для любого источника
        
        Args:
            vacancy: Словарь с данными вакансии
            source: Источник вакансии ('hh' или 'sj')
        
        Returns:
            tuple: Ключ для дедупликации (title, company, salary_key)
        """
        # Универсальное получение названия
        if source == 'hh':
            title = vacancy.get('name', '').lower().strip()
            company = vacancy.get('employer', {}).get('name', '').lower().strip()
            
            # Обработка зарплаты для HH
            salary_key = ''
            if 'salary' in vacancy and vacancy['salary']:
                salary = vacancy['salary']
                salary_from = salary.get('from', 0) or 0
                salary_to = salary.get('to', 0) or 0
                salary_key = f"{salary_from}-{salary_to}"
                
        elif source == 'sj':
            title = vacancy.get('profession', '').lower().strip()
            company = vacancy.get('firm_name', '').lower().strip()
            
            # Обработка зарплаты для SJ
            salary_key = f"{vacancy.get('payment_from', 0)}-{vacancy.get('payment_to', 0)}"
        else:
            # Универсальная обработка
            title = (
                vacancy.get('title') or 
                vacancy.get('name') or 
                vacancy.get('profession') or ''
            ).lower().strip()
            
            company = (
                vacancy.get('employer', {}).get('name') or
                vacancy.get('firm_name') or ''
            ).lower().strip()
            
            salary_key = '0-0'  # Для неизвестных источников
        
        return title, company, salary_key
    
    def _deduplicate_vacancies(self, vacancies: List[Dict], source: str) -> List[Dict]:
        """
        Универсальная дедупликация вакансий
        
        Args:
            vacancies: Список вакансий
            source: Источник ('hh' или 'sj')
        
        Returns:
            List[Dict]: Список уникальных вакансий
        """
        seen = set()
        unique_vacancies = []

        for vacancy in vacancies:
            dedup_key = self._create_dedup_key(vacancy, source)
            
            if dedup_key not in seen:
                seen.add(dedup_key)
                unique_vacancies.append(vacancy)
            else:
                logger.debug(f"Дублирующаяся {source.upper()} вакансия отфильтрована: {dedup_key[0]} в {dedup_key[1]}")

        logger.info(f"{source.upper()} дедупликация: {len(vacancies)} -> {len(unique_vacancies)} вакансий")
        return unique_vacancies

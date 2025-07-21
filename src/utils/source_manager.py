from enum import Enum
from typing import Dict, List, Optional, Set


class DataSource(Enum):
    """Перечисление доступных источников данных"""

    HH = "hh"
    SUPERJOB = "sj"


class SourceManager:
    """Менеджер для работы с источниками данных"""

    SOURCE_NAMES = {DataSource.HH: "HeadHunter (hh.ru)", DataSource.SUPERJOB: "SuperJob (superjob.ru)"}

    SOURCE_URLS = {DataSource.HH: "https://hh.ru", DataSource.SUPERJOB: "https://superjob.ru"}

    @classmethod
    def get_all_sources(cls) -> List[DataSource]:
        """Получение списка всех доступных источников"""
        return list(DataSource)

    @classmethod
    def get_source_names(cls) -> Dict[DataSource, str]:
        """Получение словаря с именами источников"""
        return cls.SOURCE_NAMES.copy()

    @classmethod
    def get_source_name(cls, source: DataSource) -> str:
        """Получение имени источника"""
        return cls.SOURCE_NAMES.get(source, str(source.value))

    @classmethod
    def get_source_url(cls, source: DataSource) -> str:
        """Получение URL источника"""
        return cls.SOURCE_URLS.get(source, "")

    @classmethod
    def parse_sources_from_strings(cls, source_strings: List[str]) -> Set[str]:
        """
        Преобразование строковых названий источников в набор

        Args:
            source_strings: Список строковых названий источников

        Returns:
            Набор валидных источников
        """
        valid_sources = set()
        valid_source_values = {source.value for source in DataSource}

        for source_str in source_strings:
            if source_str.lower() in valid_source_values:
                valid_sources.add(source_str.lower())

        return valid_sources

    @classmethod
    def validate_sources(cls, sources: Optional[Set[str]]) -> Set[str]:
        """
        Валидация набора источников

        Args:
            sources: Набор источников для валидации

        Returns:
            Набор валидных источников
        """
        if sources is None:
            return {source.value for source in DataSource}

        valid_source_values = {source.value for source in DataSource}
        return {source for source in sources if source in valid_source_values}


# Глобальный экземпляр менеджера источников
source_manager = SourceManager()

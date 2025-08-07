from unittest.mock import Mock

from src.utils.source_manager import DataSource, SourceManager, source_manager


class TestDataSource:
    """Тест перечисления DataSource"""

    def test_enum_values(self):
        """Тест значений перечисления"""
        assert DataSource.HH.value == "hh"
        assert DataSource.SUPERJOB.value == "sj"


class TestSourceManager:
    """Тест менеджера источников данных"""

    def test_source_names_constant(self):
        """Тест константы с именами источников"""
        expected = {DataSource.HH: "HeadHunter (hh.ru)", DataSource.SUPERJOB: "SuperJob (superjob.ru)"}
        assert SourceManager.SOURCE_NAMES == expected

    def test_source_urls_constant(self):
        """Тест константы с URL источников"""
        expected = {DataSource.HH: "https://hh.ru", DataSource.SUPERJOB: "https://superjob.ru"}
        assert SourceManager.SOURCE_URLS == expected

    def test_get_all_sources(self):
        """Тест получения всех источников"""
        sources = SourceManager.get_all_sources()

        assert isinstance(sources, list)
        assert len(sources) == 2
        assert DataSource.HH in sources
        assert DataSource.SUPERJOB in sources

    def test_get_source_names(self):
        """Тест получения словаря с именами источников"""
        names = SourceManager.get_source_names()

        expected = {DataSource.HH: "HeadHunter (hh.ru)", DataSource.SUPERJOB: "SuperJob (superjob.ru)"}
        assert names == expected

        # Проверяем что возвращается копия
        names[DataSource.HH] = "Modified"
        assert SourceManager.SOURCE_NAMES[DataSource.HH] == "HeadHunter (hh.ru)"

    def test_get_source_name_existing(self):
        """Тест получения имени существующего источника"""
        name = SourceManager.get_source_name(DataSource.HH)
        assert name == "HeadHunter (hh.ru)"

        name = SourceManager.get_source_name(DataSource.SUPERJOB)
        assert name == "SuperJob (superjob.ru)"

    def test_get_source_name_non_existing(self):
        """Тест получения имени несуществующего источника"""
        mock_source = Mock()
        mock_source.value = "unknown"

        name = SourceManager.get_source_name(mock_source)
        assert name == "unknown"

    def test_get_source_url_existing(self):
        """Тест получения URL существующего источника"""
        url = SourceManager.get_source_url(DataSource.HH)
        assert url == "https://hh.ru"

        url = SourceManager.get_source_url(DataSource.SUPERJOB)
        assert url == "https://superjob.ru"

    def test_get_source_url_non_existing(self):
        """Тест получения URL несуществующего источника"""
        mock_source = Mock()

        url = SourceManager.get_source_url(mock_source)
        assert url == ""

    def test_parse_sources_from_strings_valid(self):
        """Тест парсинга валидных строк источников"""
        sources = SourceManager.parse_sources_from_strings(["hh", "sj"])
        assert sources == {"hh", "sj"}

    def test_parse_sources_from_strings_mixed_case(self):
        """Тест парсинга строк с разным регистром"""
        sources = SourceManager.parse_sources_from_strings(["HH", "SJ", "Hh"])
        assert sources == {"hh", "sj"}

    def test_parse_sources_from_strings_invalid(self):
        """Тест парсинга невалидных строк"""
        sources = SourceManager.parse_sources_from_strings(["invalid", "unknown"])
        assert sources == set()

    def test_parse_sources_from_strings_mixed_valid_invalid(self):
        """Тест парсинга смеси валидных и невалидных строк"""
        sources = SourceManager.parse_sources_from_strings(["hh", "invalid", "sj"])
        assert sources == {"hh", "sj"}

    def test_parse_sources_from_strings_empty(self):
        """Тест парсинга пустого списка"""
        sources = SourceManager.parse_sources_from_strings([])
        assert sources == set()

    def test_validate_sources_none(self):
        """Тест валидации None"""
        sources = SourceManager.validate_sources(None)
        assert sources == {"hh", "sj"}

    def test_validate_sources_valid(self):
        """Тест валидации валидных источников"""
        sources = SourceManager.validate_sources({"hh", "sj"})
        assert sources == {"hh", "sj"}

    def test_validate_sources_partial_valid(self):
        """Тест валидации частично валидных источников"""
        sources = SourceManager.validate_sources({"hh", "invalid"})
        assert sources == {"hh"}

    def test_validate_sources_all_invalid(self):
        """Тест валидации всех невалидных источников"""
        sources = SourceManager.validate_sources({"invalid", "unknown"})
        assert sources == set()

    def test_validate_sources_empty_set(self):
        """Тест валидации пустого множества"""
        sources = SourceManager.validate_sources(set())
        assert sources == set()


class TestGlobalSourceManager:
    """Тест глобального экземпляра менеджера источников"""

    def test_global_instance_exists(self):
        """Тест существования глобального экземпляра"""
        assert source_manager is not None
        assert isinstance(source_manager, SourceManager)

    def test_global_instance_methods(self):
        """Тест методов глобального экземпляра"""
        sources = source_manager.get_all_sources()
        assert len(sources) == 2

        name = source_manager.get_source_name(DataSource.HH)
        assert name == "HeadHunter (hh.ru)"
